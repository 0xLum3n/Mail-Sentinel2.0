"""Deterministic extraction of common email indicators of compromise."""

from __future__ import annotations

import hashlib
import ipaddress
import re
from dataclasses import dataclass
from urllib.parse import urlparse


_URL_RE = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
_EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
_DOMAIN_RE = re.compile(r"(?<![@\w.-])(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,63}\b", re.IGNORECASE)
_HASH_RE = re.compile(r"\b(?:[a-f0-9]{32}|[a-f0-9]{40}|[a-f0-9]{64})\b", re.IGNORECASE)
_TRAILING_PUNCTUATION = ".,;:!?)]}>\"'"


@dataclass(frozen=True, slots=True)
class ExtractedIndicator:
    """A normalized IOC with its evidence source."""

    type: str
    value: str
    context: str


def _clean_url(value: str) -> str:
    return value.rstrip(_TRAILING_PUNCTUATION)


def _is_public_ip(value: str) -> bool:
    try:
        address = ipaddress.ip_address(value)
    except ValueError:
        return False
    return not (
        address.is_private
        or address.is_loopback
        or address.is_link_local
        or address.is_multicast
        or address.is_reserved
        or address.is_unspecified
    )


def _extract_url_host(url: str) -> str | None:
    try:
        hostname = urlparse(url).hostname
    except ValueError:
        return None
    return hostname.lower() if hostname else None


def extract_indicators(
    *,
    body_text: str | None,
    body_html: str | None,
    headers: dict[str, str],
    sender_email: str | None,
    reply_to_email: str | None,
    attachment_sha256s: tuple[str, ...] = (),
) -> list[ExtractedIndicator]:
    """Extract URLs, domains, public IPs, email addresses and file hashes.

    Extraction is intentionally conservative and deterministic. It does not
    declare an IOC malicious; enrichment and the scoring engine do that later.
    """
    text = "\n".join(part for part in (body_text, body_html) if part)
    indicators: list[ExtractedIndicator] = []
    seen: set[tuple[str, str]] = set()

    def add(kind: str, value: str, context: str) -> None:
        normalized = value.strip()
        if not normalized:
            return
        key = (kind, normalized.lower())
        if key in seen:
            return
        seen.add(key)
        indicators.append(ExtractedIndicator(kind, normalized, context))

    for raw_url in _URL_RE.findall(text):
        url = _clean_url(raw_url)
        add("URL", url, "message body")
        host = _extract_url_host(url)
        if not host:
            continue
        try:
            ipaddress.ip_address(host)
        except ValueError:
            add("DOMAIN", host, "URL host")
        else:
            if _is_public_ip(host):
                add("IP", host, "URL host")

    for value in _EMAIL_RE.findall(text):
        add("EMAIL", value.lower(), "message body")

    for value in (sender_email, reply_to_email):
        if value:
            add("EMAIL", value.lower(), "message header")

    for value in _DOMAIN_RE.findall(text):
        lowered = value.lower()
        try:
            ipaddress.ip_address(lowered)
        except ValueError:
            add("DOMAIN", lowered, "message text")

    for value in _HASH_RE.findall(text):
        add("HASH", value.lower(), "message text")

    for sha256 in attachment_sha256s:
        if re.fullmatch(r"[a-f0-9]{64}", sha256, re.IGNORECASE):
            add("HASH", sha256.lower(), "attachment SHA-256")

    for key, value in headers.items():
        header_text = f"{key}: {value}"
        for ip in re.findall(r"(?<![\d.])(\d{1,3}(?:\.\d{1,3}){3})(?![\d.])", header_text):
            if _is_public_ip(ip):
                add("IP", ip, key)
        for raw_hash in _HASH_RE.findall(header_text):
            add("HASH", raw_hash.lower(), key)

    return indicators


def sha256_bytes(value: bytes) -> str:
    """Return the SHA-256 digest used by attachment/content processing."""
    return hashlib.sha256(value).hexdigest()
