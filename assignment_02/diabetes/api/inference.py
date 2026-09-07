"""Model loading and the core prediction path.

Loads the persisted pipeline once (`model/model_pipeline.joblib`), rebuilds the
feature frame with the same `engineer()` logic used in the notebook, and turns a
probability into a Low / Moderate / High band using operator-editable thresholds.
"""
from __future__ import annotations

import json
import threading
from typing import Optional

import joblib
import numpy as np
import pandas as pd

from . import config as C

_LOCK = threading.Lock()
_PIPELINE = None
_FEATURE_NAMES: Optional[list[str]] = None


# --------------------------------------------------------------------------- load
def get_pipeline():
    global _PIPELINE, _FEATURE_NAMES
    if _PIPELINE is None:
        with _LOCK:
            if _PIPELINE is None:
                _PIPELINE = joblib.load(C.MODEL_PIPELINE_PATH)
                _FEATURE_NAMES = list(joblib.load(C.FEATURE_NAMES_PATH))
    return _PIPELINE


def feature_names() -> list[str]:
    get_pipeline()
    return _FEATURE_NAMES


def preprocessor():
    """The fitted ColumnTransformer (imputer + scaler), i.e. the pipeline minus the model."""
    return get_pipeline()[:-1]


def classifier():
    """The fitted RandomForestClassifier at the end of the pipeline."""
    return get_pipeline().named_steps["clf"]


# ----------------------------------------------------------------------- features
def engineer(frame: pd.DataFrame) -> pd.DataFrame:
    """Stateless feature step — identical to notebook section 12/13."""
    out = frame.copy()
    out["TotalUnhealthyDays"] = (out["MentHlth"] + out["PhysHlth"]).clip(0, 60)
    out["CardioRisk"] = ((out["Stroke"] == 1) | (out["HeartDiseaseorAttack"] == 1)).astype(int)
    return out


def to_model_frame(feat: dict) -> pd.DataFrame:
    """dict of the 21 raw features (values or None) -> 1-row DataFrame of the 23 model
    features in the exact order the pipeline expects. None stays as NaN so the
    pipeline's SimpleImputer fills it."""
    row = {k: (np.nan if feat.get(k) is None else feat.get(k)) for k in C.RAW_FEATURES}
    df = pd.DataFrame([row], dtype="float64")
    df = engineer(df)
    return df[feature_names()]


# --------------------------------------------------------------------- prediction
def predict_proba(feat: dict) -> float:
    X = to_model_frame(feat)
    return float(get_pipeline().predict_proba(X)[0, 1])


def predict_proba_batch(feats: list[dict]) -> np.ndarray:
    rows = [to_model_frame(f).iloc[0] for f in feats]
    X = pd.DataFrame(rows)[feature_names()]
    return get_pipeline().predict_proba(X)[:, 1]


# ---------------------------------------------------------------- decision bands
def load_thresholds() -> dict:
    try:
        d = json.loads(C.THRESHOLDS_PATH.read_text())
        return {"moderate_cut": float(d["moderate_cut"]), "high_cut": float(d["high_cut"])}
    except Exception:
        return {"moderate_cut": C.DEFAULT_MODERATE_CUT, "high_cut": C.DEFAULT_HIGH_CUT}


def save_thresholds(moderate_cut: float, high_cut: float, set_by: str = "dashboard") -> dict:
    import datetime as _dt
    moderate_cut = max(0.0, min(1.0, float(moderate_cut)))
    high_cut = max(0.0, min(1.0, float(high_cut)))
    if moderate_cut > high_cut:
        moderate_cut, high_cut = high_cut, moderate_cut
    payload = {"moderate_cut": moderate_cut, "high_cut": high_cut,
               "set_by": set_by, "set_at": _dt.datetime.now().isoformat(timespec="seconds")}
    C.RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    C.THRESHOLDS_PATH.write_text(json.dumps(payload, indent=2))
    return payload


_BAND_LABEL = {
    "Low": "Low risk — routine advice",
    "Moderate": "Moderate risk — re-screen in a year / lifestyle counselling",
    "High": "High risk — refer for a confirmatory blood test",
}


def band(p: float, thr: Optional[dict] = None) -> tuple[str, str]:
    thr = thr or load_thresholds()
    if p >= thr["high_cut"]:
        b = "High"
    elif p >= thr["moderate_cut"]:
        b = "Moderate"
    else:
        b = "Low"
    return b, _BAND_LABEL[b]


# ------------------------------------------------------------ uncertainty from NA
def uncertainty_band(feat: dict, imputed_fields: list[str]) -> Optional[list[float]]:
    """Re-score with each imputed *binary* field forced to 0 and to 1; report the
    min/max probability. Continuous imputations are covered separately (BMI band)."""
    flippable = [f for f in imputed_fields if f in C.BINARY_FEATURES]
    if not flippable:
        return None
    # cap the combinatorial blow-up: vary at most 6 fields jointly via corners is
    # expensive; instead vary them one at a time around the imputed baseline.
    base = predict_proba(feat)
    lo = hi = base
    for f in flippable:
        for v in (0, 1):
            p = predict_proba({**feat, f: v})
            lo, hi = min(lo, p), max(hi, p)
    return [round(lo, 4), round(hi, 4)]
