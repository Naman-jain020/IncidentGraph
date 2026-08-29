from functools import lru_cache

from langgraph.graph import END, START, StateGraph

from agent.router import route_after_reasoning
from agent.state import InvestigationState
from nodes.incident_trigger import incident_trigger_node
from nodes.reasoning import reasoning_node
from nodes.latentgraph import latentgraph_node
from nodes.github import github_node
from nodes.observability import observability_node
from nodes.aws_infra import aws_infra_node
from nodes.incident_history import incident_history_node
from nodes.rca import rca_node
from agent.checkpoint import get_checkpointer


def build_graph():
    """
    Build the IncidentGraph LangGraph workflow.

    The LLM reasoning node chooses the next investigation source.
    LangGraph performs the actual routing and state transitions.
    """
    workflow = StateGraph(InvestigationState)

    workflow.add_node(
        "incident_trigger",
        incident_trigger_node,
    )

    workflow.add_node(
        "reasoning",
        reasoning_node,
    )

    workflow.add_node(
        "latentgraph",
        latentgraph_node,
    )

    workflow.add_node(
        "github",
        github_node,
    )

    workflow.add_node(
        "observability",
        observability_node,
    )

    workflow.add_node(
        "aws_infra",
        aws_infra_node,
    )

    workflow.add_node(
        "incident_history",
        incident_history_node,
    )

    workflow.add_node(
        "rca",
        rca_node,
    )

    workflow.add_edge(
        START,
        "incident_trigger",
    )

    workflow.add_edge(
        "incident_trigger",
        "reasoning",
    )

    workflow.add_conditional_edges(
        "reasoning",
        route_after_reasoning,
        {
            "latentgraph": "latentgraph",
            "github": "github",
            "observability": "observability",
            "aws_infra": "aws_infra",
            "incident_history": "incident_history",
            "rca": "rca",
        },
    )

    # Every investigation source returns control to the
    # reasoning node so the LLM can evaluate the new state.
    workflow.add_edge(
        "latentgraph",
        "reasoning",
    )

    workflow.add_edge(
        "github",
        "reasoning",
    )

    workflow.add_edge(
        "observability",
        "reasoning",
    )

    workflow.add_edge(
        "aws_infra",
        "reasoning",
    )

    workflow.add_edge(
        "incident_history",
        "reasoning",
    )

    workflow.add_edge(
        "rca",
        END,
    )

    return workflow


@lru_cache(maxsize=1)
def get_investigation_graph():
    """
    Compile and cache the application-wide investigation graph.
    """
    workflow = build_graph()

    with get_checkpointer() as checkpointer:
        return workflow.compile(
            checkpointer=checkpointer
        )