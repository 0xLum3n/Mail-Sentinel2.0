"""Schemas for the AI SOC Analyst chat API."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ChatMessage(BaseModel):
    """One client-supplied conversation turn."""

    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=6000)

    @field_validator("content")
    @classmethod
    def strip_content(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Message content cannot be empty")
        return value


class SOCChatRequest(BaseModel):
    """Stateless chat request scoped to the current security workspace."""

    message: str = Field(min_length=1, max_length=6000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)
    email_id: str

    @field_validator("message")
    @classmethod
    def strip_message(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Message cannot be empty")
        return value


class SOCChatContext(BaseModel):
    """Security evidence supplied to the SOC Analyst model."""

    email: dict = Field(default_factory=dict)
    body_text: str = ""
    headers: dict[str, str] = Field(default_factory=dict)
    attachments: list[dict] = Field(default_factory=list)
    latest_analysis: dict | None = None


class SOCChatResponse(BaseModel):
    """Assistant response plus provider metadata."""

    message: str
    provider: str
    model: str
    response_id: str | None = None
    usage: dict | None = None
