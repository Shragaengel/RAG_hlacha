"""סריקת איכות דאטה — מזהה בעיות ניקוי ב-seifs.json וכותב דוח."""
import json, re, collections
from pathlib import Path
from config import SEIFS_FILE

seifs = json.load(open(SEIFS_FILE, encoding="utf-8"))
out = []
def p(s=""): out.append(s)

p(f"סהכ סעיפים: {len(seifs)}\n")

# 1. תו replacement (קידוד שבור)
repl = [s for s in seifs if "�" in s["text"]]
p(f"[1] תווי replacement (U+FFFD): {len(repl)} סעיפים")
for s in repl[:5]:
    i = s["text"].index("�")
    p(f"    {s['ref']}: ...{s['text'][max(0,i-25):i+25]}...")

# 2. אותיות לטיניות (תעתיק לעז: גרמנית/יידיש)
lat = [s for s in seifs if re.search(r"[A-Za-z]", s["text"])]
p(f"\n[2] אותיות לטיניות: {len(lat)} סעיפים")
for s in lat[:5]:
    m = re.search(r".{0,15}[A-Za-z]+.{0,15}", s["text"])
    p(f"    {s['ref']}: ...{m.group(0)}...")

# 3. ספרות בתוך הטקסט
dig = [s for s in seifs if re.search(r"\d", s["text"])]
p(f"\n[3] ספרות בטקסט: {len(dig)} סעיפים")
for s in dig[:5]:
    m = re.search(r".{0,15}\d+.{0,15}", s["text"])
    p(f"    {s['ref']}: ...{m.group(0)}...")

# 4. סוגריים מכל סוג
brk = collections.Counter()
for s in seifs:
    for ch in "()[]{}<>":
        brk[ch] += s["text"].count(ch)
p(f"\n[4] סוגריים: " + ", ".join(f"{k}={v}" for k,v in brk.items() if v))
for s in seifs:
    if "[" in s["text"] or "]" in s["text"]:
        m = re.search(r".{0,20}[\[\]].{0,20}", s["text"]);
        if m: p(f"    {s['ref']}: ...{m.group(0)}...")
        break

# 5. תווי גרש/גרשיים (וריאנטים)
geresh = collections.Counter()
for s in seifs:
    for ch in ["'", '"', "׳", "״", "‘", "’", "“", "”"]:
        geresh[ch] += (s["text"]+s["citation"]).count(ch)
names = {"'":"ASCII apostrophe", '"':"ASCII quote", "׳":"HEB geresh ׳",
         "״":"HEB gershayim ״", "‘":"left single ‘", "’":"right single ’",
         "“":"left double “", "”":"right double ”"}
p(f"\n[5] תווי גרש/ציטוט:")
for k,v in geresh.items():
    if v: p(f"    {names[k]}: {v}")

# 6. תגיות HTML
html = [s for s in seifs if re.search(r"<[^>]+>", s["text"])]
p(f"\n[6] תגיות HTML: {len(html)} סעיפים")

# 7. סעיפים קצרים מאוד (אולי שבר/כותרת)
short = [s for s in seifs if len(s["text"].split()) <= 5]
p(f"\n[7] סעיפים קצרים (<=5 מילים): {len(short)}")
for s in short[:8]:
    p(f"    {s['ref']} ({len(s['text'].split())} מ'): {s['text']}")

# 8. ראשי תיבות עם גרשיים (מועמדים להרחבה)
abbr = collections.Counter()
for s in seifs:
    for m in re.findall(r"\S*[״\"]\S*", s["text"]):
        abbr[m] += 1
p(f"\n[8] ראשי-תיבות נפוצים (top 20):")
for w,c in abbr.most_common(20):
    p(f"    {w}: {c}")

Path("data/quality_report.txt").write_text("\n".join(out), encoding="utf-8")
print("report written")
