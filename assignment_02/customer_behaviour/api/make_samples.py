"""Generate api/samples.json — a serving convenience, not a graded artifact.

Joins reviews_500-750.csv to product_info.csv the same way notebook §3 does, then writes:

  {
    "defaults": { ...one review of typical (median / modal) values... },
    "examples": [ { ...raw ReviewInput fields..., "_label": "...", "_recommended": 0|1 }, ... ]
  }

The web client uses `defaults` to pre-fill hidden fields and `examples` for the
"Load an example review" picker.

Run from customer_behaviour/ :   python api/make_samples.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

D = Path(__file__).resolve().parent.parent / "data" / "sephora"
OUT = Path(__file__).resolve().parent / "samples.json"
SEED = 42
N_REC, N_NOT = 22, 20            # ~42 examples, deliberately over-sampling "not recommend"

RAW_FIELDS = ["skin_type", "skin_tone", "eye_color", "hair_color", "secondary_category",
              "brand_name", "price_usd", "loves_count", "reviews", "limited_edition", "new",
              "online_only", "sephora_exclusive", "total_feedback_count",
              "total_pos_feedback_count", "total_neg_feedback_count", "submission_time",
              "review_title", "review_text"]


def load() -> pd.DataFrame:
    r = pd.read_csv(D / "reviews_500-750.csv", index_col=0)
    p = pd.read_csv(D / "product_info.csv")
    pc = ["product_id", "loves_count", "reviews", "limited_edition", "new", "online_only",
          "sephora_exclusive", "secondary_category"]
    df = r.merge(p[pc], on="product_id", how="left", suffixes=("", "_product"))
    df = df.dropna(subset=["is_recommended"]).reset_index(drop=True)
    df["is_recommended"] = df.is_recommended.astype(int)
    return df


def _clean(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    if isinstance(v, (np.integer, int)):
        return int(v)
    if isinstance(v, (np.floating, float)):
        return round(float(v), 2)
    return str(v)


def row_to_example(row: pd.Series) -> dict:
    o = {k: _clean(row.get(k)) for k in RAW_FIELDS}
    rec = int(row.is_recommended)
    stars = int(row.rating) if not pd.isna(row.rating) else 0
    o["_recommended"] = rec
    o["_label"] = ("%s  ·  %s  ·  %s"
                   % ("★" * stars + "☆" * (5 - stars),
                      "recommends" if rec else "does NOT recommend",
                      (str(row.secondary_category) or "—")))
    return o


def main() -> None:
    df = load()
    rng = np.random.default_rng(SEED)
    df = df[df.review_text.fillna("").str.len().between(40, 700)]        # readable examples

    pos = df[df.is_recommended == 1].sample(min(N_REC, (df.is_recommended == 1).sum()),
                                            random_state=int(rng.integers(1 << 30)))
    neg = df[df.is_recommended == 0].sample(min(N_NOT, (df.is_recommended == 0).sum()),
                                            random_state=int(rng.integers(1 << 30)))
    examples = [row_to_example(r) for _, r in pd.concat([neg, pos]).iterrows()]
    examples.sort(key=lambda o: (o["_recommended"], o["_label"]))

    defaults = {
        "skin_type": df.skin_type.mode().iat[0],
        "skin_tone": df.skin_tone.dropna().mode().iat[0],
        "eye_color": df.eye_color.dropna().mode().iat[0],
        "hair_color": df.hair_color.dropna().mode().iat[0],
        "secondary_category": df.secondary_category.dropna().mode().iat[0],
        "brand_name": df.brand_name.mode().iat[0],
        "price_usd": round(float(df.price_usd.median()), 2),
        "loves_count": int(df.loves_count.median()),
        "reviews": int(df.reviews.median()),
        "submission_time": "2023-01-15",
        "review_title": "",
        "review_text": "",
    }

    OUT.write_text(json.dumps({"defaults": defaults, "examples": examples},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {OUT}  ·  {len(examples)} examples  "
          f"({sum(e['_recommended'] for e in examples)} recommend / "
          f"{sum(1 - e['_recommended'] for e in examples)} not)")


if __name__ == "__main__":
    main()
