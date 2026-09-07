import React from "react";
import type { HealthResponse } from "../types";

interface NavbarProps {
  health: HealthResponse | null;
  loading: boolean;
  onRefreshHealth: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ health, loading, onRefreshHealth }) => {
  const isHealthy = health?.model_loaded === true;

  return (
    <header className="app-header">
      <div className="inner">
        <div className="brand">
          REALVAL
        </div>

        <div className="nav">
          <button type="button" className="active">Predictor</button>
          <button type="button">Market Insights</button>

          <button
            type="button"
            onClick={onRefreshHealth}
            title="Click to refresh connection status"
            disabled={loading}
          >
            <span className={`status-dot ${isHealthy ? "ok" : ""}`} style={{ marginRight: '8px' }} />
            {loading
              ? "Connecting..."
              : isHealthy
              ? `API Active (${health?.model_name || "RandomForest"})`
              : "API Offline"}
          </button>
        </div>
      </div>
    </header>
  );
};
