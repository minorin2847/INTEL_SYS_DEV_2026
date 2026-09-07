import { useEffect, useMemo, useState } from 'react'
import { api } from './api.js'
import Wizard from './components/Wizard.jsx'
import ResultScreen from './components/ResultScreen.jsx'

function useSessionId() {
  return useMemo(() => {
    const KEY = 'dx-session'
    let id = null
    try {
      id = localStorage.getItem(KEY)
    } catch {
    }
    if (!id) {
      id = 'web-' + Math.random().toString(36).slice(2, 10)
      try {
        localStorage.setItem(KEY, id)
      } catch {
      }
    }
    return id
  }, [])
}

export default function App() {
  const sessionId = useSessionId()
  const [apiOk, setApiOk] = useState(true)
  const [questions, setQuestions] = useState(null)
  
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState(null)
  const [answers, setAnswers] = useState(null)
  const [payload, setPayload] = useState(null)

  useEffect(() => {
    api.health().then(() => setApiOk(true)).catch(() => setApiOk(false))
    api.questions().then((r) => setQuestions(r.questions)).catch(() => {})
  }, [])

  async function handleSubmit(nextPayload, nextAnswers) {
    setBusy(true)
    try {
      const full = { ...nextPayload, session_id: sessionId }
      const res = await api.predict(full)
      setResult(res)
      setAnswers(nextAnswers)
      setPayload(full)
      setApiOk(true)
    } catch (e) {
      if (e.kind === 'network') setApiOk(false)
    } finally {
      setBusy(false)
    }
  }

  function handleRestart() {
    setResult(null)
  }

  return (
    <div className="app-viewport">
      {result ? (
        <ResultScreen
          result={result}
          questions={questions}
          answers={answers}
          payload={payload}
          sessionId={sessionId}
          onRestart={handleRestart}
        />
      ) : (
        <Wizard
          questions={questions || []}
          busy={busy}
          onSubmit={handleSubmit}
          apiOk={apiOk}
        />
      )}
    </div>
  )
}
