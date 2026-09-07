# Diabetes Screening API

FastAPI service that wraps `model/model_pipeline.joblib` (preprocessing + random
forest, from `notebook/diabetes.ipynb`) and adds explanation, similar-case retrieval,
what-if analysis and an operator threshold dashboard. See `../APP_DESIGN.md` for the
full design.

## Setup

```bash
# from the diabetes/ directory, using the Anaconda environment
pip install -r requirements.txt

# 1. the notebook must already have produced model/model_pipeline.joblib etc.
# 2. build the serving-only artifacts (neighbor index, holdout scores, BMI table, thresholds)
python api/build_artifacts.py

# 3. run the API
uvicorn api.main:app --reload --port 8000
```

Interactive docs: http://localhost:8000/docs

## What `build_artifacts.py` produces (all regenerable, git-ignored)

| File | Purpose |
|---|---|
| `model/holdout_scores.joblib` | `(y_true, probability, split)` on validation + test, from a fresh train-only RF — powers the threshold dashboard |
| `api/artifacts/neighbor_index.joblib` | RF leaf matrix for 30k training rows + outcomes + profiles — powers `/similar` |
| `api/artifacts/shap_background.joblib` | 200-row preprocessed sample (reserved for interventional SHAP) |
| `api/artifacts/bmi_by_age_sex.joblib` | median BMI among non-diabetic rows by (age band, sex) — fallback BMI imputation |
| `api/runtime/thresholds.json` | decision cut-points, seeded to the max-F1 point on validation, then editable via `/config/thresholds` |

## Endpoints

| Method / path | Purpose |
|---|---|
| `POST /predict?include=explain,similar,whatif,counterfactual` | screen one respondent; `include` adds optional blocks |
| `POST /explain` | SHAP factor contributions for one respondent |
| `POST /similar` | 5 most similar training respondents by RF proximity + their outcomes |
| `POST /whatif` | risk delta for each modifiable factor + a BMI sweep |
| `POST /counterfactual?target_band=Moderate` | smallest set of modifiable changes to lower the band |
| `GET /history?session=<id>` | past screenings for a session |
| `GET /metrics` | live monitoring aggregates (flag rate, band mix, BMI-clamp rate, …) |
| `GET /threshold-curve?split=val` | precision / recall / flag rate / confusion across `high_cut` values |
| `GET /threshold-recommend?objective=recall&target=0.9` | suggested `high_cut` for an objective |
| `GET /config` · `POST /config/thresholds` | read / set decision thresholds (`X-Admin-Key` header) |
| `GET /questions` | questionnaire metadata so a client can render the form |
| `GET /model-info` · `GET /healthz` | model metadata / liveness |

## Request shape

`Age` and `Sex` are required. Every other field is optional; send `null` (or omit it)
for a "not sure" answer. `BMI` may be given directly or computed from `height_cm` +
`weight_kg`. Example:

```json
{
  "Age": 9, "Sex": 1, "height_cm": 175, "weight_kg": 104,
  "HighBP": 1, "HighChol": 1, "CholCheck": 1, "Smoker": 1, "Stroke": 0,
  "HeartDiseaseorAttack": 0, "PhysActivity": 0, "Fruits": 0, "Veggies": 1,
  "HvyAlcoholConsump": 0, "AnyHealthcare": 1, "NoDocbcCost": 0,
  "DiffWalk": 1, "GenHlth": 4, "MentHlth": 10, "PhysHlth": 15,
  "Education": 4, "Income": 3, "session_id": "demo-1"
}
```

## Config

- `DIABETES_ADMIN_KEY` (env) — key required by `POST /config/thresholds`. Default `change-me`.
