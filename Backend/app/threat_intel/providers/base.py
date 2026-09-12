"""Provider contract for external threat-intelligence services."""

from __future__ import annotations

from typing import Protocol

from app.threat_intel.schemas import ThreatIntelLookup, ThreatIntelResult


class ThreatIntelProvider(Protocol):
    """Protocol implemented by concrete threat-intelligence providers."""

    @property
    def name(self) -> str: ...

    def supports(self, indicator_type: str) -> bool: ...

    async def lookup(self, lookup: ThreatIntelLookup) -> ThreatIntelResult | None: ...
