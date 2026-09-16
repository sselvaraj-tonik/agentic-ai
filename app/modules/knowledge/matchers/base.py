from abc import ABC, abstractmethod
from typing import Optional

from app.modules.knowledge.types import QueryContext, MatchResult


class Matcher(ABC):
    """
    One tier of the inference funnel.

    run() returns a MatchResult to STOP the pipeline and answer, or None to
    fall through to the next tier. Preprocessors (e.g. spell correction) mutate
    the context and always return None.
    """
    name: str = "matcher"

    @abstractmethod
    def run(self, ctx: QueryContext) -> Optional[MatchResult]:
        ...
