# Assignment 02 — Application 2: House Price Prediction

**Intelligent System Development · From Data Representation to a Deployable Intelligent System**
Lecturer: Dinh Que Tran, Ph.D., Assoc. Prof. · Semester I.2026

This is the **house_price** application of the Assignment 02 submission.

## Pipeline & Overview

```
Data → Understand → Clean → Represent → Learn → Evaluate → Persist → Deploy (Web + Mobile)
```

This is a **Regression** task. The pipeline takes raw real-world data, represents it numerically, trains the model, and deploys it as a usable web and mobile service. 

## Dataset

| Field | Value |
|---|---|
| Name | VN Real Estate Listings (April-September 2025) |
| File | `data/VN-real-estate-Apr-Sept-2025.csv` |
| Target | `Price (Million VND)` |

To get the dataset, place `VN-real-estate-Apr-Sept-2025.csv` in the `data/` directory.

## Reproducibility & Environment

* **Python version**: 3.12/3.13
* **OS**: Windows / Linux
* **Dependencies**: See `requirements.txt`
* **Random Seed**: `RANDOM_SEED = 42` is used throughout the notebooks for exact reproducibility.

## Notebook & Retraining

Open `notebook/house_price.ipynb` and run all cells.
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
uvicorn api.main:app --host 0.0.0.0 --port 8001
# Swagger UI: http://localhost:8001/docs
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
* **API Service**: Available at `http://localhost:8001` (Swagger UI at `/docs`)
* **Web Client**: Available at `http://localhost:5174`

*Note: The mobile application is not containerized and must be run locally.*

## Testing the API (cURL)

```bash
curl -X POST http://localhost:8001/predict -H "Content-Type: application/json" -d '{"Area": 78.7, "Bedrooms": 3, "Bathrooms": 2, "Floors": 2, "Property Type": "Nhà riêng", "Province": "an-giang", "district": "Rạch Giá"}'
# Expected Response:
# {"predicted_price": 2381.21, "price_per_m2": 30.26, "formatted_price_billion": "2.38 tỷ VNĐ"}
```

## Mobile Client (Flutter)

The mobile client is a native Flutter cross-platform app. It does not train the model; it is a pure REST client (Training ≠ Inference).

```bash
cd mobile
flutter pub get
flutter run
```
Point the app to `http://localhost:8001` (or `http://10.0.2.2:8001` on an Android emulator, or your host machine's Wi-Fi LAN IP).
