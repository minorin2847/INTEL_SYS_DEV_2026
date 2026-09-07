"""FastAPI Service for House-Price Prediction (Assignment 02 · Application 2).

Pipeline flow:
    JSON request -> validation (schema.py) -> loaded ColumnTransformer (inference.py)
                 -> RandomForestRegressor -> expm1 -> JSON response (Appendix C)

Run:
    uvicorn house_price.api.main:app --reload --port 8002
"""
import sys
from pathlib import Path

# Add current directory and workspace root to sys.path
_CURR_DIR = Path(__file__).resolve().parent
_PARENT_DIR = _CURR_DIR.parent.parent
for _p in [str(_CURR_DIR), str(_PARENT_DIR)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

try:
    from . import config as C
    from . import inference as I
    from .schema import HealthOut, ListingInput, PredictionOut
except (ImportError, ValueError):
    import config as C  # type: ignore
    import inference as I  # type: ignore
    from schema import HealthOut, ListingInput, PredictionOut  # type: ignore

app = FastAPI(
    title="House-Price Prediction API",
    version="1.0.0",
    description=(
        "Assignment 02 · Application 2: Automated Valuation Model for Vietnam Real Estate. "
        "Loads a persisted sklearn Pipeline (ColumnTransformer + RandomForestRegressor). "
        "Training != Inference: no fitting at runtime."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for Web and Mobile clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _warmup() -> None:
    """Pre-warm the ML model pipeline at server startup."""
    try:
        I.get_pipeline()
        print(f"[startup] Successfully loaded model pipeline: {I.model_name()}")
    except Exception as exc:
        print(f"[startup] Warning: model pipeline not loaded at startup: {exc}")


@app.get("/", include_in_schema=False)
def root_redirect():
    """Redirect root requests to interactive Swagger documentation."""
    return RedirectResponse(url="/docs")


@app.get("/healthz", response_model=HealthOut, tags=["Health"])
def healthz() -> HealthOut:
    """Health probe reporting readiness and loaded model details."""
    ready = I.is_ready()
    return HealthOut(
        status="ok" if ready else "model-not-loaded",
        model_loaded=ready,
        model_name=I.model_name() if ready else None,
        features_count=len(I.feature_names()) if ready else None,
    )


@app.post("/predict", response_model=PredictionOut, tags=["Inference"])
def predict(input_data: ListingInput) -> PredictionOut:
    """Perform real estate valuation inference based on property attributes."""
    if not I.is_ready():
        raise HTTPException(
            status_code=503,
            detail=(
                "Model pipeline artifact 'model/model_pipeline.joblib' is not available. "
                "Ensure notebook/house_price.ipynb section 22 has been executed."
            ),
        )

    payload = input_data.model_dump(by_alias=True, exclude_none=True)

    try:
        price = I.predict_price(payload)
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Inference execution failed: {exc}",
        ) from exc

    area = payload.get("Area")
    ppm2 = round(price / area, 2) if (area and area > 0) else None

    # Format price in Vietnamese Tỷ VNĐ
    price_in_billion = price / 1000.0
    if price_in_billion >= 1.0:
        formatted_billion = f"{price_in_billion:,.2f} tỷ VNĐ"
    else:
        formatted_billion = f"{price:,.1f} triệu VNĐ"

    # One-line interpretation mandated by Course Spec Part XIII.1
    province_str = payload.get("Province", "surveyed area")
    district_str = payload.get("district", "")
    loc_display = f"{district_str}, {province_str}" if district_str else str(province_str)
    interpretation = (
        f"Estimated market value of approximately {formatted_billion} "
        f"({ppm2:,.1f} million VND/m²) for a {area} m² property in {loc_display}."
    )

    # Compute SHAP-style feature contributions & model metadata
    contributions = I.compute_feature_contributions(payload, price)
    meta = I.get_model_metadata()

    return PredictionOut(
        predicted_price=round(price, 2),
        price_per_m2=ppm2,
        formatted_price_billion=formatted_billion,
        currency=C.PRICE_UNIT,
        model_name=I.model_name(),
        interpretation=interpretation,
        feature_contributions=contributions,
        model_metadata=meta,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=C.DEFAULT_PORT)
