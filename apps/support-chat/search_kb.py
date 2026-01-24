from __future__ import annotations

import json
from pathlib import Path

KB_PATH = Path(__file__).resolve().parent / "kb.json"


def _load_entries() -> list[dict]:
    data = json.loads(KB_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict)]


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


def _tokenize(text: str) -> list[str]:
    return [token for token in _normalize(text).split(" ") if token]


def _score(question: str, tokens: list[str]) -> int:
    haystack = _normalize(question)
    score = 0
    for token in tokens:
        if token in haystack:
            score += 1
    return score


def run(payload: dict) -> dict:
    """Deterministic KB lookup based on question keyword overlap."""
    query = str(payload.get("query") or "")
    tokens = _tokenize(query)
    entries = _load_entries()

    best_answer = ""
    best_score = 0
    best_index = None

    for idx, entry in enumerate(entries):
        question = str(entry.get("question") or "")
        answer = str(entry.get("answer") or "")
        if not question or not answer:
            continue
        score = _score(question, tokens)
        if score > best_score:
            best_score = score
            best_answer = answer
            best_index = idx
        elif score == best_score and score > 0 and best_index is not None:
            # Stable tie-breaker: earlier entries win.
            if idx < best_index:
                best_answer = answer
                best_index = idx

    if best_score == 0:
        best_answer = ""

    return {"answer": best_answer}
