from __future__ import annotations

from typing import Any

from integrations import database
from models.database import (
    AffectedComponent,
    Evidence,
    Incident,
    Investigation,
    Recommendation,
)


def persist_incident(
    result: dict[str, Any],
) -> None:
    incident_data = result.get(
        "incident",
        {},
    )

    final_rca = result.get(
        "final_rca",
        {},
    )

    incident_id = incident_data.get(
        "incident_id"
    )

    if not incident_id:
        raise ValueError(
            "incident_id is required."
        )

    with database.session_scope() as session:
        incident = (
            session.query(Incident)
            .filter(
                Incident.incident_id == incident_id
            )
            .one_or_none()
        )

        if incident is None:
            incident = Incident(
                incident_id=incident_id,
                service=incident_data.get(
                    "service",
                    "unknown-service",
                ),
                problem=incident_data.get(
                    "problem",
                    "",
                ),
                severity=incident_data.get(
                    "severity",
                    "unknown",
                ),
                status="resolved",
                root_cause=final_rca.get(
                    "root_cause",
                    "",
                ),
                confidence=float(
                    final_rca.get(
                        "confidence",
                        0,
                    )
                ) / 100.0,
            )

            session.add(incident)

        investigation = Investigation(
            incident_id=incident_id,
            current_step=0,
            status="completed",
            agent_state=result,
        )

        session.add(investigation)

        for evidence in result.get(
            "evidence",
            [],
        ):
            session.add(
                Evidence(
                    incident_id=incident_id,
                    source=evidence.get(
                        "source",
                        "unknown",
                    ),
                    evidence_type=evidence.get(
                        "type",
                        "unknown",
                    ),
                    finding=evidence,
                )
            )

        for component in result.get(
            "affected_components",
            [],
        ):
            session.add(
                AffectedComponent(
                    incident_id=incident_id,
                    component_name=component.get(
                        "name",
                        "unknown",
                    ),
                    component_type=component.get(
                        "type",
                        "unknown",
                    ),
                    impact_level=component.get(
                        "impact",
                        "unknown",
                    ),
                )
            )

        for recommendation in final_rca.get(
            "recommended_fix",
            [],
        ):
            session.add(
                Recommendation(
                    incident_id=incident_id,
                    recommendation=recommendation,
                    priority="normal",
                    reason=final_rca.get(
                        "root_cause",
                        "",
                    ),
                    status="proposed",
                )
            )