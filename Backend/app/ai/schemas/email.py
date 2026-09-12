"""Structured schemas for AI-assisted email-security analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, Field, field_validator


class AIFinding(BaseModel):
    """A concise AI finding grounded in supplied evidence."""

    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1, max_length=2000)
    severity: str = Field(default="MEDIUM")
    evidence: list[str] = Field(default_factory=list, max_length=10)

    @field_validator("severity")
    @classmethod
    def normalize_severity(cls, value: str) -> str:
        value = value.upper()
        if value not in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}:
            return "MEDIUM"
        return value


class AIEmailAssessment(BaseModel):
    """Strict, bounded AI assessment returned by the analysis pipeline."""

    verdict: str = Field(default="Unknown")
    threat_type: str = Field(default="SUSPICIOUS")
    risk_score: int = Field(default=0, ge=0, le=100)
    confidence_score: int = Field(default=50, ge=0, le=100)
    summary: str = Field(default="", max_length=4000)
    reasoning: str = Field(default="", max_length=6000)
    findings: list[AIFinding] = Field(default_factory=list, max_length=10)
    recommended_actions: list[str] = Field(default_factory=list, max_length=10)

    @field_validator("verdict")
    @classmethod
    def normalize_verdict(cls, value: str) -> str:
        value = value.strip().title()
        if value not in {"Unknown", "Benign", "Suspicious", "Phishing"}:
            return "Unknown"
        return value

    @field_validator("threat_type")
    @classmethod
    def normalize_threat_type(cls, value: str) -> str:
        value = value.strip().upper()
        if value not in {"LEGITIMATE", "SUSPICIOUS", "PHISHING", "MALWARE", "BEC", "OTHER"}:
            return "SUSPICIOUS"
        return value


@dataclass(frozen=True, slots=True)
class AIAnalysisContext:
    """Structured evidence supplied to the model; never raw credentials or secrets."""

    subject: str | None
    sender: str | None
    recipient: str | None
    reply_to: str | None
    body_text: str | None
    headers: dict[str, str]
    deterministic: dict[str, Any]
    indicators: list[dict[str, Any]]
    attachments: list[dict[str, Any]]


@dataclass(frozen=True, slots=True)
class AIAnalysisResult:
    """Assessment plus provider metadata for persistence."""

    assessment: AIEmailAssessment
    provider: str
    model: str
    raw_metadata: dict[str, Any] = field(default_factory=dict)
