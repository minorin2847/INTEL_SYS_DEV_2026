import RiskHeadline from './RiskHeadline.jsx'
import ForcePlot from './ForcePlot.jsx'
import SimilarCases from './SimilarCases.jsx'
import WhatYouCanChange from './WhatYouCanChange.jsx'
import Collapsible from './Collapsible.jsx'
import HistoryPanel from './HistoryPanel.jsx'

export default function ResultScreen({ result, questions, answers, payload, sessionId, onRestart }) {
  if (!result) return null;

  const qByField = Object.fromEntries((questions || []).map((q) => [q.field, q]))

  function describeAnswer(feature) {
    const q = qByField[feature]
    if (!q) return null
    const v = answers?.[feature]
    if (v === '' || v == null) return null
    if (q.type === 'yesno') return Number(v) === 1 ? 'Yes' : 'No'
    if (q.type === 'choice') {
      const opt = q.options.find(([code]) => Number(code) === Number(v))
      return opt ? opt[1] : null
    }
    return String(v)
  }

  const ex = result.explain && result.explain.factors ? result.explain : null
  const answered = Math.round((result.completeness ?? 1) * 21)
  const pRisk = Math.round(result.probability * 100)

  // Determine risk band
  let bandStr = 'LOW RISK';
  let bandClass = 'hero-card--good';
  let badgeClass = 'hero-card__status-badge--good';
  let titleStr = 'Your risk of diabetes is relatively low';
  if (result.probability >= 0.5) {
      bandStr = 'HIGH RISK';
      bandClass = 'hero-card--bad';
      badgeClass = 'hero-card__status-badge--bad';
      titleStr = 'You have a high risk of diabetes';
  } else if (result.probability >= 0.2) {
      bandStr = 'ELEVATED RISK';
      bandClass = '';
      badgeClass = '';
      titleStr = 'Your risk is elevated compared to the average';
  }

  return (
    <div className="res-dashboard">
      <header className="res-nav">
        <div className="res-nav__left">
          <button type="button" className="btn btn--ghost" onClick={onRestart}>
            ← Retake screening
          </button>
        </div>
        <div className="res-nav__right">
          <span className="pill">Model: <b>XGBoost (BRFSS)</b></span>
        </div>
      </header>

      <main className="res-grid">
        <div className="res-col res-col--left">
          
          <div className={`hero-card ${bandClass}`}>
            <span className={`hero-card__status-badge ${badgeClass}`}>
              {bandStr}
            </span>
            <h2 className="hero-card__title">
              {titleStr}
            </h2>
            <p className="hero-card__subtitle">
              Estimated probability: <b>{pRisk}%</b>
            </p>
          </div>

          <div className="card">
            <h4 className="card-section-title">Risk Probability</h4>
            <div className="meter">
              <div className="meter__track">
                <span
                  className={`meter__fill ${result.probability >= 0.5 ? 'meter__fill--bad' : 'meter__fill--good'}`}
                  style={{ width: `${pRisk}%` }}
                />
              </div>
              <div className="meter__scale">
                <span>0%</span>
                <span>50%</span>
                <span>100%</span>
              </div>
            </div>
          </div>

          {result.warnings?.map((w, i) => (
            <div className="notice warn" key={i}>
              {w}
            </div>
          ))}

          {answered < 21 && (
            <div className="notice info">
              You answered {answered} of 21 questions. Blanks were filled with typical values.
            </div>
          )}

          <div className="card">
             <SimilarCases similar={result.similar} />
          </div>

          <div className="card">
            <Collapsible summary="Your earlier screenings" open={true}>
              <HistoryPanel sessionId={sessionId} refreshKey={1} />
            </Collapsible>
          </div>

        </div>

        <div className="res-col res-col--right">
          {ex && (
            <div className="card">
              <h4 className="card-section-title">Why this estimate</h4>
              <p className="card-hint">
                Red blocks pushed the estimate up; blue blocks pulled it down.
              </p>
              <ForcePlot
                factors={ex.all_factors || ex.factors}
                baseValue={ex.base_value}
                output={ex.predicted_probability ?? result.probability}
                describe={describeAnswer}
              />
            </div>
          )}
          
          <div className="card">
              <WhatYouCanChange
                whatif={result.whatif}
                counterfactual={result.counterfactual}
                payload={payload}
                sessionId={sessionId}
              />
          </div>
        </div>
      </main>
    </div>
  )
}
