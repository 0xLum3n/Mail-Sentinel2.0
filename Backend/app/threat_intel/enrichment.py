"""Turn provider results into safe, explainable IOC enrichment evidence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.threat_intel.schemas import ThreatIntelBatchResult, ThreatIntelLookup, ThreatIntelResult


_SUPPORTED_TYPES = {"IP", "URL", "DOMAIN", "HASH"}
_VERDICT_RANK = {"Unknown": 0, "Benign": 1, "Suspicious": 2, "Malicious": 3, "Phishing": 4}


@dataclass(frozen=True, slots=True)
class IndicatorEnrichment:
    """Aggregated evidence for one extracted indicator."""

    verdict: str
    confidence_score: int | None
    source: str
    enrichment: dict[str, Any]
    risk_weight: int
    finding_severity: str | None


def build_lookups(indicators: list[Any]) -> tuple[ThreatIntelLookup, ...]:
    """Create de-duplicated provider lookup requests for supported IOC types."""
    seen: set[tuple[str, str]] = set()
    lookups: list[ThreatIntelLookup] = []
    for indicator in indicators:
        indicator_type = str(indicator.type).upper()
        value = str(indicator.value).strip()
        key = (indicator_type, value.lower())
        if indicator_type not in _SUPPORTED_TYPES or not value or key in seen:
            continue
        seen.add(key)
        lookups.append(ThreatIntelLookup(indicator_type=indicator_type, value=value))
    return tuple(lookups)


def aggregate_results(
    indicator_type: str,
    value: str,
    results: tuple[ThreatIntelResult, ...],
) -> IndicatorEnrichment:
    """Aggregate provider evidence without allowing one weak result to erase another."""
    matches = [
        result
        for result in results
        if result.indicator_type.upper() == indicator_type.upper()
        and result.value.strip().lower() == value.strip().lower()
    ]
    useful = [result for result in matches if result.verdict != "Unknown"]
    verdicts = [result.verdict for result in useful]

    strong_malicious = [
        result for result in useful
        if result.verdict in {"Malicious", "Phishing"}
        and (result.confidence_score is None or result.confidence_score >= 70)
    ]
    suspicious = [result for result in useful if result.verdict == "Suspicious"]

    if strong_malicious:
        verdict = "Malicious"
        risk_weight = 30
        finding_severity = "HIGH"
    elif suspicious or any(result.verdict in {"Malicious", "Phishing"} for result in useful):
        verdict = "Suspicious"
        risk_weight = 15
        finding_severity = "MEDIUM"
    elif useful and all(result.verdict == "Benign" for result in useful):
        verdict = "Benign"
        risk_weight = 0
        finding_severity = None
    else:
        verdict = "Unknown"
        risk_weight = 0
        finding_severity = None

    confidence_values = [r.confidence_score for r in useful if r.confidence_score is not None]
    confidence = max(confidence_values) if confidence_values else None
    if len({r.verdict for r in useful}) > 1 and confidence is not None:
        confidence = min(confidence, 80)

    provider_names = sorted({result.provider for result in matches})
    serialized = [_serialize_result(result) for result in matches]
    return IndicatorEnrichment(
        verdict=verdict,
        confidence_score=confidence,
        source=f"threat_intel:{','.join(provider_names)}" if provider_names else "threat_intel",
        enrichment={
            "providers": serialized,
            "provider_count": len(provider_names),
            "conflicting_verdicts": len(set(verdicts)) > 1,
        },
        risk_weight=risk_weight,
        finding_severity=finding_severity,
    )


def _serialize_result(result: ThreatIntelResult) -> dict[str, Any]:
    return {
        "provider": result.provider,
        "indicator_type": result.indicator_type,
        "value": result.value,
        "verdict": result.verdict,
        "confidence_score": result.confidence_score,
        "malicious": result.malicious,
        "reputation": result.reputation,
        "categories": list(result.categories),
        "details": result.details,
        "cached": result.cached,
    }
