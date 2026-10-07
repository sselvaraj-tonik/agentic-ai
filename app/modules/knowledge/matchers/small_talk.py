import json
import random
from typing import Optional

from app.modules.knowledge.matchers.base import Matcher
from app.modules.knowledge.types import QueryContext, MatchResult
from app.modules.knowledge import db
from app.config.settings import settings


def _pick_reply(stored: str) -> str:
    """The stored answer may hold several replies: a JSON array, or a Postgres
    array literal ('{"a","b"}') from older ingests. Return one at random."""
    s = (stored or "").strip()
    candidates = None
    if s.startswith("["):
        candidates = s
    elif s.startswith("{") and s.endswith("}"):
        candidates = "[" + s[1:-1] + "]"  # quoted elements are JSON-compatible
    if candidates:
        try:
            replies = [r for r in json.loads(candidates) if isinstance(r, str) and r.strip()]
            if replies:
                return random.choice(replies)
        except ValueError:
            pass
    return stored


class SmallTalkMatcher(Matcher):
    """
    Semantic match against small-talk phrases. 'I need your help' still matches
    the stored 'hi i need help'. Returns a stored answer VERBATIM (no LLM);
    when several replies are stored, one is picked at random.
    """
    name = "small_talk"

    def run(self, ctx: QueryContext) -> Optional[MatchResult]:
        row = db.small_talk_best(ctx.embedding())
        if row and row["score"] >= settings.SMALLTALK_THRESHOLD:
            return MatchResult(
                source="small_talk",
                kind="answer",
                text=_pick_reply(row["answer"]),
                score=float(row["score"]),
            )
        return None
