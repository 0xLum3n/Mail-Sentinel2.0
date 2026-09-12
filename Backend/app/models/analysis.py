"""Email analysis, findings, indicators, and MITRE mappings."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EmailAnalysis(Base):
    """A single analysis run performed against an email message."""

    __tablename__ = "email_analyses"
    __table_args__ = (
        CheckConstraint(
            "status IN ('queued', 'running', 'completed', 'failed')",
            name="ck_email_analyses_status",
        ),
        CheckConstraint(
            "severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')",
            name="ck_email_analyses_severity",
        ),
        CheckConstraint("risk_score >= 0 AND risk_score <= 100", name="ck_email_analyses_risk_score"),
        CheckConstraint(
            "confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 100)",
            name="ck_email_analyses_confidence_score",
        ),
        Index("ix_email_analyses_email_created", "email_id", "created_at"),
        Index("ix_email_analyses_org_created", "organization_id", "created_at"),
        Index("ix_email_analyses_org_risk", "organization_id", "risk_score"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("email_messages.id", ondelete="CASCADE"),
        nullable=False,
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(String(16), nullable=False, default="queued", server_default="queued")
    risk_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    severity: Mapped[str | None] = mapped_column(String(16), nullable=True)
    threat_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    verdict: Mapped[str | None] = mapped_column(String(64), nullable=True)
    confidence_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    auth_results: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")
    engine_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ai_provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ai_model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")

    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    email: Mapped["EmailMessage"] = relationship(back_populates="analyses")
    findings: Mapped[list["AnalysisFinding"]] = relationship(
        back_populates="analysis",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    indicators: Mapped[list["Indicator"]] = relationship(
        back_populates="analysis",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    mitre_mappings: Mapped[list["MitreMapping"]] = relationship(
        back_populates="analysis",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class AnalysisFinding(Base):
    """A discrete detection finding produced by rules or AI reasoning."""

    __tablename__ = "analysis_findings"
    __table_args__ = (
        CheckConstraint(
            "severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')",
            name="ck_analysis_findings_severity",
        ),
        CheckConstraint(
            "source IN ('rule', 'threat_intel', 'ai')",
            name="ck_analysis_findings_source",
        ),
        Index("ix_analysis_findings_analysis", "analysis_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("email_analyses.id", ondelete="CASCADE"),
        nullable=False,
    )
    code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    weight: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    evidence: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    analysis: Mapped[EmailAnalysis] = relationship(back_populates="findings")


class Indicator(Base):
    """An IOC extracted from or associated with an email analysis."""

    __tablename__ = "indicators"
    __table_args__ = (
        CheckConstraint(
            "type IN ('IP', 'URL', 'DOMAIN', 'HASH', 'EMAIL')",
            name="ck_indicators_type",
        ),
        CheckConstraint(
            "verdict IN ('Unknown', 'Benign', 'Suspicious', 'Malicious', 'Phishing')",
            name="ck_indicators_verdict",
        ),
        Index("ix_indicators_analysis_type", "analysis_id", "type"),
        Index("ix_indicators_type_value", "type", "value"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("email_analyses.id", ondelete="CASCADE"),
        nullable=False,
    )
    type: Mapped[str] = mapped_column(String(16), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    verdict: Mapped[str] = mapped_column(String(16), nullable=False, default="Unknown", server_default="Unknown")
    confidence_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source: Mapped[str | None] = mapped_column(String(64), nullable=True)
    context: Mapped[str | None] = mapped_column(Text, nullable=True)
    enrichment: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    analysis: Mapped[EmailAnalysis] = relationship(back_populates="indicators")


class MitreMapping(Base):
    """MITRE ATT&CK tactic/technique mapping for an analysis."""

    __tablename__ = "mitre_mappings"
    __table_args__ = (
        Index("ix_mitre_mappings_analysis", "analysis_id"),
        Index("ix_mitre_mappings_technique", "technique_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("email_analyses.id", ondelete="CASCADE"),
        nullable=False,
    )
    tactic: Mapped[str] = mapped_column(String(128), nullable=False)
    technique_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    technique_name: Mapped[str] = mapped_column(String(255), nullable=False)
    confidence_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)

    analysis: Mapped[EmailAnalysis] = relationship(back_populates="mitre_mappings")
