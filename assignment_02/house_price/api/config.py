"""Configuration and filesystem paths for the house-price FastAPI service.

Runtime artifacts loaded:
    - model/model_pipeline.joblib : Fitted sklearn Pipeline (ColumnTransformer + RandomForestRegressor)
    - model/feature_names.joblib  : Exact 19 feature names expected by the pipeline
    - model/input_schema.json     : Human- and machine-readable schema contract
"""
from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "model"

MODEL_PIPELINE_PATH = MODEL_DIR / "model_pipeline.joblib"
FEATURE_NAMES_PATH = MODEL_DIR / "feature_names.joblib"
INPUT_SCHEMA_PATH = MODEL_DIR / "input_schema.json"

# Port assignment per course deployment plan (00_overview.md)
DEFAULT_PORT = int(os.environ.get("PORT", "8002"))

# Target price is in million VND (e.g. 2381.2 million VND = 2.38 billion VND)
PRICE_UNIT = "million VND"
PRICE_UNIT_MULTIPLIER = 1.0
