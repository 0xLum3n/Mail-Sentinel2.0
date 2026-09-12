"""Explainable deterministic risk scoring for email analysis."""

from __future__ import annotations

from dataclasses import dataclass

from app.security.header_analyzer import HeaderAnalysis
from app.security.ioc_extractor import ExtractedIndicator


@dataclass(frozen=True, slots=True)
class ScoringFinding:
    code: str
    title: str
    description: str
    severity: str
    weight: int
    evidence: dict


@dataclass(frozen=True, slots=True)
class ScoreResult:
    risk_score: int
    severity: str
    verdict: str
    threat_type: str
    confidence_score: int
    summary: str
    findings: tuple[ScoringFinding, ...]


def _severity(score: int) -> str:
    if score >= 80:
        return "CRITICAL"
    if score >= 60:
        return "HIGH"
    if score >= 30:
        return "MEDIUM"
    return "LOW"


def score_email(
    *,
    header_analysis: HeaderAnalysis,
    indicators: list[ExtractedIndicator],
    subject: str | None,
    body_text: str | None,
    attachment_names: tuple[str, ...] = (),
) -> ScoreResult:
    """Calculate a bounded, evidence-backed risk score.

    This is a first-pass deterministic engine. AI and external reputation
    providers will be layered on top later rather than replacing these checks.
    """
    score = 0
    findings: list[ScoringFinding] = []

    def add(code: str, title: str, description: str, severity: str, weight: int, evidence: dict) -> None:
        nonlocal score
        score += weight
        findings.append(ScoringFinding(code, title, description, severity, weight, evidence))

    auth_failures = [name for name, value in (("SPF", header_analysis.spf), ("DKIM", header_analysis.dkim), ("DMARC", header_analysis.dmarc)) if value in {"FAIL", "PERMERROR", "TEMPERROR"}]
    if auth_failures:
        add(
            "AUTH_FAILURE",
            "Email authentication failure",
            f"Authentication results indicate {', '.join(auth_failures)} failure/error state(s).",
            "HIGH" if len(auth_failures) >= 2 else "MEDIUM",
            20 if len(auth_failures) == 1 else 35,
            {"failed_or_error": auth_failures},
        )

    if header_analysis.sender_reply_to_mismatch:
        add(
            "REPLY_TO_MISMATCH",
            "Sender and Reply-To domains differ",
            "The visible sender domain differs from the Reply-To domain, which can indicate impersonation or redirection.",
            "MEDIUM",
            15,
            {"sender_domain": header_analysis.sender_domain, "reply_to_domain": header_analysis.reply_to_domain},
        )

    url_count = sum(1 for item in indicators if item.type == "URL")
    if url_count:
        add(
            "URL_PRESENT",
            "Message contains external URL(s)",
            f"The message contains {url_count} external URL indicator(s).",
            "LOW",
            min(20, 5 * url_count),
            {"url_count": url_count},
        )

    ip_count = sum(1 for item in indicators if item.type == "IP")
    if ip_count:
        add(
            "PUBLIC_IP_PRESENT",
            "Message contains public IP indicator(s)",
            f"The message contains {ip_count} public IP indicator(s) that may warrant reputation checks.",
            "MEDIUM",
            min(15, 5 * ip_count),
            {"ip_count": ip_count},
        )

    domain_count = sum(1 for item in indicators if item.type == "DOMAIN")
    if domain_count:
        add(
            "DOMAIN_PRESENT",
            "Message contains domain indicator(s)",
            f"The message contains {domain_count} domain indicator(s) requiring reputation/context analysis.",
            "LOW",
            min(10, 2 * domain_count),
            {"domain_count": domain_count},
        )

    urgency_terms = ("urgent", "immediately", "within 24 hours", "verify", "suspended", "password", "account")
    content = " ".join(part for part in (subject, body_text) if part).lower()
    matched_urgency = sorted({term for term in urgency_terms if term in content})
    if matched_urgency:
        add(
            "SOCIAL_ENGINEERING_LANGUAGE",
            "Potential social-engineering language",
            "The message uses urgency, verification, account, or credential-related language commonly seen in social-engineering attempts.",
            "MEDIUM",
            10,
            {"matched_terms": matched_urgency},
        )

    risky_extensions = {".exe", ".scr", ".bat", ".cmd", ".ps1", ".js", ".vbs", ".hta", ".msi", ".lnk", ".iso"}
    risky_attachments = [name for name in attachment_names if any(name.lower().endswith(ext) for ext in risky_extensions)]
    if risky_attachments:
        add(
            "RISKY_ATTACHMENT_TYPE",
            "Potentially executable attachment",
            "The message contains an attachment type commonly used to deliver executable or script content.",
            "HIGH",
            25,
            {"attachments": risky_attachments},
        )

    risk_score = min(100, max(0, score))
    severity = _severity(risk_score)

    if risk_score >= 80:
        verdict = "Phishing"
        threat_type = "PHISHING"
    elif risk_score >= 60:
        verdict = "Suspicious"
        threat_type = "SUSPICIOUS"
    else:
        verdict = "Benign"
        threat_type = "LEGITIMATE"

    confidence = min(95, 40 + len(findings) * 8)
    if not findings:
        confidence = 55

    if verdict == "Phishing":
        summary = "Multiple security signals indicate a high-risk message that should be investigated as potential phishing."
    elif verdict == "Suspicious":
        summary = "The message contains security signals that warrant further reputation and contextual analysis."
    else:
        summary = "No strong deterministic phishing signal was identified in the first-pass analysis."

    return ScoreResult(
        risk_score=risk_score,
        severity=severity,
        verdict=verdict,
        threat_type=threat_type,
        confidence_score=confidence,
        summary=summary,
        findings=tuple(findings),
    )
