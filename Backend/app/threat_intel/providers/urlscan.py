"""urlscan.io provider adapter for URL/domain visibility."""

from __future__ import annotations

from typing import Any

import httpx

from app.core.config import get_settings
from app.threat_intel.schemas import ThreatIntelLookup, ThreatIntelResult


class UrlscanProvider:
    """Read-only urlscan.io search adapter.

    Search results are treated as contextual evidence rather than a definitive
    malicious verdict because absence of a hit does not imply safety.
    """

    BASE_URL = "https://urlscan.io/api/v1/search/"

    def __init__(self, *, client: httpx.AsyncClient | None = None) -> None:
        self._client = client

    @property
    def name(self) -> str:
        return "urlscan"

    def supports(self, indicator_type: str) -> bool:
        return indicator_type.upper() in {"URL", "DOMAIN"}

    @property
    def enabled(self) -> bool:
        return bool(get_settings().urlscan_api_key)

    async def lookup(self, lookup: ThreatIntelLookup) -> ThreatIntelResult | None:
        if not self.enabled or not self.supports(lookup.indicator_type):
            return None

        query = f'page.url:"{lookup.value}"' if lookup.indicator_type.upper() == "URL" else f'domain:"{lookup.value.lower()}"'
        owns_client = self._client is None
        client = self._client or httpx.AsyncClient(timeout=get_settings().threat_intel_timeout_seconds)
        try:
            response = await client.get(
                self.BASE_URL,
                params={"q": query, "size": 5},
                headers={"API-Key": get_settings().urlscan_api_key or "", "Accept": "application/json"},
            )
            response.raise_for_status()
            payload = response.json()
        finally:
            if owns_client:
                await client.aclose()

        return self._normalize(lookup, payload)

    def _normalize(self, lookup: ThreatIntelLookup, payload: dict[str, Any]) -> ThreatIntelResult:
        results = payload.get("results", [])
        results = results if isinstance(results, list) else []
        return ThreatIntelResult(
            provider=self.name,
            indicator_type=lookup.indicator_type.upper(),
            value=lookup.value,
            verdict="Unknown",
            details={
                "observations": [
                    {
                        "scan_id": item.get("_id"),
                        "page_url": item.get("page", {}).get("url"),
                        "task_time": item.get("task", {}).get("time"),
                    }
                    for item in results[:5]
                    if isinstance(item, dict)
                ],
                "result_count": len(results),
            },
        )
