import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _get_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)

    if value is None:
        return default

    return int(value)


class Config:
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret-key")
    DEBUG = _get_bool("FLASK_DEBUG", False)
    HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    PORT = _get_int("FLASK_PORT", 5000)

    # Frontend
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173"
        ).split(",")
        if origin.strip()
    ]

    # PostgreSQL
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://incidentgraph:incidentgraph@localhost:5432/incidentgraph",
    )

    # Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv(
        "GEMINI_MODEL",
        "gemini-flash-latest"
    )

    # GitHub
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GITHUB_API_URL = os.getenv(
        "GITHUB_API_URL",
        "https://api.github.com"
    )

    # AWS
    AWS_REGION = os.getenv(
        "AWS_REGION",
        "ap-south-1"
    )

    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN")

    # Observability
    CLOUDWATCH_LOG_GROUP = os.getenv("CLOUDWATCH_LOG_GROUP")
    CLOUDWATCH_METRIC_NAMESPACE = os.getenv(
        "CLOUDWATCH_METRIC_NAMESPACE",
        "IncidentGraph"
    )

    # LatentGraph / LatentCode
    LATENTGRAPH_MCP_URL = os.getenv("LATENTGRAPH_MCP_URL")
    LATENTGRAPH_API_KEY = os.getenv("LATENTGRAPH_API_KEY")

    # LangGraph
    LANGGRAPH_CHECKPOINT_ENABLED = _get_bool(
        "LANGGRAPH_CHECKPOINT_ENABLED",
        True,
    )

    # Webhook security
    GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")
    AWS_WEBHOOK_SECRET = os.getenv("AWS_WEBHOOK_SECRET")

    # Investigation limits
    MAX_INVESTIGATION_STEPS = _get_int(
        "MAX_INVESTIGATION_STEPS",
        12,
    )

    DEFAULT_INCIDENT_LOOKBACK_MINUTES = _get_int(
        "DEFAULT_INCIDENT_LOOKBACK_MINUTES",
        30,
    )