"""Deterministic analysis of email authentication and routing headers."""

from __future__ import annotations

import re
from dataclasses import dataclass


_AUTH_VALUE_RE = re.compile(r"\b(spf|dkim|dmarc)\s*=\s*([a-zA-Z]+)", re.IGNORECASE)
_RECEIVED_IP_RE = re.compile(r"\[(\d{1,3}(?:\.\d{1,3}){3})\]")


@dataclass(frozen=True, slots=True)
class HeaderAnalysis:
    """Normalized, explainable header-analysis results."""

    spf: str
    dkim: str
    dmarc: str
    authentication_results_found: bool
    sender_reply_to_mismatch: bool
    sender_domain: str | None
    reply_to_domain: str | None
    received_ips: tuple[str, ...]


def _normalize_auth_result(value: str) -> str:
    value = value.strip().upper()
    if value in {"PASS", "FAIL", "SOFTFAIL", "NEUTRAL", "NONE", "TEMPERROR", "PERMERROR"}:
        return value
    return "UNKNOWN"


def _domain_from_email(value: str | None) -> str | None:
    if not value or "@" not in value:
        return None
    domain = value.rsplit("@", 1)[1].strip().lower().strip("<>[]")
    return domain or None


def analyze_headers(
    headers: dict[str, str],
    *,
    sender_email: str | None,
    reply_to_email: str | None,
) -> HeaderAnalysis:
    """Extract authentication results and simple routing anomalies.

    This intentionally does not perform network lookups. Header values are
    evidence supplied by the email and are not treated as cryptographic proof.
    """
    results = {"spf": "UNKNOWN", "dkim": "UNKNOWN", "dmarc": "UNKNOWN"}
    found = False
    for key, value in headers.items():
        if key.lower() != "authentication-results":
            continue
        found = True
        for match in _AUTH_VALUE_RE.finditer(value):
            results[match.group(1).lower()] = _normalize_auth_result(match.group(2))

    sender_domain = _domain_from_email(sender_email)
    reply_to_domain = _domain_from_email(reply_to_email)
    mismatch = bool(sender_domain and reply_to_domain and sender_domain != reply_to_domain)

    received_ips: list[str] = []
    for key, value in headers.items():
        if key.lower() != "received":
            continue
        received_ips.extend(_RECEIVED_IP_RE.findall(value))

    # Preserve first-seen order while deduplicating.
    unique_ips = tuple(dict.fromkeys(received_ips))
    return HeaderAnalysis(
        spf=results["spf"],
        dkim=results["dkim"],
        dmarc=results["dmarc"],
        authentication_results_found=found,
        sender_reply_to_mismatch=mismatch,
        sender_domain=sender_domain,
        reply_to_domain=reply_to_domain,
        received_ips=unique_ips,
    )
