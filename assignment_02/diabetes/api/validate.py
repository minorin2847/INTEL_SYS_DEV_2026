"""Input validation, BMI handling, and completeness.

Turns a raw questionnaire payload into the 21-field feature dict the model expects:
- computes BMI from height + weight when BMI is absent,
- clamps an out-of-range BMI to [12, 98] with a visible warning (APP_DESIGN.md 8.1),
- fills a still-missing BMI from an age x sex "healthy population" table when available,
- range-checks the coded fields (out-of-range -> treated as missing + warning),
- reports which fields were left blank and a completeness score.
"""
from __future__ import annotations

from typing import Optional

import joblib

from . import config as C

_BMI_TABLE: Optional[dict] = None
_BMI_TABLE_LOADED = False


def _bmi_table() -> Optional[dict]:
    """{(age_band:int, sex:int): median_bmi} among non-diabetic training rows.
    Built by build_artifacts.py; None if not built yet."""
    global _BMI_TABLE, _BMI_TABLE_LOADED
    if not _BMI_TABLE_LOADED:
        _BMI_TABLE_LOADED = True
        try:
            _BMI_TABLE = joblib.load(C.BMI_TABLE_PATH)
        except Exception:
            _BMI_TABLE = None
    return _BMI_TABLE


def _bmi_from_height_weight(h_cm, w_kg) -> Optional[float]:
    if h_cm is None or w_kg is None:
        return None
    try:
        m = float(h_cm) / 100.0
        if m <= 0:
            return None
        return round(float(w_kg) / (m * m), 1)
    except (TypeError, ValueError, ZeroDivisionError):
        return None


def prepare(payload: dict) -> dict:
    """Return a dict with keys:
        features        -> {21 raw feature name: value or None}
        warnings        -> [str]
        imputed_fields  -> [str]   (missing among the 21, before the pipeline imputer)
        completeness    -> float in [0, 1]
        bmi_source      -> "provided" | "height_weight" | "age_sex_table" | "pipeline_median"
    """
    warnings: list[str] = []
    feat: dict = {}

    # --- coded fields: copy through, range-check ---
    for f in C.BINARY_FEATURES + C.ORDINAL_FEATURES + ["MentHlth", "PhysHlth"]:
        v = payload.get(f)
        if v is None:
            feat[f] = None
            continue
        lo, hi = C.VALUE_RANGES[f]
        iv = int(round(float(v)))
        if iv < lo or iv > hi:
            warnings.append(f"{f}={v} is outside the valid range [{lo}, {hi}] and was ignored.")
            feat[f] = None
        else:
            feat[f] = iv

    # --- BMI ---
    bmi = payload.get("BMI")
    bmi_source = "provided"
    if bmi is None:
        bmi = _bmi_from_height_weight(payload.get("height_cm"), payload.get("weight_kg"))
        bmi_source = "height_weight" if bmi is not None else None

    if bmi is not None:
        bmi = float(bmi)
        if bmi > C.BMI_MAX:
            warnings.append(
                f"BMI value capped to the maximum value in our dataset ({C.BMI_MAX}).")
            bmi = C.BMI_MAX
        elif bmi < C.BMI_MIN:
            warnings.append(
                f"BMI value capped to the minimum value in our dataset ({C.BMI_MIN}).")
            bmi = C.BMI_MIN
        feat["BMI"] = round(bmi, 1)
    else:
        # try the age x sex healthy-population table
        table = _bmi_table()
        key = (feat.get("Age"), payload.get("Sex"))
        if table is not None and key in table:
            feat["BMI"] = round(float(table[key]), 1)
            bmi_source = "age_sex_table"
            warnings.append(
                "BMI was not provided; using the typical value for your age and sex.")
        else:
            feat["BMI"] = None
            bmi_source = "pipeline_median"

    # --- completeness (over the 21 raw features) ---
    imputed = [f for f in C.RAW_FEATURES if feat.get(f) is None]
    completeness = round(1.0 - len(imputed) / len(C.RAW_FEATURES), 3)
    if completeness < C.COMPLETENESS_WARN_BELOW:
        warnings.append(
            f"{len(imputed)} of {len(C.RAW_FEATURES)} answers were left blank and filled "
            f"with typical values - treat this estimate as indicative only.")

    return {
        "features": feat,
        "warnings": warnings,
        "imputed_fields": imputed,
        "completeness": completeness,
        "bmi_source": bmi_source,
    }
