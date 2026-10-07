import logging
from typing import Optional

from app.modules.knowledge.matchers.base import Matcher
from app.modules.knowledge.types import QueryContext, MatchResult
from app.modules.knowledge import db
from app.modules.knowledge.normalize import normalize
from app.config.settings import settings

logger = logging.getLogger(__name__)


class QuickLinkMatcher(Matcher):
    """
    Quick Links matcher — fires when user query matches a Quick Link tab name
    (e.g. 'Log-in', 'login') via exact or trigram matching. Returns the list of
    questions (variants) stored under that quick link.
    """
    name = "quick_link"

    def run(self, ctx: QueryContext) -> Optional[MatchResult]:
        norm = normalize(ctx.text)
        if not norm:
            return None
        threshold = getattr(settings, "QUICK_LINK_TRGM_THRESHOLD", 0.6)
        logger.info("QuickLinkMatcher: evaluating normalized query %r (trgm threshold=%.2f)", norm, threshold)
        ql = db.quick_link_lookup(norm, threshold)
        if ql:
            logger.info(
                "QuickLinkMatcher: MATCH found for tab %r with %d question options",
                ql["name"], len(ql["variants"])
            )
            return MatchResult(
                source="quick_link",
                kind="suggestions",
                text=f"Quick Links - {ql['name']}",
                suggestions=ql["variants"],
            )
        logger.info("QuickLinkMatcher: no quick link tab matched for query %r", norm)
        return None
