import re

_WS = re.compile(r"\s+")
_TRAILING_PUNCT = re.compile(r"[\s?!.,]+$")


def normalize(text: str) -> str:
    """Lowercase, collapse whitespace, strip trailing punctuation (lookup key)."""
    if not text:
        return ""
    t = _WS.sub(" ", text.strip().lower())
    return _TRAILING_PUNCT.sub("", t)
