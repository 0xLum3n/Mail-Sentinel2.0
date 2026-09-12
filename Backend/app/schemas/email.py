"""Pydantic schemas for email ingestion and analysis responses."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AuthResults(BaseModel):
    spf: str = "UNKNOWN"
    dkim: str = "UNKNOWN"
    dmarc: str = "UNKNOWN"


class IndicatorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    type: str
    value: str
    verdict: str
    confidence_score: int | None = Field(default=None, ge=0, le=100)
    source: str | None = None
    context: str | None = None
    enrichment: dict = Field(default_factory=dict)


class MitreMappingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tactic: str
    technique_id: str | None
    technique_name: str
    confidence_score: int | None = Field(default=None, ge=0, le=100)


class FindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str | None
    title: str
    description: str
    severity: str
    source: str
    weight: int
    evidence: dict


class EmailAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email_id: UUID
    status: str
    risk_score: int | None
    severity: str | None
    threat_type: str | None
    verdict: str | None
    confidence_score: int | None
    summary: str | None
    auth_results: AuthResults
    engine_version: str | None
    ai_provider: str | None
    ai_model: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    findings: list[FindingResponse]
    indicators: list[IndicatorResponse]
    mitre_mappings: list[MitreMappingResponse]
    metadata_json: dict = Field(default_factory=dict)


class EmailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    message_hash: str
    original_filename: str | None
    source: str
    subject: str | None
    sender_email: str | None
    recipient_email: str | None
    reply_to_email: str | None
    received_at: datetime | None
    created_at: datetime
    analyses: list[EmailAnalysisResponse]
