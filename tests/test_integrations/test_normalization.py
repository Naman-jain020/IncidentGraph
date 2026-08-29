from services.normalization import (
    canonical_service_name,
    merge_findings,
    normalize_evidence,
)


def test_canonical_service_name():
    assert (
        canonical_service_name("Payment_Service")
        == "payment-service"
    )

    assert (
        canonical_service_name("service/payment-service")
        == "payment-service"
    )


def test_normalize_evidence():
    result = normalize_evidence(
        source="github",
        evidence_type="commit",
        data={"sha": "abc123"},
    )

    assert result == {
        "source": "github",
        "type": "commit",
        "data": {"sha": "abc123"},
    }


def test_merge_findings():
    first = [
        {"source": "github"}
    ]

    second = [
        {"source": "aws"}
    ]

    result = merge_findings(first, second)

    assert result == [
        {"source": "github"},
        {"source": "aws"},
    ]