"""AI prompt exports."""

from app.ai.prompts.email_analysis import SYSTEM_PROMPT, USER_TEMPLATE
from app.ai.prompts.soc_chat import SOC_CHAT_SYSTEM_PROMPT

__all__ = ["SYSTEM_PROMPT", "USER_TEMPLATE", "SOC_CHAT_SYSTEM_PROMPT"]
