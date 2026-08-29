from datetime import datetime, timezone

from integrations.database import session_scope
from models.database import Incident


def seed_demo_incidents():
    incidents = [
        Incident(
            incident_id="INC-DEMO001",
            service="payment-service",
            problem="Payment API error rate increased",
            severity="critical",
            status="resolved",
            root_cause=(
                "A recent deployment introduced an invalid "
                "payment timeout configuration."
            ),
            confidence=0.93,
            created_at=datetime(
                2026,
                8,
                29,
                14,
                30,
                tzinfo=timezone.utc,
            ),
        ),
        Incident(
            incident_id="INC-DEMO002",
            service="order-service",
            problem="Order processing latency increased",
            severity="high",
            status="resolved",
            root_cause=(
                "Database connection pool saturation caused "
                "request queuing."
            ),
            confidence=0.87,
            created_at=datetime(
                2026,
                8,
                28,
                10,
                15,
                tzinfo=timezone.utc,
            ),
        ),
    ]

    with session_scope() as session:
        for incident in incidents:
            existing = (
                session.query(Incident)
                .filter(
                    Incident.incident_id
                    == incident.incident_id
                )
                .one_or_none()
            )

            if existing is None:
                session.add(incident)

    print("Demo incidents seeded successfully.")


if __name__ == "__main__":
    seed_demo_incidents()