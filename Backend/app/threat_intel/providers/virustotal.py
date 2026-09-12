"""VirusTotal provider adapter.

The adapter intentionally depends only on stdlib + httpx. It is disabled when
no API key is configured, and it normalizes responses into our internal schema.
"""

from __future__ import annotations

import ipaddress
from typing import Any

import httpx

from app.core.config import get_settings
from app.threat_intel.schemas import ThreatIntelLookup, ThreatIntelResult


class VirusTotalProvider:
    """Read-only VirusTotal reputation lookups for supported IOC types."""

    BASE_URL = "https://www.virustotal.com/api/v3"

    def __init__(self, *, client: httpx.AsyncClient | None = None) -> None:
        self._client = client

    @property
    def name(self) -> str:
        return "virustotal"

    def supports(self, indicator_type: str) -> bool:
        return indicator_type.upper() in {"IP", "DOMAIN", "URL", "HASH"}

    @property
    def enabled(self) -> bool:
        return bool(get_settings().virustotal_api_key)

    async def lookup(self, lookup: ThreatIntelLookup) -> ThreatIntelResult | None:
        if not self.enabled or not self.supports(lookup.indicator_type):
            return None

        endpoint = self._endpoint_for(lookup)
        headers = {"x-apikey": get_settings().virustotal_api_key or ""}
        owns_client = self._client is None
        client = self._client or httpx.AsyncClient(timeout=get_settings().threat_intel_timeout_seconds)
        try:
            response = await client.get(endpoint, headers=headers)
            response.raise_for_status()
            payload = response.json()
        finally:
            if owns_client:
                await client.aclose()

        return self._normalize(lookup, payload)

    def _endpoint_for(self, lookup: ThreatIntelLookup) -> str:
        indicator_type = lookup.indicator_type.upper()
        value = lookup.value
        if indicator_type == "IP":
            return f"{self.BASE_URL}/ip_addresses/{ipaddress.ip_address(value)}"
        if indicator_type == "DOMAIN":
            return f"{self.BASE_URL}/domains/{value.lower()}"
        if indicator_type == "HASH":
            return f"{self.BASE_URL}/files/{value.lower()}"
        if indicator_type == "URL":
            import base64

            identifier = base64.urlsafe_b64encode(value.encode()).decode().rstrip("=")
            return f"{self.BASE_URL}/urls/{identifier}"
        raise ValueError(f"Unsupported VirusTotal indicator type: {lookup.indicator_type}")

    def _normalize(self, lookup: ThreatIntelLookup, payload: dict[str, Any]) -> ThreatIntelResult:
        attributes = payload.get("data", {}).get("attributes", {})
        stats = attributes.get("last_analysis_stats", {}) or {}
        malicious = bool(stats.get("malicious", 0) or stats.get("suspicious", 0))
        total = sum(int(value or 0) for value in stats.values() if isinstance(value, int))
        bad = int(stats.get("malicious", 0) or 0) + int(stats.get("suspicious", 0) or 0)
        confidence = round((bad / total) * 100) if total else None
        verdict = "Malicious" if malicious else "Benign" if total else "Unknown"
        return ThreatIntelResult(
            provider=self.name,
            indicator_type=lookup.indicator_type.upper(),
            value=lookup.value,
            verdict=verdict,
            confidence_score=confidence,
            malicious=malicious if total else None,
            categories=tuple(_extract_categories(attributes)),
            details={"analysis_stats": stats, "reputation": attributes.get("reputation")},
        )


def _extract_categories(attributes: dict[str, Any]) -> list[str]:
    categories = attributes.get("categories")
    if isinstance(categories, dict):
        return sorted({str(value) for value in categories.values() if value})
    if isinstance(categories, list):
        return sorted({str(value) for value in categories if value})
    return []
