"""
dump_top10.py — לכל שאלה, רושם את 10 הסימנים/refs שנשלפו (top-10).
פלט: data/retrieved_top10.csv  (לאקסל) + data/retrieved_top10.txt (קריא).
שימוש: python dump_top10.py [retriever]
"""
import sys
from pathlib import Path

import pandas as pd

from config import QUESTIONS_FILE
from retrievers import get_retriever

retriever_name = sys.argv[1] if len(sys.argv) > 1 else "semantic_e5_combined"
r = get_retriever(retriever_name)
df = pd.read_excel(QUESTIONS_FILE)

rows, lines = [], [f"retriever: {retriever_name}", "=" * 70]
for i, row in df.iterrows():
    q     = str(row["שאלה"])
    gold  = str(row["מקור"]).strip()
    gsim  = int(gold.split(":")[0])
    res   = r.retrieve(q, top_k=10)

    refs    = [c["ref"] for c in res]
    simanim = [c["siman_parent"] for c in res]
    siman_hit = "V" if gsim in simanim else "X"
    ref_hit   = "V" if gold in refs else "X"

    rows.append({
        "id":           row.get("id", i + 1),
        "שאלה":         q,
        "מקור":         gold,
        "סימן_זהב":     gsim,
        "R@10_סימן":    1 if gsim in simanim else 0,
        "R@10_ref":     1 if gold in refs else 0,
        "סימנים_נשלפו": " ".join(str(s) for s in simanim),
        "refs_נשלפו":   " ".join(refs),
    })

    lines.append(f"[{row.get('id', i+1)}] siman:{siman_hit} ref:{ref_hit}  זהב={gold}")
    lines.append(f"    שאלה: {q}")
    lines.append(f"    refs:    {' '.join(refs)}")
    lines.append(f"    simanim: {' '.join(str(s) for s in simanim)}")
    lines.append("")

out_csv = Path("data/retrieved_top10.csv")
pd.DataFrame(rows).to_csv(out_csv, encoding="utf-8-sig", index=False)
Path("data/retrieved_top10.txt").write_text("\n".join(lines), encoding="utf-8")
print(f"written {out_csv} + data/retrieved_top10.txt  ({len(rows)} questions)")
