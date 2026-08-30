from __future__ import annotations

from agent.state import InvestigationState
from integrations.aws_client import AWSClient


def aws_infra_node(
    state: InvestigationState,
) -> InvestigationState:
    """
    Inspect AWS infrastructure related to the affected service.
    """
    incident = state["incident"]

    client = AWSClient(
        aws_role_arn=incident.get("aws_role_arn"),
        region_name=incident.get("aws_region"),
    )

    try:
        result = client.investigate(
            service=incident.get("service", ""),
            code_context=state.get("code_context", {}),
            observability=state.get(
                "observability_data",
                {},
            ),
        )

        finding = {
            "source": "aws",
            "type": "infrastructure_state",
            "data": result,
        }

        return {
            "infrastructure_state": result,
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
            "source": "aws",
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