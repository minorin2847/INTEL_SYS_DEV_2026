import ShapChart from './ShapChart.jsx'

export default function ResultScreen({ result, model, onRestart }) {
  if (!result) return null

  const pRec = Math.round((result.p_recommend ?? 0) * 100)
  const thr = Math.round((result.threshold ?? 0.5) * 100)
  const isLikely = (result.prediction || '').toLowerCase() === 'recommend'

  const bandStr = isLikely ? 'LIKELY TO RECOMMEND' : 'UNLIKELY TO RECOMMEND'
  const bandClass = isLikely ? 'hero-card--good' : 'hero-card--bad'
  const badgeClass = isLikely
    ? 'hero-card__status-badge--good'
    : 'hero-card__status-badge--bad'
  const titleStr = isLikely
    ? 'This customer would probably recommend it'
    : 'This customer probably would not recommend it'

  const terms = result.review_terms || {}
  const toward = terms.toward || []
  const against = terms.against || []

  const s = result.signals || {}
  const profile = [
    ['Skin type', s.skin_type || '—'],
    ['Category', s.category || '—'],
    ['Brand', s.brand || '—'],
    [
      'Price',
      s.price_usd == null
        ? '—'
        : `$${s.price_usd}${s.price_tier ? ` · ${s.price_tier}` : ''}`,
    ],
    ['Product “loves”', s.product_loves == null ? '—' : s.product_loves.toLocaleString()],
    ['Review length', `${s.review_tokens ?? '—'} words`],
  ]

  const modelName =
    (model && (model.chosen_model || model.model)) || result.model || 'Logistic Regression'

  return (
    <div className="res-dashboard">
      <header className="res-nav">
        <div className="res-nav__left">
          <button type="button" className="btn btn--ghost" onClick={onRestart}>
            ← Score another review
          </button>
        </div>
        <div className="res-nav__right">
          <span className="pill">Model: <b>{modelName}</b></span>
        </div>
      </header>

      <main className="res-grid">
        <div className="res-col res-col--left">
          <div className={`hero-card ${bandClass}`}>
            <span className={`hero-card__status-badge ${badgeClass}`}>{bandStr}</span>
            <h2 className="hero-card__title">{titleStr}</h2>
            <p className="hero-card__subtitle">
              Chance of a recommendation: <b>{pRec}%</b> — we call it “recommends” above {thr}%.
            </p>
          </div>

          <div className="card">
            <h4 className="card-section-title">Chance of a recommendation</h4>
            <div className="meter">
              <div className="meter__track">
                <span
                  className={`meter__fill ${isLikely ? 'meter__fill--good' : 'meter__fill--bad'}`}
                  style={{ width: `${pRec}%` }}
                />
              </div>
              <div className="meter__scale">
                <span>0%</span>
                <span>50%</span>
                <span>100%</span>
              </div>
            </div>
          </div>

          <div className="card">
            <h4 className="card-section-title">What the model saw</h4>
            <div className="grid-2">
              {profile.map(([k, v]) => (
                <div className="field" key={k}>
                  <span className="section-label">{k}</span>
                  <div style={{ fontWeight: 600 }}>{v}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="res-col res-col--right">
          {(toward.length > 0 || against.length > 0) && (
            <div className="card">
              <h4 className="card-section-title">Review words that moved the call</h4>
              {against.length > 0 && (
                <>
                  <p className="card-hint text-bad">▼ toward “won’t recommend”</p>
                  <div className="words-chips" style={{ marginBottom: '16px' }}>
                    {against.map((t, i) => (
                      <span key={i} className="word-chip word-chip--bad">
                        {t.term} {t.effect >= 0 ? '+' : ''}{t.effect.toFixed(2)}
                      </span>
                    ))}
                  </div>
                </>
              )}
              {toward.length > 0 && (
                <>
                  <p className="card-hint text-good">▲ toward “recommends”</p>
                  <div className="words-chips">
                    {toward.map((t, i) => (
                      <span key={i} className="word-chip word-chip--good">
                        {t.term} {t.effect >= 0 ? '+' : ''}{t.effect.toFixed(2)}
                      </span>
                    ))}
                  </div>
                </>
              )}
            </div>
          )}

          {result.contributions?.items?.length ? (
            <div className="card">
              <ShapChart contributions={result.contributions} />
            </div>
          ) : null}
        </div>
      </main>
    </div>
  )
}
