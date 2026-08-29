from __future__ import annotations

from agent.state import InvestigationState
from integrations import database
from models.database import Incident


def incident_history_node(
    state: InvestigationState,
) -> InvestigationState:
    """
    Search previous incidents for similar service/error patterns.
    """
    incident = state["incident"]

    service = incident.get("service", "")
    problem = incident.get("problem", "")

    try:
        with database.session_scope() as session:
            incidents = (
                session.query(Incident)
                .filter(
                    Incident.service == service,
                )
                .order_by(
                    Incident.created_at.desc()
                )
                .limit(10)
                .all()
            )

            historical = []

            for item in incidents:
                historical.append({
                    "incident_id": item.incident_id,
                    "service": item.service,
                    "problem": item.problem,
                    "severity": item.severity,
                    "status": item.status,
                    "root_cause": item.root_cause,
                    "confidence": item.confidence,
                    "created_at": (
                        item.created_at.isoformat()
                        if item.created_at
                        else None
                    ),
                })

        finding = {
            "source": "incident_history",
            "type": "historical_incidents",
            "query": {
                "service": service,
                "problem": problem,
            },
            "data": historical,
        }

        return {
            "historical_findings": historical,
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
            "source": "incident_history",
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