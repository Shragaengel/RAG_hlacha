"""
Step 1 — Data Loading & Parsing
================================
קלט:  data/kitzur_shulchan_aruch.csv  (ייצוא kitzur.net)
פלט:  data/seifs.json                 (יחידה אחת לכל סעיף)

הדאטה כבר מובנה ברמת סעיף — אין צורך ב-chunking או חלוקה לפי גבולות.
כל שורה: "Kitzur Shulchan Arukh {סימן}:{סעיף}",טקסט

מה הקוד עושה:
1. מדלג על 5 שורות ה-metadata בראש הקובץ
2. מפרסר כל שורה ל-(siman, seif, text)
3. מנקה ניקוד ורווחים
4. מפריד ציטוט מקור בסוף הסעיף (אחרי " - ") לשדה נפרד
5. שומר seifs.json
"""

import csv
import json
import re
from pathlib import Path

from config import TEXT_FILE, SEIFS_FILE

REF_PREFIX = "Kitzur Shulchan Arukh"
ROW_RE = re.compile(rf"^{re.escape(REF_PREFIX)}\s+(\d+):(\d+)$")


def remove_niqqud(text: str) -> str:
    """מסיר ניקוד עברי — Unicode U+0591 עד U+05C7."""
    return re.sub(r"[֑-ׇ]", "", text)


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def remove_editorial_brackets(text: str) -> str:
    """מסיר תווי סוגריים מרובעים (הערות עורך כמו ]כזה[), שומר את התוכן."""
    return re.sub(r"[\[\]]", "", text)


def normalize_geresh(text: str) -> str:
    """מנרמל גרש/גרשיים עבריים ל-ASCII לעקביות טוקניזציה: ׳→' , ״→\"."""
    return text.replace("׳", "'").replace("״", '"')


def split_source_citation(text: str) -> tuple[str, str]:
    """
    מפריד ציטוט מקור בסוף הסעיף. בקיצור שו"ע המקור מופיע אחרי " - " האחרון,
    לרוב ראשי תיבות קצרים (לדוגמה: 'רפ"ט', 'יו"ד סי' רפה רפו').

    מחזיר (body, citation). אם אין מקור מזוהה — citation ריק.
    מפריד רק אם הקטע האחרון קצר (<= 40 תווים) כדי לא לחתוך תוכן הלכתי.
    """
    idx = text.rfind(" - ")
    if idx == -1:
        return text, ""
    body, tail = text[:idx].strip(), text[idx + 3:].strip()
    if len(tail) <= 40:
        return body, tail
    return text, ""


def clean_text(text: str) -> str:
    text = remove_niqqud(text)
    text = remove_editorial_brackets(text)
    text = normalize_geresh(text)
    return normalize_whitespace(text)


def load_seifs(csv_path: Path = TEXT_FILE) -> list[dict]:
    """מפרסר את ה-CSV ומחזיר רשימת dict — אחד לכל סעיף."""
    seifs: list[dict] = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 2:
                continue
            m = ROW_RE.match(row[0].strip())
            if not m:
                continue  # שורות metadata בראש הקובץ
            siman, seif = int(m.group(1)), int(m.group(2))
            body, citation = split_source_citation(clean_text(row[1]))
            seifs.append({
                "chunk_id": len(seifs),
                "siman":    siman,
                "seif":     seif,
                "text":     body,
                "citation": citation,
                "ref":      f"{siman}:{seif}",
            })
    return seifs


def save_seifs(seifs: list[dict], path: Path = SEIFS_FILE) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(seifs, f, ensure_ascii=False, indent=2)
    print(f"נשמר: {path}  ({path.stat().st_size / 1024:.1f} KB)")


def main() -> None:
    print(f"טוען: {TEXT_FILE.name}")
    seifs = load_seifs()

    simanim = sorted({s["siman"] for s in seifs})
    word_counts = [len(s["text"].split()) for s in seifs]
    with_citation = sum(1 for s in seifs if s["citation"])

    print(f"  סעיפים:        {len(seifs):,}")
    print(f"  סימנים:        {len(simanim)}  (טווח {simanim[0]}–{simanim[-1]})")
    print(f"  עם ציטוט מקור: {with_citation} ({100*with_citation/len(seifs):.0f}%)")
    print(f"  מילים לסעיף:   min={min(word_counts)}  max={max(word_counts)}  "
          f"ממוצע={sum(word_counts)/len(word_counts):.1f}")

    print("\n--- סעיף ראשון ---")
    s0 = seifs[0]
    print(f"  {s0['ref']}: {s0['text'][:200]}...")
    if s0["citation"]:
        print(f"  [מקור: {s0['citation']}]")

    print()
    save_seifs(seifs)
    print("שלב 1 הושלם בהצלחה.")


if __name__ == "__main__":
    main()
