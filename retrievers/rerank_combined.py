"""
RerankCombinedRetriever — שליפה דו-שלבית:
  שלב 1: SemanticE5CombinedRetriever שולף top-N מועמדים (מהיר).
  שלב 2: cross-encoder (bge-reranker-v2-m3) קורא (שאלה, סיכום+טקסט) ומדרג מחדש.

ה-cross-encoder מודל מקומי (XLM-RoBERTa) — אין שום שימוש ב-GPT/OpenAI.
"""

from sentence_transformers import CrossEncoder

from .base import BaseRetriever
from .semantic_e5_combined import SemanticE5CombinedRetriever

RERANK_MODEL = "BAAI/bge-reranker-v2-m3"
CANDIDATES   = 20   # כמה מועמדים לדרג מחדש


class RerankCombinedRetriever(BaseRetriever):

    @property
    def name(self) -> str:
        return "rerank_combined"

    def __init__(self):
        self._base = SemanticE5CombinedRetriever()
        self._ce: CrossEncoder | None = None

    def _load(self) -> None:
        if self._ce is None:
            self._ce = CrossEncoder(RERANK_MODEL, max_length=512)

    def retrieve(self, query: str, top_k: int = 10) -> list[dict]:
        self._load()
        cands = self._base.retrieve(query, top_k=max(CANDIDATES, top_k))

        pairs  = [[query, f"{c.get('modern_summary','')} {c['text']}"] for c in cands]
        scores = self._ce.predict(pairs)

        order = sorted(range(len(cands)), key=lambda i: scores[i], reverse=True)
        results = []
        for rank, i in enumerate(order[:top_k], start=1):
            c = dict(cands[i])
            c["rank"]  = rank
            c["score"] = round(float(scores[i]), 4)
            results.append(c)
        return results
