from __future__ import annotations

import re

_PUNCT_RE = re.compile(r"[^a-zA-Z0-9\s]")
_SPACE_RE = re.compile(r"\s+")


def run(payload: dict) -> str:
    query = str((payload or {}).get("query") or "")
    lowered = query.lower()
    no_punct = _PUNCT_RE.sub(" ", lowered)
    normalized = _SPACE_RE.sub(" ", no_punct).strip()
    return normalized
