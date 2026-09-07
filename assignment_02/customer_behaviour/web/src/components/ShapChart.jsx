import React from 'react'

// Diverging bar chart of the linear model's per-feature pull (log-odds).
// left / --c-bad  = pushes toward "not recommend"
// right / --c-good = pushes toward "recommend"
export default function ShapChart({ contributions }) {
  if (!contributions?.items?.length) return null

  const { base_p, final_p, items, other_effect, dataset_base_rate } = contributions
  const rows = [...items]
  if (other_effect && Math.abs(other_effect) >= 0.01) {
    rows.push({ label: 'Other smaller factors combined', kind: 'other', effect: other_effect })
  }

  const maxAbs = Math.max(...rows.map((r) => Math.abs(r.effect)), 0.4)
  const width = (e) => `${Math.max(4, (Math.abs(e) / maxAbs) * 100)}%`
  const sign = (e) => (e >= 0 ? `+${e.toFixed(2)}` : e.toFixed(2))

  const basePct = Math.round(base_p * 100)
  const finalPct = Math.round(final_p * 100)
  const netDelta = finalPct - basePct

  const tagText = { text: 'review', tabular: 'profile', other: 'other' }

  return (
    <div className="shap-box">
      <div className="shap-box__head">
        <h3 className="shap-box__title">Why this prediction — each factor&apos;s pull</h3>
        <p className="shap-box__sub">
          <span className="shap-legend shap-legend--neg" /> toward “won&apos;t recommend” &nbsp;·&nbsp;
          <span className="shap-legend shap-legend--pos" /> toward “recommends”
        </p>
      </div>

      <div className="shap-rows">
        {rows.map((it, idx) => {
          const neg = it.effect < 0
          return (
            <div key={idx} className={`shap-row${it.kind === 'other' ? ' shap-row--other' : ''}`}>
              <div className="shap-row__label">
                <span className={`shap-tag shap-tag--${it.kind === 'text' ? 'txt' : it.kind === 'other' ? 'other' : 'tab'}`}>
                  {tagText[it.kind] || 'profile'}
                </span>
                <span className="shap-row__name" title={it.label}>
                  {it.label}
                </span>
              </div>
              <div className="shap-row__track">
                <span
                  className={`shap-bar shap-bar--${neg ? 'neg' : 'pos'}`}
                  style={{ width: width(it.effect) }}
                />
              </div>
              <span className={`shap-row__val ${neg ? 'text-bad' : 'text-good'}`}>{sign(it.effect)}</span>
            </div>
          )
        })}
      </div>

      <div className="shap-waterfall">
        <div className="shap-wf-step">
          <span className="shap-wf-lbl">Neutral start</span>
          <span className="shap-wf-val">{basePct}%</span>
        </div>
        <span className="shap-wf-arrow">→</span>
        <div className="shap-wf-step">
          <span className="shap-wf-lbl">Net pull</span>
          <span className={`shap-wf-val ${netDelta >= 0 ? 'text-good' : 'text-bad'}`}>
            {netDelta >= 0 ? `+${netDelta}` : netDelta} pts
          </span>
        </div>
        <span className="shap-wf-arrow">→</span>
        <div className="shap-wf-step shap-wf-step--final">
          <span className="shap-wf-lbl">Recommends</span>
          <span className="shap-wf-val">{finalPct}%</span>
        </div>
      </div>

      <p className="shap-footnote">
        Bars are log-odds pulls. Start ({basePct}%) is the model&apos;s neutral point — classes are
        weighted equally, so not the {Math.round((dataset_base_rate ?? 0.85) * 100)}% dataset rate.
        Review terms dominate: the text is written with the recommend tick (§14a).
      </p>
    </div>
  )
}
