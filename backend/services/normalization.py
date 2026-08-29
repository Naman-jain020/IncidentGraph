from __future__ import annotations

import re
from typing import Any


def canonical_service_name(
    value: str | None,
) -> str:
    if not value:
        return "unknown-service"

    value = value.strip()

    value = re.sub(
        r"^service[:/\s-]*",
        "",
        value,
        flags=re.IGNORECASE,
    )

    value = value.replace("_", "-")

    return value.lower()


def normalize_evidence(
    source: str,
    evidence_type: str,
    data: Any,
) -> dict[str, Any]:
    return {
        "source": source,
        "type": evidence_type,
        "data": data,
    }


def merge_findings(
    *finding_lists: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []

    for findings in finding_lists:
        for finding in findings:
            if finding not in merged:
                merged.append(finding)

    return merged