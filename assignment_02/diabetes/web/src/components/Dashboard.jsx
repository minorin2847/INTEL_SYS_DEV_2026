import { useEffect, useMemo, useState } from 'react'
import { api } from '../api.js'
import { pct, bandColor } from '../lib/format.js'
import TradeoffCurve from './TradeoffCurve.jsx'
import Collapsible from './Collapsible.jsx'

export default function Dashboard() {
  const [cfg, setCfg] = useState(null)
  const [curve, setCurve] = useState(null)
  const [err, setErr] = useState(null)

  const [highCut, setHighCut] = useState(0.5)
  const [modCut, setModCut] = useState(0.3)

  useEffect(() => {
    ;(async () => {
      try {
        const [c, cv] = await Promise.all([
          api.getConfig(),
          api.thresholdCurve('val'),
        ])
        setCfg(c)
        setHighCut(c.high_cut)
        setModCut(c.moderate_cut)
        setCurve(cv)
      } catch (e) {
        setErr(e.message)
      }
    })()
  }, [])

  const nearest = useMemo(() => {
    if (!curve?.available) return null
    return curve.curve.reduce((best, p) =>
      Math.abs(p.high_cut - highCut) < Math.abs(best.high_cut - highCut) ? p : best,
    )
  }, [curve, highCut])

  if (err)
    return (
      <div className="page">
        <div className="notice err">{err}</div>
      </div>
    )
  if (!cfg || !curve) return <div className="page center-empty">Loading…</div>

  if (!curve.available) {
    return (
      <div className="page">
        <h1>Operator settings</h1>
        <div className="notice warn">
          Held-out scores are not built on the server, so the trade-off preview is
          unavailable. Run <code>python api/build_artifacts.py</code>.
        </div>
      </div>
    )
  }

  const p1k = nearest.per_1000
  const trueCases = p1k.caught + p1k.missed
  const changed =
    Math.abs(highCut - cfg.high_cut) > 1e-6 || Math.abs(modCut - cfg.moderate_cut) > 1e-6

  return (
    <div className="page">
      <h1>Operator settings</h1>
      <p className="lead">
        One decision to make here: how high does the estimated risk have to be before
        this person is referred for a confirmatory lab test? A lower cut-off catches
        more real cases but sends more people for testing.
      </p>

      <div className="card">
        <h2>Referral cut-off</h2>
        <div className="slider-row">
          <input
            type="range"
            min="0.02"
            max="0.98"
            step="0.01"
            value={highCut}
            onChange={(e) => setHighCut(Number(e.target.value))}
          />
          <span className="slider-readout">{pct(highCut)}</span>
        </div>
        <p className="muted small">
          Refer everyone whose estimated risk is at least {pct(highCut)}.
        </p>

        <div className="readout-box">
          At this cut-off, out of every <strong>1,000</strong> people screened:
          <br />• about <strong>{p1k.flagged}</strong> are referred for a lab test
          <br />• of the roughly <strong>{trueCases}</strong> who truly have diabetes,{' '}
          <strong>{p1k.caught}</strong> are caught and <strong>{p1k.missed}</strong> are
          missed
          <br />• <strong>{p1k.false_alarms}</strong> of the referrals come back negative
        </div>
        <p className="muted small" style={{ marginTop: 10 }}>
          Cases caught (recall) {pct(nearest.recall)} · referrals that are real
          (precision) {pct(nearest.precision)} · measured on held-out validation data.
        </p>
      </div>

      <div className="card">
        <h2>The trade-off</h2>
        <p className="card-hint">
          Every point is a possible cut-off. Moving right refers more people and catches
          more cases, at the cost of more negative referrals.
        </p>
        <TradeoffCurve
          curve={curve.curve}
          current={{ flag_rate: nearest.flag_rate, recall: nearest.recall }}
        />
      </div>

      <div className="card">
        <Collapsible summary="Help me choose a cut-off">
          <ChooseHelper onApply={(v) => setHighCut(v)} />
        </Collapsible>
        <div className="spacer" />
        <Collapsible summary="Advanced: the Low / Moderate boundary">
          <p className="muted small">
            The estimate is also shown as a Low / Moderate / High band. Moderate starts
            here; it changes only the wording shown to the person, not who is referred.
          </p>
          <div className="slider-row">
            <input
              type="range"
              min="0.02"
              max={highCut}
              step="0.01"
              value={modCut}
              onChange={(e) => setModCut(Number(e.target.value))}
            />
            <span className="slider-readout">{pct(modCut)}</span>
          </div>
        </Collapsible>
      </div>

      <div className="card">
        <h2>Save</h2>
        <SaveRow
          changed={changed}
          highCut={highCut}
          modCut={modCut}
          onSaved={(saved) => setCfg((c) => ({ ...c, ...saved }))}
        />
      </div>

      <div className="card">
        <Collapsible summary="Recent activity on this server">
          <RecentActivity />
        </Collapsible>
      </div>
    </div>
  )
}

function ChooseHelper({ onApply }) {
  const [mode, setMode] = useState('recall')
  const [target, setTarget] = useState(90)
  const [res, setRes] = useState(null)
  const [busy, setBusy] = useState(false)

  const needsTarget = mode === 'recall' || mode === 'flag_rate'

  async function run() {
    setBusy(true)
    setRes(null)
    try {
      const r = await api.thresholdRecommend(mode, needsTarget ? target / 100 : 0.9)
      setRes(r.point)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <div className="field">
        <label>Goal</label>
        <select value={mode} onChange={(e) => setMode(e.target.value)}>
          <option value="recall">Catch at least a set share of cases</option>
          <option value="flag_rate">Refer about a set share of people</option>
          <option value="f1">Best balance of catching cases vs false alarms</option>
          <option value="youden">Best overall separation</option>
        </select>
      </div>
      {needsTarget && (
        <div className="field">
          <label>{mode === 'recall' ? 'Catch at least (%)' : 'Refer about (%)'}</label>
          <input
            type="number"
            min="1"
            max="99"
            value={target}
            onChange={(e) => setTarget(Number(e.target.value))}
          />
        </div>
      )}
      <button className="btn" onClick={run} disabled={busy}>
        {busy ? 'Working…' : 'Suggest a cut-off'}
      </button>

      {res && (
        <div className="notice info" style={{ marginTop: 12 }}>
          Suggested cut-off <strong>{pct(res.high_cut)}</strong> — catches{' '}
          {pct(res.recall)} of cases, refers {pct(res.flag_rate)} of people.
          <div className="spacer" />
          <button className="btn" onClick={() => onApply(res.high_cut)}>
            Use this
          </button>
        </div>
      )}
    </div>
  )
}

function SaveRow({ changed, highCut, modCut, onSaved }) {
  const [key, setKey] = useState('')
  const [state, setState] = useState(null) // {ok, msg}
  const [busy, setBusy] = useState(false)

  async function save() {
    setBusy(true)
    setState(null)
    try {
      const saved = await api.setThresholds(modCut, highCut, key)
      onSaved(saved)
      setState({ ok: true, msg: `Saved. Referral cut-off is now ${pct(saved.high_cut)}.` })
    } catch (e) {
      setState({ ok: false, msg: e.message })
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <div className="field">
        <label>Admin key</label>
        <input
          type="password"
          value={key}
          onChange={(e) => setKey(e.target.value)}
          placeholder="required to save"
        />
      </div>
      <button
        className="btn primary"
        onClick={save}
        disabled={busy || !key || !changed}
      >
        {busy ? 'Saving…' : 'Save cut-offs'}
      </button>
      {!changed && <span className="muted small" style={{ marginLeft: 12 }}>No changes yet.</span>}
      {state && (
        <div className={'notice ' + (state.ok ? 'info' : 'err')} style={{ marginTop: 12 }}>
          {state.msg}
        </div>
      )}
    </div>
  )
}

function RecentActivity() {
  const [m, setM] = useState(null)
  const [err, setErr] = useState(null)
  useEffect(() => {
    api.metrics().then(setM).catch((e) => setErr(e.message))
  }, [])

  if (err) return <p className="notice err">{err}</p>
  if (!m) return <p className="muted small">Loading…</p>
  if (!m.n_screenings) return <p className="muted small">No screenings logged yet.</p>

  const bd = m.band_distribution || {}
  const total = Object.values(bd).reduce((s, v) => s + v, 0) || 1
  const order = ['Low', 'Moderate', 'High']

  return (
    <div>
      <div className="stackbar" style={{ marginBottom: 10 }}>
        {order.map((b) =>
          bd[b] ? (
            <span
              key={b}
              title={`${b}: ${bd[b]}`}
              style={{ width: `${(bd[b] / total) * 100}%`, background: bandColor(b) }}
            />
          ) : null,
        )}
      </div>
      <table className="mini-table">
        <tbody>
          <tr>
            <th>Screenings logged</th>
            <td className="num">{m.n_screenings}</td>
          </tr>
          <tr>
            <th>Referred (live flag rate)</th>
            <td className="num">{pct(m.flag_rate)}</td>
          </tr>
          <tr>
            <th>BMI value capped</th>
            <td className="num">{pct(m.bmi_capped_rate)}</td>
          </tr>
          <tr>
            <th>Low-completeness submissions</th>
            <td className="num">{pct(m.low_completeness_rate)}</td>
          </tr>
        </tbody>
      </table>
    </div>
  )
}
