from __future__ import annotations

from typing import Any

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from agent.state import InvestigationState
from agent.prompts import RCA_SYSTEM_PROMPT
from config import Config
from services.incident_service import persist_incident


class RCAResult(BaseModel):
    root_cause: str
    evidence: list[str] = Field(default_factory=list)
    timeline: list[str] = Field(default_factory=list)
    blast_radius: list[str] = Field(default_factory=list)
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
    )
    recommended_fix: list[str] = Field(
        default_factory=list
    )


def rca_node(
    state: InvestigationState,
) -> InvestigationState:
    """
    Generate the final evidence-backed RCA.
    """
    if not Config.OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured."
        )

    llm = ChatOpenAI(
        model=Config.OPENAI_MODEL,
        api_key=Config.OPENAI_API_KEY,
        temperature=0,
    ).with_structured_output(RCAResult)

    context: dict[str, Any] = {
        "incident": state.get("incident"),
        "code_context": state.get("code_context"),
        "github_changes": state.get("github_changes"),
        "observability_data": state.get(
            "observability_data"
        ),
        "infrastructure_state": state.get(
            "infrastructure_state"
        ),
        "historical_findings": state.get(
            "historical_findings"
        ),
        "findings": state.get("findings"),
        "evidence": state.get("evidence"),
        "hypotheses": state.get("hypotheses"),
        "errors": state.get("errors"),
    }

    result = llm.invoke([
        (
            "system",
            RCA_SYSTEM_PROMPT,
        ),
        (
            "human",
            f"Investigation state:\n{context}",
        ),
    ])

    final_rca = result.model_dump()

    updated_state: InvestigationState = {
        "status": "completed",
        "final_rca": final_rca,
        "confidence": result.confidence / 100.0,
        "affected_components": [
            {
                "name": component,
                "impact": "potentially affected",
            }
            for component in result.blast_radius
        ],
    }

    # Persist the final investigation summary.
    try:
        persist_incident({
            "incident": state.get("incident", {}),
            "final_rca": final_rca,
            "findings": state.get("findings", []),
            "evidence": state.get("evidence", []),
            "affected_components": updated_state[
                "affected_components"
            ],
        })
    except Exception as exc:
        updated_state["errors"] = [
            *state.get("errors", []),
            {
                "source": "rca_persistence",
                "error": str(exc),
            },
        ]

    return updated_state