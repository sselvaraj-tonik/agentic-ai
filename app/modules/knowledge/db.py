import logging
import os
import time
from contextlib import contextmanager
from typing import Optional

from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

from app.config.settings import settings

logger = logging.getLogger(__name__)

_pool: Optional[ConnectionPool] = None


def to_vec(values) -> str:
    """pgvector literal, paired with a '%s::vector' cast (no type registration)."""
    return "[" + ",".join(str(float(x)) for x in values) + "]"


def _conninfo() -> str:
    return settings.DATABASE_URL.replace("postgresql+psycopg://", "postgresql://", 1)


def get_pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        _pool = ConnectionPool(
            conninfo=_conninfo(),
            min_size=1,
            max_size=int(os.getenv("KB_POOL_MAX", "4")),
            kwargs={"autocommit": True, "row_factory": dict_row},
        )
    return _pool


@contextmanager
def _cur():
    with get_pool().connection() as conn, conn.cursor() as cur:
        yield cur


# ── FAQ: nearest utterance wins, returns the parent's verbatim answer ───────
def faq_best(vec: list[float], k: int) -> Optional[dict]:
    with _cur() as cur:
        cur.execute(
            """
            SELECT f.faq_id, f.answer, f.category,
                   1 - (u.embedding <=> %s::vector) AS score
            FROM faq_utterance u
            JOIN faq f ON f.faq_id = u.faq_id
            ORDER BY u.embedding <=> %s::vector
            LIMIT %s
            """,
            (to_vec(vec), to_vec(vec), k),
        )
        row = cur.fetchone()
        return row


# ── Small talk: nearest greeting, verbatim answer ──────────────────────────
def small_talk_best(vec: list[float]) -> Optional[dict]:
    with _cur() as cur:
        cur.execute(
            """
            SELECT answer, 1 - (embedding <=> %s::vector) AS score
            FROM small_talk
            ORDER BY embedding <=> %s::vector
            LIMIT 1
            """,
            (to_vec(vec), to_vec(vec)),
        )
        return cur.fetchone()


# ── Ontology: exact / trigram lookup on the normalized utterance ───────────
def ontology_lookup(norm: str, trgm_threshold: float) -> Optional[list[str]]:
    with _cur() as cur:
        cur.execute(
            """
            SELECT suggestions, similarity(utterance_norm, %s) AS sim
            FROM ontology
            WHERE utterance_norm = %s OR similarity(utterance_norm, %s) >= %s
            ORDER BY (utterance_norm = %s) DESC, sim DESC
            LIMIT 1
            """,
            (norm, norm, norm, trgm_threshold, norm),
        )
        row = cur.fetchone()
        return list(row["suggestions"]) if row else None


# ── Open text: top-k chunks above the threshold (RAG context) ──────────────
def open_text_top(vec: list[float], k: int, threshold: float) -> list[str]:
    with _cur() as cur:
        cur.execute(
            """
            SELECT chunk_text, 1 - (embedding <=> %s::vector) AS score
            FROM open_text_chunk
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            (to_vec(vec), to_vec(vec), k),
        )
        return [r["chunk_text"] for r in cur.fetchall() if r["score"] >= threshold]


# ── Spell dictionary: {wrong_lower: correct} ───────────────────────────────
def load_spell_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    with _cur() as cur:
        cur.execute("SELECT correct_word, wrong_words FROM spell_correction")
        for row in cur.fetchall():
            correct = row["correct_word"]
            for wrong in (row["wrong_words"] or []):
                if wrong:
                    mapping[str(wrong).lower()] = correct
    return mapping
