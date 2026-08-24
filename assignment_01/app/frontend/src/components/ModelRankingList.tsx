import React, { useMemo } from 'react';
import type { ModelSummary } from '../types';
import { formatModelName } from '../types';
import { ChevronRight, Award } from 'lucide-react';
import clsx from 'clsx';
import { motion } from 'framer-motion';

export type SortMetric = 'accuracy' | 'f1';

interface ModelRankingListProps {
  summaries: ModelSummary[];
  onSelectModel: (model: string) => void;
  selectedModel: string | null;
  sortBy: SortMetric;
  onSortByChange: (metric: SortMetric) => void;
}

export const ModelRankingList: React.FC<ModelRankingListProps> = ({
  summaries,
  onSelectModel,
  selectedModel,
  sortBy,
  onSortByChange,
}) => {
  const sorted = useMemo(
    () => [...summaries].sort((a, b) => b[sortBy] - a[sortBy]),
    [summaries, sortBy]
  );

  return (
    <div className="h-full p-5 sm:p-6 flex flex-col">
      <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-[var(--app-primary)]">Output</p>
          <h2 className="mt-1 flex items-center gap-2 text-xl font-bold text-[var(--app-text)]">
            <Award className="w-5 h-5 text-[var(--app-accent)]" />
            Model Rankings
          </h2>
        </div>
        <div className="sort-toggle" role="group" aria-label="Sort models by">
          <button
            type="button"
            className={clsx(sortBy === 'accuracy' && 'active')}
            onClick={() => onSortByChange('accuracy')}
          >
            Accuracy
          </button>
          <button
            type="button"
            className={clsx(sortBy === 'f1' && 'active')}
            onClick={() => onSortByChange('f1')}
          >
            F1
          </button>
        </div>
      </div>
      <div className="flex-1 overflow-y-auto pr-1 space-y-3">
        {sorted.map((summary, idx) => {
          const metricValue = summary[sortBy];
          return (
            <motion.div
              layout
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.06 }}
              key={summary.model}
            >
              <button
                onClick={() => onSelectModel(summary.model)}
                className={clsx(
                  'ranking-button w-full text-left p-4 rounded-lg transition-all flex items-center justify-between gap-3 group',
                  selectedModel === summary.model && 'ranking-button-selected shadow-lg shadow-primary-900/10'
                )}
              >
                <div className="flex min-w-0 items-center gap-4">
                  <div className={clsx(
                    'flex h-9 w-9 shrink-0 items-center justify-center rounded-lg font-bold text-sm',
                    idx === 0 ? 'bg-amber-500/20 text-amber-500' :
                    idx === 1 ? 'bg-cyan-500/20 text-cyan-500' :
                    idx === 2 ? 'bg-orange-500/20 text-orange-500' : 'bg-primary-500/10 text-[var(--app-text-muted)]'
                  )}>
                    #{idx + 1}
                  </div>
                  <div className="min-w-0">
                    <h3 className="truncate font-semibold text-[var(--app-text)]">{formatModelName(summary.model)}</h3>
                    <div className="mt-2 flex items-center gap-3">
                      <div className="metric-track">
                        <span style={{ width: `${Math.round(metricValue * 100)}%` }} />
                      </div>
                      <p className="text-sm font-semibold text-[var(--app-primary-strong)]">
                        {sortBy === 'accuracy' ? `${(metricValue * 100).toFixed(2)}%` : metricValue.toFixed(3)}
                      </p>
                      <p className="text-xs muted-text">
                        {sortBy === 'accuracy' ? `F1 ${summary.f1.toFixed(3)}` : `Acc ${(summary.accuracy * 100).toFixed(2)}%`}
                      </p>
                    </div>
                  </div>
                </div>
                <ChevronRight className={clsx(
                  'w-5 h-5 shrink-0 transition-transform',
                  selectedModel === summary.model ? 'text-primary-500' : 'text-[var(--app-text-muted)] group-hover:text-primary-500 group-hover:translate-x-1'
                )} />
              </button>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};
