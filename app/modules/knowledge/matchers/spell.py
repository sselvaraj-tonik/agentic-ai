import re
import time
from typing import Optional

from app.modules.knowledge.matchers.base import Matcher
from app.modules.knowledge.types import QueryContext, MatchResult
from app.modules.knowledge import db

_TOKEN = re.compile(r"\w+|\W+")


class SpellCorrector(Matcher):
    """
    Pre-processor: rewrites misspelled tokens using the spell dictionary so the
    query matches the other sources (e.g. 'laon' -> 'loan'). Never answers.

    The dictionary is small and finite, so it's cached in memory with a TTL.
    """
    name = "spell"

    def __init__(self, ttl_seconds: int = 300):
        self._ttl = ttl_seconds
        self._map: dict[str, str] = {}
        self._loaded_at = 0.0

    def _get_map(self) -> dict[str, str]:
        now = time.time()
        if now - self._loaded_at > self._ttl or not self._map:
            try:
                self._map = db.load_spell_map()
                self._loaded_at = now
            except Exception:
                # Never let spell-check break inference; fall through uncorrected.
                pass
        return self._map

    def run(self, ctx: QueryContext) -> Optional[MatchResult]:
        mapping = self._get_map()
        if not mapping:
            return None
        corrected = "".join(
            mapping.get(tok.lower(), tok) if tok.strip() and tok.isalnum() else tok
            for tok in _TOKEN.findall(ctx.text)
        )
        if corrected != ctx.text:
            ctx.text = corrected
            ctx.reset_embedding()
        return None
