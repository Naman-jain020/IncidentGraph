from __future__ import annotations

from typing import Any

from agent.state import InvestigationState
from integrations.latentgraph_client import LatentGraphClient


def _extract_query(state: InvestigationState) -> str:
    history = state.get("investigation_history", [])

    for item in reversed(history):
        if item.get("node") == "reasoning":
            return item.get(
                "query",
                f"Understand the code involved in {state['incident']['service']}",
            )

    return (
        f"Understand the code and dependencies of "
        f"{state['incident']['service']}"
    )


def latentgraph_node(
    state: InvestigationState,
) -> InvestigationState:
    """
    Gather code intelligence from LatentGraph.
    """
    incident = state["incident"]

    client = LatentGraphClient(
        repository=incident.get("repository", ""),
    )

    query = _extract_query(state)

    try:
        result = client.investigate(
            service=incident.get("service", ""),
            query=query,
        )

        finding = {
            "source": "latentgraph",
            "type": "code_intelligence",
            "service": incident.get("service"),
            "data": result,
        }

        code_context = dict(
            state.get("code_context", {})
        )

        code_context.update(result)

        return {
            "code_context": code_context,
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
            "source": "latentgraph",
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