"""
config.py — נתיבים מרכזיים לפרויקט
==================================
ערוך קובץ זה פעם אחת לפי קובץ הדאטה שתבחר.
שאר הקבצים מייבאים מכאן — אין צורך לשנות אותם.

הדאטה: קיצור שולחן ערוך (מחולק לסימנים וסעיפים).
"""
from pathlib import Path

# תיקיית השורש של הפרויקט
HERE = Path(__file__).parent

# תיקיית נתונים (טקסט מקור, שאלות, אינדקסים שנבנים)
DATA_DIR = HERE / "data"

# ─── קובץ טקסט המקור (קיצור שולחן ערוך) ──────────────────────────────────────
# CSV מלא מ-Sefaria (תורת אמת): 221 סימנים, 2765 סעיפים, מנוקד.
# פורמט: "Kitzur Shulchan Arukh {סימן}:{סעיף}",טקסט
TEXT_FILE = DATA_DIR / "kitzur_shulchan_aruch_full.csv"

# יחידות מפורסרות ברמת סעיף (פלט step_01)
SEIFS_FILE = DATA_DIR / "seifs.json"

# סעיפים + סיכום מודרני (text + modern_summary)
SEIFS_WITH_SUMMARY = DATA_DIR / "seifs_with_summary.json"

# ─── קובץ השאלות (להערכה) ────────────────────────────────────────────────────
# Excel/CSV עם עמודות: שאלה, תשובה, מקור (סימן+סעיף).
QUESTIONS_FILE = DATA_DIR / "questions.xlsx"

# ─── Embeddings ───────────────────────────────────────────────────────────────
EMBED_MODEL            = "intfloat/multilingual-e5-large"      # 1024-dim, רב-לשוני
EMBEDDINGS_E5_LARGE    = DATA_DIR / "seifs_e5_large.npy"       # קידוד טקסט מקורי בלבד
EMBEDDINGS_E5_COMBINED = DATA_DIR / "seifs_combined_e5_large.npy"  # קידוד סיכום + טקסט

# ─── גנרציה ───────────────────────────────────────────────────────────────────
# backend ברירת מחדל: "ollama" (מקומי) או "openai" (GPT — דורש מפתח משלך)
GEN_BACKEND  = "ollama"

# Ollama מקומי (DictaLM 2.0, עברי, 7.3B)
OLLAMA_URL   = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "aminadaven/dictalm2.0-instruct:q4_k_m"

# OpenAI / GPT — אופציונלי. המפתח נטען מ-OPENAI_API_KEY (סביבה או .env) ואינו נשמר בקוד.
OPENAI_MODEL = "gpt-4o-mini"

# ─── פלטים ────────────────────────────────────────────────────────────────────
EXPERIMENTS_DIR = HERE / "experiments"
