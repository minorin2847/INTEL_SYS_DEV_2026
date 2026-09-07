import React from "react";
import type { PredictionResponse, ListingInput } from "../types";

interface ResultCardProps {
  result: PredictionResponse | null;
  input: ListingInput;
  onReset: () => void;
}

export const ResultCard: React.FC<ResultCardProps> = ({ result, input, onReset }) => {
  if (!result) return null;

  const formatMoney = (val: number) => val.toLocaleString("en-US");
  
  const factors = result.feature_contributions || [];
  const topFactors = [...factors].sort((a, b) => Math.abs(b.impact_million) - Math.abs(a.impact_million)).slice(0, 5);

  return (
    <div className="res-dashboard">
      <header className="res-nav">
        <div className="res-nav__left">
          <button type="button" className="btn btn--ghost" onClick={onReset}>
            ← Start New Valuation
          </button>
        </div>
        <div className="res-nav__right">
          <span className="pill">Model: <b>Random Forest Regressor</b></span>
        </div>
      </header>
      
      <main className="res-grid">
        <div className="res-col res-col--left">
          <div className="hero-card hero-card--good">
            <span className="hero-card__status-badge hero-card__status-badge--good">
              Estimated Value
            </span>
            <h2 className="hero-card__title" style={{fontSize: '48px', margin: '8px 0'}}>
              {formatMoney(result.predicted_price)} <span style={{fontSize: '20px', color: 'var(--muted)', fontWeight: 600}}>million VND</span>
            </h2>
            <p className="hero-card__subtitle">
              Based on historical listing data across Vietnam.
            </p>
          </div>

          <div className="card">
            <h4 className="card-section-title">Property Details</h4>
            <div className="grid-2">
              <div className="field">
                <span className="section-label">Area</span>
                <div style={{fontWeight: 600}}>{input.Area} m²</div>
              </div>
              <div className="field">
                <span className="section-label">Location</span>
                <div style={{fontWeight: 600}}>{input.Province || "N/A"}</div>
              </div>
              <div className="field">
                <span className="section-label">Architecture</span>
                <div style={{fontWeight: 600}}>{input.Bedrooms}B · {input.Bathrooms}ba · {input.Floors}F</div>
              </div>
              <div className="field">
                <span className="section-label">Type</span>
                <div style={{fontWeight: 600}}>{input["Property Type"] || "N/A"}</div>
              </div>
            </div>
          </div>
          
          <div className="notice info">
             This valuation identifies general market trends but cannot account for interior finishing quality or seller urgency. Use this as a baseline negotiation anchor.
          </div>
        </div>
        
        <div className="res-col res-col--right">
            <div className="card">
              <h4 className="card-section-title">Key Price Drivers (SHAP)</h4>
              <p className="card-hint">Features that most strongly influenced the final price.</p>
              
              <div className="shap-box">
                <div className="shap-rows">
                  {topFactors.map((f, i) => (
                    <div key={i} className="shap-row">
                      <div className="shap-row__label">
                        <span className="shap-tag shap-tag--tab">{f.name}</span>
                      </div>
                      <div className="shap-row__track">
                        <div 
                          className={`shap-bar ${f.impact_million >= 0 ? 'shap-bar--pos' : 'shap-bar--neg'}`}
                          style={{
                            width: `${Math.min(100, Math.abs(f.impact_million) / 100 * 100)}%`,
                            right: f.impact_million < 0 ? 0 : 'auto',
                            left: f.impact_million >= 0 ? 0 : 'auto'
                          }}
                        />
                      </div>
                      <div className={`shap-row__val ${f.impact_million >= 0 ? 'text-good' : 'text-bad'}`}>
                        {f.impact_million >= 0 ? '+' : ''}{f.impact_million.toFixed(1)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
        </div>
      </main>
    </div>
  );
};
