from agent.graph import build_graph
from agent.router import route_after_reasoning


def test_router_routes_to_latentgraph():
    state = {
        "next_action": "latentgraph"
    }

    assert (
        route_after_reasoning(state)
        == "latentgraph"
    )


def test_router_defaults_to_rca_for_invalid_action():
    state = {
        "next_action": "invalid-node"
    }

    assert route_after_reasoning(state) == "rca"


def test_graph_contains_expected_nodes():
    graph = build_graph()

    compiled = graph.compile()

    expected_nodes = {
        "incident_trigger",
        "reasoning",
        "latentgraph",
        "github",
        "observability",
        "aws_infra",
        "incident_history",
        "rca",
    }

    assert expected_nodes.issubset(
        set(compiled.nodes.keys())
    )