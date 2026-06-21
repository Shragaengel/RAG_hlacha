"""
query.py — שליפה אינטראקטיבית מהירה לבדיקת שאלה בודדת.
שימוש:  python query.py "השאלה שלי" [retriever] [top_k]
הפלט נכתב ל-data/_last_query.txt (עברית תקינה, ללא mojibake בקונסול).
"""
import sys
from pathlib import Path

from retrievers import get_retriever

query     = sys.argv[1] if len(sys.argv) > 1 else input("שאלה: ")
retriever = sys.argv[2] if len(sys.argv) > 2 else "semantic_e5_combined"
top_k     = int(sys.argv[3]) if len(sys.argv) > 3 else 10

r   = get_retriever(retriever)
res = r.retrieve(query, top_k=top_k)

lines = [f"שאילתה: {query}", f"retriever: {retriever}", "-" * 60]
for c in res:
    lines.append(f"#{c['rank']:<2} ref={c['ref']:<7} score={c['score']:.4f}")
    lines.append(f"     {c['text'][:160]}")
out = Path("data/_last_query.txt")
out.write_text("\n".join(lines), encoding="utf-8")
print(f"written {out}")
