import axios from "axios";
import type { HealthResponse, ListingInput, PredictionResponse } from "../types";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8001";

export const client = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
    "ngrok-skip-browser-warning": "true",
  },
});

export async function fetchHealth(): Promise<HealthResponse> {
  const { data } = await client.get<HealthResponse>("/healthz");
  return data;
}

export async function predictPrice(payload: ListingInput): Promise<PredictionResponse> {
  const { data } = await client.post<PredictionResponse>("/predict", payload);
  return data;
}
