"""
Renders stored answers/results into the plain-text string the /chat API returns.
FAQ answers are returned VERBATIM — this only selects the right channel and
concatenates the stored text messages; it never rewrites wording.
"""
from typing import Optional

from app.modules.knowledge.types import MatchResult


def render_faq_answer(answer: dict, channel: str = "default") -> Optional[str]:
    """
    answer = {response_type, answer_default, answers}
      - answer_default (str)  -> returned as-is
      - answers (list)        -> pick the channel entry, join its text messages
    """
    if not answer:
        return None

    default = answer.get("answer_default")
    if isinstance(default, str) and default.strip():
        return default

    answers = answer.get("answers")
    if isinstance(answers, list) and answers:
        entry = _pick_channel(answers, channel)
        parts = []
        for msg in entry.get("messages", []) or []:
            if msg.get("type") == "text" and msg.get("content"):
                parts.append(msg["content"].rstrip("\n"))
        if parts:
            return "\n".join(parts)
    return None


def _pick_channel(answers: list, channel: str) -> dict:
    for a in answers:
        if a.get("channel") == channel:
            return a
    for a in answers:
        if a.get("channel") == "default":
            return a
    return answers[0]


def to_text(result: MatchResult) -> str:
    """Final string for the chat response."""
    if result.kind == "suggestions" and result.suggestions:
        lines = "\n".join(f"• {s}" for s in result.suggestions)
        return f"Did you mean:\n{lines}"
    return result.text or ""
