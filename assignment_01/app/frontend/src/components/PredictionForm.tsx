import React, { useState } from 'react';
import { Loader2, SendHorizontal } from 'lucide-react';

interface PredictionFormProps {
  onSubmit: (data: Record<string, number>) => void;
  loading: boolean;
}

const defaultValues = {
  Pregnancies: 6,
  Glucose: 148,
  BloodPressure: 72,
  SkinThickness: 35,
  Insulin: 0,
  BMI: 33.6,
  DiabetesPedigreeFunction: 0.627,
  Age: 50,
};

export const PredictionForm: React.FC<PredictionFormProps> = ({ onSubmit, loading }) => {
  const [formData, setFormData] = useState<Record<string, number>>(defaultValues);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({ ...prev, [e.target.name]: parseFloat(e.target.value) || 0 }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="glass-panel h-full p-5 sm:p-6">
      <div className="mb-5">
        <p className="text-xs font-semibold uppercase tracking-wide text-[var(--app-primary)]">Input</p>
        <h2 className="mt-1 text-xl font-bold text-[var(--app-text)]">Patient Features</h2>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {Object.entries(defaultValues).map(([key]) => (
            <div key={key} className="flex flex-col gap-1">
              <label htmlFor={key} className="text-sm muted-text font-medium">
                {key.replace(/([A-Z])/g, ' $1').trim()}
              </label>
              <input
                type="number"
                step="any"
                id={key}
                name={key}
                value={formData[key]}
                onChange={handleChange}
                className="surface-control rounded-lg px-3 py-2.5 text-sm font-semibold transition-all"
                required
              />
            </div>
          ))}
        </div>

        <button
          type="submit"
          disabled={loading}
          className="primary-gradient flex w-full items-center justify-center gap-2 rounded-lg px-6 py-3 font-bold text-white shadow-lg shadow-primary-500/25 transition-all hover:-translate-y-0.5 active:translate-y-0 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <SendHorizontal className="w-5 h-5" />}
          {loading ? 'Analyzing...' : 'Predict Outcome'}
        </button>
      </form>
    </div>
  );
};
