export interface ListingInput {
  Area: number;
  Width?: number;
  Length?: number;
  Bedrooms?: number;
  Bathrooms?: number;
  Floors?: number;
  "Alley Width"?: number;
  "Agent Listing Count"?: number;
  "Property Type"?: string;
  Position?: string;
  Direction?: string;
  "Road Type"?: string;
  Province?: string;
  "Agent Role"?: string;
  ward?: string;
  district?: string;
}

export interface FeatureContribution {
  name: string;
  label: string;
  impact_million: number;
  direction: "positive" | "negative";
  importance_pct: number;
}

export interface ModelMetadata {
  algorithm: string;
  n_estimators: number;
  max_depth: number;
  features_count: number;
  transformed_features: number;
  target_transform: string;
  zero_leakage: boolean;
}

export interface PredictionResponse {
  predicted_price: number;
  price_per_m2: number | null;
  formatted_price_billion: string;
  currency: string;
  model_name: string;
  interpretation: string;
  feature_contributions?: FeatureContribution[];
  model_metadata?: ModelMetadata;
}

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
  model_name: string | null;
  features_count?: number;
}

export interface Preset {
  id: string;
  name: string;
  description: string;
  data: ListingInput;
}
