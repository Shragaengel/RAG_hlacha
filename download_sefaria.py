"""
download_sefaria.py — מוריד את קיצור שולחן ערוך המלא מ-Sefaria
==============================================================
מקור:  https://www.sefaria.org/Kitzur_Shulchan_Arukh  (גרסת Torat Emet, מנוקד)
פלט:   data/kitzur_shulchan_aruch_full.csv

פורמט זהה לקובץ הקיים:
    Kitzur Shulchan Arukh {siman}:{seif},"text"

הטקסט נשמר גולמי (כולל ניקוד) — הניקוי נעשה ב-step_01.
"""

import csv
import json
import time
import urllib.request
from pathlib import Path

from config import DATA_DIR

BASE   = "https://www.sefaria.org/api/v3/texts/Kitzur_Shulchan_Arukh%20{siman}?version=source"
SHAPE  = "https://www.sefaria.org/api/shape/Kitzur_Shulchan_Arukh"
OUT    = DATA_DIR / "kitzur_shulchan_aruch_full.csv"
HEADERS = {"User-Agent": "Mozilla/5.0 (research; halacha RAG)"}


def fetch_json(url: str, retries: int = 3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            return json.load(urllib.request.urlopen(req, timeout=40))
        except Exception as e:
            if attempt == retries - 1:
                raise
            time.sleep(2 * (attempt + 1))


def get_seifim(siman: int) -> list[str]:
    d = fetch_json(BASE.format(siman=siman))
    versions = d.get("versions") or [{}]
    text = versions[0].get("text") or d.get("text") or []
    return [str(t) for t in text]


def main() -> None:
    shape = fetch_json(SHAPE)[0]
    n_simanim = shape["length"]
    print(f"קיצור שו\"ע — {n_simanim} סימנים. מוריד...")

    rows, total_seifim = [], 0
    for siman in range(1, n_simanim + 1):
        seifim = get_seifim(siman)
        for j, txt in enumerate(seifim, start=1):
            if txt.strip():
                rows.append((f"Kitzur Shulchan Arukh {siman}:{j}", txt))
                total_seifim += 1
        if siman % 20 == 0 or siman == n_simanim:
            print(f"  סימן {siman}/{n_simanim}  (סהכ {total_seifim} סעיפים)")
        time.sleep(0.35)

    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Index Title", "Kitzur Shulchan Arukh"])
        w.writerow(["Version Title", "Torat Emet (Sefaria)"])
        w.writerow(["Language", "he"])
        w.writerow(["Version Source", "https://www.sefaria.org/Kitzur_Shulchan_Arukh"])
        w.writerow(["Version Notes", ""])
        for ref, txt in rows:
            w.writerow([ref, txt])

    print(f"\nנשמר: {OUT.name}  ({total_seifim} סעיפים, {n_simanim} סימנים)")


if __name__ == "__main__":
    main()
