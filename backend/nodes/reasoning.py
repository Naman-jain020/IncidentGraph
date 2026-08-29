from __future__ import annotations

from typing import Literal

from langchain_openai import ChatOpenAI
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
    return ChatOpenAI(
        model=Config.OPENAI_MODEL,
        api_key=Config.OPENAI_API_KEY,
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

    if not Config.OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured."
        )

    llm = _get_llm().with_structured_output(
        InvestigationDecision
    )

    messages = [
        (
            "system",
            INVESTIGATION_SYSTEM_PROMPT,
        ),
        (
            "human",
            _build_reasoning_context(state),
        ),
    ]

    decision = llm.invoke(messages)

    history_entry = {
        "node": "reasoning",
        "step": current_step,
        "decision": decision.next_action,
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
        "next_action": decision.next_action,
        "confidence": decision.confidence / 100.0,
        "hypotheses": hypotheses,
        "investigation_history": [
            *state.get("investigation_history", []),
            history_entry,
        ],
    }