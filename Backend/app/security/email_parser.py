"""Safe, deterministic parsing of uploaded email messages."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from email import policy
from email.parser import BytesParser
from email.utils import getaddresses, parsedate_to_datetime
from typing import BinaryIO


SUPPORTED_EXTENSIONS = {".eml", ".txt", ".nine"}
MAX_EMAIL_SIZE_BYTES = 5 * 1024 * 1024


@dataclass(frozen=True, slots=True)
class ParsedEmail:
    """Normalized email fields extracted without making a security verdict."""

    subject: str | None
    sender_email: str | None
    recipient_email: str | None
    reply_to_email: str | None
    body_text: str | None
    body_html: str | None
    headers: dict[str, str]
    received_at: datetime | None


def _first_address(value: str | None) -> str | None:
    if not value:
        return None
    addresses = getaddresses([value])
    for _, address in addresses:
        if address:
            return address.strip().lower()
    return None


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def parse_email(raw_bytes: bytes) -> ParsedEmail:
    """Parse an RFC822-like message into fields required by Mail Sentinel."""
    message = BytesParser(policy=policy.default).parsebytes(raw_bytes)

    text_parts: list[str] = []
    html_parts: list[str] = []
    if message.is_multipart():
        for part in message.walk():
            if part.is_multipart() or part.get_content_disposition() == "attachment":
                continue
            content_type = part.get_content_type()
            try:
                payload = part.get_content()
            except (LookupError, UnicodeDecodeError):
                continue
            if not isinstance(payload, str):
                continue
            if content_type == "text/plain":
                text_parts.append(payload)
            elif content_type == "text/html":
                html_parts.append(payload)
    else:
        try:
            payload = message.get_content()
        except (LookupError, UnicodeDecodeError):
            payload = None
        if isinstance(payload, str):
            if message.get_content_type() == "text/html":
                html_parts.append(payload)
            else:
                text_parts.append(payload)

    headers: dict[str, str] = {}
    for key, value in message.items():
        if key not in headers:
            headers[key] = str(value)

    return ParsedEmail(
        subject=str(message.get("Subject")) if message.get("Subject") is not None else None,
        sender_email=_first_address(message.get("From")),
        recipient_email=_first_address(message.get("To")),
        reply_to_email=_first_address(message.get("Reply-To")),
        body_text="\n".join(text_parts).strip() or None,
        body_html="\n".join(html_parts).strip() or None,
        headers=headers,
        received_at=_parse_date(message.get("Date")),
    )


def validate_upload(filename: str, size_bytes: int) -> None:
    """Validate frontend-compatible filename and size constraints."""
    dot_index = filename.rfind(".")
    extension = filename[dot_index:].lower() if dot_index >= 0 else ""
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError("Unsupported file type. Use .eml, .txt, or .nine.")
    if size_bytes <= 0:
        raise ValueError("The uploaded email is empty.")
    if size_bytes > MAX_EMAIL_SIZE_BYTES:
        raise ValueError("File is too large. Maximum allowed size is 5 MB.")


def read_upload(stream: BinaryIO, *, size_limit: int = MAX_EMAIL_SIZE_BYTES) -> bytes:
    """Read an upload while enforcing the size limit without trusting client headers."""
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = stream.read(64 * 1024)
        if not chunk:
            break
        total += len(chunk)
        if total > size_limit:
            raise ValueError("File is too large. Maximum allowed size is 5 MB.")
        chunks.append(chunk)
    if total == 0:
        raise ValueError("The uploaded email is empty.")
    return b"".join(chunks)
