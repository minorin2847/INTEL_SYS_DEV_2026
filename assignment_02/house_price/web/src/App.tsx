import React, { useState, useEffect } from "react";
import { Navbar } from "./components/Navbar";
import { PredictionForm } from "./components/PredictionForm";
import { ResultCard } from "./components/ResultCard";
import { ErrorBanner } from "./components/ErrorBanner";
import { fetchHealth, predictPrice } from "./services/api";
import type { ListingInput, PredictionResponse, HealthResponse } from "./types";

const DEFAULT_FORM_DATA: ListingInput = {
  Area: 78.7,
  Width: 4.0,
  Length: 19.6,
  Bedrooms: 3,
  Bathrooms: 2,
  Floors: 2,
  "Alley Width": 3.5,
  "Agent Listing Count": 1,
  "Property Type": "Nhà riêng",
  Position: "Đường chính",
  Direction: "Nam",
  "Road Type": "Đường nhựa",
  Province: "an-giang",
  "Agent Role": "Chính chủ",
  ward: "Phường An Hòa",
  district: "Rạch Giá",
};

export const App: React.FC = () => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [healthLoading, setHealthLoading] = useState(false);
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [formData, setFormData] = useState<ListingInput>(DEFAULT_FORM_DATA);
  const [submitting, setSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [currentStep, setCurrentStep] = useState(1);

  const checkServerHealth = async () => {
    setHealthLoading(true);
    try {
      const res = await fetchHealth();
      setHealth(res);
    } catch {
      setHealth(null);
    } finally {
      setHealthLoading(false);
    }
  };

  useEffect(() => {
    checkServerHealth();
  }, []);

  const handlePredict = async (dataToPredict: ListingInput) => {
    setSubmitting(true);
    setErrorMessage("");

    try {
      const res = await predictPrice(dataToPredict);
      setPrediction(res);
      setCurrentStep(5);
    } catch (err: any) {
      if (err.response) {
        if (err.response.status === 422) {
          const detail = err.response.data?.detail;
          if (Array.isArray(detail)) {
            const msgs = detail.map((d: any) => `${d.loc?.join(".")}: ${d.msg}`).join("; ");
            setErrorMessage(`Validation error: ${msgs}`);
          } else {
            setErrorMessage(`Validation error: ${JSON.stringify(detail)}`);
          }
        } else if (err.response.status === 503) {
          setErrorMessage("Model pipeline not loaded on server. Please verify model_pipeline.joblib.");
        } else {
          setErrorMessage(`Server error (${err.response.status}): ${err.response.data?.detail || "Unknown error"}`);
        }
      } else if (err.request) {
        setErrorMessage("Cannot connect to API server at http://localhost:8001. Please ensure the backend is running.");
      } else {
        setErrorMessage(`Error: ${err.message}`);
      }
    } finally {
      setSubmitting(false);
    }
  };

  const handleReset = () => {
    setPrediction(null);
    setFormData(DEFAULT_FORM_DATA);
    setErrorMessage("");
    setCurrentStep(1);
  };

  return (
    <>
      <Navbar
        health={health}
        loading={healthLoading}
        onRefreshHealth={checkServerHealth}
      />

      <div className="app-viewport">
        <ErrorBanner
          message={errorMessage}
          onDismiss={() => setErrorMessage("")}
        />

        {currentStep <= 4 ? (
          <PredictionForm
            formData={formData}
            onFormDataChange={setFormData}
            onSubmit={handlePredict}
            loading={submitting}
            onReset={handleReset}
            currentStep={currentStep}
            onStepChange={setCurrentStep}
          />
        ) : (
          <ResultCard
            result={prediction}
            input={formData}
            onReset={handleReset}
          />
        )}
      </div>
    </>
  );
};

export default App;
