# House-Price Prediction — Web app (React + TypeScript + Vite)

Thin client of the FastAPI service (Appendix D). It runs **no model** — it collects one
listing, `POST`s it to `/predict`, and shows the returned price.

```
Browser (React form) → REST API → build_features + saved pipeline → RandomForest(log1p) → expm1 → JSON
```

## Appendix D — report template

| | |
|---|---|
| **Framework** | React 18 + TypeScript + Vite; `axios` |
| **Endpoint** | `POST http://<host>:8002/predict` (also `GET /healthz`) |
| **Input** | `Area` (required, m²); optional `Width, Length, Bedrooms, Bathrooms, Floors, "Alley Width", "Agent Listing Count"`, `"Property Type", Position, Direction, "Road Type", Province, "Agent Role", ward, district` |
| **Validation** | Pydantic `schema.py` on the API — `Area > 0` required; missing optional numerics are median-imputed by the loaded pipeline; unknown categoricals map to `"Unknown"` / an all-zero one-hot row |
| **Preprocessing** | loaded from training (`model_pipeline.joblib`): `SimpleImputer(median) → log1p → StandardScaler` (numeric); `OneHotEncoder(handle_unknown="ignore", min_frequency=50)` (categorical) — never re-fitted on a request |
| **Loaded model** | `RandomForestRegressor` trained on `log1p(Price)`; the response inverts with `expm1` |
| **Output** | `{ "predicted_price": 2540.82, "price_per_m2": 32.28, "currency": "million VND", "model": "RandomForest", "contributions": [...], "model_meta": {...} }` |

### Example request

```bash
curl -s http://localhost:8002/predict -H "content-type: application/json" -d '{
  "Area": 78.7, "Width": 4.0, "Bedrooms": 3, "Bathrooms": 2, "Floors": 2,
  "Agent Listing Count": 2, "Property Type": "Nhà riêng", "Position": "Đường chính",
  "Direction": "Nam", "Road Type": "Đường nhựa", "Province": "an-giang",
  "Agent Role": "Chính chủ", "district": "Rạch Giá"
}'
```

### Example response

```json
{ "predicted_price": 2540.82, "price_per_m2": 32.28, "currency": "million VND", "model": "RandomForest" }
```

## Run

```bash
# API first: from house_price/  ->  python -m uvicorn api.main:app --port 8002
cd web
npm install
npm run dev            # http://localhost:5173   (VITE_API_BASE defaults to http://localhost:8002)
```

`VITE_API_BASE=https://host npm run build` for a static build (`web/dist/`).

## Layout

```
web/src/
  main.tsx  App.tsx                shell: health check, form state, result
  services/api.ts                  axios wrapper (fetchHealth, predictPrice)
  types/index.ts                   ListingInput · PredictionResponse · ModelMetadata
  components/
    PredictionForm.tsx             the listing form + validation
    ResultCard.tsx                 predicted price + price/m² + feature contributions
    Navbar.tsx  ErrorBanner.tsx
  constants/options.ts             Property Type / Direction / Province option lists
  lib/format.ts                    Tỷ / triệu VND formatting
```

## Screenshots for the report (IDs W1–W3)

1. **W1** — the listing form with a valid example filled in.
2. **W2** — the result card: predicted price, price/m², interpretation.
3. **W3** — `http://localhost:8002/docs` `POST /predict` "Try it out" (evidence the app calls the API).
