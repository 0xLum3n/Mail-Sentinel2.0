"""Provider-neutral AI orchestration for email security analysis."""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from app.ai.prompts import SYSTEM_PROMPT, USER_TEMPLATE
from app.ai.schemas import AIAnalysisContext, AIAnalysisResult, AIEmailAssessment
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class AIAnalysisService:
    """Call an OpenAI-compatible model and validate its structured output."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        provider: str | None = None,
        base_url: str | None = None,
        timeout_seconds: float | None = None,
    ) -> None:
        settings = get_settings()
        self.provider = (provider or settings.ai_provider or "").strip().lower()
        self.api_key = api_key if api_key is not None else settings.ai_api_key
        self.model = model if model is not None else settings.ai_model
        self.base_url = (base_url or settings.ai_base_url).rstrip("/")
        self.timeout = timeout_seconds or settings.ai_timeout_seconds

    @property
    def enabled(self) -> bool:
        return bool(self.provider and self.api_key and self.model)

    async def analyze(self, context: AIAnalysisContext) -> AIAnalysisResult | None:
        """Return a validated assessment, or None when AI is disabled/unavailable."""
        if not self.enabled:
            return None
        if self.provider not in {"openai", "openai-compatible"}:
            logger.warning("Unsupported AI provider configured: %s", self.provider)
            return None

        payload = {
            "model": self.model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": USER_TEMPLATE.format(
                        metadata=json.dumps(
                            {
                                "subject": context.subject,
                                "sender": context.sender,
                                "recipient": context.recipient,
                                "reply_to": context.reply_to,
                            },
                            ensure_ascii=False,
                        ),
                        body=_truncate(context.body_text or "", 12000),
                        headers=json.dumps(context.headers, ensure_ascii=False),
                        deterministic=json.dumps(context.deterministic, ensure_ascii=False),
                        indicators=json.dumps(context.indicators, ensure_ascii=False),
                        attachments=json.dumps(context.attachments, ensure_ascii=False),
                    ),
                },
            ],
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
            content = _extract_content(data)
            assessment = AIEmailAssessment.model_validate(json.loads(content))
            return AIAnalysisResult(
                assessment=assessment,
                provider=self.provider,
                model=self.model or "unknown",
                raw_metadata={
                    "response_id": data.get("id"),
                    "usage": data.get("usage"),
                },
            )
        except Exception as exc:
            logger.warning("AI email analysis unavailable: %s", exc)
            return None


def _extract_content(data: dict[str, Any]) -> str:
    choices = data.get("choices") or []
    if not choices:
        raise ValueError("AI response contained no choices")
    content = choices[0].get("message", {}).get("content")
    if not isinstance(content, str) or not content.strip():
        raise ValueError("AI response contained no message content")
    return content


def _truncate(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    return value[:limit] + "\n[TRUNCATED BY MAIL SENTINEL]"
