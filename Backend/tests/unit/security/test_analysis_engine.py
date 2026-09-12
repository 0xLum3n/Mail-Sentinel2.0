from app.models.email import EmailMessage
from app.security.analysis_engine import analyze_email
from app.security.email_parser import parse_email


def _email(raw: bytes) -> EmailMessage:
    parsed = parse_email(raw)
    email = EmailMessage(
        subject=parsed.subject,
        sender_email=parsed.sender_email,
        recipient_email=parsed.recipient_email,
        reply_to_email=parsed.reply_to_email,
        body_text=parsed.body_text,
        body_html=parsed.body_html,
        headers=parsed.headers,
    )
    email.attachments = []
    return email


def test_high_signal_message_gets_elevated_score() -> None:
    raw = b"""Authentication-Results: mx.example; spf=fail; dkim=fail; dmarc=fail\nReceived: from attacker ([8.8.8.8]) by mx.local;\nFrom: billing@evil.example\nReply-To: login@evil-login.example\nTo: analyst@example.com\nSubject: URGENT: Verify Your Account Within 24 Hours\nContent-Type: text/plain; charset=utf-8\n\nVerify your account immediately at https://evil-login.example/verify\n"""
    result = analyze_email(_email(raw))

    assert result.headers.spf == "FAIL"
    assert result.headers.dkim == "FAIL"
    assert result.headers.dmarc == "FAIL"
    assert any(item.type == "URL" for item in result.indicators)
    assert any(item.type == "IP" and item.value == "8.8.8.8" for item in result.indicators)
    assert result.score.risk_score >= 60
    assert result.score.threat_type == "SUSPICIOUS"


def test_clean_message_has_no_strong_deterministic_signal() -> None:
    raw = b"""Authentication-Results: mx.example; spf=pass; dkim=pass; dmarc=pass\nFrom: hr@example.com\nTo: user@example.com\nSubject: Weekly Schedule\nContent-Type: text/plain; charset=utf-8\n\nHere is the weekly schedule for next Monday.\n"""
    result = analyze_email(_email(raw))

    assert result.headers.spf == "PASS"
    assert result.headers.dkim == "PASS"
    assert result.headers.dmarc == "PASS"
    assert result.score.risk_score < 30
    assert result.score.severity == "LOW"
