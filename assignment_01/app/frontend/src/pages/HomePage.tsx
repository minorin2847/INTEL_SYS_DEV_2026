import { useEffect, useState } from 'react';
import { PredictionForm } from '../components/PredictionForm';
import { api } from '../lib/api';
import { navigate } from '../lib/router';
import type { HistoryItem, PredictionResponse } from '../types';
import { ChevronRight, Clock, History as HistoryIcon } from 'lucide-react';
import clsx from 'clsx';
import { motion } from 'framer-motion';

export function HomePage() {
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [historyLoading, setHistoryLoading] = useState(true);

  const loadHistory = () => {
    setHistoryLoading(true);
    api.get<HistoryItem[]>('/api/history')
      .then(res => setHistory(res.data))
      .catch(err => console.error('Failed to load history:', err))
      .finally(() => setHistoryLoading(false));
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handlePredict = async (data: Record<string, number>) => {
    setLoading(true);
    try {
      const response = await api.post<PredictionResponse>('/api/predict', data);
      navigate(`/result/${response.data.id}`);
    } catch (error) {
      console.error('Prediction failed:', error);
      alert('Prediction failed. Ensure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="relative z-10 grid w-full grid-cols-1 gap-5 lg:grid-cols-12 items-start">
      <section className="lg:col-span-5">
        <PredictionForm onSubmit={handlePredict} loading={loading} />
      </section>
      <section className="lg:col-span-7">
        <div className="results-stage flex h-full flex-col p-5 sm:p-6">
          <div className="mb-5 flex items-center justify-between gap-3">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-[var(--app-primary)]">Records</p>
              <h2 className="mt-1 flex items-center gap-2 text-xl font-bold text-[var(--app-text)]">
                <HistoryIcon className="w-5 h-5 text-[var(--app-accent)]" />
                Prediction History
              </h2>
            </div>
            <p className="text-sm muted-text">{history.length} total</p>
          </div>

          {historyLoading ? (
            <div className="flex flex-1 items-center justify-center py-12 text-sm muted-text">Loading history...</div>
          ) : history.length === 0 ? (
            <div className="empty-state flex-1">
              <div className="empty-icon">
                <Clock className="h-7 w-7" />
              </div>
              <div>
                <h2>No predictions yet</h2>
                <p>Submit the patient features to run the six models and start building history here.</p>
              </div>
            </div>
          ) : (
            <div className="flex-1 space-y-3 overflow-y-auto pr-1">
              {history.map((item, idx) => {
                const isDiabetic = item.prediction === 1;
                return (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.04 }}
                    key={item.id}
                  >
                    <button
                      onClick={() => navigate(`/result/${item.id}`)}
                      className="history-card w-full text-left flex items-center justify-between gap-3 group"
                    >
                      <div className="min-w-0">
                        <h3 className={clsx(
                          'truncate font-semibold',
                          isDiabetic ? 'text-[var(--app-danger)]' : 'text-[var(--app-success)]'
                        )}>
                          {isDiabetic ? 'Diabetic' : 'Non-Diabetic'} Patient
                        </h3>
                        <p className="mt-1 truncate text-xs muted-text">Patient ID: {item.id}</p>
                      </div>
                      <ChevronRight className="w-5 h-5 shrink-0 text-[var(--app-text-muted)] transition-transform group-hover:text-primary-500 group-hover:translate-x-1" />
                    </button>
                  </motion.div>
                );
              })}
            </div>
          )}
        </div>
      </section>
    </main>
  );
}
