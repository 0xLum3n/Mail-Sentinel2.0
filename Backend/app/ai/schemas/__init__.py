"""Structured schemas for AI-assisted security analysis."""

from app.ai.schemas.chat import ChatMessage, SOCChatContext, SOCChatRequest, SOCChatResponse
from app.ai.schemas.email import AIAnalysisContext, AIAnalysisResult, AIEmailAssessment, AIFinding

__all__ = [
    "AIAnalysisContext",
    "AIAnalysisResult",
    "AIEmailAssessment",
    "AIFinding",
    "ChatMessage",
    "SOCChatContext",
    "SOCChatRequest",
    "SOCChatResponse",
]
