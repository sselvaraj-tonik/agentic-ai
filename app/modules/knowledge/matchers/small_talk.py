from typing import Optional

from app.modules.knowledge.matchers.base import Matcher
from app.modules.knowledge.types import QueryContext, MatchResult
from app.modules.knowledge import db
from app.config.settings import settings


class SmallTalkMatcher(Matcher):
    """
    Semantic match against small-talk phrases. 'I need your help' still matches
    the stored 'hi i need help'. Returns the stored answer VERBATIM (no LLM).
    """
    name = "small_talk"

    def run(self, ctx: QueryContext) -> Optional[MatchResult]:
        row = db.small_talk_best(ctx.embedding())
        if row and row["score"] >= settings.SMALLTALK_THRESHOLD:
            return MatchResult(
                source="small_talk",
                kind="answer",
                text=row["answer"],
                score=float(row["score"]),
            )
        return None
