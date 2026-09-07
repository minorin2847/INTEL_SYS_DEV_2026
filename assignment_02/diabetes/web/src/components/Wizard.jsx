import { useMemo, useState } from 'react'

function initialAnswers(questions) {
  const a = {}
  for (const q of questions) {
    if (q.type === 'yesno') a[q.field] = 0
    else if (q.type === 'choice') a[q.field] = ''
    else if (q.field === 'MentHlth' || q.field === 'PhysHlth') a[q.field] = 0
    else a[q.field] = ''
  }
  return a
}

export default function Wizard({ questions, busy, onSubmit, apiOk }) {
  const [answers, setAnswers] = useState(() => initialAnswers(questions))
  const [touched, setTouched] = useState(false)
  const [step, setStep] = useState(0)

  const sections = useMemo(() => {
    const m = new Map()
    for (const q of questions) {
      if (!m.has(q.section)) m.set(q.section, [])
      m.get(q.section).push(q)
    }
    return [...m.entries()]
  }, [questions])

  const sectionNames = sections.map(([name]) => name)
  const currentSection = sections[step]
  const stepFields = currentSection ? currentSection[1] : []

  const missingRequired = ['Age', 'Sex'].filter((f) => answers[f] === '' || answers[f] == null)
  const canNext = stepFields.every(q => !q.required || (answers[q.field] !== '' && answers[q.field] != null))

  const set = (field, value) => setAnswers((s) => ({ ...s, [field]: value }))

  function next() {
    setTouched(true)
    if (!canNext) return
    setTouched(false)
    if (step < sections.length - 1) setStep(s => s + 1)
    else submit()
  }

  function back() {
    setTouched(false)
    if (step > 0) setStep(s => s - 1)
  }

  function submit() {
    if (missingRequired.length) {
      setTouched(true)
      return
    }
    const payload = {}
    for (const q of questions) {
      const v = answers[q.field]
      if (q.type === 'yesno') {
        payload[q.field] = Number(v)
      } else if (q.type === 'choice') {
        if (v !== '' && v != null) payload[q.field] = Number(v)
      } else {
        if (v !== '' && v != null && !Number.isNaN(Number(v))) payload[q.field] = Number(v)
      }
    }
    onSubmit(payload, answers)
  }

  const isLast = step === sections.length - 1

  return (
    <div className="wiz-split">
      <aside className="wiz-sidebar">
        <div className="wiz-branding">
          <h1>Diabetes Health Screening</h1>
          <span>BRFSS CDC Survey</span>
        </div>
        <ol className="stepper vert" aria-label="Progress">
          {sectionNames.map((title, i) => (
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
            <span className={`pill ${apiOk === false ? 'pill--bad' : apiOk ? 'pill--good' : ''}`}>
              {apiOk === false ? 'API offline' : apiOk ? 'API connected' : 'connecting…'}
            </span>
          </div>
        </header>

        {apiOk === false && (
          <div className="banner banner--top">
            <span>
              API isn't reachable. Start the API with <code>uvicorn api.main:app --port 8000</code> and reload.
            </span>
          </div>
        )}

        <main className="wiz-body">
          <div className="wiz-step-hdr">
            <p className="wiz-step-badge">Step {step + 1} of {sections.length}</p>
            <h2 className="wiz-step-title">{currentSection?.[0]}</h2>
            <p className="wiz-step-sub">Answer what applies to you. Fields marked * are required.</p>
          </div>

          <div className="field-grid">
            {stepFields.map((q) => (
              <Field
                key={q.field}
                q={q}
                value={answers[q.field]}
                invalid={touched && missingRequired.includes(q.field) && q.required}
                onChange={(v) => set(q.field, v)}
              />
            ))}
          </div>
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
              onClick={next}
            >
              {isLast ? (busy ? 'Scoring…' : 'See my estimate') : 'Next →'}
            </button>
          </div>
        </footer>
      </div>
    </div>
  )
}

function Field({ q, value, invalid, onChange }) {
  const wide = q.type === 'yesno'
  return (
    <div
      id={'field-' + q.field}
      className={
        'field' +
        (q.required ? ' required' : '') +
        (invalid ? ' invalid' : '')
      }
      style={wide ? { gridColumn: '1 / -1' } : undefined}
    >
      <label className="field__label" htmlFor={'input-' + q.field}>
        {q.label}
      </label>

      {q.type === 'yesno' && (
        <div className="toggle" role="group" aria-label={q.label}>
          <button
            type="button"
            className={Number(value) === 1 ? 'on' : ''}
            onClick={() => onChange(1)}
          >
            Yes
          </button>
          <button
            type="button"
            className={Number(value) === 0 ? 'on' : ''}
            onClick={() => onChange(0)}
          >
            No
          </button>
        </div>
      )}

      {q.type === 'choice' && (
        <select
          id={'input-' + q.field}
          value={value}
          className={invalid ? 'is-invalid' : ''}
          onChange={(e) => onChange(e.target.value)}
        >
          <option value="">
            {q.required ? 'Select…' : 'Prefer not to say'}
          </option>
          {q.options.map(([code, text]) => (
            <option key={code} value={code}>
              {text}
            </option>
          ))}
        </select>
      )}

      {q.type === 'number' && (
        <input
          id={'input-' + q.field}
          type="number"
          inputMode="decimal"
          className={invalid ? 'is-invalid' : ''}
          value={value}
          min={q.min}
          max={q.max}
          placeholder={
            q.field === 'BMI'
              ? 'leave blank to compute from height & weight'
              : q.min != null
                ? `${q.min}–${q.max}`
                : ''
          }
          onChange={(e) => onChange(e.target.value)}
        />
      )}

      {q.note && <div className="field__note">{q.note}</div>}
      {invalid && <div className="field__err">This field is required</div>}
    </div>
  )
}
