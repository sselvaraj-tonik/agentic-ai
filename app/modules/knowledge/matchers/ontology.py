from typing import Optional

from app.modules.knowledge.matchers.base import Matcher
from app.modules.knowledge.types import QueryContext, MatchResult
from app.modules.knowledge import db
from app.modules.knowledge.normalize import normalize
from app.config.settings import settings


class OntologyMatcher(Matcher):
    """
    "Did you mean?" — fires only when the whole message is (near-)exactly a
    bare ontology utterance (e.g. user types just 'refunded?'). Returns the
    stored suggestion list.
    """
    name = "ontology"

    def run(self, ctx: QueryContext) -> Optional[MatchResult]:
        norm = normalize(ctx.text)
        if not norm:
            return None
        suggestions = db.ontology_lookup(norm, settings.ONTOLOGY_TRGM_THRESHOLD)
        if suggestions:
            return MatchResult(
                source="ontology",
                kind="suggestions",
                suggestions=suggestions,
            )
        return None
