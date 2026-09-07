"""FastAPI service for the customer-behaviour model (Sephora skincare reviews).

    POST /predict        one review  -> recommend / not recommend + confidence
    POST /predict/batch
    GET  /questions      form metadata (the web + mobile clients render from this)
    GET  /samples        typical-value defaults + real example reviews
    GET  /model-info     chosen model, representation, feature order, framing note
    GET  /healthz

Run:  uvicorn api.main:app --port 8000        (from customer_behaviour/)

Target: recommended = is_recommended.  Model: Logistic Regression on
tabular (skin profile + product) + TF-IDF(review title + body).  See notebook §14a
for the leakage discussion (the review text is co-authored with the recommend tick).
"""
from __future__ import annotations

import json
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from . import config as C
from . import inference as I
from .schema import BatchInput, Prediction, ReviewInput

_SAMPLES_PATH = Path(__file__).resolve().parent / "samples.json"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    I.get_pipeline()            # fail fast if the artifact is missing
    I._explainer()             # warm the linear-SHAP reference
    yield


app = FastAPI(
    title="Sephora customer-behaviour — product-recommendation prediction",
    version="2.0.0",
    description="Predicts whether a skincare reviewer recommends the product "
                "(is_recommended) from their skin profile + the product + the review "
                "text. Model: %s (%s)." % (C.CHOSEN_MODEL, C.REPRESENTATION),
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)


@app.post("/predict", response_model=Prediction, summary="Score one review")
def predict(review: ReviewInput):
    try:
        return I.predict_one(review.model_dump())
    except Exception as exc:                       # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"prediction failed: {exc}") from exc


@app.post("/predict/batch", summary="Score many reviews")
def predict_batch(payload: BatchInput):
    try:
        return {"predictions": I.predict_batch([r.model_dump() for r in payload.reviews])}
    except Exception as exc:                       # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"prediction failed: {exc}") from exc


@app.get("/questions", summary="Form metadata for the web / mobile clients")
def questions():
    return {
        "fields": C.FORM_FIELDS,
        "sections": C.FORM_SECTIONS,
        "fixed_inputs": C.FIXED_INPUTS,
        "skin_types": C.SKIN_TYPES,
        "skin_tones": C.SKIN_TONES,
        "eye_colors": C.EYE_COLORS,
        "hair_colors": C.HAIR_COLORS,
        "categories": C.CATEGORIES,
        "brands": C.BRANDS,
        "target": C.TARGET_DESC,
    }


@app.get("/samples", summary="Typical-value defaults + real example reviews")
def samples():
    if not _SAMPLES_PATH.exists():
        raise HTTPException(status_code=503,
                            detail="samples.json missing — run  python api/make_samples.py")
    return json.loads(_SAMPLES_PATH.read_text(encoding="utf-8"))


@app.get("/model-info")
def model_info():
    return I.model_info()


@app.get("/healthz")
def healthz():
    try:
        I.get_pipeline()
        return {"status": "ok", "model": C.CHOSEN_MODEL}
    except Exception as exc:                       # noqa: BLE001
        raise HTTPException(status_code=503, detail=str(exc)) from exc
