"""
Deterministic, reorderable knowledge-inference pipeline.

A user query is run through an ordered list of matchers (configured by
settings.INFERENCE_ORDER). The first matcher that produces a result wins.
See app/modules/knowledge/pipeline.py.
"""
from app.modules.knowledge.service import answer_query

__all__ = ["answer_query"]
