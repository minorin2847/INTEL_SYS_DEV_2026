# Customer-behaviour API — product-recommendation prediction

FastAPI service that loads the persisted pipeline from
`customer_behaviour/model/model_pipeline.joblib` and predicts whether a Sephora
skincare reviewer **recommends the product** (`is_recommended`).

```
raw review JSON ─▶ validation (pydantic) ─▶ build_features()  ─▶ fitted pipeline ─▶ JSON
                                            (stateless, no fit)   (ColumnTransformer:
                                                                   impute+log1p+scale,
                                                                   one-hot,
                                                                   TF-IDF(title+body))
                                                                   + LogisticRegression
```

The API **never fits** a scaler / encoder / vectoriser — it only calls `transform` /
`predict_proba` on the object trained in notebook §22.

Target: **`is_recommended`**. See notebook §14a — the review text is written in the same
session as the recommend tick, so the reported ROC-AUC (~0.96) is partly text↔label
co-authorship; the tabular-only signal is ~0.8, the text-only ~0.96.

## Run — local

```bash
cd customer_behaviour
python -m venv .venv && . .venv/Scripts/activate      # Windows;  .venv/bin/activate on *nix
pip install -r requirements.txt                       # notebook + API; api/requirements.txt is serving-only
python api/make_samples.py                            # writes api/samples.json from data/sephora/
python -m uvicorn api.main:app --port 8000 --reload   # run from customer_behaviour/, NOT api/
# docs / try-it:  http://localhost:8000/docs
```

## Run — Docker

`customer_behaviour/docker-compose.yml` builds this API **and** the nginx-served web
client:

```bash
cd customer_behaviour
docker compose up --build
#   web  -> http://localhost:5174   (its /api/* is proxied to the api container)
#   api  -> http://localhost:8000/docs
```

The image installs `api/requirements.txt` (serving deps only — `scikit-learn==1.9.0`
pinned to the version that pickled `model_pipeline.joblib`) and copies `api/` + `model/`.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/predict` | score one review |
| POST | `/predict/batch` | score `{ "reviews": [ ... ] }` |
| GET | `/questions` | form metadata — the web + mobile clients render their form from this |
| GET | `/samples` | `{ "defaults": {…typical values…}, "examples": [ {…review…, "_label", "_recommended"} ] }` — the web client's "Load a real review" picker |
| GET | `/model-info` | chosen model, representation, feature order, framing note |
| GET | `/healthz` | liveness + model name |

`api/samples.json` is a serving convenience (not graded). Regenerate with
`python api/make_samples.py` (joins `data/sephora/reviews_500-750.csv` +
`product_info.csv`, picks ~42 real reviews). It is small and committed so the API works
out of the box.

## Appendix D — Web report template

| | |
|---|---|
| **Framework** | FastAPI (Uvicorn) |
| **Endpoint** | `POST /predict` |
| **Input** | reviewer skin profile (`skin_type`, `skin_tone`, `eye_color`, `hair_color`), product (`price_usd`, `secondary_category`, `brand_name`, `loves_count`, `reviews`), review (`review_title`, `review_text`). Optional: edition flags, ingredient / highlight strings, feedback-vote counts, `submission_time` |
| **Validation** | pydantic `ReviewInput` — `review_text` (≥ 1 char) and `price_usd` (≥ 0) effectively required; everything else optional |
| **Excluded (leakage)** | the review's own star `rating`, the product average rating (notebook §1.3 / §14a) |
| **Preprocessing** | loaded from training: `SimpleImputer(median)` → `log1p` (money / popularity) → `StandardScaler`; `OneHotEncoder(handle_unknown="ignore", min_frequency=25)`; `TfidfVectorizer(1–2-gram, min_df=10, max 40000, English stop-words)` on `review_title + " . " + review_text` |
| **Loaded model** | `LogisticRegression(class_weight="balanced")`, representation `tabular + TF-IDF(text)`, seed 42, scikit-learn 1.9.0 |
| **Output** | `{"prediction","confidence","p_recommend","threshold","review_terms","signals","contributions","model","representation"}` |

### Example request

```bash
curl -s http://localhost:8000/predict -H "content-type: application/json" -d '{
  "skin_type": "oily", "skin_tone": "light",
  "secondary_category": "Moisturizers", "brand_name": "Skinfix",
  "price_usd": 32.0, "loves_count": 21000, "reviews": 1800,
  "review_title": "Not for oily skin",
  "review_text": "Broke me out within a week and felt greasy all day. Smells strongly of perfume. Wanted to love it but returned it."
}'
```

### Example response

```json
{
  "prediction": "not recommend",
  "confidence": 0.996,
  "p_recommend": 0.004,
  "threshold": 0.5,
  "review_terms": {
    "toward": [{"term": "love", "effect": 0.21}],
    "against": [{"term": "wanted love", "effect": -1.80}, {"term": "broke", "effect": -1.44},
                {"term": "returned", "effect": -1.07}]
  },
  "signals": {"skin_type": "Oily", "category": "Moisturizers", "brand": "Skinfix",
              "price_usd": 32.0, "price_tier": "mid", "product_loves": null,
              "review_tokens": 27, "has_title": true},
  "contributions": {
    "base_p": 0.8723, "final_p": 0.004, "dataset_base_rate": 0.846,
    "items": [
      {"label": "review: “wanted love”", "kind": "text", "effect": -1.7982},
      {"label": "review: “broke”",       "kind": "text", "effect": -1.4446},
      {"label": "review: “returned”",    "kind": "text", "effect": -1.0707}
    ],
    "other_effect": -0.31,
    "note": "bars are log-odds contributions; reference = the model's class-balanced average review"
  },
  "model": "LogisticRegression", "representation": "tabular + TF-IDF(text)"
}
```

### `contributions` — the explanation

An **exact linear-SHAP decomposition** (no `shap` library). For the deployed
`LogisticRegression`, with `model/feature_means.joblib` giving the mean of every
transformed feature over the fit set:

```
phi_j   = coef_j * (x_j - mean_j)              # per-feature log-odds pull
z_base  = intercept + coef . mean              # sigmoid(z_base) = base_p
sigmoid(z_base + sum_j phi_j) == final_p       # holds exactly
```

`base_p` is the model's neutral point for an average review (the classes are weighted
equally in training, so it is not the 85% dataset recommend rate). `items` are the top
~12 factors by |effect| with labels derived from the raw review (`txt__<tok>` →
`review: "<tok>"`, one-hot → `Category: …` / `Brand: …`, scaled numeric →
`… : above/below average`); the rest are folded into `other_effect`. `review_terms` is
the same text branch re-expressed as the words present in *this* review, split by sign.
`contributions` is `null` if the deployed model is not linear.
