from typing import Literal

from agent.state import InvestigationState


Route = Literal[
    "latentgraph",
    "github",
    "observability",
    "aws_infra",
    "incident_history",
    "rca",
]


VALID_ROUTES: set[str] = {
    "latentgraph",
    "github",
    "observability",
    "aws_infra",
    "incident_history",
    "rca",
}


def route_after_reasoning(state: InvestigationState) -> Route:
    """
    Route the investigation according to the structured
    decision produced by the reasoning node.
    """
    action = state.get("next_action", "rca")

    if action not in VALID_ROUTES:
        return "rca"

    return action  # type: ignore[return-value]