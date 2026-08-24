import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X,
  Loader2,
  Target,
  Percent,
  Award,
  TrendingUp,
  TrendingDown,
  Activity,
  AlertCircle,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from 'recharts';
import clsx from 'clsx';
import { api } from '../lib/api';
import type { DetailedModelResult, SHAPFeature } from '../types';
import { formatModelName } from '../types';

interface ModelDetailsPanelProps {
  isOpen: boolean;
  onClose: () => void;
  model: string | null;
  resultId: string | null;
}

const CustomSHAPTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload as SHAPFeature;
    const isPositive = data.value > 0;
    return (
      <div className="rounded-xl border border-[var(--app-border)] bg-[var(--app-surface-solid)] p-3.5 text-xs shadow-2xl min-w-[210px] space-y-1.5">
        <div className="flex items-center justify-between border-b border-[var(--app-border)] pb-1.5">
          <span className="font-semibold text-[var(--app-text)]">{data.feature}</span>
          <span className={clsx(
            'rounded px-1.5 py-0.5 font-mono font-medium',
            isPositive ? 'bg-rose-500/15 text-rose-500' : 'bg-emerald-500/15 text-emerald-500'
          )}>
            {data.value > 0 ? `+${data.value.toFixed(4)}` : data.value.toFixed(4)}
          </span>
        </div>
        <p className="muted-text leading-relaxed">
          {isPositive ? (
            <span className="flex items-center gap-1 font-medium text-rose-500">
              <TrendingUp className="w-3.5 h-3.5" /> Pushes toward Diabetic
            </span>
          ) : (
            <span className="flex items-center gap-1 font-medium text-emerald-500">
              <TrendingDown className="w-3.5 h-3.5" /> Pushes toward Non-Diabetic
            </span>
          )}
        </p>
      </div>
    );
  }
  return null;
};

export const ModelDetailsPanel: React.FC<ModelDetailsPanelProps> = ({
  isOpen,
  onClose,
  model,
  resultId,
}) => {
  const [data, setData] = useState<DetailedModelResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && model && resultId) {
      setLoading(true);
      setError(null);
      api.get<DetailedModelResult>(`/api/result/${resultId}?model=${model}`)
        .then(res => {
          // Sorted by raw SHAP value descending: strongest "raises risk" (positive)
          // factors first, strongest "lowers risk" (negative) factors last.
          const sortedData = {
            ...res.data,
            shap_values: [...res.data.shap_values].sort((a, b) => b.value - a.value),
          };
          setData(sortedData);
        })
        .catch(err => {
          console.error(err);
          setError('Could not load the model details. Is the backend running?');
        })
        .finally(() => setLoading(false));
    }
  }, [isOpen, model, resultId]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 z-40 bg-slate-950/50 backdrop-blur-sm"
          />

          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 28, stiffness: 220 }}
            className="glass-panel fixed right-0 top-0 bottom-0 z-50 flex w-full max-w-2xl flex-col overflow-y-auto rounded-none sm:rounded-l-2xl"
            style={{ background: 'var(--app-surface-solid)' }}
          >
            <div className="sticky top-0 z-10 flex items-center justify-between gap-4 border-b border-[var(--app-border)] p-6" style={{ background: 'var(--app-surface-solid)' }}>
              <div className="flex min-w-0 items-center gap-3">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[var(--app-primary-soft)] text-[var(--app-primary)]">
                  <Activity className="w-5 h-5" />
                </div>
                <div className="min-w-0">
                  <h2 className="truncate text-xl font-bold text-[var(--app-text)]">
                    {data ? formatModelName(data.model) : 'Model Details'}
                  </h2>
                  <p className="mt-0.5 text-xs muted-text">Prediction breakdown &amp; SHAP feature attribution</p>
                </div>
              </div>

              <button
                onClick={onClose}
                className="theme-toggle shrink-0 rounded-xl p-2 transition-colors"
                aria-label="Close panel"
              >
                <X className="w-5 h-5 text-[var(--app-text-muted)]" />
              </button>
            </div>

            <div className="flex-1 space-y-6 p-6">
              {loading ? (
                <div className="flex h-96 flex-col items-center justify-center gap-3 text-[var(--app-primary)]">
                  <Loader2 className="w-8 h-8 animate-spin" />
                  <span className="text-sm muted-text">Computing SHAP values...</span>
                </div>
              ) : error ? (
                <div className="flex h-96 flex-col items-center justify-center rounded-2xl border p-6 text-center"
                     style={{ background: 'var(--app-danger-soft)', borderColor: 'var(--app-danger)' }}>
                  <AlertCircle className="mb-2 h-10 w-10" style={{ color: 'var(--app-danger)' }} />
                  <p className="text-sm font-medium" style={{ color: 'var(--app-danger)' }}>{error}</p>
                </div>
              ) : data ? (
                <>
                  {/* Stat cards */}
                  <div className="grid grid-cols-1 gap-3.5 sm:grid-cols-2 lg:grid-cols-4">
                    <div
                      className="rounded-2xl border p-4 shadow-md"
                      style={{
                        background: data.prediction === 1 ? 'var(--app-danger-soft)' : 'var(--app-success-soft)',
                        borderColor: data.prediction === 1 ? 'var(--app-danger)' : 'var(--app-success)',
                      }}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold muted-text">Prediction</span>
                        <Target className="w-4 h-4" style={{ color: data.prediction === 1 ? 'var(--app-danger)' : 'var(--app-success)' }} />
                      </div>
                      <div className="mt-3">
                        <span className="text-xl font-black tracking-tight" style={{ color: data.prediction === 1 ? 'var(--app-danger)' : 'var(--app-success)' }}>
                          {data.prediction === 1 ? 'Diabetic' : 'Non-Diabetic'}
                        </span>
                        <p className="mt-0.5 text-[11px] muted-text">
                          {data.prediction === 1 ? 'High-risk signal detected' : 'Low-risk profile'}
                        </p>
                      </div>
                    </div>

                    <div className="rounded-2xl border border-[var(--app-border)] p-4 shadow-md" style={{ background: 'var(--app-primary-soft)' }}>
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold muted-text">Confidence</span>
                        <Percent className="w-4 h-4 text-[var(--app-primary)]" />
                      </div>
                      <div className="mt-3">
                        <span className="text-xl font-black tracking-tight text-[var(--app-primary-strong)]">
                          {(data.confidence * 100).toFixed(1)}%
                        </span>
                        <p className="mt-0.5 text-[11px] muted-text">Class probability</p>
                      </div>
                    </div>

                    <div className="rounded-2xl border border-[var(--app-border)] p-4 shadow-md">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold muted-text">Accuracy</span>
                        <Award className="w-4 h-4 text-[var(--app-accent)]" />
                      </div>
                      <div className="mt-3">
                        <span className="text-xl font-black tracking-tight" style={{ color: 'var(--app-accent)' }}>
                          {(data.accuracy * 100).toFixed(1)}%
                        </span>
                        <p className="mt-0.5 text-[11px] muted-text">Held-out test set</p>
                      </div>
                    </div>

                    <div className="rounded-2xl border border-[var(--app-border)] p-4 shadow-md">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold muted-text">F1 Score</span>
                        <Award className="w-4 h-4 text-[var(--app-primary)]" />
                      </div>
                      <div className="mt-3">
                        <span className="text-xl font-black tracking-tight" style={{ color: 'var(--app-primary)' }}>
                          {data.f1.toFixed(3)}
                        </span>
                        <p className="mt-0.5 text-[11px] muted-text">Held-out test set</p>
                      </div>
                    </div>
                  </div>

                  {/* SHAP chart */}
                  <div className="glass-panel space-y-4 p-5">
                    <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[var(--app-border)] pb-3">
                      <div>
                        <h3 className="text-sm font-semibold text-[var(--app-text)]">Feature contribution</h3>
                        <p className="text-xs muted-text">SHAP values show how each feature moved the prediction</p>
                      </div>
                      <div className="flex items-center gap-3 text-xs">
                        <div className="flex items-center gap-1.5 text-rose-500">
                          <span className="h-2.5 w-2.5 rounded-full bg-rose-500" />
                          Raises risk
                        </div>
                        <div className="flex items-center gap-1.5 text-emerald-500">
                          <span className="h-2.5 w-2.5 rounded-full bg-emerald-500" />
                          Lowers risk
                        </div>
                      </div>
                    </div>

                    <div className="h-[340px] w-full pt-2">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={data.shap_values} layout="vertical" margin={{ top: 5, right: 25, left: 10, bottom: 5 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="var(--app-border)" horizontal={false} />
                          <XAxis type="number" stroke="var(--app-text-muted)" fontSize={11} tickLine={false} />
                          <YAxis dataKey="feature" type="category" width={110} stroke="var(--app-text-muted)" fontSize={11} tickLine={false} axisLine={false} />
                          <Tooltip content={<CustomSHAPTooltip />} cursor={{ fill: 'var(--app-primary-soft)' }} />
                          <ReferenceLine x={0} stroke="var(--app-text-muted)" strokeWidth={1.5} />
                          <Bar dataKey="value" radius={[4, 4, 4, 4]}>
                            {data.shap_values.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.value > 0 ? '#bf616a' : '#a3be8c'} />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  {/* All factors, sorted positive (raises risk) to negative (lowers risk) */}
                  <div className="glass-panel p-5">
                    <h3 className="mb-3 text-sm font-semibold text-[var(--app-text)]">Feature contributions</h3>
                    <div className="space-y-2.5">
                      {data.shap_values.map((item, idx) => {
                        const isPos = item.value > 0;
                        const percentWidth = Math.min(100, Math.abs(item.value) * 150);
                        return (
                          <div key={idx} className="flex items-center justify-between rounded-xl border border-[var(--app-border)] p-2.5" style={{ background: 'var(--app-surface)' }}>
                            <div className="mr-4 flex-1">
                              <div className="mb-1 flex items-center justify-between">
                                <span className="text-xs font-medium text-[var(--app-text)]">{item.feature}</span>
                                <span className={clsx('font-mono text-xs font-semibold', isPos ? 'text-rose-500' : 'text-emerald-500')}>
                                  {isPos ? `+${item.value.toFixed(4)}` : item.value.toFixed(4)}
                                </span>
                              </div>
                              <div className="h-1.5 w-full overflow-hidden rounded-full" style={{ background: 'var(--app-border)' }}>
                                <div className={clsx('h-full rounded-full', isPos ? 'bg-rose-500' : 'bg-emerald-500')} style={{ width: `${percentWidth}%` }} />
                              </div>
                            </div>
                            <span className={clsx(
                              'whitespace-nowrap rounded-md px-2 py-0.5 text-[11px] font-medium',
                              isPos ? 'bg-rose-500/10 text-rose-500' : 'bg-emerald-500/10 text-emerald-500'
                            )}>
                              {isPos ? 'Raises risk' : 'Lowers risk'}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </>
              ) : null}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};
