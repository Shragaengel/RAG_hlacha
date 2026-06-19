"""מאחד את 250 השאלות הקיימות + כל questions_new_part_*.csv → סט מלא מאומת."""
import csv, glob, json, collections
from pathlib import Path
import pandas as pd
from config import SEIFS_FILE, DATA_DIR, QUESTIONS_FILE

seifs = json.load(open(SEIFS_FILE, encoding="utf-8"))
valid_refs = {s["ref"] for s in seifs}
all_simanim = {s["siman"] for s in seifs}

rows, seen, problems = [], set(), []

def add(r, src_name):
    r = {k.strip(): (str(v) if v is not None else "").strip() for k, v in r.items()}
    ref = r.get("מקור", "")
    if ref not in valid_refs:
        problems.append(f"{src_name}: מקור לא קיים — '{ref}'"); return
    if ref in seen:
        return  # כפילות ref — שומרים את הראשון
    seen.add(ref)
    rows.append({"שאלה": r["שאלה"], "תשובה": r["תשובה"], "מקור": ref,
                 "טקסט_מקור": r.get("טקסט_מקור", "")})

# 1. הקיימות
for r in csv.DictReader(open(DATA_DIR / "questions.csv", encoding="utf-8-sig")):
    add(r, "questions.csv")
n_existing = len(rows)

# 2. החדשות
for pf in sorted(glob.glob(str(DATA_DIR / "questions_new_part_*.csv"))):
    for r in csv.DictReader(open(pf, encoding="utf-8-sig")):
        add(r, Path(pf).name)

covered = {int(r["מקור"].split(":")[0]) for r in rows}
missing_sim = sorted(all_simanim - covered)

print(f"קיימות: {n_existing}  |  חדשות: {len(rows)-n_existing}  |  סהכ: {len(rows)}")
print(f"סימנים מכוסים: {len(covered)} / 221")
print(f"סימנים חסרים: {missing_sim if missing_sim else 'אין'}")
print(f"בעיות: {len(problems)}")
for p in problems[:10]:
    print("  -", p)

if not missing_sim and not problems:
    df = pd.DataFrame(rows, columns=["שאלה", "תשובה", "מקור", "טקסט_מקור"])
    df.insert(0, "id", range(1, len(df) + 1))
    df.to_csv(DATA_DIR / "questions.csv", encoding="utf-8-sig", index=False)
    df.to_excel(QUESTIONS_FILE, index=False)
    print(f"\nנשמר: questions.csv + questions.xlsx  ({len(df)} שאלות, כל 221 הסימנים)")
else:
    print("\n[לא נשמר — יש בעיות]")
