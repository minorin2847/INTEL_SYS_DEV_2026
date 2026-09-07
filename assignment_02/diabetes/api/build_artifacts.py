"""One-off packaging step: build the serving-only artifacts the extra features need.

Run once, from the diabetes/ directory, AFTER the notebook has produced
model/model_pipeline.joblib:

    F:/anaconda/python.exe api/build_artifacts.py

Produces:
    model/holdout_scores.joblib        (y_true, probability, split) on val + test
    api/artifacts/neighbor_index.joblib  RF leaf matrix + outcomes + profiles (30k rows)
    api/artifacts/shap_background.joblib  small preprocessed sample (optional use)
    api/artifacts/bmi_by_age_sex.joblib   median BMI among non-diabetic rows, by age x sex
    api/runtime/thresholds.json           seeded with the max-F1 cut on validation

None of these are graded deliverables — they are regenerable from model/ + data/.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # allow `import api.*`
from api import config as C          # noqa: E402
from api import inference as I       # noqa: E402

SEED = 42


def load_frame() -> pd.DataFrame:
    df = pd.read_csv(C.RAW_CSV_PATH).drop_duplicates().reset_index(drop=True)
    df["Diabetes_binary"] = (df["Diabetes_012"] >= 1).astype(int)
    return df


def split(df: pd.DataFrame):
    X = I.engineer(df[C.RAW_FEATURES])[C.MODEL_FEATURES]
    y = df["Diabetes_binary"].astype(int)
    X_tr, X_tmp, y_tr, y_tmp = train_test_split(
        X, y, test_size=0.30, stratify=y, random_state=SEED)
    X_val, X_te, y_val, y_te = train_test_split(
        X_tmp, y_tmp, test_size=0.50, stratify=y_tmp, random_state=SEED)
    return X_tr, y_tr, X_val, y_val, X_te, y_te


def make_prep() -> ColumnTransformer:
    scale = C.CONTINUOUS_FEATURES + C.ORDINAL_FEATURES + ["TotalUnhealthyDays"]
    pass_through = C.BINARY_FEATURES + ["CardioRisk"]
    return ColumnTransformer([
        ("num", Pipeline([("i", SimpleImputer(strategy="median")),
                          ("s", StandardScaler())]), scale),
        ("bin", "passthrough", pass_through),
    ])


def build_holdout_scores(X_tr, y_tr, X_val, y_val, X_te, y_te) -> np.ndarray:
    """Honest holdout scores: fit a fresh RF on TRAIN ONLY (notebook section 19 specs)
    and score val + test. The shipped model_pipeline.joblib was refit on train+val,
    so it cannot give an unbiased validation score."""
    rf = RandomForestClassifier(
        n_estimators=300, max_depth=12, min_samples_leaf=20, n_jobs=-1,
        class_weight="balanced_subsample", random_state=SEED)
    pipe = Pipeline([("prep", make_prep()), ("clf", rf)]).fit(X_tr, y_tr)
    pv = pipe.predict_proba(X_val)[:, 1]
    pt = pipe.predict_proba(X_te)[:, 1]
    rows = np.column_stack([
        np.r_[y_val.to_numpy(), y_te.to_numpy()],
        np.r_[pv, pt],
        np.r_[np.zeros(len(pv)), np.ones(len(pt))],   # 0 = val, 1 = test
    ])
    return rows


def seed_thresholds(scores: np.ndarray) -> dict:
    val = scores[scores[:, 2] == 0]
    y, p = val[:, 0].astype(int), val[:, 1]
    best_cut, best_f1 = 0.5, -1.0
    for cut in np.linspace(0.05, 0.9, 86):
        f1 = f1_score(y, (p >= cut).astype(int), zero_division=0)
        if f1 > best_f1:
            best_cut, best_f1 = float(cut), float(f1)
    payload = {"moderate_cut": round(max(0.1, best_cut - 0.15), 3),
               "high_cut": round(best_cut, 3),
               "set_by": "build_artifacts (max-F1 on validation)",
               "set_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    C.RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    C.THRESHOLDS_PATH.write_text(json.dumps(payload, indent=2))
    return payload


def build_neighbor_index(df: pd.DataFrame, X_tr, y_tr, n: int = 30_000) -> dict:
    pipe = I.get_pipeline()
    rf = pipe.named_steps["clf"]
    idx = train_test_split(X_tr.index, train_size=min(n, len(X_tr)),
                           stratify=y_tr, random_state=SEED)[0]
    Xsub = pipe[:-1].transform(X_tr.loc[idx])
    leaves = rf.apply(Xsub).astype(np.int32)
    outcomes = y_tr.loc[idx].to_numpy().astype(np.int8)
    profiles = [_profile(df.loc[i]) for i in idx]
    return {"leaves": leaves, "outcomes": outcomes, "profiles": profiles,
            "n_estimators": int(rf.n_estimators)}


_AGE_LABEL = {1: "18-24", 2: "25-29", 3: "30-34", 4: "35-39", 5: "40-44", 6: "45-49",
              7: "50-54", 8: "55-59", 9: "60-64", 10: "65-69", 11: "70-74",
              12: "75-79", 13: "80+"}


def _profile(r: pd.Series) -> str:
    sex = "M" if r["Sex"] == 1 else "F"
    tags = []
    if r["HighBP"] == 1: tags.append("high BP")
    if r["HighChol"] == 1: tags.append("high chol")
    if r["Smoker"] == 1: tags.append("smoker")
    if r["PhysActivity"] == 0: tags.append("inactive")
    if r["DiffWalk"] == 1: tags.append("walk difficulty")
    tag = ", ".join(tags) if tags else "few risk flags"
    return f"{sex}, age {_AGE_LABEL.get(int(r['Age']), '?')}, BMI {r['BMI']:.0f}, GenHlth {int(r['GenHlth'])} ({tag})"


def build_bmi_table(df: pd.DataFrame) -> dict:
    healthy = df[df["Diabetes_binary"] == 0]
    g = healthy.groupby(["Age", "Sex"])["BMI"].median()
    return {(int(a), int(s)): float(v) for (a, s), v in g.items()}


def main() -> None:
    C.ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    C.RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

    print("loading data ...")
    df = load_frame()
    print(f"  {len(df):,} rows after de-duplication")
    X_tr, y_tr, X_val, y_val, X_te, y_te = split(df)

    print("building holdout scores (fresh train-only RF) ...")
    t0 = time.time()
    scores = build_holdout_scores(X_tr, y_tr, X_val, y_val, X_te, y_te)
    joblib.dump(scores, C.HOLDOUT_SCORES_PATH)
    print(f"  -> {C.HOLDOUT_SCORES_PATH.name}  {scores.shape}  ({time.time()-t0:.0f}s)")

    print("seeding decision thresholds ...")
    thr = seed_thresholds(scores)
    print(f"  -> {thr}")

    print("building neighbor index (RF proximity) ...")
    t0 = time.time()
    ni = build_neighbor_index(df, X_tr, y_tr)
    joblib.dump(ni, C.NEIGHBOR_INDEX_PATH)
    print(f"  -> {C.NEIGHBOR_INDEX_PATH.name}  leaves {ni['leaves'].shape}  ({time.time()-t0:.0f}s)")

    print("building shap background sample ...")
    bg = I.get_pipeline()[:-1].transform(
        train_test_split(X_tr, train_size=200, stratify=y_tr, random_state=SEED)[0])
    joblib.dump(np.asarray(bg), C.SHAP_BACKGROUND_PATH)
    print(f"  -> {C.SHAP_BACKGROUND_PATH.name}  {np.asarray(bg).shape}")

    print("building BMI-by-age-sex table (non-diabetic rows) ...")
    tbl = build_bmi_table(df)
    joblib.dump(tbl, C.BMI_TABLE_PATH)
    print(f"  -> {C.BMI_TABLE_PATH.name}  {len(tbl)} cells")

    print("\ndone. start the API with:  uvicorn api.main:app --port 8000")


if __name__ == "__main__":
    main()
