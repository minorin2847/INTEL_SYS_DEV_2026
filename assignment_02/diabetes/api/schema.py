"""Pydantic request/response models for the diabetes screening API.

The request mirrors the questionnaire: `Age` and `Sex` are required, every other
field is optional and may be sent as ``null`` for a "not sure" answer. `BMI` may be
supplied directly or left to be computed from `height_cm` + `weight_kg`.
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class QuestionnaireInput(BaseModel):
    # --- required identity anchors ---
    Age: int = Field(..., ge=1, le=13, description="5-year age band, 1=18-24 ... 13=80+")
    Sex: int = Field(..., ge=0, le=1, description="0=female, 1=male")

    # --- body ---
    BMI: Optional[float] = Field(None, description="kg/m^2; computed from height+weight if omitted")
    height_cm: Optional[float] = Field(None, ge=100, le=250)
    weight_kg: Optional[float] = Field(None, ge=20, le=400)

    # --- binary indicators (0/1), all optional ---
    HighBP: Optional[int] = Field(None, ge=0, le=1)
    HighChol: Optional[int] = Field(None, ge=0, le=1)
    CholCheck: Optional[int] = Field(None, ge=0, le=1)
    Smoker: Optional[int] = Field(None, ge=0, le=1)
    Stroke: Optional[int] = Field(None, ge=0, le=1)
    HeartDiseaseorAttack: Optional[int] = Field(None, ge=0, le=1)
    PhysActivity: Optional[int] = Field(None, ge=0, le=1)
    Fruits: Optional[int] = Field(None, ge=0, le=1)
    Veggies: Optional[int] = Field(None, ge=0, le=1)
    HvyAlcoholConsump: Optional[int] = Field(None, ge=0, le=1)
    AnyHealthcare: Optional[int] = Field(None, ge=0, le=1)
    NoDocbcCost: Optional[int] = Field(None, ge=0, le=1)
    DiffWalk: Optional[int] = Field(None, ge=0, le=1)

    # --- ordinal / count ---
    GenHlth: Optional[int] = Field(None, ge=1, le=5)
    MentHlth: Optional[int] = Field(None, ge=0, le=30)
    PhysHlth: Optional[int] = Field(None, ge=0, le=30)
    Education: Optional[int] = Field(None, ge=1, le=6)
    Income: Optional[int] = Field(None, ge=1, le=8)

    # --- client bookkeeping ---
    session_id: Optional[str] = Field(None, description="opaque client id for history grouping")

    model_config = {
        "json_schema_extra": {
            "example": {
                "Age": 9, "Sex": 1, "height_cm": 175, "weight_kg": 104,
                "HighBP": 1, "HighChol": 1, "CholCheck": 1, "Smoker": 1, "Stroke": 0,
                "HeartDiseaseorAttack": 0, "PhysActivity": 0, "Fruits": 0, "Veggies": 1,
                "HvyAlcoholConsump": 0, "AnyHealthcare": 1, "NoDocbcCost": 0,
                "DiffWalk": 1, "GenHlth": 4, "MentHlth": 10, "PhysHlth": 15,
                "Education": 4, "Income": 3, "session_id": "demo-1",
            }
        }
    }


class ThresholdConfig(BaseModel):
    moderate_cut: float = Field(..., ge=0.0, le=1.0)
    high_cut: float = Field(..., ge=0.0, le=1.0)


# Responses are returned as plain dicts (documented here for reference):
#
# PredictResponse = {
#   "probability": float, "band": "Low"|"Moderate"|"High",
#   "band_label": str, "thresholds": {"moderate_cut": float, "high_cut": float},
#   "uncertainty_band": [lo, hi] | null, "completeness": float,
#   "imputed_fields": [str], "warnings": [str],
#   "explain": {...} | null, "similar": {...} | null, "whatif": {...} | null
# }
