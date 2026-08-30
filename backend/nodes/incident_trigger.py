from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from agent.state import InvestigationState


def create_incident_input(payload: dict[str, Any]) -> InvestigationState:
    """
    Convert an incoming API/webhook payload into the initial
    LangGraph investigation state, including user-provided repository,
    AWS IAM roles, observability, and MCP configurations.
    """
    incident_id = payload.get("incident_id") or f"INC-{uuid4().hex[:8].upper()}"

    incident = {
        "incident_id": incident_id,
        "service": payload.get("service", "unknown-service"),
        "problem": payload.get("problem", "Unknown production issue"),
        "severity": payload.get("severity", "unknown"),
        "timestamp": payload.get(
            "timestamp",
            datetime.now(timezone.utc).isoformat(),
        ),
        "repository": payload.get("repository", ""),
        "source": payload.get("source", "manual"),
        # Dynamic User-provided Configurations & Integrations
        "aws_role_arn": payload.get("aws_role_arn", ""),
        "aws_region": payload.get("aws_region", "us-east-1"),
        "log_group_name": payload.get("log_group_name", ""),
        "mcp_url": payload.get("mcp_url", ""),
        "mcp_api_key": payload.get("mcp_api_key", ""),
    }

    return {
        "incident": incident,
        "status": "investigating",
        "current_step": 0,
        "next_action": "latentgraph",
        "investigation_history": [],
        "findings": [],
        "evidence": [],
        "hypotheses": [],
        "code_context": {},
        "github_changes": {},
        "infrastructure_state": {},
        "observability_data": {},
        "historical_findings": [],
        "affected_components": [],
        "confidence": 0.0,
        "final_rca": {},
        "errors": [],
    }


def incident_trigger_node(
    state: InvestigationState,
) -> InvestigationState:
    """
    LangGraph entry node.

    If the API has already initialized the incident state,
    preserve it and only ensure required fields exist.
    """
    incident = state.get("incident", {})

    if not incident:
        raise ValueError("Incident information is required.")

    return {
        "status": "investigating",
        "current_step": state.get("current_step", 0),
        "findings": state.get("findings", []),
        "evidence": state.get("evidence", []),
        "hypotheses": state.get("hypotheses", []),
        "investigation_history": state.get(
            "investigation_history",
            [],
        ),
        "errors": state.get("errors", []),
    }