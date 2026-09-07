import React, { useState } from "react";
import type { ListingInput } from "../types";

interface PredictionFormProps {
  formData: ListingInput;
  onFormDataChange: React.Dispatch<React.SetStateAction<ListingInput>>;
  onSubmit: (data: ListingInput) => void;
  loading: boolean;
  onReset: () => void;
  currentStep: number;
  onStepChange: (step: number) => void;
}

const TOP_PROVINCES = [
  { slug: "an-giang", label: "An Giang" },
  { slug: "tp-ho-chi-minh", label: "Ho Chi Minh City" },
  { slug: "ha-noi", label: "Hanoi" },
  { slug: "da-nang", label: "Da Nang" },
  { slug: "binh-duong", label: "Binh Duong" },
  { slug: "dong-nai", label: "Dong Nai" },
  { slug: "can-tho", label: "Can Tho" },
  { slug: "hai-phong", label: "Hai Phong" },
  { slug: "khanh-hoa", label: "Khanh Hoa" },
  { slug: "lam-dong", label: "Lam Dong" },
  { slug: "ba-ria-vung-tau", label: "Ba Ria - Vung Tau" },
  { slug: "long-an", label: "Long An" },
];

const PROPERTY_TYPE_CARDS = [
  { value: "Nhà riêng", title: "Townhouse", desc: "Standalone residential home" },
  { value: "Căn hộ chung cư", title: "Apartment", desc: "Condo / High-rise unit" },
  { value: "Đất", title: "Residential Land", desc: "Plot with building rights" },
  { value: "Nhà mặt phố", title: "Street-Front", desc: "Commercial street access" },
  { value: "Biệt thự", title: "Villa / Estate", desc: "Luxury detached residence" },
];

const POSITION_CARDS = [
  { value: "Đường chính", title: "Main Street", desc: "Direct street front" },
  { value: "Trong hẻm", title: "In Alley", desc: "Quiet residential lane" },
  { value: "Mặt tiền", title: "Corner Frontage", desc: "High visibility corner" },
];

const ROAD_TYPE_CARDS = [
  { value: "Đường nhựa", title: "Asphalt Road", desc: "Smooth paved road" },
  { value: "Đường bê tông", title: "Concrete Road", desc: "Paved concrete alley" },
  { value: "Đường đất", title: "Dirt Road", desc: "Unpaved access" },
];

const DIRECTION_CARDS = [
  { value: "Nam", label: "South" },
  { value: "Đông Nam", label: "Southeast" },
  { value: "Đông", label: "East" },
  { value: "Bắc", label: "North" },
  { value: "Tây", label: "West" },
  { value: "Tây Nam", label: "Southwest" },
  { value: "Tây Bắc", label: "Northwest" },
  { value: "Đông Bắc", label: "Northeast" },
];

const AREA_QUICK_CARDS = [
  { area: 45, label: "Compact", sub: "45 m²" },
  { area: 78.7, label: "Townhouse", sub: "78.7 m²" },
  { area: 120, label: "Spacious", sub: "120 m²" },
  { area: 250, label: "Estate", sub: "250 m²" },
];

const LAYOUT_PRESET_CARDS = [
  { beds: 1, baths: 1, floors: 1, label: "1 Bed Studio" },
  { beds: 2, baths: 2, floors: 1, label: "2 Bed Standard" },
  { beds: 3, baths: 2, floors: 2, label: "3 Bed Family" },
  { beds: 4, baths: 3, floors: 3, label: "4+ Bed Villa" },
];

export const PredictionForm: React.FC<PredictionFormProps> = ({
  formData,
  onFormDataChange,
  onSubmit,
  loading,
  onReset,
  currentStep,
  onStepChange,
}) => {
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target;
    

    if (type === "number") {
      const parsed = value === "" ? undefined : parseFloat(value);
      onFormDataChange((prev) => ({ ...prev, [name]: parsed }));
    } else {
      onFormDataChange((prev) => ({ ...prev, [name]: value === "" ? undefined : value }));
    }
  };

  const updateCounter = (field: "Bedrooms" | "Bathrooms" | "Floors", delta: number) => {
    
    onFormDataChange((prev) => {
      const current = prev[field] ?? 1;
      const next = Math.max(1, Math.min(20, current + delta));
      return { ...prev, [field]: next };
    });
  };

  const handleNext = () => {
    if (currentStep === 1) {
      if (!formData.Area || formData.Area <= 0) {
        setValidationError("Please specify a valid usable area (> 0 m²).");
        return;
      }
    }
    setValidationError(null);
    if (currentStep < 4) {
      onStepChange(currentStep + 1);
    } else {
      onSubmit(formData);
    }
  };

  const handleBack = () => {
    setValidationError(null);
    if (currentStep > 1) {
      onStepChange(currentStep - 1);
    }
  };

  const currentArea = formData.Area ?? 78.7;
  const sliderArea = Math.min(500, Math.max(15, currentArea));

  const STEP_TITLES: Record<number, { title: string; desc: string }> = {
    1: { title: "Land Dimensions & Area", desc: "Specify usable floor area and lot boundaries" },
    2: { title: "Living Space & Architecture", desc: "Select room configuration and structural floors" },
    3: { title: "Location & Street Access", desc: "Select administrative district and plot position" },
    4: { title: "Property Attributes & Road", desc: "Choose property classification, road surface, and orientation" },
  };

  const sections = ["Dimensions", "Architecture", "Location", "Attributes"];

  return (
    <div className="wiz-split">
      <aside className="wiz-sidebar">
        <div className="wiz-branding">
          <h1>Real Estate Valuation</h1>
          <span>Vietnam Real Estate Market</span>
        </div>
        <ol className="stepper vert" aria-label="Progress">
          {sections.map((title, i) => {
            const stepNum = i + 1;
            return (
              <li
                key={title}
                className={`stepper__item${stepNum === currentStep ? ' is-active' : stepNum < currentStep ? ' is-done' : ''}`}
              >
                <button
                  type="button"
                  className="stepper__dot"
                  disabled={stepNum > currentStep}
                  onClick={() => stepNum < currentStep && onStepChange(stepNum)}
                >
                  {stepNum < currentStep ? '✓' : stepNum}
                </button>
                <span className="stepper__label">{title}</span>
              </li>
            );
          })}
        </ol>
      </aside>

      <div className="wiz-content">
        <header className="wiz-hdr">
          <div className="wiz-hdr__right">
            <button type="button" onClick={onReset} className="btn btn--ghost" disabled={loading}>
              Reset All
            </button>
          </div>
        </header>

        <main className="wiz-body">
        <div className="wiz-step-hdr">
          <p className="wiz-step-badge">Step {currentStep} of 4</p>
          <h2 className="wiz-step-title">{STEP_TITLES[currentStep]?.title}</h2>
          <p className="wiz-step-sub">{STEP_TITLES[currentStep]?.desc}</p>
        </div>

        {validationError && (
          <div className="notice err" role="alert">
            {validationError}
          </div>
        )}

        {currentStep === 1 && (
          <div className="card">
            <div className="card" style={{ background: 'var(--surface-solid)', marginBottom: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                <label style={{ fontWeight: 600 }}>Usable Area</label>
                <span><strong>{currentArea.toLocaleString("en-US")}</strong> m²</span>
              </div>

              <div className="slider-row">
                <input
                  id="Area"
                  type="range"
                  min="15"
                  max="500"
                  step="1"
                  value={sliderArea}
                  onChange={(e) => {
                    
                    onFormDataChange((prev) => ({ ...prev, Area: parseFloat(e.target.value) }));
                  }}
                />
                <div className="slider-readout" style={{ fontWeight: '600' }}>{sliderArea} m²</div>
              </div>
            </div>

            <div className="section-label">Choose Common Area Benchmark</div>
            <div className="option-cards-grid-4">
              {AREA_QUICK_CARDS.map((ac) => (
                <button
                  key={ac.area}
                  type="button"
                  className={`choice-card ${formData.Area === ac.area ? "selected" : ""}`}
                  onClick={() => {
                    
                    onFormDataChange((prev) => ({ ...prev, Area: ac.area }));
                  }}
                >
                  <span className="card-opt-title">{ac.label}</span>
                  <span className="card-opt-desc">{ac.sub}</span>
                </button>
              ))}
            </div>

            <div className="grid-2">
              <div className="field">
                <label htmlFor="Width">Frontage Width (m)</label>
                <input
                  id="Width"
                  name="Width"
                  type="number"
                  step="0.1"
                  min="0.5"
                  max="500"
                  value={formData.Width ?? ""}
                  onChange={handleChange}
                  placeholder="e.g. 4.0"
                />
              </div>

              <div className="field">
                <label htmlFor="Length">Lot Depth (m)</label>
                <input
                  id="Length"
                  name="Length"
                  type="number"
                  step="0.1"
                  min="1"
                  max="1000"
                  value={formData.Length ?? ""}
                  onChange={handleChange}
                  placeholder="e.g. 19.6"
                />
              </div>
            </div>

            <div className="field">
              <label htmlFor="Alley Width">Alley Access Width (m)</label>
              <input
                id="Alley Width"
                name="Alley Width"
                type="number"
                step="0.1"
                min="0"
                max="50"
                value={formData["Alley Width"] ?? ""}
                onChange={handleChange}
                placeholder="e.g. 3.5 (leave blank if frontage is on main road)"
              />
            </div>
          </div>
        )}

        {currentStep === 2 && (
          <div className="card">
            <div className="section-label">Choose Living Layout Architecture</div>
            <div className="option-cards-grid-4">
              {LAYOUT_PRESET_CARDS.map((lp) => {
                const isSelected =
                  formData.Bedrooms === lp.beds &&
                  formData.Bathrooms === lp.baths &&
                  formData.Floors === lp.floors;
                return (
                  <button
                    key={lp.label}
                    type="button"
                    className={`choice-card ${isSelected ? "selected" : ""}`}
                    onClick={() => {
                      
                      onFormDataChange((prev) => ({
                        ...prev,
                        Bedrooms: lp.beds,
                        Bathrooms: lp.baths,
                        Floors: lp.floors,
                      }));
                    }}
                  >
                    <span className="card-opt-title">{lp.label}</span>
                    <span className="card-opt-desc">
                      {lp.beds}B / {lp.baths}BA · {lp.floors}F
                    </span>
                  </button>
                );
              })}
            </div>

            <div className="steppers-grid">
              <div className="stepper-card">
                <span className="stepper-label">Bedrooms</span>
                <div className="stepper-control">
                  <button type="button" className="stepper-btn" onClick={() => updateCounter("Bedrooms", -1)}>-</button>
                  <span className="stepper-val">{formData.Bedrooms ?? 1}</span>
                  <button type="button" className="stepper-btn" onClick={() => updateCounter("Bedrooms", 1)}>+</button>
                </div>
              </div>

              <div className="stepper-card">
                <span className="stepper-label">Bathrooms</span>
                <div className="stepper-control">
                  <button type="button" className="stepper-btn" onClick={() => updateCounter("Bathrooms", -1)}>-</button>
                  <span className="stepper-val">{formData.Bathrooms ?? 1}</span>
                  <button type="button" className="stepper-btn" onClick={() => updateCounter("Bathrooms", 1)}>+</button>
                </div>
              </div>

              <div className="stepper-card">
                <span className="stepper-label">Total Floors</span>
                <div className="stepper-control">
                  <button type="button" className="stepper-btn" onClick={() => updateCounter("Floors", -1)}>-</button>
                  <span className="stepper-val">{formData.Floors ?? 1}</span>
                  <button type="button" className="stepper-btn" onClick={() => updateCounter("Floors", 1)}>+</button>
                </div>
              </div>
            </div>
          </div>
        )}

        {currentStep === 3 && (
          <div className="card">
            <div className="section-label">Choose Street Access Position</div>
            <div className="option-cards-grid-3">
              {POSITION_CARDS.map((pos) => (
                <button
                  key={pos.value}
                  type="button"
                  className={`choice-card ${formData.Position === pos.value ? "selected" : ""}`}
                  onClick={() => {
                    
                    onFormDataChange((prev) => ({ ...prev, Position: pos.value }));
                  }}
                >
                  <span className="card-opt-title">{pos.title}</span>
                  <span className="card-opt-desc">{pos.desc}</span>
                </button>
              ))}
            </div>

            <div className="grid-2">
              <div className="field">
                <label htmlFor="Province">Province / City</label>
                <select
                  id="Province"
                  name="Province"
                  value={formData.Province ?? ""}
                  onChange={handleChange}
                >
                  {TOP_PROVINCES.map((p) => (
                    <option key={p.slug} value={p.slug}>{p.label}</option>
                  ))}
                </select>
              </div>

              <div className="field">
                <label htmlFor="district">District / County</label>
                <input
                  id="district"
                  name="district"
                  type="text"
                  value={formData.district ?? ""}
                  onChange={handleChange}
                  placeholder="e.g. Rach Gia, District 7"
                />
              </div>
            </div>

            <div className="field">
              <label htmlFor="ward">Ward / Commune</label>
              <input
                id="ward"
                name="ward"
                type="text"
                value={formData.ward ?? ""}
                onChange={handleChange}
                placeholder="e.g. An Hoa Ward"
              />
            </div>
          </div>
        )}

        {currentStep === 4 && (
          <div className="card">
            <div className="section-label">Choose Property Classification</div>
            <div className="option-cards-grid-3">
              {PROPERTY_TYPE_CARDS.map((pt) => (
                <button
                  key={pt.value}
                  type="button"
                  className={`choice-card ${formData["Property Type"] === pt.value ? "selected" : ""}`}
                  onClick={() => {
                    
                    onFormDataChange((prev) => ({ ...prev, "Property Type": pt.value }));
                  }}
                >
                  <span className="card-opt-title">{pt.title}</span>
                  <span className="card-opt-desc">{pt.desc}</span>
                </button>
              ))}
            </div>

            <div className="section-label">Choose Road Surface Access</div>
            <div className="option-cards-grid-3">
              {ROAD_TYPE_CARDS.map((rt) => (
                <button
                  key={rt.value}
                  type="button"
                  className={`choice-card ${formData["Road Type"] === rt.value ? "selected" : ""}`}
                  onClick={() => {
                    
                    onFormDataChange((prev) => ({ ...prev, "Road Type": rt.value }));
                  }}
                >
                  <span className="card-opt-title">{rt.title}</span>
                  <span className="card-opt-desc">{rt.desc}</span>
                </button>
              ))}
            </div>

            <div className="section-label">Compass Direction</div>
            <div className="option-cards-grid-4">
              {DIRECTION_CARDS.map((d) => (
                <button
                  key={d.value}
                  type="button"
                  className={`choice-card-sm ${formData.Direction === d.value ? "selected" : ""}`}
                  onClick={() => {
                    
                    onFormDataChange((prev) => ({ ...prev, Direction: d.value }));
                  }}
                >
                  {d.label}
                </button>
              ))}
            </div>

            <div className="field">
              <label htmlFor="Agent Role">Listed By</label>
              <select
                id="Agent Role"
                name="Agent Role"
                value={formData["Agent Role"] ?? "Chính chủ"}
                onChange={handleChange}
              >
                <option value="Chính chủ">Direct Owner (Chính chủ)</option>
                <option value="Môi giới">Real Estate Agent (Môi giới)</option>
              </select>
            </div>
          </div>
        )}
      </main>

      <footer className="wiz-foot">
        <div className="wiz-foot__container">
          <button type="button" className="btn btn--ghost" disabled={currentStep === 1 || loading} onClick={handleBack}>
            ← Back
          </button>
          <button
            type="button"
            className="btn btn--primary"
            disabled={loading}
            onClick={handleNext}
          >
            {loading ? "Valuating…" : (currentStep < 4 ? 'Next →' : 'Predict Valuation')}
          </button>
        </div>
      </footer>
      </div>
    </div>
  );
};
