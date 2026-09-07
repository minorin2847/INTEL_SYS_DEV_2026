import React, { useEffect, useMemo, useState } from 'react'
import { api, ApiError } from './api.js'
import Wizard from './components/Wizard.jsx'
import ResultScreen from './components/ResultScreen.jsx'
import { exampleToValues } from './lib/sephora.js'

const FALLBACK = {
  skin_type: 'oily',
  skin_tone: 'light',
  eye_color: 'brown',
  hair_color: 'brown',
  secondary_category: 'Moisturizers',
  brand_name: 'Skinfix',
  price_usd: 32,
  loves_count: 21000,
  reviews: 1800,
  review_title: 'Not for oily skin',
  review_text:
    'Broke me out within a week and felt greasy all day. Smells strongly of perfume. Wanted to love it but returned it.',
}

export default function App() {
  const [meta, setMeta] = useState(null)
  const [model, setModel] = useState(null)
  const [samples, setSamples] = useState(null)
  const [values, setValues] = useState(FALLBACK)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)
  const [apiUp, setApiUp] = useState(null)

  useEffect(() => {
    api.health().then(() => setApiUp(true)).catch(() => setApiUp(false))
    api.questions().then(setMeta).catch((e) => setError(e.message))
    api.modelInfo().then(setModel).catch(() => {})
    api
      .samples()
      .then((s) => {
        setSamples(s)
        const seed = s.examples?.find((e) => e._recommended === 0) || s.examples?.[0]
        if (seed) setValues(exampleToValues(seed, s.defaults))
      })
      .catch(() => {})
  }, [])

  const numberFields = useMemo(
    () => new Set((meta?.fields || []).filter((f) => f.type === 'number').map((f) => f.field)),
    [meta],
  )

  async function handleSubmit() {
    setError(null)
    setBusy(true)
    const payload = {}
    for (const [k, v] of Object.entries(values)) {
      if (v === '' || v == null) continue
      payload[k] = numberFields.has(k) ? Number(v) : v
    }
    try {
      setResult(await api.predict(payload))
    } catch (err) {
      setError(err instanceof ApiError ? err.message : String(err))
    } finally {
      setBusy(false)
    }
  }

  function handleRestart() {
    setResult(null)
    setError(null)
  }

  return (
    <div className="app-viewport">
      {result ? (
        <ResultScreen result={result} model={model} onRestart={handleRestart} />
      ) : (
        <Wizard
          meta={meta}
          values={values}
          setValues={setValues}
          samples={samples}
          apiUp={apiUp}
          onSubmit={handleSubmit}
          busy={busy}
          error={error}
          setError={setError}
        />
      )}
    </div>
  )
}
