from flask import Blueprint, jsonify, request

from nodes.incident_trigger import create_incident_input
from agent.graph import get_investigation_graph
from config import Config


incident_bp = Blueprint("incidents", __name__)


@incident_bp.post("")
def create_incident():
    """
    Start a new incident investigation.

    Expected JSON:
    {
        "service": "PaymentService",
        "problem": "Payment failures increased",
        "severity": "critical",
        "timestamp": "2026-08-29T14:32:00Z",
        "repository": "owner/repository"
    }
    """
    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        return jsonify({
            "error": "invalid_request",
            "message": "Request body must be a JSON object."
        }), 400

    required_fields = ("service", "problem")

    missing = [
        field
        for field in required_fields
        if not payload.get(field)
    ]

    if missing:
        return jsonify({
            "error": "missing_fields",
            "fields": missing
        }), 400

    try:
        initial_state = create_incident_input(payload)

        graph = get_investigation_graph()

        result = graph.invoke(
            initial_state,
            config={
                "configurable": {
                    "thread_id": initial_state["incident"]["incident_id"]
                },
                "recursion_limit": Config.MAX_INVESTIGATION_STEPS * 2,
            },
        )

        return jsonify({
            "incident": result.get("incident"),
            "status": result.get("status"),
            "findings": result.get("findings", []),
            "evidence": result.get("evidence", []),
            "affected_components": result.get(
                "affected_components",
                []
            ),
            "confidence": result.get("confidence", 0),
            "final_rca": result.get("final_rca"),
            "investigation_history": result.get(
                "investigation_history",
                []
            ),
        }), 200

    except Exception as exc:
        return jsonify({
            "error": "investigation_failed",
            "message": str(exc)
        }), 500


@incident_bp.get("/<incident_id>")
def get_incident(incident_id: str):
    """
    Retrieve the latest persisted LangGraph state for an incident.
    """
    try:
        graph = get_investigation_graph()

        state = graph.get_state({
            "configurable": {
                "thread_id": incident_id
            }
        })

        if not state or not state.values:
            return jsonify({
                "error": "not_found",
                "message": f"Incident {incident_id} was not found."
            }), 404

        return jsonify(state.values), 200

    except Exception as exc:
        return jsonify({
            "error": "state_retrieval_failed",
            "message": str(exc)
        }), 500