"""
Step 2 — Embeddings (multilingual-e5-large)
============================================
קלט:  data/seifs.json
פלט:  data/seifs_e5_large.npy   (מטריצת embeddings מנורמלת, שורה i ↔ seifs[i])

הערות:
- E5 דורש prefix: "passage: " למסמכים, "query: " לשאילתות (נעשה ב-retriever).
- normalize_embeddings=True → דמיון קוסינוס = מכפלה פנימית (query @ emb.T).
- סדר השורות תואם בדיוק לסדר ב-seifs.json (chunk_id).
"""

import json

import numpy as np
from sentence_transformers import SentenceTransformer

from config import SEIFS_FILE, EMBED_MODEL, EMBEDDINGS_E5_LARGE


def main() -> None:
    with open(SEIFS_FILE, encoding="utf-8") as f:
        seifs = json.load(f)
    texts = [f"passage: {s['text']}" for s in seifs]

    print(f"טוען מודל: {EMBED_MODEL}")
    model = SentenceTransformer(EMBED_MODEL)

    print(f"מקודד {len(texts)} סעיפים...")
    emb = model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        batch_size=16,
        show_progress_bar=True,
    ).astype(np.float32)

    np.save(EMBEDDINGS_E5_LARGE, emb)
    print(f"נשמר: {EMBEDDINGS_E5_LARGE.name}  shape={emb.shape}  dtype={emb.dtype}")
    print("שלב 2 הושלם בהצלחה.")


if __name__ == "__main__":
    main()
