from typing import Optional

from app.modules.knowledge.matchers.base import Matcher
from app.modules.knowledge.types import QueryContext, MatchResult

# Code-level fallback — always available, even if the DB is empty/unreachable.
FALLBACK_REPLY = (
    "I couldn't find an answer for that. You can reach our Customer Care via the "
    "Tonik App, Viber (Tonik Digital Bank), Hotline +63253222645, or "
    "customercare@tonikbank.com."
)


class FallbackMatcher(Matcher):
    """Terminal tier: no source matched. Always returns the canned reply."""
    name = "fallback"

    def run(self, ctx: QueryContext) -> Optional[MatchResult]:
        return MatchResult(source="fallback", kind="fallback", text=FALLBACK_REPLY)
