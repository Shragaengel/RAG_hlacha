"""
Step 4 — RAG מלא: שאלה → שליפה → גנרציה → תשובה
================================================================
סוגר את לולאת ה-RAG: שולף את הסעיפים הרלוונטיים (combined), בונה פרומפט,
ושולח למודל גנרציה. שני backends:
  • "ollama" (ברירת מחדל) — DictaLM 2.0 מקומי, אופליין.
  • "openai" — GPT. דורש מפתח משלך ב-OPENAI_API_KEY (סביבה/.env). לא נשמר בקוד.

שימוש:
    python step_04_rag_answer.py "האם מותר לאכול דג עם בשר?"
    python step_04_rag_answer.py "..." 5                 # 5 סעיפי הקשר
    python step_04_rag_answer.py "..." 3 openai          # backend GPT (BYO key)
"""

import json
import os
import sys
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

from config import OLLAMA_URL, OLLAMA_MODEL, OPENAI_MODEL, GEN_BACKEND
from retrievers import get_retriever

load_dotenv(Path(__file__).parent / ".env")

RETRIEVER   = "semantic_e5_combined"
TOP_K_CTX   = 3

SYSTEM_PROMPT = (
    "אתה עוזר הלכתי המבוסס על קיצור שולחן ערוך. "
    "ענה על השאלה על סמך הסעיפים שלהלן. "
    "תן תשובה קצרה וישירה בלבד — מילה או משפט אחד קצר שקובע את הדין "
    "(מותר/אסור/חייב/פטור/מספר/שם), ואחריו בסוגריים הסימן והסעיף. "
    "בלי הקדמות, בלי נימוקים ובלי הסברים מיותרים.\n\n"
    "הסעיפים:\n{context}"
)


def build_context(chunks: list[dict], mode: str = "text") -> str:
    """mode: 'text' (סעיף מקורי) | 'summary' (סיכום מודרני) | 'both'."""
    def body(c: dict) -> str:
        summ = c.get("modern_summary", "")
        if mode == "summary":
            return summ or c["text"]
        if mode == "both":
            return f"{summ} {c['text']}".strip()
        return c["text"]
    return "\n\n".join(
        f"[סימן {c['siman_parent']} סעיף {c['seif']}] {body(c)}" for c in chunks
    )


def ask_ollama(question: str, context: str, model: str = OLLAMA_MODEL) -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT.format(context=context)},
            {"role": "user",   "content": question},
        ],
        "stream": False,
        "options": {"temperature": 0.2, "num_predict": 80},
    }
    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    resp = json.load(urllib.request.urlopen(req, timeout=600))
    return resp["message"]["content"].strip()


def ask_openai(question: str, context: str, model: str = OPENAI_MODEL) -> str:
    """גנרציה דרך GPT. המפתח נטען מ-OPENAI_API_KEY (לא נשמר בקוד)."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "חסר OPENAI_API_KEY. הוסף מפתח משלך ל-.env (ראה .env.example) "
            "או הגדר משתנה סביבה, כדי להשתמש ב-backend של GPT."
        )
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.format(context=context)},
            {"role": "user",   "content": question},
        ],
        temperature=0.2,
        max_tokens=120,
    )
    return resp.choices[0].message.content.strip()


def generate(question: str, context: str, backend: str, model: str | None) -> str:
    """מפנה לבקנד הנכון. backend: 'ollama' | 'openai'."""
    if backend == "openai":
        return ask_openai(question, context, model or OPENAI_MODEL)
    return ask_ollama(question, context, model or OLLAMA_MODEL)


def answer(question: str, top_k_ctx: int = TOP_K_CTX, backend: str = GEN_BACKEND,
           model: str | None = None, ctx_mode: str = "text") -> tuple[str, list[dict]]:
    """מחזיר (תשובה, סעיפים שנשלפו). backend: ollama|openai. ctx_mode: text|summary|both."""
    retriever = get_retriever(RETRIEVER)
    chunks = retriever.retrieve(question, top_k=top_k_ctx)
    ans = generate(question, build_context(chunks, ctx_mode), backend, model)
    return ans, chunks


def main() -> None:
    question  = sys.argv[1] if len(sys.argv) > 1 else input("שאלה: ")
    top_k_ctx = int(sys.argv[2]) if len(sys.argv) > 2 else TOP_K_CTX
    backend   = sys.argv[3] if len(sys.argv) > 3 else GEN_BACKEND

    ans, chunks = answer(question, top_k_ctx, backend=backend)

    lines = [f"שאלה: {question}", "", "תשובה:", ans, "", "מקורות שנשלפו:"]
    for c in chunks:
        lines.append(f"  [{c['ref']}] (score={c['score']:.3f}) {c['text'][:90]}...")
    Path("data/_last_answer.txt").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
