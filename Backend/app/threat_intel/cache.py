"""Redis-backed cache for normalized threat-intelligence results."""

from __future__ import annotations

import json
from dataclasses import asdict

from typing import TYPE_CHECKING

from app.core.config import get_settings
from app.threat_intel.schemas import ThreatIntelResult

if TYPE_CHECKING:
    from redis.asyncio import Redis


class ThreatIntelCache:
    """Small cache wrapper that keeps Redis details out of provider code."""

    PREFIX = "ti:v1"

    def __init__(self, redis: "Redis") -> None:
        self.redis = redis

    def _key(self, provider: str, indicator_type: str, value: str) -> str:
        normalized = value.strip().lower()
        return f"{self.PREFIX}:{provider}:{indicator_type.upper()}:{normalized}"

    async def get(self, provider: str, indicator_type: str, value: str) -> ThreatIntelResult | None:
        raw = await self.redis.get(self._key(provider, indicator_type, value))
        if not raw:
            return None
        payload = json.loads(raw)
        payload["cached"] = True
        return ThreatIntelResult(**payload)

    async def set(self, result: ThreatIntelResult) -> None:
        payload = asdict(result)
        payload["categories"] = list(result.categories)
        payload["cached"] = False
        await self.redis.set(
            self._key(result.provider, result.indicator_type, result.value),
            json.dumps(payload, separators=(",", ":")),
            ex=get_settings().threat_intel_cache_ttl_seconds,
        )
