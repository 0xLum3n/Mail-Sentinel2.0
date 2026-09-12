"""First-pass deterministic Mail Sentinel email analysis engine."""

from __future__ import annotations

from dataclasses import dataclass

from app.models.email import EmailMessage
from app.security.header_analyzer import HeaderAnalysis, analyze_headers
from app.security.ioc_extractor import ExtractedIndicator, extract_indicators
from app.security.scoring import ScoreResult, score_email


@dataclass(frozen=True, slots=True)
class EngineResult:
    """Complete deterministic result ready for persistence."""

    headers: HeaderAnalysis
    indicators: tuple[ExtractedIndicator, ...]
    score: ScoreResult


def analyze_email(email: EmailMessage) -> EngineResult:
    """Analyze an already-parsed EmailMessage without network/AI dependencies."""
    header_analysis = analyze_headers(
        email.headers,
        sender_email=email.sender_email,
        reply_to_email=email.reply_to_email,
    )
    attachment_names = tuple(attachment.filename for attachment in email.attachments)
    attachment_hashes = tuple(attachment.sha256 for attachment in email.attachments)
    indicators = extract_indicators(
        body_text=email.body_text,
        body_html=email.body_html,
        headers=email.headers,
        sender_email=email.sender_email,
        reply_to_email=email.reply_to_email,
        attachment_sha256s=attachment_hashes,
    )
    score = score_email(
        header_analysis=header_analysis,
        indicators=indicators,
        subject=email.subject,
        body_text=email.body_text,
        attachment_names=attachment_names,
    )
    return EngineResult(header_analysis, tuple(indicators), score)
