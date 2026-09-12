"""Authentication and account lifecycle business logic."""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth_session import AuthSession
from app.models.organization import Organization, OrganizationMembership
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenPair
from app.security.passwords import hash_password, verify_password
from app.security.tokens import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    hash_refresh_token,
)


def _slugify(value: str) -> str:
    """Generate a URL-safe organization slug."""
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:70] or "organization"


async def _build_unique_org_slug(session: AsyncSession, name: str) -> str:
    """Generate a unique organization slug before insertion."""
    base = _slugify(name)
    candidate = base
    counter = 2
    while await session.scalar(
        select(Organization.id).where(Organization.slug == candidate)
    ) is not None:
        suffix = f"-{counter}"
        candidate = f"{base[: 80 - len(suffix)]}{suffix}"
        counter += 1
    return candidate


def _raise_conflict(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)


async def _issue_token_pair(
    session: AsyncSession,
    user: User,
    *,
    user_agent: str | None,
    ip_address: str | None,
) -> TokenPair:
    """Create an access token and persist the corresponding refresh session."""
    access_token, expires_in = create_access_token(user.id)
    refresh_token, refresh_expires = create_refresh_token()
    session.add(
        AuthSession(
            user_id=user.id,
            token_hash=hash_refresh_token(refresh_token),
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=refresh_expires,
        )
    )
    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
    )


async def register_user(
    session: AsyncSession,
    request: RegisterRequest,
    *,
    user_agent: str | None,
    ip_address: str | None,
) -> tuple[User, Organization, TokenPair]:
    """Create a user, an initial organization, membership, and credentials."""
    existing = await session.scalar(
        select(User).where(func.lower(User.email) == request.email.lower())
    )
    if existing is not None:
        _raise_conflict("An account with this email already exists")

    organization = Organization(
        name=request.organization_name,
        slug=await _build_unique_org_slug(session, request.organization_name),
    )
    user = User(
        email=request.email,
        password_hash=hash_password(request.password),
        first_name=request.first_name,
        last_name=request.last_name,
        is_active=True,
        is_email_verified=False,
    )
    session.add_all([organization, user])
    await session.flush()

    session.add(
        OrganizationMembership(
            organization_id=organization.id,
            user_id=user.id,
            role="owner",
        )
    )
    tokens = await _issue_token_pair(
        session,
        user,
        user_agent=user_agent,
        ip_address=ip_address,
    )

    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise

    await session.refresh(user)
    return user, organization, tokens


async def authenticate_user(session: AsyncSession, request: LoginRequest) -> User:
    """Validate credentials and return the corresponding active user."""
    user = await session.scalar(
        select(User).where(func.lower(User.email) == request.email.lower())
    )
    if user is None or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")
    return user


async def login_user(
    session: AsyncSession,
    request: LoginRequest,
    *,
    user_agent: str | None,
    ip_address: str | None,
) -> tuple[User, TokenPair]:
    """Authenticate a user, update last-login time, and issue credentials."""
    user = await authenticate_user(session, request)
    user.last_login_at = datetime.now(timezone.utc)
    tokens = await _issue_token_pair(
        session,
        user,
        user_agent=user_agent,
        ip_address=ip_address,
    )
    await session.commit()
    await session.refresh(user)
    return user, tokens


async def refresh_user_tokens(
    session: AsyncSession,
    request: RefreshRequest,
    *,
    user_agent: str | None,
    ip_address: str | None,
) -> TokenPair:
    """Rotate a valid refresh token exactly once."""
    token_hash = hash_refresh_token(request.refresh_token)
    auth_session = await session.scalar(
        select(AuthSession).where(AuthSession.token_hash == token_hash)
    )
    now = datetime.now(timezone.utc)
    if (
        auth_session is None
        or auth_session.revoked_at is not None
        or auth_session.expires_at <= now
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await session.get(User, auth_session.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is unavailable")

    auth_session.revoked_at = now
    tokens = await _issue_token_pair(
        session,
        user,
        user_agent=user_agent,
        ip_address=ip_address,
    )
    await session.commit()
    return tokens


async def logout_user(session: AsyncSession, refresh_token: str) -> None:
    """Revoke a refresh-token session if it exists."""
    token_hash = hash_refresh_token(refresh_token)
    auth_session = await session.scalar(
        select(AuthSession).where(AuthSession.token_hash == token_hash)
    )
    if auth_session is not None and auth_session.revoked_at is None:
        auth_session.revoked_at = datetime.now(timezone.utc)
        await session.commit()


async def get_user_from_access_token(session: AsyncSession, token: str) -> User:
    """Resolve a bearer access token to an active user."""
    try:
        payload = decode_access_token(token)
        user_id = uuid.UUID(str(payload["sub"]))
    except (ValueError, TypeError, KeyError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user = await session.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is unavailable",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
