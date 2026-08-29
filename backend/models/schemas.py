from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class IncidentCreate(BaseModel):
    service: str
    problem: str
    severity: str = "unknown"
    timestamp: datetime | None = None
    repository: str | None = None
    source: str = "manual"


class EvidenceSchema(BaseModel):
    source: str
    type: str
    data: Any


class RCAResponse(BaseModel):
    root_cause: str
    evidence: list[str] = Field(
        default_factory=list
    )
    timeline: list[str] = Field(
        default_factory=list
    )
    blast_radius: list[str] = Field(
        default_factory=list
    )
    confidence: float = Field(
        ge=0,
        le=100,
    )
    recommended_fix: list[str] = Field(
        default_factory=list
    )


class IncidentResponse(BaseModel):
    incident_id: str
    service: str
    problem: str
    severity: str
    status: Literal[
        "investigating",
        "completed",
        "failed",
    ]
    confidence: float
    final_rca: RCAResponse | None = None