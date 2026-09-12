"""Email ingestion and analysis-record orchestration."""

from __future__ import annotations

import hashlib
import uuid
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis import EmailAnalysis
from app.models.email import EmailAttachment, EmailMessage
from app.models.organization import Organization
from app.models.user import User
from app.schemas.email import EmailAnalysisResponse, EmailResponse
from app.security.email_parser import parse_email, validate_upload


async def ingest_email(
    session: AsyncSession,
    *,
    organization: Organization,
    user: User,
    filename: str | None,
    raw_bytes: bytes,
    source: str = "email_upload",
) -> EmailMessage:
    """Persist an uploaded message and queue its first analysis run."""
    normalized_filename = filename.strip() if filename else None
    if normalized_filename:
        validate_upload(normalized_filename, len(raw_bytes))
    elif len(raw_bytes) == 0:
        raise ValueError("The uploaded email is empty.")
    elif len(raw_bytes) > 5 * 1024 * 1024:
        raise ValueError("File is too large. Maximum allowed size is 5 MB.")

    parsed = parse_email(raw_bytes)
    message_hash = hashlib.sha256(raw_bytes).hexdigest()

    email = EmailMessage(
        organization_id=organization.id,
        uploaded_by_user_id=user.id,
        message_hash=message_hash,
        original_filename=normalized_filename,
        source=source,
        subject=parsed.subject,
        sender_email=parsed.sender_email,
        recipient_email=parsed.recipient_email,
        reply_to_email=parsed.reply_to_email,
        body_text=parsed.body_text,
        body_html=parsed.body_html,
        raw_content=raw_bytes.decode("utf-8", errors="replace"),
        headers=parsed.headers,
        received_at=parsed.received_at,
    )
    session.add(email)
    await session.flush()

    # Queue the analysis without inventing a verdict. The worker will populate
    # risk, findings, indicators, MITRE mappings, and the AI-backed assessment.
    analysis = EmailAnalysis(
        email_id=email.id,
        organization_id=organization.id,
        status="queued",
        engine_version="0.1.0",
        ai_provider=None,
        ai_model=None,
        started_at=None,
        completed_at=None,
    )
    session.add(analysis)

    # Attachments are intentionally metadata-only at this stage. Their bytes
    # should be handled by a dedicated isolated storage/scanning pipeline.
    for part in _iter_attachments(raw_bytes):
        session.add(
            EmailAttachment(
                email_id=email.id,
                filename=part[0],
                content_type=part[1],
                size_bytes=part[2],
                sha256=part[3],
                storage_key=None,
            )
        )

    await session.commit()
    loaded = await get_email_for_organization(
        session, organization_id=organization.id, email_id=email.id
    )
    if loaded is None:
        raise RuntimeError("Persisted email could not be reloaded")
    return loaded


def _iter_attachments(raw_bytes: bytes):
    """Yield attachment metadata without persisting untrusted bytes in PostgreSQL."""
    from email import policy
    from email.parser import BytesParser

    message = BytesParser(policy=policy.default).parsebytes(raw_bytes)
    for part in message.walk():
        if part.is_multipart() or part.get_content_disposition() != "attachment":
            continue
        payload = part.get_payload(decode=True) or b""
        filename = part.get_filename() or "unnamed-attachment"
        content_type = part.get_content_type()
        yield filename[:255], content_type[:255], len(payload), hashlib.sha256(payload).hexdigest()


async def get_email_for_organization(
    session: AsyncSession,
    *,
    organization_id: uuid.UUID,
    email_id: uuid.UUID,
) -> EmailMessage | None:
    """Load an email and its analysis graph for the caller's organization."""
    return await session.scalar(
        select(EmailMessage)
        .where(
            EmailMessage.id == email_id,
            EmailMessage.organization_id == organization_id,
        )
        .options(
            selectinload(EmailMessage.analyses).selectinload(EmailAnalysis.findings),
            selectinload(EmailMessage.analyses).selectinload(EmailAnalysis.indicators),
            selectinload(EmailMessage.analyses).selectinload(EmailAnalysis.mitre_mappings),
            selectinload(EmailMessage.attachments),
        )
    )


def to_email_response(email: EmailMessage) -> EmailResponse:
    """Convert an ORM email into the public API representation."""
    analyses = sorted(email.analyses, key=lambda item: item.created_at, reverse=True)
    return EmailResponse(
        id=email.id,
        message_hash=email.message_hash,
        original_filename=email.original_filename,
        source=email.source,
        subject=email.subject,
        sender_email=email.sender_email,
        recipient_email=email.recipient_email,
        reply_to_email=email.reply_to_email,
        received_at=email.received_at,
        created_at=email.created_at,
        analyses=[
            EmailAnalysisResponse(
                id=analysis.id,
                email_id=analysis.email_id,
                status=analysis.status,
                risk_score=analysis.risk_score,
                severity=analysis.severity,
                threat_type=analysis.threat_type,
                verdict=analysis.verdict,
                confidence_score=analysis.confidence_score,
                summary=analysis.summary,
                auth_results=analysis.auth_results,
                engine_version=analysis.engine_version,
                ai_provider=analysis.ai_provider,
                ai_model=analysis.ai_model,
                started_at=analysis.started_at,
                completed_at=analysis.completed_at,
                created_at=analysis.created_at,
                findings=analysis.findings,
                indicators=analysis.indicators,
                mitre_mappings=analysis.mitre_mappings,
                metadata_json=analysis.metadata_json,
            )
            for analysis in analyses
        ],
    )
