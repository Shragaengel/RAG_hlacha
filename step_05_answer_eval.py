"""
Step 5 — הערכת איכות התשובה (RAG מלא)
======================================
לכל שאלה: שליפה (combined) → גנרציה (DictaLM/Ollama) → ניקוד מול תשובת האמת.

מדדי תשובה (התשובה הצפויה קצרה 1-3 מילים, התשובה שנוצרת ארוכה):
  • Contains  — האם תשובת האמת מופיעה בתוך התשובה שנוצרה (המדד הראשי)
  • F1        — חפיפת טוקנים בין האמת לתשובה
  • Exact     — התאמה מלאה לאחר נרמול
  • Ctx_hit   — האם הסעיף הנכון (ref) נכלל בהקשר שנשלח למודל

שמירה מצטברת + חידוש: כל שורה נכתבת מיד; הרצה חוזרת מדלגת על מה שכבר נעשה.

שימוש:
    python step_05_answer_eval.py                 # כל השאלות (resume)
    python step_05_answer_eval.py --test 10       # 10 ראשונות
    python step_05_answer_eval.py --report        # רק לסכם מה שכבר קיים
"""

import argparse
import csv
import re
import sys
import time
from pathlib import Path

import pandas as pd

from config import QUESTIONS_FILE, GEN_BACKEND
from step_04_rag_answer import answer as rag_answer, TOP_K_CTX

OUT_CSV = Path("experiments/answer_eval.csv")
FIELDS = ["id", "שאלה", "תשובת_אמת", "מקור", "תשובת_RAG",
          "Contains", "F1", "Exact", "Ctx_hit", "ctx_refs"]


def normalize(t: str) -> str:
    t = str(t)
    t = re.sub(r"[֑-ׇ]", "", t)             # ניקוד
    t = re.sub(r"[.,;:!?\"'״׳()\[\]]", " ", t)  # פיסוק
    return re.sub(r"\s+", " ", t).strip()


def score(gold: str, pred: str) -> dict:
    g, p = normalize(gold), normalize(pred)
    gt, pt = g.split(), p.split()
    contains = 1 if g and g in p else 0
    exact = 1 if g == p else 0
    if gt and pt:
        overlap = len(set(gt) & set(pt))
        prec = overlap / len(pt); rec = overlap / len(gt)
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    else:
        f1 = 0.0
    return {"Contains": contains, "F1": round(f1, 4), "Exact": exact}


def load_done(path: Path) -> set:
    if not path.exists():
        return set()
    try:
        df = pd.read_csv(path, encoding="utf-8-sig")
        return set(df["id"].astype(str))
    except Exception:
        return set()


def run(df: pd.DataFrame, top_k_ctx: int, model, out_csv: Path,
        ctx_mode: str = "text", backend: str = GEN_BACKEND) -> None:
    out_csv.parent.mkdir(exist_ok=True)
    done = load_done(out_csv)
    new_file = not out_csv.exists()
    f = open(out_csv, "a", encoding="utf-8-sig", newline="")
    w = csv.DictWriter(f, fieldnames=FIELDS)
    if new_file:
        w.writeheader(); f.flush()

    todo = df[~df["id"].astype(str).isin(done)]
    print(f"לעשות: {len(todo)} (כבר נעשו: {len(done)})")
    start = time.time()

    for n, (_, row) in enumerate(todo.iterrows(), 1):
        q = str(row["שאלה"]); gold = str(row["תשובה"]); src = str(row["מקור"])
        try:
            ans, chunks = rag_answer(q, top_k_ctx, backend=backend, model=model, ctx_mode=ctx_mode)
        except Exception as e:
            print(f"[{row['id']}] שגיאה: {e}"); continue
        refs = [c["ref"] for c in chunks]
        sc = score(gold, ans)
        ctx_hit = 1 if src in refs else 0
        w.writerow({"id": row["id"], "שאלה": q, "תשובת_אמת": gold, "מקור": src,
                    "תשובת_RAG": ans.replace("\n", " "), **sc,
                    "Ctx_hit": ctx_hit, "ctx_refs": " ".join(refs)})
        f.flush()
        el = time.time() - start; rate = el / n
        print(f"[{n}/{len(todo)}] id={row['id']} C={sc['Contains']} F1={sc['F1']:.2f} "
              f"ctx={ctx_hit} | {rate:.1f}s/q | נותר ~{rate*(len(todo)-n)/60:.0f} דק'")
    f.close()


def report(out_csv: Path = OUT_CSV) -> None:
    if not out_csv.exists():
        print("אין תוצאות עדיין."); return
    df = pd.read_csv(out_csv, encoding="utf-8-sig")
    n = len(df)
    print("\n" + "=" * 50)
    print(f"הערכת תשובות — {n} שאלות")
    print("=" * 50)
    print(f"  Contains (תשובת האמת בתוך התשובה): {df['Contains'].mean():.4f}")
    print(f"  F1 (חפיפת טוקנים):                 {df['F1'].mean():.4f}")
    print(f"  Exact:                             {df['Exact'].mean():.4f}")
    print(f"  Ctx_hit (הסעיף הנכון בהקשר):       {df['Ctx_hit'].mean():.4f}")
    print("=" * 50)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", type=int, default=None)
    ap.add_argument("--topk", type=int, default=TOP_K_CTX)
    ap.add_argument("--questions", type=str, default=None, help="קובץ שאלות חלופי (csv/xlsx)")
    ap.add_argument("--backend", choices=["ollama", "openai"], default=GEN_BACKEND,
                    help="מנוע גנרציה: ollama (מקומי) / openai (GPT, דורש מפתח)")
    ap.add_argument("--model", type=str, default=None, help="שם המודל (ברירת מחדל לפי backend)")
    ap.add_argument("--out", type=str, default=str(OUT_CSV), help="נתיב פלט")
    ap.add_argument("--ctx", choices=["text", "summary", "both"], default="text",
                    help="מקור ההקשר למודל: סעיף מקורי / סיכום מודרני / שניהם")
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()

    out_csv = Path(args.out)
    if args.report:
        report(out_csv); return

    qfile = Path(args.questions) if args.questions else QUESTIONS_FILE
    df = (pd.read_csv(qfile, encoding="utf-8-sig") if str(qfile).endswith(".csv")
          else pd.read_excel(qfile))
    if "id" not in df.columns:
        df.insert(0, "id", range(1, len(df) + 1))
    if args.test:
        df = df.head(args.test)
    print(f"backend: {args.backend}  |  מודל: {args.model or '(ברירת מחדל)'}  |  הקשר: {args.ctx}")
    run(df, args.topk, args.model, out_csv, args.ctx, args.backend)
    report(out_csv)


if __name__ == "__main__":
    main()
