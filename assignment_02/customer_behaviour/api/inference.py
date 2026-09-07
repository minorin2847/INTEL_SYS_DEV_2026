"""Model loading and the core prediction path (Sephora is_recommended model).

Loads the persisted pipeline once (``model/model_pipeline.joblib``), rebuilds the
feature frame with the same stateless ``build_features()`` used in the notebook, turns
P(recommend) into a decision, and — the deployed model is Logistic Regression — returns
an exact per-feature contribution breakdown (linear SHAP around the training mean) plus
the review terms pushing the prediction each way.
"""
from __future__ import annotations

import json
import threading

import numpy as np
import pandas as pd
from scipy.special import expit

from . import config as C
from .features import build_features

_LOCK = threading.Lock()
_PIPELINE = None
_EXPL = None            # {names, means, coef, intercept}  or  None if artifact missing


def get_pipeline():
    global _PIPELINE
    if _PIPELINE is None:
        with _LOCK:
            if _PIPELINE is None:
                import joblib
                _PIPELINE = joblib.load(C.MODEL_PIPELINE_PATH)
    return _PIPELINE


def _explainer():
    global _EXPL
    if _EXPL is not None:
        return _EXPL or None
    _EXPL = {}
    try:
        import joblib
        d = joblib.load(C.MODEL_MEANS_PATH)
        if "coef" in d and "intercept" in d:
            _EXPL = {
                "names": list(d["names"]),
                "means": np.asarray(d["means"], dtype=float).ravel(),
                "coef": np.asarray(d["coef"], dtype=float).ravel(),
                "intercept": float(d["intercept"]),
            }
    except Exception:
        _EXPL = {}
    return _EXPL or None


def _score(frame: pd.DataFrame) -> float:
    pipe = get_pipeline()
    if hasattr(pipe, "predict_proba"):
        return float(pipe.predict_proba(frame)[0, 1])
    return float(expit(pipe.decision_function(frame)[0]))


# --------------------------------------------------------------------------- main
def predict_one(raw_review: dict) -> dict:
    merged = {**C.FIXED_INPUTS, **{k: v for k, v in raw_review.items() if v is not None}}
    feat = build_features(pd.DataFrame([merged]))
    p = _score(feat)
    label = "recommend" if p >= C.DECISION_THRESHOLD else "not recommend"
    confidence = p if label == "recommend" else 1.0 - p
    return {
        "prediction": label,
        "confidence": round(confidence, 4),
        "p_recommend": round(p, 4),
        "threshold": C.DECISION_THRESHOLD,
        "review_terms": _review_terms(feat),
        "signals": _signals(feat),
        "contributions": _contributions(feat, p),
        "model": C.CHOSEN_MODEL,
        "representation": C.REPRESENTATION,
    }


def predict_batch(raw_reviews: list[dict]) -> list[dict]:
    return [predict_one(o) for o in raw_reviews]


# --------------------------------------------------------------- transformed row
def _transform(feat: pd.DataFrame):
    """Return (names, x) — the pipeline's preprocessed feature vector for one review."""
    pipe = get_pipeline()
    pre = pipe.named_steps["prep"]
    Xt = pre.transform(feat)
    x = np.asarray(Xt.todense()).ravel() if hasattr(Xt, "todense") else np.asarray(Xt).ravel()
    try:
        names = list(pre.get_feature_names_out())
    except Exception:
        names = [f"f{i}" for i in range(len(x))]
    return names, x


# ------------------------------------------------------------------ review terms
def _review_terms(feat: pd.DataFrame, k: int = 8) -> dict | None:
    ex = _explainer()
    if ex is None:
        return None
    names, x = _transform(feat)
    if len(names) != len(ex["names"]) or len(x) != len(ex["coef"]):
        return None
    coef = ex["coef"]
    toward, against = [], []
    for j, nm in enumerate(names):
        if not nm.startswith("txt__") or x[j] <= 0:
            continue
        eff = float(coef[j] * x[j])
        term = nm.split("__", 1)[1]
        (toward if eff > 0 else against).append((term, round(eff, 4)))
    toward.sort(key=lambda t: -t[1])
    against.sort(key=lambda t: t[1])
    if not toward and not against:
        return None
    return {
        "toward": [{"term": t, "effect": e} for t, e in toward[:k]],
        "against": [{"term": t, "effect": e} for t, e in against[:k]],
    }


# ------------------------------------------------------------------ contributions
_TAB_PRETTY = {
    "price_usd": "Price", "loves_count": "Product loves", "reviews": "Product review count",
    "total_feedback_count": "Feedback votes on this review",
    "total_neg_feedback_count": "Not-helpful votes",
    "n_ingredients": "Ingredient-list length", "n_highlights": "Product highlights",
    "review_age_days": "Review age", "pos_feedback_ratio": "Share of helpful votes",
    "price_missing": "Price missing", "has_title": "Has a review title",
    "limited_edition": "Limited edition", "new": "New product",
    "online_only": "Online only", "sephora_exclusive": "Sephora exclusive",
}
_CAT_PRETTY = {
    "skin_type_": "Skin type: {}", "skin_tone_": "Skin tone: {}",
    "eye_color_": "Eye colour: {}", "hair_color_": "Hair colour: {}",
    "secondary_category_": "Category: {}", "brand_name_": "Brand: {}",
}


def _pretty(name: str, x_val: float) -> str:
    if name.startswith("txt__"):
        return 'review term: ' + name.split('__', 1)[1]
    rest = name.split("__")[-1]
    for pre, tpl in _CAT_PRETTY.items():
        if rest.startswith(pre):
            v = rest[len(pre):].replace("infrequent_sklearn", "other").replace("_", " ").title()
            return tpl.format(v)
    label = _TAB_PRETTY.get(rest, rest.replace("_", " ").capitalize())
    if rest in ("price_missing", "has_title", "limited_edition", "new", "online_only", "sephora_exclusive"):
        return label
    return f"{label}: {'above average' if x_val >= 0 else 'below average'}"


def _contributions(feat: pd.DataFrame, p: float, top_k: int = 12) -> dict | None:
    ex = _explainer()
    if ex is None:
        return None
    names, x = _transform(feat)
    means, coef, b0 = ex["means"], ex["coef"], ex["intercept"]
    if not (len(x) == len(means) == len(coef) == len(names)):
        return None

    phi = coef * (x - means)                       # per-feature log-odds contribution
    base_p = float(expit(b0 + float(coef @ means)))
    has_text = bool(str(feat.iloc[0].get(C.TEXT_COLUMN, "") or "").strip())

    items, other = [], 0.0
    for j in np.argsort(-np.abs(phi)):
        e = float(phi[j])
        is_txt = names[j].startswith("txt__")
        if abs(e) < 1e-4 or (is_txt and (not has_text or x[j] <= 0)):
            other += e
            continue
        if len(items) < top_k:
            items.append({
                "label": _pretty(names[j], float(x[j])),
                "kind": "text" if is_txt else "tabular",
                "effect": round(e, 4),
            })
        else:
            other += e

    return {
        "base_p": round(base_p, 4),
        "final_p": round(p, 4),
        "dataset_base_rate": C.DATASET_BASE_RATE,
        "items": items,
        "other_effect": round(other, 4),
        "note": "bars are log-odds contributions; reference (base_p) = the model's neutral "
                "point for an average review, class-balanced so not the 85% dataset rate",
    }


# ------------------------------------------------------------------------ signals
def _signals(feat: pd.DataFrame) -> dict:
    row = feat.iloc[0]

    def num(c):
        v = row.get(c)
        return None if v is None or (isinstance(v, float) and np.isnan(v)) else round(float(v), 1)

    txt = str(row.get(C.TEXT_COLUMN, "") or "")
    price = num("price_usd")
    tier = None
    if price is not None:
        tier = "budget" if price < 25 else "mid" if price < 55 else "premium"
    def clean(c):
        v = row.get(c)
        return None if v in (None, "__na__") else str(v).title()

    return {
        "skin_type": clean("skin_type"),
        "skin_tone": clean("skin_tone"),
        "category": clean("secondary_category"),
        "brand": None if row.get("brand_name") in (None, "__na__") else str(row.get("brand_name")).title(),
        "price_usd": price,
        "price_tier": tier,
        "product_loves": num("loves_count"),
        "review_tokens": len(txt.split()),
        "has_title": bool(row.get("has_title", 0)),
    }


def model_info() -> dict:
    pipe = get_pipeline()
    schema = json.loads(C.INPUT_SCHEMA_PATH.read_text(encoding="utf-8"))
    ex = _explainer()
    return {
        "chosen_model": C.CHOSEN_MODEL,
        "representation": C.REPRESENTATION,
        "target": schema["target"],
        "framing": schema.get("framing", ""),
        "decision_threshold": C.DECISION_THRESHOLD,
        "dataset_base_rate": C.DATASET_BASE_RATE,
        "random_seed": C.RANDOM_SEED,
        "sklearn_version": C.SKLEARN_VERSION,
        "pipeline_steps": [s[0] for s in pipe.steps],
        "explainable": ex is not None,
        "n_features": len(ex["names"]) if ex else None,
        "raw_input_fields": C.RAW_INPUT_FIELDS,
        "tabular_feature_order": C.TABULAR_FEATURE_ORDER,
    }
