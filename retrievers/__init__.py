"""
Retriever Registry — מוסיפים כאן כל retriever חדש.

הוספת retriever חדש:
    1. צור קובץ חדש ב-retrievers/ (לדוגמה: semantic_e5.py)
    2. ייבא אותו והוסף כניסה ל-REGISTRY למטה
    3. הרץ: python run_experiment.py --retriever semantic_e5 --name exp_001_baseline
"""

from .base import BaseRetriever
from .semantic_e5_large import SemanticE5LargeRetriever
from .semantic_e5_combined import SemanticE5CombinedRetriever

REGISTRY: dict[str, type[BaseRetriever]] = {
    "semantic_e5_large":    SemanticE5LargeRetriever,
    "semantic_e5_combined": SemanticE5CombinedRetriever,
}


def get_retriever(name: str) -> BaseRetriever:
    """מחזיר instance של retriever לפי שם."""
    if name not in REGISTRY:
        available = list(REGISTRY.keys())
        raise ValueError(f"Retriever '{name}' לא נמצא. זמינים: {available}")
    return REGISTRY[name]()


def list_retrievers() -> list[str]:
    return list(REGISTRY.keys())
