# RAG_hlacha — מערכת RAG לקיצור שולחן ערוך

מערכת Retrieval-Augmented Generation מעל **קיצור שולחן ערוך** המלא:
שאלה בעברית טבעית → שליפת הסעיף/ים הרלוונטיים → תשובה מבוססת-מקור.

## הדאטה
- **קיצור שולחן ערוך המלא** מ-[Sefaria](https://www.sefaria.org/Kitzur_Shulchan_Arukh) (גרסת תורת אמת).
- **221 סימנים, 2,765 סעיפים** — יחידת השליפה היא סעיף בודד.
- לכל סעיף נוצר גם **סיכום מודרני** (עברית בת-זמננו עם מינוח חלופי/הפוך, למשל "מגולה"→"לא מכוסה") לגישור פערי אוצר מילים בשליפה.

## הצינור (Pipeline)
| שלב | קובץ | תיאור |
|---|---|---|
| הורדה | `download_sefaria.py` | מושך את הספר המלא מ-Sefaria API |
| 1 | `step_01_data_loading.py` | פרסור וניקוי → `data/seifs.json` |
| סיכומים | `merge_summaries.py` | איחוד סיכומים מודרניים → `data/seifs_with_summary.json` |
| 2 | `step_02_embeddings.py` / `build_combined_embeddings.py` | embeddings (e5-large) — טקסט / סיכום+טקסט |
| 3 | `step_03_evaluate.py` | הערכת שליפה — Recall@K, MRR (רמת סימן וסעיף) |
| 4 | `step_04_rag_answer.py` | RAG מלא: שליפה → גנרציה → תשובה |
| 5 | `step_05_answer_eval.py` | הערכת איכות התשובה |

## שליפה (Retrieval)
- מודל: `intfloat/multilingual-e5-large`, דמיון קוסינוס מעל NumPy `.npy`.
- ה-retriever המוביל: **`semantic_e5_combined`** — מקודד `סיכום מודרני + טקסט`.

**תוצאות (886 שאלות הערכה, כל 221 הסימנים):**

| מדד | טקסט בלבד | סיכום+טקסט (combined) |
|---|---|---|
| Recall@1 (סימן) | 0.84 | **0.90** |
| Recall@10 (סימן) | 0.98 | **0.99** |
| Recall@1 (סעיף מדויק) | 0.73 | **0.82** |
| MRR (סעיף) | 0.80 | **0.88** |

הסיכום המודרני שיפר את הדיוק ברמת הסעיף ב-~9 נקודות.

## גנרציה (Generation)
שני backends, נבחרים ב-`--backend`:
- **`ollama`** (ברירת מחדל) — DictaLM 2.0 מקומי, לגמרי אופליין.
- **`openai`** — GPT, **הבא-מפתח-משלך**: נטען מ-`OPENAI_API_KEY` (`.env`), לא נשמר בקוד.

> הערה: על CPU ללא GPU, מודל מקומי 7B איטי (~40 שנ'/תשובה) ולא תמיד אמין בפסיקה. השליפה היא הנכס החזק של המערכת; פסיקה אמינה דורשת מודל חזק.

## התקנה והרצה
```bash
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt

# בניית הדאטה (פעם אחת)
python download_sefaria.py
python step_01_data_loading.py
python step_02_embeddings.py
python build_combined_embeddings.py

# שאלה בודדת
python step_04_rag_answer.py "האם מותר לטלטל מוקצה בשבת?"

# דרך GPT (אחרי יצירת .env עם מפתח — ראה .env.example)
python step_04_rag_answer.py "..." 3 openai

# הערכה
python step_03_evaluate.py --retriever semantic_e5_combined
```

## מבנה
```
config.py              הגדרות (מודלים, נתיבים, backend)
step_01..05 / build_*  הצינור
query.py               שליפה מהירה אינטראקטיבית
gen_presentation.py    מצגת HTML של תוצאות ההערכה
retrievers/            semantic_e5_large, semantic_e5_combined
data/                  ספר מלא, seifs, סיכומים, שאלות, embeddings (.npy לא ב-git)
experiments/           תוצאות הערכה
```

הקבצים הגדולים (`*.npy`), `.venv/`, ו-`.env` מסוננים מ-git.
