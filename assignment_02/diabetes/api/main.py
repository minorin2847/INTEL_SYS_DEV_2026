"""FastAPI service for the diabetes screening application.

    Raw questionnaire  ->  validation + BMI handling  ->  engineer()  ->  fitted
    pipeline (imputer + scaler + random forest)  ->  probability  ->  band

plus optional explanation (SHAP), similar cases (RF proximity), what-if /
counterfactual, monitoring, and an operator threshold dashboard.

Run:  uvicorn api.main:app --reload --port 8000    (from the diabetes/ directory)
Docs: http://localhost:8000/docs
"""
from __future__ import annotations

from typing import Optional

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from . import config as C
from . import dashboard as D
from . import explain as E
from . import inference as I
from . import monitoring as M
from . import similarity as S
from . import validate as V
from . import whatif as W
from .schema import QuestionnaireInput, ThresholdConfig

app = FastAPI(
    title="Diabetes Screening API",
    version="1.0.0",
    description="Assignment 02 · Application 1 — questionnaire → risk band, with "
                "explanation, similar cases, what-if analysis and an operator dashboard.",
)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)


@app.on_event("startup")
def _warm() -> None:
    I.get_pipeline()          # load the model once at startup


# --------------------------------------------------------------------- core route
def _run_predict(inp: QuestionnaireInput, include: set[str], log: bool = True) -> dict:
    payload = inp.model_dump()
    prep = V.prepare(payload)
    feat = prep["features"]

    p = I.predict_proba(feat)
    b, b_label = I.band(p)
    thr = I.load_thresholds()

    result = {
        "probability": round(p, 4),
        "band": b,
        "band_label": b_label,
        "thresholds": thr,
        "uncertainty_band": I.uncertainty_band(feat, prep["imputed_fields"]),
        "completeness": prep["completeness"],
        "imputed_fields": prep["imputed_fields"],
        "bmi_source": prep["bmi_source"],
        "warnings": prep["warnings"],
    }
    if "explain" in include:
        try:
            result["explain"] = E.explain(feat)
        except Exception as exc:                       # SHAP is optional
            result["explain"] = {"available": False, "reason": str(exc)}
    if "similar" in include:
        result["similar"] = S.similar(feat)
    if "whatif" in include:
        result["whatif"] = W.whatif(feat)
    if "counterfactual" in include:
        result["counterfactual"] = W.counterfactual(feat)

    if log:
        M.log_screening(payload.get("session_id"), feat, result)
    return result


@app.post("/predict", summary="Screen one respondent")
def predict(
    inp: QuestionnaireInput,
    include: str = Query("", description="comma list: explain,similar,whatif,counterfactual"),
    log: bool = Query(True, description="set false for what-if probes that should not be recorded"),
):
    want = {s.strip() for s in include.split(",") if s.strip()}
    return _run_predict(inp, want, log=log)


@app.post("/explain")
def explain_route(inp: QuestionnaireInput):
    feat = V.prepare(inp.model_dump())["features"]
    try:
        return E.explain(feat)
    except Exception as exc:
        raise HTTPException(503, f"explainer unavailable: {exc}")


@app.post("/similar")
def similar_route(inp: QuestionnaireInput):
    return S.similar(V.prepare(inp.model_dump())["features"])


@app.post("/whatif")
def whatif_route(inp: QuestionnaireInput):
    return W.whatif(V.prepare(inp.model_dump())["features"])


@app.post("/counterfactual")
def counterfactual_route(inp: QuestionnaireInput, target_band: str = Query("Moderate")):
    return W.counterfactual(V.prepare(inp.model_dump())["features"], target_band)


# ------------------------------------------------------------------- monitoring
@app.get("/history")
def history_route(session: str = Query(..., description="session_id used at predict time"),
                  limit: int = 50):
    return {"session": session, "screenings": M.history(session, limit)}


@app.get("/metrics")
def metrics_route():
    return M.metrics()


# --------------------------------------------------------------------- dashboard
@app.get("/threshold-curve")
def threshold_curve_route(split: str = Query("val", pattern="^(val|test)$"), grid: int = 49):
    return D.threshold_curve(split, grid)


@app.get("/threshold-recommend")
def threshold_recommend_route(objective: str = "recall", target: float = 0.90):
    return D.recommend(objective, target)


@app.get("/config")
def get_config_route():
    return D.get_config()


@app.post("/config/thresholds")
def set_thresholds_route(cfg: ThresholdConfig, x_admin_key: str = Header("")):
    if x_admin_key != C.ADMIN_KEY:
        raise HTTPException(401, "bad or missing X-Admin-Key")
    saved = I.save_thresholds(cfg.moderate_cut, cfg.high_cut, set_by="dashboard")
    return {"ok": True, **saved}


# ------------------------------------------------------------------------- meta
@app.get("/questions", summary="Questionnaire metadata for rendering the form")
def questions_route():
    return {"required": C.REQUIRED_FIELDS, "questions": C.QUESTIONS}


@app.get("/model-info")
def model_info_route():
    import json
    schema = json.loads(C.INPUT_SCHEMA_PATH.read_text())
    return {
        "chosen_model": schema.get("chosen_model"),
        "random_seed": schema.get("random_seed"),
        "sklearn_version": schema.get("sklearn_version"),
        "raw_features": C.RAW_FEATURES,
        "engineered_features": C.ENGINEERED_FEATURES,
        "thresholds": I.load_thresholds(),
        "features_available": {
            "explain_shap": _shap_ok(),
            "similar_cases": S.available(),
            "threshold_dashboard": D.available(),
        },
    }


@app.get("/healthz")
def healthz():
    return {"status": "ok", "model_loaded": I._PIPELINE is not None}


def _shap_ok() -> bool:
    try:
        import shap  # noqa: F401
        return True
    except Exception:
        return False
