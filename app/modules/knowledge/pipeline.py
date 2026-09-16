import logging
import time

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

# Human-readable technique per tier, for log lines.
TECHNIQUE: dict[str, str] = {
    "spell": "in-memory {wrong->correct} map",
    "small_talk": "embed + HNSW cosine (verbatim)",
    "ontology": "normalized exact / pg_trgm on full message",
    "faq": "1x embed + HNSW cosine, threshold-gated (verbatim)",
    "open_text": "reuse embed + HNSW + LLM generate",
    "fallback": "code-level constant",
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
        pipeline_start = time.perf_counter()
        for tier, matcher in enumerate(self.matchers):
            technique = TECHNIQUE.get(matcher.name, "")
            logger.info("Tier %d '%s' [%s] — evaluating", tier, matcher.name, technique)
            t0 = time.perf_counter()
            try:
                result = matcher.run(ctx)
            except Exception as e:  # noqa: BLE001
                logger.error("Tier %d '%s' failed: %s", tier, matcher.name, e)
                continue
            took_ms = (time.perf_counter() - t0) * 1000
            if result is not None:
                total_ms = (time.perf_counter() - pipeline_start) * 1000
                logger.info(
                    "Tier %d '%s' — MATCH (kind=%s, score=%s) in %.1fms; "
                    "resolved in %.1fms total",
                    tier, matcher.name, result.kind, result.score, took_ms, total_ms,
                )
                return result
            logger.info("Tier %d '%s' — pass (%.1fms)", tier, matcher.name, took_ms)
        # Unreachable (fallback always matches), but keep the type contract.
        from app.modules.knowledge.matchers.fallback import FALLBACK_REPLY
        return MatchResult(source="fallback", kind="fallback", text=FALLBACK_REPLY)


def build_pipeline() -> InferencePipeline:
    return InferencePipeline(list(settings.INFERENCE_ORDER))
