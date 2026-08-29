from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.database import Base, Incident


def test_incident_model():
    engine = create_engine(
        "sqlite:///:memory:",
        future=True,
    )

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)

    with Session() as session:
        incident = Incident(
            incident_id="INC-TEST123",
            service="payment-service",
            problem="Payment failure",
            severity="critical",
            status="investigating",
            confidence=0.8,
            created_at=datetime.now(timezone.utc),
        )

        session.add(incident)
        session.commit()

        result = (
            session.query(Incident)
            .filter_by(
                incident_id="INC-TEST123"
            )
            .one()
        )

        assert result.service == "payment-service"
        assert result.severity == "critical"