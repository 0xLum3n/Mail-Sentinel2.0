from app.threat_intel.enrichment import aggregate_results
from app.threat_intel.schemas import ThreatIntelResult


def test_malicious_evidence_wins_but_conflict_is_retained() -> None:
    result = aggregate_results(
        "IP",
        "1.2.3.4",
        (
            ThreatIntelResult(
                provider="virustotal",
                indicator_type="IP",
                value="1.2.3.4",
                verdict="Malicious",
                confidence_score=90,
            ),
            ThreatIntelResult(
                provider="abuseipdb",
                indicator_type="IP",
                value="1.2.3.4",
                verdict="Benign",
                confidence_score=5,
            ),
        ),
    )

    assert result.verdict == "Malicious"
    assert result.risk_weight == 30
    assert result.finding_severity == "HIGH"
    assert result.enrichment["conflicting_verdicts"] is True
    assert len(result.enrichment["providers"]) == 2


def test_unknown_context_does_not_raise_risk() -> None:
    result = aggregate_results(
        "URL",
        "https://example.test/login",
        (
            ThreatIntelResult(
                provider="urlscan",
                indicator_type="URL",
                value="https://example.test/login",
                verdict="Unknown",
            ),
        ),
    )

    assert result.verdict == "Unknown"
    assert result.risk_weight == 0
    assert result.finding_severity is None


def test_all_benign_evidence_is_benign_without_negative_scoring() -> None:
    result = aggregate_results(
        "DOMAIN",
        "example.com",
        (
            ThreatIntelResult(
                provider="virustotal",
                indicator_type="DOMAIN",
                value="example.com",
                verdict="Benign",
                confidence_score=99,
            ),
            ThreatIntelResult(
                provider="urlscan",
                indicator_type="DOMAIN",
                value="example.com",
                verdict="Benign",
                confidence_score=95,
            ),
        ),
    )

    assert result.verdict == "Benign"
    assert result.risk_weight == 0
    assert result.finding_severity is None
