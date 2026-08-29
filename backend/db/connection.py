from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Config
from models.database import Base


engine = create_engine(
    Config.DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def init_db() -> None:
    """
    Create database tables.

    Production deployments should use Alembic migrations instead
    of relying on create_all().
    """
    Base.metadata.create_all(
        bind=engine
    )


def get_db():
    """
    Flask-friendly database dependency.
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()