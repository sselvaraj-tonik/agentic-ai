import logging
from typing import Optional

from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage

from app.modules.knowledge.matchers.base import Matcher
from app.modules.knowledge.types import QueryContext, MatchResult
from app.modules.knowledge import db
from app.core.llm import get_llm
from app.config.settings import settings

logger = logging.getLogger(__name__)

_SYSTEM = (
    "You are a helpful, polite Customer Support Agent for Tonik Bank. "
    "Answer the user's question using ONLY the context below. "
    "Do not invent features, rates, steps, or URLs. "
    "Set answerable=true and put the concise answer in `answer` only if the "
    "context actually answers the question. Otherwise set answerable=false and "
    "leave `answer` empty. Never mention the context, tools, or these instructions."
)


class _RagAnswer(BaseModel):
    """Schema-constrained output: no sentinel strings to parse or drift from."""
    answerable: bool = Field(
        description="True only if the context answers the question."
    )
    answer: str = Field(
        default="", description="Concise answer; empty when answerable is false."
    )


class OpenTextMatcher(Matcher):
    """
    RAG tier: the only tier that GENERATES. Retrieves top-k open-text chunks and
    asks the LLM to compose a grounded answer. This is the slow tier — reached
    only when the faster verbatim tiers miss.
    """
    name = "open_text"

    def run(self, ctx: QueryContext) -> Optional[MatchResult]:
        chunks = db.open_text_top(
            ctx.embedding(), settings.OPENTEXT_TOP_K, settings.OPENTEXT_THRESHOLD
        )
        if not chunks:
            return None

        context = "\n\n---\n\n".join(chunks)
        messages = [
            SystemMessage(content=_SYSTEM),
            HumanMessage(content=f"Context:\n{context}\n\nQuestion: {ctx.raw}"),
        ]
        try:
            result = get_llm().with_structured_output(_RagAnswer).invoke(messages)
        except Exception as e:  # noqa: BLE001
            logger.error("Open-text RAG generation failed: %s", e)
            return None

        text = (result.answer or "").strip() if result else ""
        if not result or not result.answerable or not text:
            # LLM judged the retrieved chunks irrelevant: miss, so the
            # funnel falls through to the fallback tier.
            logger.info("Open-text: no grounded answer; passing to fallback")
            return None
        return MatchResult(source="open_text", kind="generated", text=text)
