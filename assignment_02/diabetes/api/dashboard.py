"""Operator dashboard support: threshold trade-off preview and threshold config.

`model/holdout_scores.joblib` is an array of shape (N, 3): columns
[y_true, probability, split] where split is 0 for validation, 1 for test. The
dashboard recomputes precision / recall / flag rate / confusion at any candidate
`high_cut` on the *validation* rows, without re-running the model.
"""
from __future__ import annotations

import threading
from typing import Optional

import joblib
import numpy as np

from . import config as C
from . import inference as I

_LOCK = threading.Lock()
_SCORES = None
_SCORES_LOADED = False


def _scores() -> Optional[np.ndarray]:
    global _SCORES, _SCORES_LOADED
    if not _SCORES_LOADED:
        with _LOCK:
            if not _SCORES_LOADED:
                _SCORES_LOADED = True
                try:
                    _SCORES = np.asarray(joblib.load(C.HOLDOUT_SCORES_PATH), dtype=float)
                except Exception:
                    _SCORES = None
    return _SCORES


def available() -> bool:
    return _scores() is not None


def _split(which: str):
    s = _scores()
    if s is None:
        return None, None
    if s.shape[1] >= 3:
        mask = s[:, 2] == (0 if which == "val" else 1)
        y, p = s[mask, 0], s[mask, 1]
    else:
        y, p = s[:, 0], s[:, 1]
    return y.astype(int), p


def _point(y, p, cut):
    pred = (p >= cut).astype(int)
    tp = int(((pred == 1) & (y == 1)).sum())
    fp = int(((pred == 1) & (y == 0)).sum())
    fn = int(((pred == 0) & (y == 1)).sum())
    tn = int(((pred == 0) & (y == 0)).sum())
    n = len(y)
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    spec = tn / (tn + fp) if tn + fp else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    return {
        "high_cut": round(float(cut), 3),
        "precision": round(prec, 4), "recall": round(rec, 4),
        "specificity": round(spec, 4), "f1": round(f1, 4),
        "flag_rate": round((tp + fp) / n, 4),
        "confusion": {"tn": tn, "fp": fp, "fn": fn, "tp": tp},
        "per_1000": {"flagged": round((tp + fp) / n * 1000),
                     "caught": round(tp / n * 1000),
                     "missed": round(fn / n * 1000),
                     "false_alarms": round(fp / n * 1000)},
    }


def threshold_curve(which: str = "val", grid: int = 49) -> dict:
    y, p = _split(which)
    if y is None:
        return {"available": False,
                "reason": "holdout scores not built — run `python api/build_artifacts.py`"}
    cuts = np.linspace(0.02, 0.98, grid)
    curve = [_point(y, p, c) for c in cuts]
    thr = I.load_thresholds()
    return {
        "available": True, "split": which, "n": int(len(y)),
        "prevalence": round(float(y.mean()), 4),
        "current": {**thr, **_point(y, p, thr["high_cut"])},
        "curve": curve,
    }


def recommend(objective: str = "recall", target: float = 0.90, which: str = "val") -> dict:
    y, p = _split(which)
    if y is None:
        return {"available": False}
    cuts = np.linspace(0.02, 0.98, 97)
    pts = [_point(y, p, c) for c in cuts]
    if objective == "recall":
        cand = [pt for pt in pts if pt["recall"] >= target]
        pick = min(cand, key=lambda d: d["flag_rate"]) if cand else max(pts, key=lambda d: d["recall"])
    elif objective == "flag_rate":
        pick = min(pts, key=lambda d: abs(d["flag_rate"] - target))
    elif objective == "f1":
        pick = max(pts, key=lambda d: d["f1"])
    else:  # youden
        pick = max(pts, key=lambda d: d["recall"] + d["specificity"] - 1)
    return {"available": True, "objective": objective, "target": target, "point": pick}


def get_config() -> dict:
    import json
    thr = I.load_thresholds()
    meta = {}
    try:
        meta = json.loads(C.THRESHOLDS_PATH.read_text())
    except Exception:
        pass
    return {
        "moderate_cut": thr["moderate_cut"], "high_cut": thr["high_cut"],
        "set_by": meta.get("set_by", "default"), "set_at": meta.get("set_at"),
        "holdout_available": available(),
    }
