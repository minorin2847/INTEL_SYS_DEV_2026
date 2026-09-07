"""Five most similar training respondents, by random-forest proximity.

Proximity(a, b) = fraction of trees in which a and b fall in the same leaf. The index
(a leaf matrix for a stratified training subsample, plus outcomes and de-identified
profile strings) is built by build_artifacts.py. If it is missing, `available` is
False and the endpoint degrades gracefully.
"""
from __future__ import annotations

import threading
from typing import Optional

import joblib
import numpy as np

from . import config as C
from . import inference as I

_LOCK = threading.Lock()
_INDEX: Optional[dict] = None
_INDEX_LOADED = False


def _index() -> Optional[dict]:
    global _INDEX, _INDEX_LOADED
    if not _INDEX_LOADED:
        with _LOCK:
            if not _INDEX_LOADED:
                _INDEX_LOADED = True
                try:
                    _INDEX = joblib.load(C.NEIGHBOR_INDEX_PATH)
                except Exception:
                    _INDEX = None
    return _INDEX


def available() -> bool:
    return _index() is not None


def similar(feat: dict, k: int = 5) -> dict:
    idx = _index()
    if idx is None:
        return {"available": False,
                "reason": "neighbor index not built — run `python api/build_artifacts.py`"}

    X = I.to_model_frame(feat)
    Xt = I.preprocessor().transform(X)
    q_leaf = I.classifier().apply(Xt)[0]                 # (n_estimators,)

    leaves = idx["leaves"]                               # (n_index, n_estimators)
    prox = (leaves == q_leaf).mean(axis=1)               # (n_index,)
    order = np.argsort(prox)[::-1][:k]

    outcomes = idx["outcomes"]
    profiles = idx["profiles"]
    neighbors = [{
        "profile": str(profiles[i]),
        "outcome": "diabetes / pre-diabetes" if int(outcomes[i]) == 1 else "no diabetes",
        "proximity": round(float(prox[i]), 3),
    } for i in order]

    return {
        "available": True,
        "method": "random-forest proximity (shared-leaf frequency)",
        "k": k,
        "n_with_diabetes": int(sum(int(outcomes[i]) for i in order)),
        "max_proximity": round(float(prox[order[0]]), 3),
        "neighbors": neighbors,
    }
