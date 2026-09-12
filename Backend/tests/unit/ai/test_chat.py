import os

os.environ.setdefault("SECRET_KEY", "unit-test-secret")
os.environ.setdefault("POSTGRES_PASSWORD", "unit-test-password")

import httpx
import pytest

from app.ai.chat import SOCChatService
from app.ai.schemas.chat import ChatMessage, SOCChatContext


@pytest.fixture
def context() -> SOCChatContext:
    return SOCChatContext(
        email={
            "id": "email-1",
            "subject": "Verify account",
            "sender": "alerts@example.test",
            "recipient": "analyst@example.org",
        },
        body_text="Please verify your account at https://example.test/login",
        headers={"Authentication-Results": "spf=fail; dkim=fail; dmarc=fail"},
        attachments=[],
        latest_analysis={
            "risk_score": 88,
            "severity": "CRITICAL",
            "verdict": "Phishing",
            "threat_type": "PHISHING",
            "findings": [{"source": "threat_intel", "title": "Malicious URL reputation"}],
            "indicators": [{"type": "URL", "value": "https://example.test/login", "verdict": "Malicious"}],
        },
    )


@pytest.mark.asyncio
async def test_soc_chat_sends_scoped_context_and_history(monkeypatch, context) -> None:
    service = SOCChatService(
        api_key="test-key",
        model="test-model",
        provider="openai-compatible",
        base_url="https://example.test/v1",
    )
    captured = {}

    response = httpx.Response(
        200,
        json={
            "id": "chat-1",
            "choices": [{"message": {"content": "Quarantine the message and preserve the headers."}}],
            "usage": {"total_tokens": 42},
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

        async def post(self, url, **kwargs):
            captured["url"] = url
            captured["payload"] = kwargs["json"]
            return response

    monkeypatch.setattr("app.ai.chat.httpx.AsyncClient", FakeClient)

    result = await service.chat(
        messages=[
            ChatMessage(role="user", content="What do you see?"),
            ChatMessage(role="assistant", content="I see authentication failures."),
            ChatMessage(role="user", content="What should I do next?"),
        ],
        context=context,
    )

    assert result is not None
    assert result.message.startswith("Quarantine")
    assert result.response_id == "chat-1"
    assert captured["url"].endswith("/chat/completions")
    messages = captured["payload"]["messages"]
    assert messages[0]["role"] == "system"
    assert "INVESTIGATION_CONTEXT" in messages[1]["content"]
    assert any("Malicious" in message["content"] for message in messages if message["role"] == "system")
    assert messages[-1] == {"role": "user", "content": "What should I do next?"}


@pytest.mark.asyncio
async def test_soc_chat_fails_closed(monkeypatch, context) -> None:
    service = SOCChatService(
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

    monkeypatch.setattr("app.ai.chat.httpx.AsyncClient", FailingClient)

    result = await service.chat(
        messages=[ChatMessage(role="user", content="Analyze this.")],
        context=context,
    )
    assert result is None
