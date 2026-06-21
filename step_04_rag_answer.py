"""
Step 4 — RAG מלא: שאלה → שליפה → גנרציה (Ollama מקומי) → תשובה
================================================================
סוגר את לולאת ה-RAG: שולף את הסעיפים הרלוונטיים (combined), בונה פרומפט,
ושולח ל-DictaLM 2.0 דרך Ollama המקומי. בלי GPT, לגמרי אופליין.

שימוש:
    python step_04_rag_answer.py "האם מותר לאכול דג עם בשר?"
    python step_04_rag_answer.py "..." 5      # 5 סעיפי הקשר
"""

import json
import sys
import urllib.request
from pathlib import Path

from config import OLLAMA_URL, OLLAMA_MODEL
from retrievers import get_retriever

RETRIEVER   = "semantic_e5_combined"
TOP_K_CTX   = 3

SYSTEM_PROMPT = (
    "אתה עוזר הלכתי המבוסס על קיצור שולחן ערוך. "
    "ענה על השאלה אך ורק על סמך הסעיפים המצורפים למטה. "
    "אם התשובה אינה נמצאת בסעיפים, אמור בפירוש שאינך יודע ולא נמצא בהם מענה. "
    "ענה בעברית ברורה ותמציתית, וציין בסוף את הסימן והסעיף שעליהם התבססת.\n\n"
    "הסעיפים:\n{context}"
)


def build_context(chunks: list[dict]) -> str:
    return "\n\n".join(
        f"[סימן {c['siman_parent']} סעיף {c['seif']}] {c['text']}" for c in chunks
    )


def ask_ollama(question: str, context: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT.format(context=context)},
            {"role": "user",   "content": question},
        ],
        "stream": False,
        "options": {"temperature": 0.2},
    }
    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    resp = json.load(urllib.request.urlopen(req, timeout=600))
    return resp["message"]["content"].strip()


def answer(question: str, top_k_ctx: int = TOP_K_CTX) -> tuple[str, list[dict]]:
    """מחזיר (תשובה, סעיפים שנשלפו)."""
    retriever = get_retriever(RETRIEVER)
    chunks = retriever.retrieve(question, top_k=top_k_ctx)
    ans = ask_ollama(question, build_context(chunks))
    return ans, chunks


def main() -> None:
    question  = sys.argv[1] if len(sys.argv) > 1 else input("שאלה: ")
    top_k_ctx = int(sys.argv[2]) if len(sys.argv) > 2 else TOP_K_CTX

    ans, chunks = answer(question, top_k_ctx)

    lines = [f"שאלה: {question}", "", "תשובה:", ans, "", "מקורות שנשלפו:"]
    for c in chunks:
        lines.append(f"  [{c['ref']}] (score={c['score']:.3f}) {c['text'][:90]}...")
    Path("data/_last_answer.txt").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
