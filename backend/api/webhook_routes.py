import hashlib
import hmac
import json

from flask import Blueprint, current_app, jsonify, request

from nodes.incident_trigger import create_incident_input
from agent.graph import get_investigation_graph


webhook_bp = Blueprint("webhooks", __name__)


def _verify_github_signature(
    payload: bytes,
    signature: str | None,
    secret: str | None,
) -> bool:
    if not secret:
        return False

    if not signature:
        return False

    expected = "sha256=" + hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, signature)


@webhook_bp.post("/github")
def github_webhook():
    """
    Receive GitHub push/deployment events.

    This endpoint is intentionally limited to triggering
    investigation/update workflows. It does not modify GitHub.
    """
    raw_payload = request.get_data()

    signature = request.headers.get("X-Hub-Signature-256")

    secret = current_app.config.get("GITHUB_WEBHOOK_SECRET")

    if secret and not _verify_github_signature(
        raw_payload,
        signature,
        secret,
    ):
        return jsonify({
            "error": "invalid_signature"
        }), 401

    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        return jsonify({
            "error": "invalid_payload"
        }), 400

    event = request.headers.get("X-GitHub-Event", "unknown")

    if event not in {
        "push",
        "deployment",
        "deployment_status",
    }:
        return jsonify({
            "status": "ignored",
            "event": event,
        }), 200

    return jsonify({
        "status": "accepted",
        "event": event,
        "message": "GitHub event received."
    }), 202


@webhook_bp.post("/cloudwatch")
def cloudwatch_webhook():
    """
    Receive normalized CloudWatch/SNS alarm events.

    The endpoint accepts an already delivered JSON event.
    AWS/SNS signature verification can be added when the
    production delivery mechanism is finalized.
    """
    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        return jsonify({
            "error": "invalid_payload"
        }), 400

    incident = payload.get("incident", payload)

    if not isinstance(incident, dict):
        return jsonify({
            "error": "invalid_incident"
        }), 400

    if not incident.get("service"):
        incident["service"] = payload.get(
            "service",
            "unknown-service"
        )

    if not incident.get("problem"):
        incident["problem"] = payload.get(
            "alarm_name",
            "CloudWatch alarm triggered"
        )

    try:
        initial_state = create_incident_input(incident)

        graph = get_investigation_graph()

        graph.invoke(
            initial_state,
            config={
                "configurable": {
                    "thread_id": initial_state[
                        "incident"
                    ]["incident_id"]
                }
            },
        )

        return jsonify({
            "status": "accepted",
            "incident_id": initial_state[
                "incident"
            ]["incident_id"],
        }), 202

    except Exception as exc:
        return jsonify({
            "error": "investigation_trigger_failed",
            "message": str(exc)
        }), 500