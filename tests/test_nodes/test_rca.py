from unittest.mock import patch

from nodes.rca import RCAResult, rca_node


def test_rca_node_generates_final_rca():
    state = {
        "incident": {
            "incident_id": "INC-TEST123",
            "service": "payment-service",
            "problem": "Payment failures increased",
        },
        "findings": [
            {
                "source": "github",
                "type": "deployment",
                "data": {
                    "commit": "abc123"
                },
            }
        ],
        "evidence": [
            {
                "source": "observability",
                "type": "runtime_evidence",
                "data": {
                    "error_rate": 85
                },
            }
        ],
        "code_context": {},
        "github_changes": {},
        "observability_data": {},
        "infrastructure_state": {},
        "historical_findings": [],
        "hypotheses": [],
        "errors": [],
    }

    rca = RCAResult(
        root_cause="A faulty deployment introduced a payment "
        "processing regression.",
        evidence=[
            "Error rate increased immediately after deployment."
        ],
        timeline=[
            "Deployment completed.",
            "Payment errors increased.",
        ],
        blast_radius=[
            "payment-service"
        ],
        confidence=92,
        recommended_fix=[
            "Rollback the faulty deployment."
        ],
    )

    class FakeLLM:
        def with_structured_output(self, _):
            return self

        def invoke(self, _):
            return rca

    with patch(
        "nodes.rca.ChatGoogleGenerativeAI",
        return_value=FakeLLM(),
    ), patch(
        "nodes.rca.Config.GEMINI_API_KEY",
        "mock-gemini-key",
    ), patch(
        "nodes.rca.persist_incident"
    ):
        result = rca_node(state)

    assert result["status"] == "completed"
    assert result["final_rca"]["confidence"] == 92
    assert result["confidence"] == 0.92