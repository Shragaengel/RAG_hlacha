"""
SemanticE5LargeRetriever — שליפה סמנטית ברמת סעיף עם multilingual-e5-large.

טוען data/seifs_e5_large.npy (מטריצה מנורמלת) + data/seifs.json.
שאילתה: prefix "query:" → דמיון קוסינוס (query @ emb.T) → top-k.
"""

import json

import numpy as np
from sentence_transformers import SentenceTransformer

from config import SEIFS_FILE, EMBED_MODEL, EMBEDDINGS_E5_LARGE
from .base import BaseRetriever


class SemanticE5LargeRetriever(BaseRetriever):

    @property
    def name(self) -> str:
        return "semantic_e5_large"

    def __init__(self):
        self._model: SentenceTransformer | None = None
        self._emb: np.ndarray | None = None
        self._seifs: list[dict] | None = None

    def _load(self) -> None:
        if self._model is not None:
            return
        self._model = SentenceTransformer(EMBED_MODEL)
        self._emb = np.load(str(EMBEDDINGS_E5_LARGE))
        with open(SEIFS_FILE, encoding="utf-8") as f:
            self._seifs = json.load(f)

    def retrieve(self, query: str, top_k: int = 10) -> list[dict]:
        self._load()
        k = min(top_k, len(self._seifs))

        q_vec = self._model.encode(
            "query: " + query,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        scores = self._emb @ q_vec
        top = np.argpartition(scores, -k)[-k:]
        top = top[np.argsort(scores[top])[::-1]]

        results = []
        for rank, idx in enumerate(top, start=1):
            s = self._seifs[idx]
            results.append({
                "rank":         rank,
                "chunk_id":     s["chunk_id"],
                "score":        round(float(scores[idx]), 4),
                "text":         s["text"],
                "siman_parent": s["siman"],
                "seif":         s["seif"],
                "ref":          s["ref"],
            })
        return results
