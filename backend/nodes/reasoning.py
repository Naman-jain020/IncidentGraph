from __future__ import annotations

from typing import Literal

from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from agent.state import InvestigationState
from agent.prompts import INVESTIGATION_SYSTEM_PROMPT
from config import Config


class InvestigationDecision(BaseModel):
    next_action: Literal[
        "latentgraph",
        "github",
        "observability",
        "aws_infra",
        "incident_history",
        "rca",
    ]

    reason: str = Field(min_length=1)
    query: str = Field(min_length=1)
    hypothesis: str = ""
    confidence: float = Field(default=0.0, ge=0.0, le=100.0)


def _build_reasoning_context(
    state: InvestigationState,
) -> str:
    return f"""
CURRENT INCIDENT:
{state.get("incident", {})}

CURRENT STEP:
{state.get("current_step", 0)}

CODE CONTEXT:
{state.get("code_context", {})}

GITHUB CHANGES:
{state.get("github_changes", {})}

OBSERVABILITY:
{state.get("observability_data", {})}

AWS / INFRASTRUCTURE:
{state.get("infrastructure_state", {})}

HISTORICAL FINDINGS:
{state.get("historical_findings", [])}

AFFECTED COMPONENTS:
{state.get("affected_components", [])}

CURRENT HYPOTHESES:
{state.get("hypotheses", [])}

PREVIOUS FINDINGS:
{state.get("findings", [])}

PREVIOUS EVIDENCE:
{state.get("evidence", [])}

INVESTIGATION HISTORY:
{state.get("investigation_history", [])}

ERRORS:
{state.get("errors", [])}
"""


def _get_llm():
    return ChatGoogleGenerativeAI(
        model=Config.GEMINI_MODEL,
        google_api_key=Config.GEMINI_API_KEY,
        temperature=0,
    )


def reasoning_node(
    state: InvestigationState,
) -> InvestigationState:
    """
    Decide which specialized investigation node should run next.
    """

    current_step = state.get("current_step", 0) + 1

    if current_step > Config.MAX_INVESTIGATION_STEPS:
        return {
            "current_step": current_step,
            "next_action": "rca",
            "investigation_history": [
                *state.get("investigation_history", []),
                {
                    "node": "reasoning",
                    "decision": "rca",
                    "reason": "Maximum investigation steps reached.",
                },
            ],
        }

    if not Config.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    incident = state.get("incident", {})

    # Check permissions & user-provided credentials
    has_aws_permission = bool(incident.get("aws_role_arn"))
    has_mcp_permission = bool(incident.get("mcp_url")) or bool(Config.LATENTGRAPH_API_KEY)
    has_log_permission = bool(incident.get("log_group_name")) or bool(Config.CLOUDWATCH_LOG_GROUP)

    disabled_actions = []
    if not has_aws_permission:
        disabled_actions.append("aws_infra")
    if not has_mcp_permission:
        disabled_actions.append("latentgraph")
    if not has_log_permission:
        disabled_actions.append("observability")

    system_prompt = INVESTIGATION_SYSTEM_PROMPT
    if disabled_actions:
        system_prompt += f"\n\nCRITICAL CONSTRAINTS: The user HAS NOT granted access to: {', '.join(disabled_actions)}. DO NOT select any of these actions under any circumstances."

    llm = _get_llm().with_structured_output(
        InvestigationDecision
    )

    messages = [
        (
            "system",
            system_prompt,
        ),
        (
            "human",
            _build_reasoning_context(state),
        ),
    ]

    decision = llm.invoke(messages)

    final_action = decision.next_action
    if final_action in disabled_actions:
        final_action = "github" if "github" not in disabled_actions else "rca"

    history_entry = {
        "node": "reasoning",
        "step": current_step,
        "decision": final_action,
        "reason": decision.reason,
        "query": decision.query,
        "hypothesis": decision.hypothesis,
        "confidence": decision.confidence,
    }

    hypotheses = list(state.get("hypotheses", []))

    if decision.hypothesis:
        hypotheses.append({
            "step": current_step,
            "hypothesis": decision.hypothesis,
            "confidence": decision.confidence,
        })

    return {
        "current_step": current_step,
        "next_action": final_action,
        "confidence": decision.confidence / 100.0,
        "hypotheses": hypotheses,
        "investigation_history": [
            *state.get("investigation_history", []),
            history_entry,
        ],
    }