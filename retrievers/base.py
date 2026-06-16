"""
BaseRetriever — interface אחיד לכל שיטות השליפה.

כל retriever חדש חייב לרשת מחלקה זו ולממש name + retrieve().
המבנה המוחזר זהה תמיד, כך שמנוע ההערכה עובד עם כל retriever ללא שינוי.
"""

from abc import ABC, abstractmethod


class BaseRetriever(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        """שם ייחודי לניסוי (לדוגמה: 'semantic_e5', 'bm25')."""

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 10) -> list[dict]:
        """
        שולף יחידות (סעיפים/chunks) רלוונטיות לשאילתה.

        Args:
            query:  שאלה בעברית
            top_k:  כמה יחידות להחזיר

        Returns:
            רשימת dict ממוינת לפי רלוונטיות, כל אחד מכיל לפחות:
                rank          — דירוג (1 = הכי רלוונטי)
                chunk_id      — מזהה היחידה
                score         — ציון רלוונטיות (גבוה = טוב יותר)
                text          — טקסט היחידה
                siman_parent  — מספר הסימן שהיחידה שייכת אליו
                seif          — מספר הסעיף (אם רלוונטי, אחרת None)
        """
