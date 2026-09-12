"""AbuseIPDB provider adapter for IP reputation."""

from __future__ import annotations

from typing import Any

import httpx

from app.core.config import get_settings
from app.threat_intel.schemas import ThreatIntelLookup, ThreatIntelResult


class AbuseIPDBProvider:
    """Read-only AbuseIPDB lookup adapter."""

    BASE_URL = "https://api.abuseipdb.com/api/v2/check"

    def __init__(self, *, client: httpx.AsyncClient | None = None) -> None:
        self._client = client

    @property
    def name(self) -> str:
        return "abuseipdb"

    def supports(self, indicator_type: str) -> bool:
        return indicator_type.upper() == "IP"

    @property
    def enabled(self) -> bool:
        return bool(get_settings().abuseipdb_api_key)

    async def lookup(self, lookup: ThreatIntelLookup) -> ThreatIntelResult | None:
        if not self.enabled or not self.supports(lookup.indicator_type):
            return None

        owns_client = self._client is None
        client = self._client or httpx.AsyncClient(timeout=get_settings().threat_intel_timeout_seconds)
        try:
            response = await client.get(
                self.BASE_URL,
                params={"ipAddress": lookup.value, "maxAgeInDays": 90},
                headers={"Key": get_settings().abuseipdb_api_key or "", "Accept": "application/json"},
            )
            response.raise_for_status()
            payload = response.json()
        finally:
            if owns_client:
                await client.aclose()

        return self._normalize(lookup, payload)

    def _normalize(self, lookup: ThreatIntelLookup, payload: dict[str, Any]) -> ThreatIntelResult:
        data = payload.get("data", {}) or {}
        score = data.get("abuseConfidenceScore")
        score_int = int(score) if isinstance(score, (int, float)) else None
        if score_int is None:
            verdict = "Unknown"
        elif score_int >= 80:
            verdict = "Malicious"
        elif score_int >= 25:
            verdict = "Suspicious"
        else:
            verdict = "Benign"
        categories = tuple(str(value) for value in (data.get("usageType"),) if value)
        return ThreatIntelResult(
            provider=self.name,
            indicator_type="IP",
            value=lookup.value,
            verdict=verdict,
            confidence_score=score_int,
            malicious=score_int >= 80 if score_int is not None else None,
            reputation=score_int,
            categories=categories,
            details={
                "country_code": data.get("countryCode"),
                "isp": data.get("isp"),
                "domain": data.get("domain"),
                "total_reports": data.get("totalReports"),
                "last_reported_at": data.get("lastReportedAt"),
            },
        )
