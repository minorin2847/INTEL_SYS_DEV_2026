import { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { navigate } from '../lib/router';
import type { ResultSummaryResponse } from '../types';
import { ModelDetailsPanel } from '../components/ModelDetailsPanel';
import { ModelRankingList, type SortMetric } from '../components/ModelRankingList';
import { ArrowLeft, Loader2, AlertCircle } from 'lucide-react';
import clsx from 'clsx';

interface ResultPageProps {
  resultId: string;
}

export function ResultPage({ resultId }: ResultPageProps) {
  const [data, setData] = useState<ResultSummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<SortMetric>('accuracy');

  useEffect(() => {
    setLoading(true);
    setError(null);
    setData(null);
    api.get<ResultSummaryResponse>(`/api/result/${resultId}`)
      .then(res => setData(res.data))
      .catch(err => {
        console.error(err);
        setError('Could not find this patient result. It may have expired or the backend was restarted.');
      })
      .finally(() => setLoading(false));
  }, [resultId]);

  const isDiabetic = data?.prediction === 1;

  return (
    <main className="relative z-10 space-y-5">
      <button
        onClick={() => navigate('/')}
        className="theme-toggle inline-flex items-center gap-2 rounded-lg px-4 py-2.5 text-sm font-semibold text-[var(--app-text)] transition-transform hover:-translate-y-0.5 active:translate-y-0"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to form
      </button>

      {loading ? (
        <div className="results-stage flex min-h-[26rem] flex-col items-center justify-center gap-3 text-[var(--app-primary)]">
          <Loader2 className="w-8 h-8 animate-spin" />
          <span className="text-sm muted-text">Loading patient result...</span>
        </div>
      ) : error ? (
        <div className="results-stage flex min-h-[26rem] flex-col items-center justify-center gap-3 p-6 text-center">
          <AlertCircle className="h-10 w-10" style={{ color: 'var(--app-danger)' }} />
          <p className="text-sm font-medium" style={{ color: 'var(--app-danger)' }}>{error}</p>
        </div>
      ) : data ? (
        <>
          <section className="hero-band">
            <div className="hero-copy">
              <div className="status-pill">
                <span className="status-dot" />
                Patient ID: {data.id}
              </div>
              <h2 className={clsx(isDiabetic ? 'text-[var(--app-danger)]' : 'text-[var(--app-success)]')}>
                {isDiabetic ? 'Diabetic' : 'Non-Diabetic'} Patient
              </h2>
              <p>
                Overall verdict from the highest-F1 model. Explore how all six trained
                models scored this same patient below, ranked by accuracy or F1.
              </p>
            </div>
          </section>

          <div className="results-stage">
            <ModelRankingList
              summaries={data.results}
              onSelectModel={setSelectedModel}
              selectedModel={selectedModel}
              sortBy={sortBy}
              onSortByChange={setSortBy}
            />
          </div>
        </>
      ) : null}

      <ModelDetailsPanel
        isOpen={!!selectedModel}
        onClose={() => setSelectedModel(null)}
        model={selectedModel}
        resultId={resultId}
      />
    </main>
  );
}
