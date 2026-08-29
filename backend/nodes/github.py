from __future__ import annotations

from agent.state import InvestigationState
from integrations.github_client import GitHubClient


def github_node(
    state: InvestigationState,
) -> InvestigationState:
    """
    Retrieve recent commits, PRs and deployments relevant to
    the affected service.
    """
    incident = state["incident"]

    client = GitHubClient()

    try:
        result = client.investigate(
            repository=incident.get("repository", ""),
            service=incident.get("service", ""),
            incident_time=incident.get("timestamp", ""),
            code_context=state.get("code_context", {}),
        )

        finding = {
            "source": "github",
            "type": "change_and_deployment",
            "data": result,
        }

        return {
            "github_changes": result,
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
            "source": "github",
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