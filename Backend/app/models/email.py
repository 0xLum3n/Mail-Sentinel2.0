"""Stored email message model and relationships."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EmailMessage(Base):
    """An ingested email belonging to an organization."""

    __tablename__ = "email_messages"
    __table_args__ = (
        Index("ix_email_messages_org_created", "organization_id", "created_at"),
        Index("ix_email_messages_org_sender", "organization_id", "sender_email"),
        Index("ix_email_messages_org_message_hash", "organization_id", "message_hash"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    uploaded_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    message_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source: Mapped[str] = mapped_column(String(64), nullable=False, default="email_upload", server_default="email_upload")

    subject: Mapped[str | None] = mapped_column(Text, nullable=True)
    sender_email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    recipient_email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    reply_to_email: Mapped[str | None] = mapped_column(String(320), nullable=True)

    body_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_html: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_content: Mapped[str] = mapped_column(Text, nullable=False)
    headers: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")

    received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    attachments: Mapped[list["EmailAttachment"]] = relationship(
        back_populates="email",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    analyses: Mapped[list["EmailAnalysis"]] = relationship(
        back_populates="email",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="EmailAnalysis.created_at.desc()",
    )


class EmailAttachment(Base):
    """Metadata for an attachment extracted from an ingested email."""

    __tablename__ = "email_attachments"
    __table_args__ = (
        Index("ix_email_attachments_email", "email_id"),
        Index("ix_email_attachments_sha256", "sha256"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("email_messages.id", ondelete="CASCADE"),
        nullable=False,
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    storage_key: Mapped[str | None] = mapped_column(String(512), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    email: Mapped[EmailMessage] = relationship(back_populates="attachments")
