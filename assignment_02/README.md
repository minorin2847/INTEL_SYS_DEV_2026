# Assignment 02 — From Data Representation to Deployable Intelligent Systems

Three intelligent applications built on the **same pipeline**, so their differences can
be compared side by side:

```
Raw data → Understand → Clean → Represent → Learn → Evaluate → Persist → Deploy
```

| # | Application | Task | Raw form | Representation | Status |
|---|---|---|---|---|---|
| 1 | **Diabetes** prediction | binary classification | CSV (BRFSS survey) | feature matrix `X ∈ ℝ^{N×23}` | ✅ notebook · API · web · mobile |
| 2 | **House price** prediction | regression | CSV | encoded + scaled feature matrix | ✅ notebook · API · web · mobile |
| 3 | **Customer behaviour** (Sephora skincare reviews) | binary classification | CSV tables + review comments | tabular profile **‖** TF-IDF text `ℝ^{~13000}` | ✅ notebook · API · web · mobile |

Each application is self-contained under its own folder with an identical layout
(Appendix A):

```
<app>/
  data/        raw dataset (or download reference)
  notebook/    <app>.ipynb  — the 23-section ML experiment, executed with outputs
  model/       model_pipeline.joblib  +  feature_names.joblib  +  input_schema.json
  api/         FastAPI service exposing POST /predict
  web/         React + Vite single-page client (no model in the browser)
  mobile/      Flutter client (REST client of the API)
  requirements.txt
report/        Assignment_02.pdf  (final ~10-page report)
```

The **report** is written from each app's `Report_Deliverable.md` guide
(`diabetes/Report_Deliverable.md`, `customer_behaviour/Report_Deliverable.md`) plus the
executed notebooks.

---

## Environment

| | |
|---|---|
| Python | 3.13 (3.14 also tested for diabetes) |
| OS | Windows 11 |
| Random seed | `RANDOM_SEED = 42` everywhere (numpy, `random`, every split / subsample / estimator) |
| Node (web) | 18+ |
| Flutter (mobile) | 3.19+ |

Each app pins its Python deps in `<app>/requirements.txt`. Install per app:

```bash
cd assignment_02/<app>
pip install -r requirements.txt
```

Every `mobile/` client targets **Android only** — each `mobile/android/` folder is
committed as-is (no other platform folders, no `flutter create` step needed); just
`flutter pub get` and `flutter run`. Requires the Flutter SDK plus an Android SDK
(`flutter doctor` should show the Android toolchain check passing) and either a
connected device or a running emulator.

---

## Data-representation summary (mandatory table)

| Application | Raw form | Numerical representation | Model input |
|---|---|---|---|
| Diabetes | CSV / table | 21 raw + 2 engineered → feature vector, `StandardScaler` on 8 numeric cols, no one-hot | `X ∈ ℝ^{N×23}` dense |
| House price | CSV / table | encoded + scaled feature matrix | `X ∈ ℝ^{N×d}` *(pending)* |
| Customer behaviour | 2 CSV tables + review text | Tabular profile (skin type, brand, price) **‖** `TfidfVectorizer(1–2-gram)` on the review text | `X ∈ ℝ^{N×d}` sparse, `N ≈ 104,000` |

Every dimension is explained in the corresponding notebook §12 and in the report.

---

## Application 1 — Diabetes

**Dataset:** Kaggle `alexteboul/diabetes-health-indicators-dataset`
(`diabetes_012_health_indicators_BRFSS2015.csv`), already in `diabetes/data/`.
253,680 rows → 229,781 after de-duplication. Target `Diabetes_binary`.
**Deployed model:** Random Forest, test ROC-AUC ≈ 0.81, recall ≈ 0.74.

```bash
cd assignment_02/diabetes

# 1. reproduce the experiment (writes model/*.joblib)
jupyter nbconvert --to notebook --execute notebook/diabetes.ipynb --output diabetes.ipynb
python api/build_artifacts.py            # one-off serving artifacts (neighbour index, SHAP bg)

# 2. run the API  ->  http://localhost:8000/docs
uvicorn api.main:app --port 8000

# 3. run the web client  ->  http://localhost:5173
npm --prefix web install && npm --prefix web run dev

# 4. run the mobile client — Android only (10.0.2.2 is the emulator's alias for the host)
cd mobile && flutter pub get
flutter run --dart-define=API_URL=http://10.0.2.2:8000
```

`POST /predict` example:

```bash
curl -s http://localhost:8000/predict -H 'content-type: application/json' -d '{
  "Age": 9, "Sex": 1, "HighBP": 1, "HighChol": 1, "BMI": 34, "GenHlth": 4,
  "DiffWalk": 1, "PhysActivity": 0, "Smoker": 1
}'
# -> { "prediction": "diabetic", "confidence": 0.85, ... }
```

More detail: `diabetes/api/README.md`, `diabetes/web/README.md`, `diabetes/mobile/README.md`.

---

## Application 2 — House price

**Task:** regression on a Kaggle house-price dataset. **Deployed model:** Random Forest
(trained on `log1p(price)`, predictions inverted with `expm1`).

```bash
cd assignment_02/house_price
pip install -r requirements.txt

# 1. reproduce the experiment (writes model/model_pipeline.joblib)
jupyter nbconvert --to notebook --execute notebook/house_price.ipynb --output house_price.ipynb

# 2. run the API  ->  http://localhost:8002/docs
uvicorn house_price.api.main:app --reload --host 0.0.0.0 --port 8002

# 3. run the web client
npm --prefix web install && npm --prefix web run dev

# 4. run the mobile client — Android only (defaults to http://10.0.2.2:8002,
#    the Android emulator's alias for the host; switchable at runtime in-app)
cd mobile && flutter pub get
flutter run
```

More detail: `house_price/mobile/README.md`.

---

## Application 3 — Customer behaviour (Sephora Skincare Reviews)

**Dataset:** Kaggle `nadyinky/sephora-products-and-skincare-reviews` (2 CSVs), in `customer_behaviour/data/`.
104k Sephora skincare reviews. Target `is_recommended`.
**Deployed model:** Logistic Regression on the **tabular + comment-text** representation.
Adding the review text lifts mean ROC-AUC significantly over tabular features alone.

```bash
cd assignment_02/customer_behaviour
pip install -r requirements.txt

# 1. reproduce the experiment (writes model/*.joblib + input_schema.json)
python -m nbclient notebook/customer_behaviour.ipynb        # or: jupyter nbconvert --execute

# 2. run the API  ->  http://localhost:8000/docs
uvicorn api.main:app --port 8000

# 3. run the web client  ->  http://localhost:5174
npm --prefix web install && npm --prefix web run dev

# 4. run the mobile client — Android only
cd mobile && flutter pub get
flutter run --dart-define=API_URL=http://10.0.2.2:8000
```

Or run the API + web together in Docker:

```bash
cd assignment_02/customer_behaviour
docker compose up --build
#   web -> http://localhost:5174   ·   api -> http://localhost:8000/docs
```

`POST /predict` example:

```bash
curl -s http://localhost:8000/predict -H 'content-type: application/json' -d '{
  "skin_type": "normal", "skin_tone": "medium", "category": "treatments",
  "price_usd": 20.0, "review_text": "This product works amazing!"
}'
# -> { "prediction": "recommend", "p_recommend": 0.92, ... }
```

More detail: `customer_behaviour/api/README.md`, `customer_behaviour/web/README.md`,
`customer_behaviour/mobile/README.md`, `customer_behaviour/Report_Deliverable.md`.

---

## Deployment architecture (shared by all apps)

```
User input → API request → validation → SAME preprocessing (loaded from training) → saved model → prediction → JSON → web / mobile UI
```

**Data-leakage rule:** the deployed service loads the preprocessing pipeline that was
fitted on the *training* split and only calls `.transform()` / `.predict_proba()`. It
never fits a new scaler, encoder, imputer or vectoriser on user input or test data.
The notebooks verify this in §23 by reloading the artifact from disk and asserting the
prediction matches the in-memory pipeline.
