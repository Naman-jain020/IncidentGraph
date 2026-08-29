from __future__ import annotations

from agent.state import InvestigationState
from integrations.observability_client import ObservabilityClient


def observability_node(
    state: InvestigationState,
) -> InvestigationState:
    """
    Collect logs, metrics and traces for the affected service.
    """
    incident = state["incident"]

    client = ObservabilityClient()

    try:
        result = client.investigate(
            service=incident.get("service", ""),
            incident_time=incident.get("timestamp", ""),
            code_context=state.get("code_context", {}),
        )

        finding = {
            "source": "observability",
            "type": "runtime_evidence",
            "data": result,
        }

        return {
            "observability_data": result,
            "findings": [
                *state.get("findings", []),
                finding,
            ],
            "evidence": [
                *state.get("evidence", []),
                finding,
            ],
        }

    except Exception as exc:
        error = {
            "source": "observability",
            "error": str(exc),
        }

        return {
            "errors": [
                *state.get("errors", []),
                error,
            ],
            "findings": [
                *state.get("findings", []),
                error,
            ],
        }