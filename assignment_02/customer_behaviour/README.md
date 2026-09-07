# Assignment 02 — Application 3: Customer Behaviour (Sephora)

**Intelligent System Development · From Data Representation to a Deployable Intelligent System**
Lecturer: Dinh Que Tran, Ph.D., Assoc. Prof. · Semester I.2026

This is the **customer_behaviour** application of the Assignment 02 submission.

## Pipeline & Overview

```
Data → Understand → Clean → Represent → Learn → Evaluate → Persist → Deploy (Web + Mobile)
```

This is a **Classification (Text + Tabular)** task. The pipeline takes raw real-world data, represents it numerically, trains the model, and deploys it as a usable web and mobile service. 

## Dataset

| Field | Value |
|---|---|
| Name | Sephora Products and Skincare Reviews |
| File | `data/reviews_500-750.csv and product_info.csv` |
| Target | `is_recommended` |

To get the dataset, place `reviews_500-750.csv and product_info.csv` in the `data/` directory.

## Reproducibility & Environment

* **Python version**: 3.12/3.13
* **OS**: Windows / Linux
* **Dependencies**: See `requirements.txt`
* **Random Seed**: `RANDOM_SEED = 42` is used throughout the notebooks for exact reproducibility.

## Notebook & Retraining

Open `notebook/customer_behaviour.ipynb` and run all cells.
This will load the data, clean it, represent it, evaluate models, and persist the best model to the `model/` directory.
The persisted artifacts are:
* `model/model_pipeline.joblib`
* `model/feature_names.joblib`
* `model/input_schema.json` (Expected input schema)

## How to run WITHOUT Docker

### 1. API Service
Ensure you have installed the requirements:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
Run the API:
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8002
# Swagger UI: http://localhost:8002/docs
```

### 2. Web Client
```bash
cd web
npm install
npm run dev
# The web app will be available on http://localhost:5173 or 5174
```

## How to run WITH Docker

You can run the API and Web applications seamlessly using Docker Compose. The Docker configuration will build and serve both the API and the React Web App.

```bash
docker compose up --build -d
```
* **API Service**: Available at `http://localhost:8002` (Swagger UI at `/docs`)
* **Web Client**: Available at `http://localhost:5175`

*Note: The mobile application is not containerized and must be run locally.*

## Testing the API (cURL)

```bash
curl -X POST http://localhost:8002/predict -H "Content-Type: application/json" -d '{"skin_type": "normal", "skin_tone": "medium", "category": "treatments", "price_usd": 20.0, "review_text": "This product works amazing!"}'
# Expected Response:
# {"prediction": "recommend", "p_recommend": 0.92}
```

## Mobile Client (Flutter)

The mobile client is a native Flutter cross-platform app. It does not train the model; it is a pure REST client (Training ≠ Inference).

```bash
cd mobile
flutter pub get
flutter run
```
Point the app to `http://localhost:8002` (or `http://10.0.2.2:8002` on an Android emulator, or your host machine's Wi-Fi LAN IP).
