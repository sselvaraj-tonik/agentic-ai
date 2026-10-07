import json
import logging
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
    replies = None
    if s.startswith("["):
        try:
            replies = json.loads(s)
        except ValueError:
            pass
    elif s.startswith("{") and s.endswith("}"):
        replies = _parse_pg_array(s)
    replies = [r for r in (replies or []) if isinstance(r, str) and r.strip()]
    return random.choice(replies) if replies else stored


def _parse_pg_array(s: str) -> list[str]:
    """Parse a 1-D Postgres text-array literal. Elements are quoted only when
    they hold special characters, so '{"a, b",Awesome!}' mixes both forms."""
    items, buf, i, n = [], [], 1, len(s) - 1
    while i < n:
        ch = s[i]
        if ch == '"':
            i += 1
            while i < n and s[i] != '"':
                if s[i] == "\\" and i + 1 < n:
                    i += 1
                buf.append(s[i])
                i += 1
        elif ch == ",":
            items.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
        i += 1
    items.append("".join(buf))
    return items


logger = logging.getLogger(__name__)


class SmallTalkMatcher(Matcher):
    """
    Semantic match against small-talk phrases. 'I need your help' still matches
    the stored 'hi i need help'. Returns a stored answer VERBATIM (no LLM);
    when several replies are stored, one is picked at random.
    """
    name = "small_talk"

    def run(self, ctx: QueryContext) -> Optional[MatchResult]:
        rows = db.small_talk_top(ctx.embedding(), 3)
        logger.debug("small_talk top candidates: %s",
                    [(r["question"], round(float(r["score"]), 3)) for r in rows])
        row = rows[0] if rows else None
        if row and row["score"] >= settings.SMALLTALK_THRESHOLD:
            return MatchResult(
                source="small_talk",
                kind="answer",
                text=_pick_reply(row["answer"]),
                score=float(row["score"]),
            )
        return None
