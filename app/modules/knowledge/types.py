from dataclasses import dataclass, field
from typing import Optional


@dataclass
class QueryContext:
    """
    Carries the query through the pipeline. `text` is the working form
    (spell-correction mutates it); `embedding()` is computed once and reused
    by every vector matcher, so we embed at most once per request.
    """
    raw: str
    text: str = ""
    _embedding: Optional[list[float]] = field(default=None, repr=False)

    def __post_init__(self):
        if not self.text:
            self.text = self.raw

    def embedding(self) -> list[float]:
        if self._embedding is None:
            # Imported lazily so types/render stay importable without the
            # embedding backend, and the heavy client loads only when needed.
            from app.modules.knowledge.embeddings import embed_query
            self._embedding = embed_query(self.text)
        return self._embedding

    def reset_embedding(self):
        """Call after mutating `text` so the vector is recomputed."""
        self._embedding = None


@dataclass
class MatchResult:
    source: str                     # small_talk | faq | open_text | ontology | fallback
    kind: str                       # answer | suggestions | generated | fallback
    text: Optional[str] = None
    suggestions: Optional[list[str]] = None
    score: Optional[float] = None
