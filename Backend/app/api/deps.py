"""Reusable FastAPI dependencies."""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db_session
from app.models.organization import Organization, OrganizationMembership
from app.models.user import User
from app.services.auth_service import get_user_from_access_token

bearer_scheme = HTTPBearer(auto_error=False)
DBSession = Annotated[AsyncSession, Depends(get_db_session)]


async def get_current_user(
    session: DBSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> User:
    """Return the authenticated user associated with the bearer token."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await get_user_from_access_token(session, credentials.credentials)


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_organization(
    session: DBSession,
    current_user: CurrentUser,
) -> Organization:
    """Return the user's current workspace.

    The initial release has one workspace selected at a time. A dedicated
    organization-switching mechanism can later replace this deterministic
    selection without changing endpoint contracts.
    """
    organization = await session.scalar(
        select(Organization)
        .join(OrganizationMembership, OrganizationMembership.organization_id == Organization.id)
        .where(OrganizationMembership.user_id == current_user.id)
        .order_by(OrganizationMembership.created_at.asc())
        .limit(1)
    )
    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No security workspace is assigned to this account",
        )
    return organization


CurrentOrganization = Annotated[Organization, Depends(get_current_organization)]
