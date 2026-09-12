"""Authentication API request and response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    """Create a user and their initial organization."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    organization_name: str = Field(default="My Organization", min_length=2, max_length=120)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()

    @field_validator("first_name", "last_name", "organization_name")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        normalized = " ".join(value.strip().split())
        if not normalized:
            raise ValueError("Value cannot be blank")
        return normalized


class LoginRequest(BaseModel):
    """Authenticate a user with email and password."""

    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class RefreshRequest(BaseModel):
    """Rotate a refresh token."""

    refresh_token: str = Field(min_length=1)


class LogoutRequest(BaseModel):
    """Revoke a refresh-token session."""

    refresh_token: str = Field(min_length=1)


class TokenPair(BaseModel):
    """Issued access and refresh credentials."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(gt=0)


class AuthenticatedUser(BaseModel):
    """Minimal authenticated-user representation."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    is_active: bool
    is_email_verified: bool
    created_at: datetime


class RegisterResponse(BaseModel):
    """Registration result returned to the frontend."""

    user: AuthenticatedUser
    organization_id: UUID
    tokens: TokenPair
