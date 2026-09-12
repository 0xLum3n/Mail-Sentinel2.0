"""Threat-intelligence orchestration and cache-aware enrichment."""

from __future__ import annotations

import asyncio
import logging

from app.threat_intel.cache import ThreatIntelCache
from app.threat_intel.providers.abuseipdb import AbuseIPDBProvider
from app.threat_intel.providers.base import ThreatIntelProvider
from app.threat_intel.providers.urlscan import UrlscanProvider
from app.threat_intel.providers.virustotal import VirusTotalProvider
from app.threat_intel.schemas import ThreatIntelBatchResult, ThreatIntelLookup, ThreatIntelResult

logger = logging.getLogger(__name__)


class ThreatIntelService:
    """Run enabled provider lookups and normalize their evidence."""

    def __init__(self, *, cache: ThreatIntelCache, providers: tuple[ThreatIntelProvider, ...] | None = None) -> None:
        self.cache = cache
        self.providers = providers or (
            VirusTotalProvider(),
            AbuseIPDBProvider(),
            UrlscanProvider(),
        )

    async def enrich(self, lookups: tuple[ThreatIntelLookup, ...]) -> ThreatIntelBatchResult:
        tasks = [self._enrich_one(lookup, provider) for lookup in lookups for provider in self.providers if provider.supports(lookup.indicator_type)]
        if not tasks:
            return ThreatIntelBatchResult(results=())

        outcomes = await asyncio.gather(*tasks, return_exceptions=True)
        results: list[ThreatIntelResult] = []
        errors: dict[str, str] = {}
        for outcome in outcomes:
            if isinstance(outcome, Exception):
                provider_name = getattr(outcome, "provider", "unknown")
                errors[provider_name] = str(outcome)
                logger.warning("Threat-intelligence provider failure: %s", outcome)
            elif outcome is not None:
                results.append(outcome)
        return ThreatIntelBatchResult(results=tuple(results), provider_errors=errors)

    async def _enrich_one(self, lookup: ThreatIntelLookup, provider: ThreatIntelProvider) -> ThreatIntelResult | None:
        # Cache availability is an optimization, not a prerequisite for an
        # analysis. A Redis outage must not turn an otherwise valid IOC lookup
        # into an analysis failure.
        try:
            cached = await self.cache.get(provider.name, lookup.indicator_type, lookup.value)
        except Exception as exc:
            logger.warning("Threat-intelligence cache read failed: %s", exc)
            cached = None
        if cached is not None:
            return cached

        try:
            result = await provider.lookup(lookup)
        except Exception as exc:
            error = RuntimeError(f"{provider.name}: {exc}")
            setattr(error, "provider", provider.name)
            raise error from exc

        if result is not None:
            try:
                await self.cache.set(result)
            except Exception as exc:
                logger.warning("Threat-intelligence cache write failed: %s", exc)
        return result
