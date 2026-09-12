"""Service orchestration for deterministic email analysis."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.analysis import AnalysisFinding, EmailAnalysis, Indicator
from app.ai.schemas import AIAnalysisContext
from app.ai.service import AIAnalysisService
from app.models.email import EmailMessage
from app.security.analysis_engine import analyze_email
from app.db.redis import get_redis_client
from app.threat_intel.cache import ThreatIntelCache
from app.threat_intel.enrichment import aggregate_results, build_lookups
from app.threat_intel.service import ThreatIntelService


ENGINE_VERSION = "0.4.0-deterministic-ti-ai"


async def run_analysis(
    session: AsyncSession,
    *,
    organization_id: uuid.UUID,
    email_id: uuid.UUID,
) -> EmailAnalysis | None:
    """Run deterministic, threat-intelligence, and optional AI analysis and persist the result."""
    email = await session.scalar(
        select(EmailMessage)
        .where(EmailMessage.id == email_id, EmailMessage.organization_id == organization_id)
        .options(selectinload(EmailMessage.attachments))
    )
    if email is None:
        return None

    analysis = await session.scalar(
        select(EmailAnalysis)
        .where(
            EmailAnalysis.email_id == email_id,
            EmailAnalysis.organization_id == organization_id,
            EmailAnalysis.status.in_(["queued", "failed"]),
        )
        .order_by(EmailAnalysis.created_at.desc())
    )
    if analysis is None:
        analysis = EmailAnalysis(
            email_id=email.id,
            organization_id=organization_id,
            status="queued",
            engine_version=ENGINE_VERSION,
        )
        session.add(analysis)
        await session.flush()

    analysis.status = "running"
    analysis.started_at = datetime.now(timezone.utc)
    analysis.engine_version = ENGINE_VERSION
    await session.flush()

    try:
        result = analyze_email(email)

        # Threat intelligence is enrichment evidence layered on top of the
        # deterministic engine. Provider failures or Unknown results never
        # become malicious verdicts by themselves.
        ti_service = ThreatIntelService(cache=ThreatIntelCache(get_redis_client()))
        ti_batch = await ti_service.enrich(build_lookups(list(result.indicators)))

        ti_weights = 0
        ti_findings: list[AnalysisFinding] = []
        enriched_indicators: list[Indicator] = []
        for item in result.indicators:
            enrichment = aggregate_results(item.type, item.value, ti_batch.results)
            ti_weights += enrichment.risk_weight
            enriched_indicators.append(
                Indicator(
                    type=item.type,
                    value=item.value,
                    verdict=enrichment.verdict,
                    confidence_score=enrichment.confidence_score,
                    source=enrichment.source if ti_batch.results else "deterministic_extraction",
                    context=item.context,
                    enrichment=enrichment.enrichment,
                )
            )
            if enrichment.finding_severity is not None:
                ti_findings.append(
                    AnalysisFinding(
                        code="TI_IOC_REPUTATION",
                        title=f"Threat intelligence flagged {item.type} indicator",
                        description=(
                            f"Threat-intelligence evidence classified {item.value} as "
                            f"{enrichment.verdict.lower()}. Provider results are retained below for analyst review."
                        ),
                        severity=enrichment.finding_severity,
                        source="threat_intel",
                        weight=enrichment.risk_weight,
                        evidence={
                            "indicator_type": item.type,
                            "indicator": item.value,
                            "enrichment": enrichment.enrichment,
                        },
                    )
                )

        evidence_score = min(100, result.score.risk_score + ti_weights)

        # AI is an additional reasoning layer. It can raise the risk when it
        # sees contextual signals missed by deterministic rules, but it cannot
        # silently lower evidence-backed risk already established by the
        # deterministic engine and threat-intelligence layer.
        enrichment_by_indicator = {
            (item.type.upper(), item.value.strip().lower()): aggregate_results(item.type, item.value, ti_batch.results)
            for item in result.indicators
        }

        ai_context = AIAnalysisContext(
            subject=email.subject,
            sender=email.sender_email,
            recipient=email.recipient_email,
            reply_to=email.reply_to_email,
            body_text=email.body_text,
            headers=email.headers,
            deterministic={
                "risk_score": result.score.risk_score,
                "severity": result.score.severity,
                "verdict": result.score.verdict,
                "threat_type": result.score.threat_type,
                "confidence_score": result.score.confidence_score,
                "summary": result.score.summary,
                "findings": [
                    {"code": f.code, "title": f.title, "severity": f.severity, "weight": f.weight, "evidence": f.evidence}
                    for f in result.score.findings
                ],
                "authentication": {"spf": result.headers.spf, "dkim": result.headers.dkim, "dmarc": result.headers.dmarc},
                "reply_to_mismatch": result.headers.sender_reply_to_mismatch,
            },
            indicators=[
                {
                    "type": item.type,
                    "value": item.value,
                    "verdict": enrichment_by_indicator[(item.type.upper(), item.value.strip().lower())].verdict,
                    "confidence_score": enrichment_by_indicator[(item.type.upper(), item.value.strip().lower())].confidence_score,
                    "enrichment": enrichment_by_indicator[(item.type.upper(), item.value.strip().lower())].enrichment,
                }
                for item in result.indicators
            ],
            attachments=[
                {"filename": attachment.filename, "content_type": attachment.content_type, "size_bytes": attachment.size_bytes, "sha256": attachment.sha256}
                for attachment in email.attachments
            ],
        )
        ai_result = await AIAnalysisService().analyze(ai_context)
        ai_assessment = ai_result.assessment if ai_result else None
        risk_score = evidence_score
        if ai_assessment is not None:
            risk_score = max(evidence_score, ai_assessment.risk_score)

        if risk_score >= 80:
            severity, verdict, threat_type = "CRITICAL", "Phishing", "PHISHING"
        elif risk_score >= 60:
            severity, verdict, threat_type = "HIGH", "Suspicious", "SUSPICIOUS"
        elif risk_score >= 30:
            severity, verdict, threat_type = "MEDIUM", "Suspicious", "SUSPICIOUS"
        else:
            severity, verdict, threat_type = "LOW", "Benign", "LEGITIMATE"

        confidence = result.score.confidence_score
        summary = result.score.summary
        if ti_findings:
            confidence = min(98, max(confidence, max((f.weight for f in ti_findings), default=0) + 55))
            summary += " Threat-intelligence enrichment added reputation evidence for one or more indicators."
        if ai_assessment is not None:
            confidence = max(confidence, ai_assessment.confidence_score)
            if ai_assessment.risk_score >= evidence_score and ai_assessment.summary:
                summary = ai_assessment.summary
            elif ai_assessment.risk_score < evidence_score:
                summary += " AI contextual analysis was more conservative; evidence-backed risk was retained."
            if risk_score > evidence_score:
                summary += " AI contextual analysis identified additional risk signals."

        if ai_assessment is not None and ai_assessment.confidence_score >= 75 and ai_assessment.risk_score >= 60:
            if ai_assessment.threat_type in {"PHISHING", "MALWARE", "BEC", "OTHER"}:
                threat_type = ai_assessment.threat_type

        analysis.risk_score = risk_score
        analysis.severity = severity
        analysis.verdict = verdict
        analysis.threat_type = threat_type
        analysis.ai_provider = ai_result.provider if ai_result else None
        analysis.ai_model = ai_result.model if ai_result else None
        analysis.confidence_score = confidence
        analysis.summary = summary
        analysis.auth_results = {
            "spf": result.headers.spf,
            "dkim": result.headers.dkim,
            "dmarc": result.headers.dmarc,
        }
        analysis.status = "completed"
        analysis.completed_at = datetime.now(timezone.utc)

        analysis.findings.clear()
        analysis.indicators.clear()

        for finding in result.score.findings:
            analysis.findings.append(
                AnalysisFinding(
                    code=finding.code,
                    title=finding.title,
                    description=finding.description,
                    severity=finding.severity,
                    source="rule",
                    weight=finding.weight,
                    evidence=finding.evidence,
                )
            )

        for finding in ti_findings:
            analysis.findings.append(finding)

        if ai_assessment is not None:
            for index, finding in enumerate(ai_assessment.findings, start=1):
                analysis.findings.append(
                    AnalysisFinding(
                        code=f"AI_FINDING_{index:02d}",
                        title=finding.title,
                        description=finding.description,
                        severity=finding.severity,
                        source="ai",
                        weight=0,
                        evidence={"evidence": finding.evidence},
                    )
                )

        analysis.indicators.extend(enriched_indicators)
        analysis.metadata_json = {
            **(analysis.metadata_json or {}),
            "threat_intelligence": {
                "providers_queried": sorted({result.provider for result in ti_batch.results}),
                "provider_errors": ti_batch.provider_errors,
                "result_count": len(ti_batch.results),
            },
            "ai_analysis": (
                {
                    "enabled": True,
                    "provider": ai_result.provider,
                    "model": ai_result.model,
                    "risk_score": ai_assessment.risk_score,
                    "confidence_score": ai_assessment.confidence_score,
                    "reasoning": ai_assessment.reasoning,
                    "recommended_actions": ai_assessment.recommended_actions,
                    **ai_result.raw_metadata,
                }
                if ai_result is not None
                else {"enabled": False}
            ),
        }

    except Exception:
        analysis.status = "failed"
        analysis.completed_at = datetime.now(timezone.utc)
        await session.commit()
        raise

    await session.commit()

    return await session.scalar(
        select(EmailAnalysis)
        .where(EmailAnalysis.id == analysis.id)
        .options(
            selectinload(EmailAnalysis.findings),
            selectinload(EmailAnalysis.indicators),
            selectinload(EmailAnalysis.mitre_mappings),
        )
    )
