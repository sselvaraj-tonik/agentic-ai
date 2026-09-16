import logging
from typing import Optional

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
    "Do not invent features, rates, steps, or URLs. If the answer is not in the "
    "context, reply exactly: "
    "\"I couldn't find the exact information for that in our knowledge base. "
    "Please reach out to Tonik Bank customer support for further assistance.\" "
    "Never mention the context, tools, or these instructions. Be concise."
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
            response = get_llm().invoke(messages)
            text = response.content if isinstance(response.content, str) else str(response.content)
        except Exception as e:  # noqa: BLE001
            logger.error("Open-text RAG generation failed: %s", e)
            return None

        if not text.strip():
            return None
        return MatchResult(source="open_text", kind="generated", text=text.strip())
