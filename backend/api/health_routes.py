from datetime import datetime, timezone

from flask import Blueprint, jsonify


health_bp = Blueprint("health", __name__)


@health_bp.get("")
def health():
    return jsonify({
        "status": "ok",
        "service": "incidentgraph-backend",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }), 200


@health_bp.get("/ready")
def readiness():
    """
    Basic application readiness check.

    External dependency checks will be added once the
    integration clients and database layer are implemented.
    """
    return jsonify({
        "status": "ready",
        "dependencies": {
            "database": "not_checked",
            "latentgraph": "not_checked",
            "github": "not_checked",
            "aws": "not_checked",
            "observability": "not_checked",
        },
    }), 200