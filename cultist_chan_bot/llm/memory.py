"""Vector memory for persona context."""

from __future__ import annotations

from typing import List

import numpy as np
import faiss
import json
from pathlib import Path

try:
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover - optional dependency errors
    SentenceTransformer = None


from .config import load_config

_EMBED_DIM = 384
_MODEL: SentenceTransformer | None = None

_CFG = load_config()
_INDEX_PATH = Path(_CFG.MEMORY_PATH)
_DATA_PATH = _INDEX_PATH.with_suffix(".json")

_INDEX: faiss.IndexFlatIP | None = None
_DATA: List[dict] = []


def _get_encoder() -> SentenceTransformer:
    global _MODEL
    if _MODEL is None:
        if not SentenceTransformer:
            raise RuntimeError("sentence-transformers not available")
        _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _MODEL


def _embed(text: str) -> np.ndarray:
    model = _get_encoder()
    vec = model.encode([text])[0].astype("float32")
    return np.expand_dims(vec, 0)


def _load_memory() -> None:
    """Load stored vectors from disk."""
    global _INDEX, _DATA
    if _INDEX_PATH.exists():
        try:
            _INDEX = faiss.read_index(str(_INDEX_PATH))
        except Exception:
            _INDEX = faiss.IndexFlatIP(_EMBED_DIM)
        if _DATA_PATH.exists():
            _DATA = json.loads(_DATA_PATH.read_text())
        else:
            _DATA = []
    else:
        _INDEX = faiss.IndexFlatIP(_EMBED_DIM)
        _DATA = []


def _persist_memory() -> None:
    faiss.write_index(_INDEX, str(_INDEX_PATH))
    _DATA_PATH.write_text(json.dumps(_DATA))


def save_interaction(user_id: int, message: str, reply: str) -> None:
    """Save conversation pair for user."""
    vec = _embed(message + " " + reply)
    _INDEX.add(vec)
    _DATA.append({"user_id": user_id, "message": message, "reply": reply})
    _persist_memory()


def retrieve_context(user_id: int, k: int = 3, query: str | None = None) -> List[dict]:
    """Return similar past interactions."""
    if not _DATA:
        return []
    if query:
        vec = _embed(query)
        _, idxs = _INDEX.search(vec, len(_DATA))
        ids = idxs[0]
    else:
        ids = range(len(_DATA) - 1, -1, -1)
    results = []
    for i in ids:
        item = _DATA[i]
        if item["user_id"] == user_id:
            results.append({"message": item["message"], "reply": item["reply"]})
            if len(results) >= k:
                break
    return results


_load_memory()

