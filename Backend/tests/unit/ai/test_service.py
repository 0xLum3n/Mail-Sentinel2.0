import os

os.environ.setdefault("SECRET_KEY", "unit-test-secret")
os.environ.setdefault("POSTGRES_PASSWORD", "unit-test-password")

import httpx
import pytest

from app.ai.schemas import AIAnalysisContext
from app.ai.service import AIAnalysisService


@pytest.mark.asyncio
async def test_ai_service_validates_structured_response(monkeypatch) -> None:
    service = AIAnalysisService(
        api_key="test-key",
        model="test-model",
        provider="openai-compatible",
        base_url="https://example.test/v1",
    )

    response = httpx.Response(
        200,
        json={
            "id": "resp-1",
            "choices": [{
                "message": {
                    "content": '{"verdict":"Phishing","threat_type":"PHISHING","risk_score":88,"confidence_score":91,"summary":"Credential harvesting indicators are present.","reasoning":"Authentication failure and a suspicious login URL are consistent with phishing.","findings":[{"title":"Credential harvesting","description":"The message requests account verification through an external URL.","severity":"HIGH","evidence":["URL_PRESENT"]}],"recommended_actions":["Quarantine the message."]}'
                }
            }],
            "usage": {"total_tokens": 123},
        },
        request=httpx.Request("POST", "https://example.test/v1/chat/completions"),
    )

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            return None
        async def post(self, *args, **kwargs):
            return response

    monkeypatch.setattr("app.ai.service.httpx.AsyncClient", FakeClient)

    result = await service.analyze(
        AIAnalysisContext(
            subject="Verify account",
            sender="alerts@example.test",
            recipient="analyst@example.org",
            reply_to="support@other.test",
            body_text="Please verify your account.",
            headers={"Authentication-Results": "spf=fail; dkim=fail; dmarc=fail"},
            deterministic={"risk_score": 70},
            indicators=[{"type": "URL", "value": "https://other.test/login", "verdict": "Unknown"}],
            attachments=[],
        )
    )

    assert result is not None
    assert result.assessment.verdict == "Phishing"
    assert result.assessment.risk_score == 88
    assert result.assessment.findings[0].severity == "HIGH"


@pytest.mark.asyncio
async def test_ai_service_fails_closed_on_provider_error(monkeypatch) -> None:
    service = AIAnalysisService(
        api_key="test-key",
        model="test-model",
        provider="openai-compatible",
        base_url="https://example.test/v1",
    )

    class FailingClient:
        def __init__(self, *args, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            return None
        async def post(self, *args, **kwargs):
            raise httpx.ConnectError("offline")

    monkeypatch.setattr("app.ai.service.httpx.AsyncClient", FailingClient)

    result = await service.analyze(
        AIAnalysisContext(
            subject="Test",
            sender=None,
            recipient=None,
            reply_to=None,
            body_text="Hello",
            headers={},
            deterministic={},
            indicators=[],
            attachments=[],
        )
    )
    assert result is None
