"""Authentication API routes."""

from fastapi import APIRouter, Request, status

from app.api.deps import CurrentUser, DBSession
from app.schemas.auth import (
    AuthenticatedUser,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    TokenPair,
)
from app.services.auth_service import login_user, logout_user, refresh_user_tokens, register_user

router = APIRouter(tags=["Authentication"])


def _client_ip(request: Request) -> str | None:
    """Return the direct client address when available."""
    return request.client.host if request.client else None


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    http_request: Request,
    session: DBSession,
) -> RegisterResponse:
    """Register a new user and create their initial organization."""
    user, organization, tokens = await register_user(
        session,
        request,
        user_agent=http_request.headers.get("user-agent"),
        ip_address=_client_ip(http_request),
    )
    return RegisterResponse(
        user=AuthenticatedUser.model_validate(user),
        organization_id=organization.id,
        tokens=tokens,
    )


@router.post("/login", response_model=TokenPair)
async def login(request: LoginRequest, http_request: Request, session: DBSession) -> TokenPair:
    """Authenticate with email and password and return access/refresh tokens."""
    _, tokens = await login_user(
        session,
        request,
        user_agent=http_request.headers.get("user-agent"),
        ip_address=_client_ip(http_request),
    )
    return tokens


@router.post("/refresh", response_model=TokenPair)
async def refresh(
    request: RefreshRequest,
    http_request: Request,
    session: DBSession,
) -> TokenPair:
    """Rotate a refresh token and issue fresh credentials."""
    return await refresh_user_tokens(
        session,
        request,
        user_agent=http_request.headers.get("user-agent"),
        ip_address=_client_ip(http_request),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: LogoutRequest, session: DBSession) -> None:
    """Revoke a refresh token."""
    await logout_user(session, request.refresh_token)


@router.get("/me", response_model=AuthenticatedUser)
async def me(current_user: CurrentUser) -> AuthenticatedUser:
    """Return the currently authenticated account."""
    return AuthenticatedUser.model_validate(current_user)
