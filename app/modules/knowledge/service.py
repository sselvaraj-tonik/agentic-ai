from functools import lru_cache

from app.modules.knowledge.pipeline import build_pipeline, InferencePipeline
from app.modules.knowledge.types import MatchResult


@lru_cache(maxsize=1)
def _pipeline() -> InferencePipeline:
    return build_pipeline()


def answer_query(query: str) -> MatchResult:
    """Run the query through the configured inference funnel."""
    return _pipeline().run(query or "")
