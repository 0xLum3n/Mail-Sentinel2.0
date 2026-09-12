"""Email ingestion and retrieval endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from app.api.deps import CurrentOrganization, CurrentUser, DBSession
from app.schemas.email import EmailResponse
from app.services.analysis_service import run_analysis
from app.services.email_service import get_email_for_organization, ingest_email, to_email_response
from app.security.email_parser import MAX_EMAIL_SIZE_BYTES, SUPPORTED_EXTENSIONS

router = APIRouter(tags=["Email Analysis"])


@router.post("", response_model=EmailResponse, status_code=status.HTTP_201_CREATED)
async def upload_email(
    session: DBSession,
    current_user: CurrentUser,
    organization: CurrentOrganization,
    file: UploadFile = File(...),
) -> EmailResponse:
    """Accept one frontend-compatible raw email file and queue analysis."""
    filename = file.filename or ""
    extension = filename[filename.rfind(".") :].lower() if "." in filename else ""
    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unsupported file type. Use .eml, .txt, or .nine.",
        )

    raw_bytes = await file.read(MAX_EMAIL_SIZE_BYTES + 1)
    if len(raw_bytes) > MAX_EMAIL_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File is too large. Maximum allowed size is 5 MB.",
        )
    if not raw_bytes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The uploaded email is empty.",
        )

    try:
        email = await ingest_email(
            session,
            organization=organization,
            user=current_user,
            filename=filename,
            raw_bytes=raw_bytes,
        )
    except ValueError as exc:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    return to_email_response(email)


@router.get("/{email_id}", response_model=EmailResponse)
async def get_email(
    email_id: uuid.UUID,
    session: DBSession,
    organization: CurrentOrganization,
) -> EmailResponse:
    """Return one email and all of its analysis runs for the current workspace."""
    email = await get_email_for_organization(
        session, organization_id=organization.id, email_id=email_id
    )
    if email is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email investigation not found")
    return to_email_response(email)


@router.post("/{email_id}/analyze", response_model=EmailResponse)
async def analyze_email_endpoint(
    email_id: uuid.UUID,
    session: DBSession,
    organization: CurrentOrganization,
) -> EmailResponse:
    """Run the complete deterministic, threat-intelligence, and optional AI analysis."""
    try:
        analysis = await run_analysis(
            session,
            organization_id=organization.id,
            email_id=email_id,
        )
    except Exception as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email analysis failed",
        ) from exc

    if analysis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email investigation not found",
        )

    email = await get_email_for_organization(
        session, organization_id=organization.id, email_id=email_id
    )
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email investigation not found",
        )
    return to_email_response(email)
