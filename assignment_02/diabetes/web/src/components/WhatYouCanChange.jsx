import { useEffect, useMemo, useRef, useState } from 'react'
import { api } from '../api.js'
import { pct, points, whatifSentence, cfPhrase, dedupeChanges } from '../lib/format.js'
import Sparkline from './Sparkline.jsx'

export default function WhatYouCanChange({ whatif, counterfactual, payload, sessionId }) {
  const allFactors = (whatif?.factors || []).filter((f) => Math.abs(f.delta) >= 0.005)
  const factors = allFactors.filter((f) => f.delta < 0)
  const raisers = allFactors.filter((f) => f.delta > 0)
  const sweep = whatif?.bmi_sweep || []
  const curBmi = whatif?.current_bmi ?? null
  const baseRisk = whatif?.base_risk

  const [bmi, setBmi] = useState(curBmi ?? 28)
  const [liveRisk, setLiveRisk] = useState(baseRisk ?? null)
  const [scoring, setScoring] = useState(false)
  const timer = useRef(null)

  const bmiRange = useMemo(() => {
    if (sweep.length) {
      const xs = sweep.map((p) => p.bmi)
      return [Math.min(...xs, 16), Math.max(...xs, 45)]
    }
    return [16, 50]
  }, [sweep])

  useEffect(() => {
    if (curBmi == null) return
    if (Math.abs(bmi - curBmi) < 0.51) {
      setLiveRisk(baseRisk ?? null)
      return
    }
    if (timer.current) clearTimeout(timer.current)
    timer.current = setTimeout(async () => {
      setScoring(true)
      try {
        const r = await api.predict(
          { ...payload, BMI: Number(bmi), session_id: sessionId },
          '',
          { log: false },
        )
        setLiveRisk(r.probability)
      } catch {
        /* leave last value */
      } finally {
        setScoring(false)
      }
    }, 350)
    return () => timer.current && clearTimeout(timer.current)
  }, [bmi]) // eslint-disable-line react-hooks/exhaustive-deps

  const cfChanges = dedupeChanges(counterfactual?.changes)
  const nothingToShow =
    allFactors.length === 0 && curBmi == null && cfChanges.length === 0

  return (
    <div className="card">
      <h2>What could change the estimate</h2>
      <p className="card-hint">
        Re-scoring your answers with one habit changed at a time. These are patterns
        in the survey data, not promises about your health.
      </p>

      {nothingToShow && (
        <p className="muted">
          The habits this tool can vary are already at their healthier setting for you.
        </p>
      )}

      {factors.length > 0 && (
        <div>
          {factors.map((f) => (
            <div className="change-row" key={f.feature}>
              <div className="desc">{whatifSentence(f)}</div>
              <div className="from-to">
                {pct(baseRisk)} &rarr; {pct(f.new_risk)}
              </div>
              <span className="delta-chip down">{points(f.delta)} pts</span>
            </div>
          ))}
        </div>
      )}

      {factors.length === 0 && allFactors.length > 0 && (
        <p className="muted">
          None of the habits this tool can vary would lower your estimate on their own.
        </p>
      )}

      {raisers.length > 0 && (
        <p className="muted small" style={{ marginTop: 8 }}>
          For reference, the model links{' '}
          {raisers.map((f) => whatifSentence(f).replace(/^If /, '').toLowerCase()).join(', and ')}{' '}
          to a slightly <em>higher</em> estimate for someone with your other answers.
        </p>
      )}

      {curBmi != null && (
        <div style={{ marginTop: 18 }}>
          <div className="section-label" style={{ marginTop: 0 }}>
            Try a different BMI
          </div>
          <div className="slider-row">
            <input
              type="range"
              min={bmiRange[0]}
              max={bmiRange[1]}
              step="0.5"
              value={bmi}
              onChange={(e) => setBmi(Number(e.target.value))}
            />
            <span className="slider-readout">
              BMI {bmi.toFixed(1)}
            </span>
          </div>
          <div className="muted small">
            Estimated risk at this BMI:{' '}
            <strong>{scoring ? '…' : pct(liveRisk)}</strong>
            {curBmi != null && (
              <> · your entered BMI is {curBmi.toFixed(1)}</>
            )}
          </div>
          {sweep.length > 1 && (
            <div style={{ marginTop: 8 }}>
              <Sparkline
                points={sweep.map((p) => ({ x: p.bmi, y: p.risk }))}
                width={320}
                height={60}
                marker={{
                  x: bmi,
                  y:
                    sweep.reduce((best, p) =>
                      Math.abs(p.bmi - bmi) < Math.abs(best.bmi - bmi) ? p : best,
                    ).risk,
                }}
              />
            </div>
          )}
        </div>
      )}

      {cfChanges.length > 0 && (
        <div className="notice info" style={{ marginTop: 16 }}>
          If you {cfChanges.map(cfPhrase).join(', and ')}, the estimate would move from{' '}
          <strong>
            {pct(counterfactual.from_risk)} ({counterfactual.from_band})
          </strong>{' '}
          to{' '}
          <strong>
            {pct(counterfactual.to_risk)} ({counterfactual.to_band})
          </strong>
          {counterfactual.feasible
            ? ` - into the ${counterfactual.target_band} band.`
            : ` - still short of the ${counterfactual.target_band} band.`}
        </div>
      )}

      {whatif?.caveat && (
        <p className="muted small" style={{ marginTop: 14 }}>
          {whatif.caveat}
        </p>
      )}
    </div>
  )
}
