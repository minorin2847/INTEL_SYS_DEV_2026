"""What-if and counterfactual explanations.

Only *modifiable* factors are varied (BMI, smoking, heavy drinking, physical activity,
fruit, vegetables). Every response carries the caveat that these are model
associations from survey data, not causal effects or medical advice.
"""
from __future__ import annotations

import numpy as np

from . import config as C
from . import inference as I

CAVEAT = (
    "These figures show how the model's estimate changes given patterns in survey "
    "data. They are not a prediction of your future health and are not medical advice."
)


def _healthy_bmi_target(current: float) -> float:
    # aim for the top of the "normal" range, but never increase BMI in the what-if
    return float(min(current, 24.9)) if current is not None else 24.9


def whatif(feat: dict) -> dict:
    base = I.predict_proba(feat)
    factors = []

    for f, healthy in C.MODIFIABLE_BINARY.items():
        cur = feat.get(f)
        if cur is None or int(cur) == healthy:
            continue
        p = I.predict_proba({**feat, f: healthy})
        factors.append({
            "feature": f, "label": C.FEATURE_LABELS.get(f, f),
            "from": int(cur), "to": int(healthy),
            "new_risk": round(p, 4), "delta": round(p - base, 4),
        })

    # 1-D BMI sweep (spans both directions so "BMI 80 -> 60" and the reverse show)
    sweep = []
    cur_bmi = feat.get("BMI")
    if cur_bmi is not None:
        lo = min(float(cur_bmi), 22.0)
        hi = max(float(cur_bmi), 40.0)
        for b in np.round(np.arange(lo, hi + 0.001, 1.0), 1):
            sweep.append({"bmi": float(b),
                          "risk": round(I.predict_proba({**feat, "BMI": float(b)}), 4)})

    factors.sort(key=lambda d: d["delta"])          # most protective change first
    return {
        "base_risk": round(base, 4),
        "factors": factors,
        "bmi_sweep": sweep,
        "current_bmi": None if cur_bmi is None else float(cur_bmi),
        "caveat": CAVEAT,
    }


def counterfactual(feat: dict, target_band: str = "Moderate") -> dict:
    """Greedy search: repeatedly apply the single modifiable change with the largest
    risk reduction until the band reaches `target_band` or nothing helps."""
    order = {"Low": 0, "Moderate": 1, "High": 2}
    thr = I.load_thresholds()

    cur = dict(feat)
    from_risk = I.predict_proba(cur)
    changes: list[dict] = []

    def worse_than_target(p):
        return order[I.band(p, thr)[0]] > order[target_band]

    for _ in range(len(C.MODIFIABLE_BINARY) + 3):
        p_now = I.predict_proba(cur)
        if not worse_than_target(p_now):
            break

        best = None
        # binary flips
        for f, healthy in C.MODIFIABLE_BINARY.items():
            if cur.get(f) is None or int(cur[f]) == healthy:
                continue
            p = I.predict_proba({**cur, f: healthy})
            if best is None or p < best[0]:
                best = (p, f, int(cur[f]), int(healthy))
        # BMI step of 5 toward a healthy target
        if cur.get("BMI") is not None and float(cur["BMI"]) > 25.0:
            new_bmi = round(max(25.0, float(cur["BMI"]) - 5.0), 1)
            p = I.predict_proba({**cur, "BMI": new_bmi})
            if best is None or p < best[0]:
                best = (p, "BMI", float(cur["BMI"]), new_bmi)

        if best is None or best[0] >= p_now - 1e-6:
            break
        p, f, frm, to = best
        cur[f] = to
        changes.append({"feature": f, "label": C.FEATURE_LABELS.get(f, f),
                        "from": frm, "to": to, "risk_after": round(p, 4)})

    to_risk = I.predict_proba(cur)
    return {
        "from_risk": round(from_risk, 4),
        "from_band": I.band(from_risk, thr)[0],
        "to_risk": round(to_risk, 4),
        "to_band": I.band(to_risk, thr)[0],
        "target_band": target_band,
        "feasible": order[I.band(to_risk, thr)[0]] <= order[target_band],
        "changes": changes,
        "caveat": CAVEAT,
    }
