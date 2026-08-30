from unittest.mock import patch

from nodes.reasoning import (
    InvestigationDecision,
    reasoning_node,
)


def test_reasoning_node_returns_structured_decision():
    state = {
        "incident": {
            "incident_id": "INC-TEST123",
            "service": "payment-service",
            "problem": "Payment failures increased",
        },
        "current_step": 0,
        "findings": [],
        "evidence": [],
        "hypotheses": [],
        "investigation_history": [],
        "errors": [],
    }

    decision = InvestigationDecision(
        next_action="latentgraph",
        reason="The code path needs to be identified.",
        query="Find the payment failure code path.",
        hypothesis="A recent code change may have introduced "
        "the failure.",
        confidence=60,
    )

    class FakeLLM:
        def with_structured_output(self, _):
            return self

        def invoke(self, _):
            return decision

    with patch(
        "nodes.reasoning._get_llm",
        return_value=FakeLLM(),
    ), patch(
        "nodes.reasoning.Config.GEMINI_API_KEY",
        "mock-gemini-key",
    ):
        result = reasoning_node(state)

    assert result["next_action"] == "latentgraph"
    assert result["current_step"] == 1
    assert len(
        result["investigation_history"]
    ) == 1