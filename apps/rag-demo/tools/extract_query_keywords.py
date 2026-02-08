from __future__ import annotations

import re

_PUNCT_RE = re.compile(r"[^a-zA-Z0-9\s]")
_SPACE_RE = re.compile(r"\s+")
_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "with",
}


def _normalize(value: str) -> str:
    lowered = value.lower()
    no_punct = _PUNCT_RE.sub(" ", lowered)
    return _SPACE_RE.sub(" ", no_punct).strip()


def run(payload: dict) -> list[str]:
    query = str((payload or {}).get("query") or "")
    normalized = _normalize(query)
    if not normalized:
        return []

    ordered: list[str] = []
    seen: set[str] = set()
    for token in normalized.split(" "):
        if not token or token in _STOPWORDS:
            continue
        if token in seen:
            continue
        seen.add(token)
        ordered.append(token)
        if len(ordered) >= 24:
            break
    return ordered
