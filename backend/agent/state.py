from typing import Any, TypedDict


class Incident(TypedDict, total=False):
    incident_id: str
    service: str
    problem: str
    severity: str
    timestamp: str
    repository: str
    source: str


class InvestigationState(TypedDict, total=False):
    # Incident
    incident: Incident
    status: str

    # Investigation
    current_step: int
    next_action: str
    investigation_history: list[dict[str, Any]]

    # Evidence
    findings: list[dict[str, Any]]
    evidence: list[dict[str, Any]]
    hypotheses: list[dict[str, Any]]

    # Source-specific context
    code_context: dict[str, Any]
    github_changes: dict[str, Any]
    infrastructure_state: dict[str, Any]
    observability_data: dict[str, Any]
    historical_findings: list[dict[str, Any]]

    # Impact
    affected_components: list[dict[str, Any]]

    # Final reasoning
    confidence: float
    final_rca: dict[str, Any]

    # Error handling
    errors: list[dict[str, Any]]