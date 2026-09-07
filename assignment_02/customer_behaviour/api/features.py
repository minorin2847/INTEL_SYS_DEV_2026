"""Stateless raw-review -> feature-frame step (port of notebook §12 ``build_features``).

No fitted parameters — every column is a deterministic function of one raw review, so
training and serving share one code path. The fitted imputers / scaler / one-hot /
TF-IDF all live inside ``model_pipeline.joblib`` and run *after* this step.

Serving difference: a request may omit optional fields. Any absent source column is
treated as missing (NaN) so the pipeline's median imputers fill it exactly as fitted,
rather than substituting a wrong constant.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config as C

_REF = pd.Timestamp(C._SNAPSHOT)

# raw columns build_features() may read
_RAW_COLS = [
    "submission_time", "price_usd", "loves_count", "reviews", "review_title", "review_text",
    "ingredients", "highlights", "limited_edition", "new", "online_only", "sephora_exclusive",
    "total_feedback_count", "total_pos_feedback_count", "total_neg_feedback_count",
    "skin_type", "skin_tone", "eye_color", "hair_color", "secondary_category", "brand_name",
]


def build_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Raw review-level frame -> exactly ``TABULAR_FEATURE_ORDER + [TEXT_COLUMN]``."""
    d = frame.copy()

    def col(name, default=np.nan):
        return d[name] if name in d.columns else pd.Series(default, index=d.index)

    d["ts"] = pd.to_datetime(col("submission_time"), errors="coerce")
    d["review_age_days"] = (_REF - d["ts"]).dt.total_seconds() / 86400.0

    for c in ["price_usd", "loves_count", "reviews"]:
        d[c] = pd.to_numeric(col(c), errors="coerce")
    d["price_missing"] = d["price_usd"].isna().astype(int)

    title = col("review_title", "").fillna("").astype(str)
    text = col("review_text", "").fillna("").astype(str)
    d["has_title"] = title.str.strip().ne("").astype(int)
    d["review_all"] = (title + " . " + text).str.strip()

    # ingredients / highlights: NaN when the source is absent -> pipeline imputes the median
    ing = col("ingredients")
    hig = col("highlights")
    d["n_ingredients"] = np.where(ing.notna(), ing.fillna("").astype(str).str.count(",") + 1, np.nan)
    d["n_highlights"] = np.where(hig.notna(), hig.fillna("").astype(str).str.count(","), np.nan)

    for c in ["total_feedback_count", "total_pos_feedback_count", "total_neg_feedback_count"]:
        d[c] = pd.to_numeric(col(c, 0), errors="coerce").fillna(0)
    d["pos_feedback_ratio"] = (d["total_pos_feedback_count"]
                               / d["total_feedback_count"].replace(0, np.nan)).fillna(0.0)

    for c in ["limited_edition", "new", "online_only", "sephora_exclusive"]:
        d[c] = pd.to_numeric(col(c, 0), errors="coerce").fillna(0).astype(int)

    for c in ["skin_type", "skin_tone", "eye_color", "hair_color",
              "secondary_category", "brand_name"]:
        s = col(c)
        d[c] = s.where(s.notna(), "__na__").astype(str).str.strip().str.lower()
    d.loc[d["eye_color"] == "grey", "eye_color"] = "gray"

    return d[C.TABULAR_FEATURE_ORDER + [C.TEXT_COLUMN]]
