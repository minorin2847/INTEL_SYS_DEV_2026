# Assignment 02 — Application 1: Diabetes Prediction

**Intelligent System Development · From Data Representation to a Deployable Intelligent System**
Lecturer: Dinh Que Tran, Ph.D., Assoc. Prof. · Semester I.2026

This is the **diabetes** application of the Assignment 02 submission.

## Pipeline & Overview

```
Data → Understand → Clean → Represent → Learn → Evaluate → Persist → Deploy (Web + Mobile)
```

This is a **Classification** task. The pipeline takes raw real-world data, represents it numerically, trains the model, and deploys it as a usable web and mobile service. 

## Dataset

| Field | Value |
|---|---|
| Name | Diabetes Health Indicators Dataset (BRFSS 2015) |
| File | `data/diabetes_012_health_indicators_BRFSS2015.csv` |
| Target | `Diabetes_binary (0 or 1)` |

To get the dataset, place `diabetes_012_health_indicators_BRFSS2015.csv` in the `data/` directory.

## Reproducibility & Environment

* **Python version**: 3.12/3.13
* **OS**: Windows / Linux
* **Dependencies**: See `requirements.txt`
* **Random Seed**: `RANDOM_SEED = 42` is used throughout the notebooks for exact reproducibility.

## Notebook & Retraining

Open `notebook/diabetes.ipynb` and run all cells.
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
uvicorn api.main:app --host 0.0.0.0 --port 8000
# Swagger UI: http://localhost:8000/docs
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
* **API Service**: Available at `http://localhost:8000` (Swagger UI at `/docs`)
* **Web Client**: Available at `http://localhost:5173`

*Note: The mobile application is not containerized and must be run locally.*

## Testing the API (cURL)

```bash
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{"HighBP": 1, "HighChol": 1, "BMI": 30.0, "GenHlth": 4, "Age": 9, "Fruits": 0, "Veggies": 1, "Smoker": 1, "Stroke": 0, "HeartDiseaseorAttack": 0, "PhysActivity": 0, "HvyAlcoholConsump": 0, "AnyHealthcare": 1, "NoDocbcCost": 0, "MentHlth": 0, "PhysHlth": 0, "DiffWalk": 0, "Sex": 1, "Education": 4, "Income": 5, "CholCheck": 1}'
# Expected Response:
# {"prediction": "diabetic", "confidence": 0.85}
```

## Mobile Client (Flutter)

The mobile client is a native Flutter cross-platform app. It does not train the model; it is a pure REST client (Training ≠ Inference).

```bash
cd mobile
flutter pub get
flutter run
```
Point the app to `http://localhost:8000` (or `http://10.0.2.2:8000` on an Android emulator, or your host machine's Wi-Fi LAN IP).
