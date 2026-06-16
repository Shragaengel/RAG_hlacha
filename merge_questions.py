"""מאחד את 4 קבצי השאלות לקובץ אחד מאומת — data/questions.csv + questions.xlsx."""
import csv, json, collections
from pathlib import Path
import pandas as pd
from config import SEIFS_FILE, DATA_DIR, QUESTIONS_FILE

seifs = json.load(open(SEIFS_FILE, encoding="utf-8"))
valid_refs = {s["ref"] for s in seifs}

parts = [DATA_DIR / f"questions_part_{i}.csv" for i in range(1, 5)]
rows, problems = [], []
seen_refs = collections.Counter()

for p in parts:
    with open(p, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            r = {k.strip(): (v or "").strip() for k, v in r.items()}
            src = r.get("מקור", "")
            if not all(r.get(c) for c in ("שאלה", "תשובה", "מקור", "טקסט_מקור")):
                problems.append(f"{p.name}: שדה ריק — {src}")
            if src not in valid_refs:
                problems.append(f"{p.name}: מקור לא קיים ב-seifs.json — '{src}'")
            seen_refs[src] += 1
            rows.append(r)

dups = {ref: n for ref, n in seen_refs.items() if n > 1}

print(f"סהכ שאלות: {len(rows)}")
simanim = sorted({int(r['מקור'].split(':')[0]) for r in rows})
print(f"סימנים מכוסים: {len(simanim)} / 39  -> {simanim}")
print(f"refs ייחודיים: {len(seen_refs)}")
print(f"כפילויות בין חלקים: {len(dups)}  {dups if dups else ''}")
print(f"בעיות תקינות: {len(problems)}")
for x in problems[:20]:
    print("   -", x)

if not problems and not dups:
    df = pd.DataFrame(rows, columns=["שאלה", "תשובה", "מקור", "טקסט_מקור"])
    df.insert(0, "id", range(1, len(df) + 1))
    out_csv = DATA_DIR / "questions.csv"
    df.to_csv(out_csv, encoding="utf-8-sig", index=False)
    df.to_excel(QUESTIONS_FILE, index=False)
    print(f"\nנשמר: {out_csv.name} + {QUESTIONS_FILE.name}  ({len(df)} שאלות)")
else:
    print("\n[לא נשמר — יש בעיות לתיקון]")
