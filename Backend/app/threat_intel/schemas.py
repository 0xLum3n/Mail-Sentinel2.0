"""Schemas used by the threat-intelligence enrichment layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ThreatIntelLookup:
    """A normalized indicator lookup request."""

    indicator_type: str
    value: str


@dataclass(frozen=True, slots=True)
class ThreatIntelResult:
    """Provider-independent enrichment result."""

    provider: str
    indicator_type: str
    value: str
    verdict: str
    confidence_score: int | None = None
    malicious: bool | None = None
    reputation: int | None = None
    categories: tuple[str, ...] = ()
    details: dict[str, Any] = field(default_factory=dict)
    cached: bool = False


@dataclass(frozen=True, slots=True)
class ThreatIntelBatchResult:
    """Combined result for one analysis enrichment pass."""

    results: tuple[ThreatIntelResult, ...]
    provider_errors: dict[str, str] = field(default_factory=dict)
