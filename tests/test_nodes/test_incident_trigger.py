from nodes.incident_trigger import (
    create_incident_input,
    incident_trigger_node,
)


def test_create_incident_input():
    payload = {
        "service": "payment-service",
        "problem": "Payment requests are failing",
        "severity": "critical",
        "repository": "acme/payment-service",
        "timestamp": "2026-08-29T14:30:00Z",
        "source": "test",
    }

    state = create_incident_input(payload)

    assert state["incident"]["service"] == "payment-service"
    assert (
        state["incident"]["problem"]
        == "Payment requests are failing"
    )
    assert state["incident"]["severity"] == "critical"
    assert state["incident"]["repository"] == (
        "acme/payment-service"
    )
    assert state["status"] == "investigating"
    assert state["findings"] == []
    assert state["evidence"] == []


def test_incident_trigger_node_preserves_state():
    state = {
        "incident": {
            "incident_id": "INC-TEST123",
            "service": "payment-service",
            "problem": "High error rate",
        },
        "findings": [
            {"source": "test"}
        ],
        "evidence": [],
        "hypotheses": [],
        "investigation_history": [],
        "errors": [],
    }

    result = incident_trigger_node(state)

    assert result["status"] == "investigating"
    assert result["current_step"] == 0
    assert result["findings"] == [
        {"source": "test"}
    ]