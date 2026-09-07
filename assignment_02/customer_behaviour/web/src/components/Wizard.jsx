import React, { useMemo, useState } from 'react'
import ThemeToggle from './ThemeToggle.jsx'
import ExamplePicker from './ExamplePicker.jsx'
import Field from './Field.jsx'
import { exampleToValues } from '../lib/sephora.js'

const STEP_META = [
  { title: 'Your skin profile', sub: 'Who is writing the review.' },
  { title: 'The product', sub: 'Category, brand, price, popularity.' },
  { title: 'The review', sub: 'What the customer wrote — the model leans on this.' },
]
const REQUIRED = { 0: [], 1: ['price_usd'], 2: ['review_text'] }

export default function Wizard({ meta, values, setValues, samples, apiUp, onSubmit, busy, error, setError }) {
  const [step, setStep] = useState(0)
  const [touched, setTouched] = useState(false)

  const onChange = (k, v) => setValues((s) => ({ ...s, [k]: v }))

  const sections = meta?.sections || STEP_META.map((s) => s.title)
  const fieldsBySection = useMemo(() => {
    const map = {}
    for (const f of meta?.fields || []) (map[f.section] ??= []).push(f)
    return map
  }, [meta])

  const stepFields = fieldsBySection[sections[step]] || []
  const reviewExamples = (meta?.fields || []).find((f) => f.field === 'review_text')?.examples || []

  const missing = (REQUIRED[step] || []).filter((k) => {
    const v = values[k]
    return v === '' || v == null
  })
  const canNext = missing.length === 0

  function loadExample(ex) {
    setError(null)
    setTouched(false)
    setValues(exampleToValues(ex, samples?.defaults))
    setStep(2)
  }

  function next() {
    setError(null)
    if (!canNext) {
      setTouched(true)
      return
    }
    setTouched(false)
    if (step < sections.length - 1) setStep((s) => s + 1)
    else onSubmit()
  }

  function back() {
    setError(null)
    setTouched(false)
    if (step > 0) setStep((s) => s - 1)
  }

  const isLast = step === sections.length - 1

  return (
    <div className="wiz-split">
      <aside className="wiz-sidebar">
        <div className="wiz-branding">
          <h1>Product Recommendation</h1>
          <span>Customer Insights</span>
        </div>
        <ol className="stepper vert" aria-label="Progress">
          {sections.map((title, i) => (
            <li
              key={title}
              className={`stepper__item${i === step ? ' is-active' : i < step ? ' is-done' : ''}`}
            >
              <button
                type="button"
                className="stepper__dot"
                disabled={i > step}
                onClick={() => i < step && setStep(i)}
              >
                {i < step ? '✓' : i + 1}
              </button>
              <span className="stepper__label">{title}</span>
            </li>
          ))}
        </ol>
      </aside>

      <div className="wiz-content">
        <header className="wiz-hdr">
          <div className="wiz-hdr__right">
            <span className={`pill ${apiUp === false ? 'pill--bad' : apiUp ? 'pill--good' : ''}`}>
              {apiUp === false ? 'API offline' : apiUp ? 'API connected' : 'connecting…'}
            </span>
          </div>
        </header>

        {apiUp === false && (
          <div className="banner banner--top">
            <span>
              API isn't reachable. Start the API with <code>uvicorn api.main:app --port 8000</code> and reload.
            </span>
          </div>
        )}

        <main className="wiz-body">
        <div className="wiz-step-hdr">
          <p className="wiz-step-badge">Step {step + 1} of {sections.length}</p>
          <h2 className="wiz-step-title">{sections[step]}</h2>
          <p className="wiz-step-sub">{STEP_META[step]?.sub}</p>
        </div>

        <div className="field-grid">
          {stepFields.map((f) => (
            <Field
              key={f.field}
              f={f}
              value={values[f.field]}
              onChange={onChange}
              invalid={touched && missing.includes(f.field)}
            />
          ))}
        </div>

        {isLast && reviewExamples.length > 0 && (
          <div className="examples">
            <span className="examples__lbl">Try a real review:</span>
            <div className="examples__chips">
              {reviewExamples.map(([title, text]) => (
                <button
                  type="button"
                  key={title}
                  className="examples__chip"
                  title={text}
                  onClick={() => setValues((s) => ({ ...s, review_title: title, review_text: text }))}
                >
                  {title}
                </button>
              ))}
            </div>
          </div>
        )}

        {error && <p className="form-error" role="alert">{error}</p>}
      </main>

      <footer className="wiz-foot">
        <div className="wiz-foot__container">
          <button type="button" className="btn btn--ghost" disabled={step === 0 || busy} onClick={back}>
            ← Back
          </button>
          <button
            type="button"
            className="btn btn--primary"
            disabled={busy || (!canNext && touched)}
            title={!canNext ? `Fill in: ${missing.join(', ')}` : undefined}
            onClick={next}
          >
            {isLast ? (busy ? 'Scoring…' : 'Predict') : 'Next →'}
          </button>
        </div>
      </footer>
      </div>
    </div>
  )
}
