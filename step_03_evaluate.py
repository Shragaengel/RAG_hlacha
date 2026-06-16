"""
Step 3 — Retrieval Evaluation
=============================
מריץ את שאלות ההערכה דרך retriever ומחשב מדדי שליפה:

  • Recall@K  (K=1,3,5,10) — האם נמצא הסעיף הנכון בין K הראשונים
  • MRR                     — Mean Reciprocal Rank (ממוצע 1/rank)

שתי רמות רלוונטיות:
  • סימן       — נשלף סעיף מאותו סימן (siman_parent תואם)
  • סעיף (ref) — נשלף הסעיף המדויק (siman:seif תואם)

עמודת "מקור" בקובץ השאלות בפורמט "siman:seif" (למשל "11:1").

שימוש:
    python step_03_evaluate.py --retriever semantic_e5_large
    python step_03_evaluate.py --retriever semantic_e5_large --test 30
"""

import argparse
from pathlib import Path

import pandas as pd

from config import QUESTIONS_FILE
from retrievers import get_retriever, list_retrievers


def parse_ref(source: str) -> tuple[int, int]:
    """'11:1' → (11, 1)."""
    siman, seif = str(source).strip().split(":")
    return int(siman), int(seif)


def recall_at_k(chunks: list[dict], pred, k: int) -> float:
    return 1.0 if any(pred(c) for c in chunks[:k]) else 0.0


def reciprocal_rank(chunks: list[dict], pred) -> float:
    for rank, c in enumerate(chunks, start=1):
        if pred(c):
            return 1.0 / rank
    return 0.0


def run_evaluation(retriever, df: pd.DataFrame, top_k: int = 10) -> pd.DataFrame:
    rows = []
    for i, row in df.iterrows():
        question = str(row["שאלה"])
        siman, seif = parse_ref(row["מקור"])
        chunks = retriever.retrieve(question, top_k=top_k)

        siman_hit = lambda c: c["siman_parent"] == siman
        ref_hit   = lambda c: c["siman_parent"] == siman and c.get("seif") == seif

        rec = {
            "id":     row.get("id", i + 1),
            "שאלה":   question,
            "מקור":   row["מקור"],
            "top_ref": chunks[0]["ref"] if chunks else "",
            "top_score": chunks[0]["score"] if chunks else 0.0,
        }
        for k in (1, 3, 5, 10):
            rec[f"R@{k}"]      = recall_at_k(chunks, siman_hit, k)
            rec[f"R@{k}_ref"]  = recall_at_k(chunks, ref_hit, k)
        rec["MRR"]     = reciprocal_rank(chunks, siman_hit)
        rec["MRR_ref"] = reciprocal_rank(chunks, ref_hit)
        rows.append(rec)

        mark = "+" if rec["R@3"] else " "
        rmark = "+" if rec["R@3_ref"] else " "
        print(f"[{i+1}/{len(df)}] siman[{mark}] ref[{rmark}] "
              f"top={rec['top_ref']}({rec['top_score']:.3f}) gold={row['מקור']}")

    return pd.DataFrame(rows)


def print_summary(rdf: pd.DataFrame) -> None:
    n = len(rdf)
    print("\n" + "=" * 56)
    print(f"תוצאות שליפה — {n} שאלות")
    print("=" * 56)
    print(f"\n[רמת סימן]")
    for k in (1, 3, 5, 10):
        print(f"  Recall@{k:<2} {rdf[f'R@{k}'].mean():.4f}")
    print(f"  MRR        {rdf['MRR'].mean():.4f}")
    print(f"\n[רמת סעיף מדויק (ref)]")
    for k in (1, 3, 5, 10):
        print(f"  Recall@{k:<2} {rdf[f'R@{k}_ref'].mean():.4f}")
    print(f"  MRR        {rdf['MRR_ref'].mean():.4f}")
    print("=" * 56)


def main() -> None:
    parser = argparse.ArgumentParser(description="הערכת שליפה — Recall@K, MRR")
    parser.add_argument("--retriever", default="semantic_e5_large",
                        help=f"זמינים: {list_retrievers()}")
    parser.add_argument("--test", type=int, default=None, help="הרץ רק N שאלות ראשונות")
    parser.add_argument("--topk", type=int, default=10)
    parser.add_argument("--out", type=str, default=None, help="נתיב לשמירת results.csv")
    args = parser.parse_args()

    print(f"טוען retriever: {args.retriever}...")
    retriever = get_retriever(args.retriever)

    df = pd.read_excel(QUESTIONS_FILE)
    if args.test:
        df = df.head(args.test)
    print(f"מעריך {len(df)} שאלות...\n")

    rdf = run_evaluation(retriever, df, top_k=args.topk)

    out = Path(args.out) if args.out else Path(f"results_{args.retriever}.csv")
    rdf.to_csv(out, encoding="utf-8-sig", index=False)
    print(f"\nנשמר: {out}")
    print_summary(rdf)


if __name__ == "__main__":
    main()
