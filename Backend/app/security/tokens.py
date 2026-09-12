"""JWT access-token and opaque refresh-token helpers."""

from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from app.core.config import get_settings


def _utcnow() -> datetime:
    """Return the current timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


def create_access_token(user_id: uuid.UUID) -> tuple[str, int]:
    """Create a short-lived JWT access token."""
    settings = get_settings()
    now = _utcnow()
    expires = now + timedelta(minutes=settings.access_token_expire_minutes)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "type": "access",
        "iat": now,
        "exp": expires,
        "jti": str(uuid.uuid4()),
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
    return token, int((expires - now).total_seconds())


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT access token."""
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise ValueError("Invalid access token") from exc

    if payload.get("type") != "access":
        raise ValueError("Invalid access token type")
    subject = payload.get("sub")
    if not subject:
        raise ValueError("Access token is missing a subject")
    return payload


def create_refresh_token() -> tuple[str, datetime]:
    """Create a high-entropy opaque refresh token and its expiry timestamp."""
    settings = get_settings()
    token = secrets.token_urlsafe(64)
    expires_at = _utcnow() + timedelta(days=settings.refresh_token_expire_days)
    return token, expires_at


def hash_refresh_token(token: str) -> str:
    """Hash a refresh token before storing it in PostgreSQL."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
