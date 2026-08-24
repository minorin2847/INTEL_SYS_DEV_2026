export type ModelSummary = {
  model: string;
  accuracy: number;
  f1: number;
};

export type PredictionResponse = {
  id: string;
  prediction: number;
  created_at: string;
  results: ModelSummary[];
};

export type ResultSummaryResponse = PredictionResponse;

export type HistoryItem = {
  id: string;
  prediction: number;
  created_at: string;
};

export type SHAPFeature = {
  feature: string;
  value: number;
};

export type DetailedModelResult = {
  model: string;
  prediction: number;
  confidence: number;
  accuracy: number;
  f1: number;
  shap_values: SHAPFeature[];
};

export const formatModelName = (name: string) =>
  name.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
