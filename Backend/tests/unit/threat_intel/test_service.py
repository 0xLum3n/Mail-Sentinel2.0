from __future__ import annotations

import asyncio
from dataclasses import replace

from app.threat_intel.schemas import ThreatIntelLookup, ThreatIntelResult
from app.threat_intel.service import ThreatIntelService


class FakeCache:
    def __init__(self) -> None:
        self.values: dict[tuple[str, str, str], ThreatIntelResult] = {}

    async def get(self, provider: str, indicator_type: str, value: str):
        result = self.values.get((provider, indicator_type, value))
        return replace(result, cached=True) if result is not None else None

    async def set(self, result: ThreatIntelResult) -> None:
        self.values[(result.provider, result.indicator_type, result.value)] = result


class FakeProvider:
    name = "fake"

    def __init__(self, result: ThreatIntelResult | None) -> None:
        self.result = result
        self.calls = 0

    def supports(self, indicator_type: str) -> bool:
        return indicator_type == "IP"

    async def lookup(self, lookup: ThreatIntelLookup):
        self.calls += 1
        return self.result


def test_service_caches_provider_result() -> None:
    async def scenario() -> None:
        cache = FakeCache()
        provider = FakeProvider(
            ThreatIntelResult(
                provider="fake",
                indicator_type="IP",
                value="8.8.8.8",
                verdict="Benign",
            )
        )
        service = ThreatIntelService(cache=cache, providers=(provider,))

        first = await service.enrich((ThreatIntelLookup("IP", "8.8.8.8"),))
        second = await service.enrich((ThreatIntelLookup("IP", "8.8.8.8"),))

        assert len(first.results) == 1
        assert len(second.results) == 1
        assert provider.calls == 1
        assert second.results[0].cached is True
    asyncio.run(scenario())
