"""AI SOC Analyst chat endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from app.ai.chat import SOCChatService, build_investigation_context
from app.ai.schemas.chat import ChatMessage, SOCChatContext, SOCChatRequest, SOCChatResponse
from app.api.deps import CurrentOrganization, DBSession

router = APIRouter(tags=["AI SOC Analyst"])


@router.get("/context/{email_id}", response_model=SOCChatContext)
async def get_soc_context(
    email_id: UUID,
    session: DBSession,
    organization: CurrentOrganization,
) -> SOCChatContext:
    """Return the tenant-scoped evidence package used by the SOC Analyst."""
    context = await build_investigation_context(
        session,
        organization_id=organization.id,
        email_id=email_id,
    )
    if context is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email investigation not found")
    return context


@router.post("/chat", response_model=SOCChatResponse)
async def soc_chat(
    payload: SOCChatRequest,
    session: DBSession,
    organization: CurrentOrganization,
) -> SOCChatResponse:
    """Ask Aegis a security question, optionally scoped to one investigation."""
    try:
        email_id = UUID(payload.email_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid email_id") from exc

    context = await build_investigation_context(
        session,
        organization_id=organization.id,
        email_id=email_id,
    )
    if context is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email investigation not found")

    messages = [*payload.history, ChatMessage(role="user", content=payload.message)]
    normalized_messages = messages

    result = await SOCChatService().chat(messages=normalized_messages, context=context)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI SOC Analyst is not configured or is temporarily unavailable",
        )
    return result
