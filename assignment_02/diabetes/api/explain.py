"""Per-prediction explanation with SHAP.

`shap.TreeExplainer` on the fitted random forest, evaluated on the *preprocessed*
feature vector (the same array the model sees). Returns the signed contribution of
each feature toward the positive class, as plain-language factor bars.
"""
from __future__ import annotations

import threading
from typing import Optional

import numpy as np

from . import config as C
from . import inference as I

_LOCK = threading.Lock()
_EXPLAINER = None


def _get_explainer():
    global _EXPLAINER
    if _EXPLAINER is None:
        with _LOCK:
            if _EXPLAINER is None:
                import shap
                _EXPLAINER = shap.TreeExplainer(I.classifier())
    return _EXPLAINER


def _positive_class_values(sv, expected):
    """Normalise the several shapes shap returns for a binary RF into
    (contribs: 1d array over features, base_value: float)."""
    arr = np.asarray(sv)
    if isinstance(expected, (list, tuple, np.ndarray)) and np.ndim(expected) >= 1:
        base = float(np.asarray(expected).ravel()[-1])
    else:
        base = float(expected)
    if arr.ndim == 3:            # (n_samples, n_features, n_classes)
        return arr[0, :, -1], base
    if arr.ndim == 2:            # (n_samples, n_features)
        return arr[0], base
    if arr.ndim == 1:
        return arr, base
    raise ValueError(f"unexpected shap output shape {arr.shape}")


def explain(feat: dict, top_k: int = 8) -> dict:
    X = I.to_model_frame(feat)
    Xt = I.preprocessor().transform(X)
    names = I.feature_names()

    explainer = _get_explainer()
    try:
        sv = explainer.shap_values(Xt, check_additivity=False)
    except TypeError:
        sv = explainer.shap_values(Xt)
    contribs, base = _positive_class_values(sv, explainer.expected_value)

    items = []
    for name, val in zip(names, contribs):
        items.append({
            "feature": name,
            "label": C.FEATURE_LABELS.get(name, name),
            "value": round(float(val), 4),
            "direction": "increases risk" if val > 0 else "decreases risk",
        })
    items.sort(key=lambda d: abs(d["value"]), reverse=True)
    return {
        "base_value": round(float(base), 4),
        "predicted_probability": round(I.predict_proba(feat), 4),
        "factors": items[:top_k],
        "all_factors": items,
    }
