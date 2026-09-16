import logging

from app.modules.knowledge.matchers.base import Matcher
from app.modules.knowledge.matchers.spell import SpellCorrector
from app.modules.knowledge.matchers.small_talk import SmallTalkMatcher
from app.modules.knowledge.matchers.ontology import OntologyMatcher
from app.modules.knowledge.matchers.faq import FaqMatcher
from app.modules.knowledge.matchers.open_text import OpenTextMatcher
from app.modules.knowledge.matchers.fallback import FallbackMatcher
from app.modules.knowledge.types import QueryContext, MatchResult
from app.config.settings import settings

logger = logging.getLogger(__name__)

# name -> factory. To add a tier, register it here and reference it in
# settings.INFERENCE_ORDER. To reorder, just change INFERENCE_ORDER.
REGISTRY: dict[str, type[Matcher]] = {
    "spell": SpellCorrector,
    "small_talk": SmallTalkMatcher,
    "ontology": OntologyMatcher,
    "faq": FaqMatcher,
    "open_text": OpenTextMatcher,
    "fallback": FallbackMatcher,
}


class InferencePipeline:
    def __init__(self, order: list[str]):
        unknown = [n for n in order if n not in REGISTRY]
        if unknown:
            raise ValueError(f"Unknown matcher(s) in INFERENCE_ORDER: {unknown}")
        # Guarantee a terminal fallback even if it's left out of the config.
        if "fallback" not in order:
            order = [*order, "fallback"]
        self.matchers: list[Matcher] = [REGISTRY[name]() for name in order]
        logger.info("Inference pipeline order: %s", [m.name for m in self.matchers])

    def run(self, query: str) -> MatchResult:
        ctx = QueryContext(raw=query)
        for matcher in self.matchers:
            try:
                result = matcher.run(ctx)
            except Exception as e:  # noqa: BLE001
                logger.error("Matcher '%s' failed: %s", matcher.name, e)
                continue
            if result is not None:
                logger.info(
                    "Matched by '%s' (score=%s)", result.source, result.score
                )
                return result
        # Unreachable (fallback always matches), but keep the type contract.
        from app.modules.knowledge.matchers.fallback import FALLBACK_REPLY
        return MatchResult(source="fallback", kind="fallback", text=FALLBACK_REPLY)


def build_pipeline() -> InferencePipeline:
    return InferencePipeline(list(settings.INFERENCE_ORDER))
