"""מאחד את 8 קבצי הסיכומים, מאמת כיסוי מלא, ובונה data/seifs_with_summary.json."""
import json, collections
from pathlib import Path
from config import SEIFS_FILE, DATA_DIR

seifs = json.load(open(SEIFS_FILE, encoding="utf-8"))
valid_refs = {s["ref"] for s in seifs}

import glob
ref2sum, counts, problems = {}, collections.Counter(), []
part_files = sorted(glob.glob(str(DATA_DIR / "summaries_part_*.json")))
for pf in part_files:
    i = pf
    part = json.load(open(pf, encoding="utf-8"))
    for o in part:
        ref, summ = o.get("ref", ""), (o.get("modern_summary") or "").strip()
        if ref not in valid_refs:
            problems.append(f"part_{i}: ref לא קיים — '{ref}'")
        if not summ:
            problems.append(f"part_{i}: סיכום ריק — {ref}")
        counts[ref] += 1
        ref2sum[ref] = summ

dups     = {r: n for r, n in counts.items() if n > 1}
missing  = valid_refs - set(ref2sum)

print(f"סהכ סיכומים: {len(ref2sum)} / {len(valid_refs)}")
print(f"חסרים: {len(missing)}  {sorted(missing) if missing else ''}")
print(f"כפילויות: {len(dups)}  {dups if dups else ''}")
print(f"בעיות: {len(problems)}")
for x in problems[:20]:
    print("   -", x)

if not problems and not dups and not missing:
    for s in seifs:
        s["modern_summary"] = ref2sum[s["ref"]]
    out = DATA_DIR / "seifs_with_summary.json"
    json.dump(seifs, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    avg = sum(len(v.split()) for v in ref2sum.values()) / len(ref2sum)
    print(f"\nנשמר: {out.name}  ({len(seifs)} סעיפים, ממוצע {avg:.1f} מילים לסיכום)")
else:
    print("\n[לא נשמר — יש בעיות לתיקון]")
