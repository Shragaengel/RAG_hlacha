"""
build_combined_embeddings.py — embedding על שרשור "סיכום מודרני + טקסט מקורי"
============================================================================
קלט:  data/seifs_with_summary.json
פלט:  data/seifs_combined_e5_large.npy   (שורה i ↔ seifs[i])

encoding_text = "passage: " + modern_summary + " " + text
הרציונל: הסיכום מגשר אוצר מילים (מילים חלופיות/הפוכות), הטקסט שומר על דיוק המקור.
"""

import json

import numpy as np
from sentence_transformers import SentenceTransformer

from config import SEIFS_WITH_SUMMARY, EMBED_MODEL, EMBEDDINGS_E5_COMBINED


def main() -> None:
    with open(SEIFS_WITH_SUMMARY, encoding="utf-8") as f:
        seifs = json.load(f)
    texts = [f"passage: {s['modern_summary']} {s['text']}" for s in seifs]

    print(f"טוען מודל: {EMBED_MODEL}")
    model = SentenceTransformer(EMBED_MODEL)

    print(f"מקודד {len(texts)} סעיפים (סיכום + טקסט)...")
    emb = model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        batch_size=16,
        show_progress_bar=True,
    ).astype(np.float32)

    np.save(EMBEDDINGS_E5_COMBINED, emb)
    print(f"נשמר: {EMBEDDINGS_E5_COMBINED.name}  shape={emb.shape}  dtype={emb.dtype}")
    print("הושלם בהצלחה.")


if __name__ == "__main__":
    main()
