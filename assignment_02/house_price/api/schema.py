"""Pydantic request and response models for the house price prediction service.

Mirrors the 19 features in model/feature_names.joblib and model/input_schema.json.
Only `Area` is required; all other features are optional and are imputed by the
pre-fitted ColumnTransformer (no data leakage at inference).
"""
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class ListingInput(BaseModel):
    # Required core feature
    Area: float = Field(
        ...,
        gt=0,
        le=10_000,
        description="Usable property area in square meters (required, 1-10000 m²)",
    )

    # Optional numerical dimensions and attributes
    Width: Optional[float] = Field(None, gt=0, le=500, description="Frontage width in meters")
    Length: Optional[float] = Field(None, gt=0, le=1_000, description="Lot depth in meters")
    Bedrooms: Optional[float] = Field(None, ge=0, le=50, description="Number of bedrooms")
    Bathrooms: Optional[float] = Field(None, ge=0, le=50, description="Number of bathrooms")
    Floors: Optional[float] = Field(None, ge=0, le=100, description="Number of floors")
    AlleyWidth: Optional[float] = Field(None, ge=0, le=100, alias="Alley Width", description="Alley width in meters")
    AgentListingCount: Optional[float] = Field(
        None, ge=0, le=10_000, alias="Agent Listing Count", description="Listing count of the posting agent"
    )

    # Optional categorical features (unknowns mapped to 'Unknown' bucket in pipeline)
    PropertyType: Optional[str] = Field(
        None, alias="Property Type", description="Property category (e.g., 'Nhà riêng', 'Căn hộ chung cư', 'Đất')"
    )
    Position: Optional[str] = Field(
        None, description="Property position (e.g., 'Đường chính', 'Trong hẻm')"
    )
    Direction: Optional[str] = Field(
        None, description="Compass direction (e.g., 'Đông', 'Tây', 'Nam', 'Bắc', 'Đông Nam')"
    )
    RoadType: Optional[str] = Field(
        None, alias="Road Type", description="Access road surface (e.g., 'Đường nhựa', 'Đường bê tông')"
    )
    Province: Optional[str] = Field(
        None, description="Province/City slug or name (e.g., 'tp-ho-chi-minh', 'ha-noi', 'an-giang')"
    )
    AgentRole: Optional[str] = Field(
        None, alias="Agent Role", description="Role of seller ('Chính chủ' or 'Môi giới')"
    )

    # Location specifics (parsed or free-form)
    ward: Optional[str] = Field(None, description="Ward name (e.g., 'Phường An Hòa')")
    district: Optional[str] = Field(None, description="District / City name (e.g., 'Rạch Giá', 'Quận 1')")

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "Area": 78.7,
                "Width": 4.0,
                "Length": 19.6,
                "Bedrooms": 3,
                "Bathrooms": 2,
                "Floors": 2,
                "Alley Width": 3.5,
                "Agent Listing Count": 1,
                "Property Type": "Nhà riêng",
                "Position": "Đường chính",
                "Direction": "Nam",
                "Road Type": "Đường nhựa",
                "Province": "an-giang",
                "Agent Role": "Chính chủ",
                "ward": "Phường An Hòa",
                "district": "Rạch Giá",
            }
        },
    }


class FeatureContribution(BaseModel):
    name: str = Field(..., description="Feature group or variable name")
    label: str = Field(..., description="Human-readable label for the feature")
    impact_million: float = Field(..., description="Estimated price contribution in million VND relative to baseline")
    direction: str = Field(..., description="'positive' (increases price) or 'negative' (decreases price)")
    importance_pct: float = Field(..., description="Relative feature importance percentage from tree ensemble")


class ModelMetadata(BaseModel):
    algorithm: str = Field(..., description="Algorithm name")
    n_estimators: int = Field(100, description="Number of ensemble trees")
    max_depth: int = Field(16, description="Max depth of decision trees")
    features_count: int = Field(18, description="Raw feature dimensions")
    transformed_features: int = Field(117, description="Transformed feature dimensions after OneHotEncoding")
    target_transform: str = Field("log1p(Price) -> expm1(y)", description="Target skewness transformation")
    zero_leakage: bool = Field(True, description="Strict Training != Inference adherence")


class PredictionOut(BaseModel):
    predicted_price: float = Field(..., description="Estimated listing price in million VND")
    price_per_m2: Optional[float] = Field(None, description="Estimated unit price in million VND/m²")
    formatted_price_billion: Optional[str] = Field(None, description="Formatted price in Vietnamese Tỷ VNĐ")
    currency: str = Field("million VND", description="Unit of currency")
    model_name: str = Field(..., description="Deployed machine learning model name")
    interpretation: Optional[str] = Field(None, description="Brief natural language interpretation of the prediction")
    feature_contributions: Optional[list[FeatureContribution]] = Field(
        None, description="SHAP-style feature contributions decomposing valuation"
    )
    model_metadata: Optional[ModelMetadata] = Field(
        None, description="Technical model specifications and pipeline parameters"
    )


class HealthOut(BaseModel):
    status: str = Field(..., description="'ok' when model is ready, 'model-not-loaded' otherwise")
    model_loaded: bool = Field(..., description="Boolean flag indicating if pipeline artifact is loaded")
    model_name: Optional[str] = Field(None, description="Name of loaded model algorithm")
    features_count: Optional[int] = Field(None, description="Number of expected features")
