from typing import Optional

from app.modules.knowledge.matchers.base import Matcher
from app.modules.knowledge.types import QueryContext, MatchResult
from app.modules.knowledge import db
from app.modules.knowledge.render import render_faq_answer
from app.config.settings import settings


class FaqMatcher(Matcher):
    """
    Semantic match over FAQ questions + variants. Above threshold, returns the
    stored answer VERBATIM (no LLM) — Answer_default_default or the Answers[]
    channel content, unchanged.
    """
    name = "faq"

    def run(self, ctx: QueryContext) -> Optional[MatchResult]:
        row = db.faq_best(ctx.embedding(), settings.FAQ_TOP_K)
        if not row or row["score"] < settings.FAQ_THRESHOLD:
            return None
        text = render_faq_answer(row["answer"], channel=settings.FAQ_ANSWER_CHANNEL)
        if not text:
            return None
        return MatchResult(
            source="faq",
            kind="answer",
            text=text,
            score=float(row["score"]),
        )
