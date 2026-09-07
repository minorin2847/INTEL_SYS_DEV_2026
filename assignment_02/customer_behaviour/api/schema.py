"""Pydantic request / response models for the customer-behaviour API (Sephora)."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ReviewInput(BaseModel):
    """One review, matching the notebook's persisted ``raw_input_fields`` (§22).

    Only ``review_text`` and ``price_usd`` are effectively required; every other
    field is optional. Missing numerics are median-imputed inside the pipeline;
    missing categoricals fall back to a ``__na__`` one-hot level.
    """
    review_text: str = Field(..., min_length=1, description="Body of the review")
    price_usd: float = Field(..., ge=0, description="Product retail price, USD")

    review_title: Optional[str] = Field(None, description="Short review headline")
    skin_type: Optional[str] = Field(None, examples=["combination"])
    skin_tone: Optional[str] = Field(None, examples=["light"])
    eye_color: Optional[str] = Field(None, examples=["brown"])
    hair_color: Optional[str] = Field(None, examples=["brown"])
    secondary_category: Optional[str] = Field(None, examples=["Moisturizers"])
    brand_name: Optional[str] = Field(None, examples=["Skinfix"])
    loves_count: Optional[float] = Field(None, ge=0)
    reviews: Optional[float] = Field(None, ge=0, description="Product's total review count")
    ingredients: Optional[str] = Field(None, description="Raw ingredients list (comma-separated)")
    highlights: Optional[str] = Field(None, description="Raw product highlights (comma-separated)")
    limited_edition: Optional[int] = Field(None, ge=0, le=1)
    new: Optional[int] = Field(None, ge=0, le=1)
    online_only: Optional[int] = Field(None, ge=0, le=1)
    sephora_exclusive: Optional[int] = Field(None, ge=0, le=1)
    total_feedback_count: Optional[float] = Field(None, ge=0)
    total_pos_feedback_count: Optional[float] = Field(None, ge=0)
    total_neg_feedback_count: Optional[float] = Field(None, ge=0)
    submission_time: Optional[str] = Field(None, description="ISO date the review was posted")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "skin_type": "oily", "skin_tone": "light", "eye_color": "brown",
                "hair_color": "brown", "secondary_category": "Moisturizers",
                "brand_name": "Skinfix", "price_usd": 32.0, "loves_count": 21000,
                "reviews": 1800, "submission_time": "2023-02-10",
                "review_title": "Not for oily skin",
                "review_text": "Broke me out within a week and felt greasy all day. "
                               "Smells strongly of perfume. Wanted to love it but returned it.",
            }]
        }
    }


class BatchInput(BaseModel):
    reviews: list[ReviewInput]


class Prediction(BaseModel):
    prediction: str                       # "recommend" | "not recommend"
    confidence: float
    p_recommend: float
    threshold: float
    review_terms: Optional[dict] = None   # {"toward": [...], "against": [...]}
    signals: dict
    contributions: Optional[dict] = None  # linear-SHAP breakdown (None if not linear)
    model: str
    representation: str
