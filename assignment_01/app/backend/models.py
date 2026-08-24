from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class PredictionRequest(BaseModel):
    Pregnancies: float
    Glucose: float
    BloodPressure: float
    SkinThickness: float
    Insulin: float
    BMI: float
    DiabetesPedigreeFunction: float
    Age: float

class ModelResultSummary(BaseModel):
    model: str
    accuracy: float
    f1: float

class PredictionResponse(BaseModel):
    id: str
    prediction: int
    created_at: str
    results: List[ModelResultSummary]

class ResultSummaryResponse(BaseModel):
    id: str
    prediction: int
    created_at: str
    results: List[ModelResultSummary]

class HistoryItem(BaseModel):
    id: str
    prediction: int
    created_at: str

class SHAPFeature(BaseModel):
    feature: str
    value: float

class DetailedModelResult(BaseModel):
    model: str
    prediction: int
    confidence: float
    accuracy: float
    f1: float
    shap_values: List[SHAPFeature]
