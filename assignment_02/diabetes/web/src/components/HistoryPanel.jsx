import { useCallback, useEffect, useState } from 'react'
import { api } from '../api.js'
import { pct, bandColor, timeAgo } from '../lib/format.js'

export default function HistoryPanel({ sessionId, refreshKey }) {
  const [rows, setRows] = useState(null)
  const [err, setErr] = useState(null)

  const load = useCallback(async () => {
    setErr(null)
    try {
      const r = await api.history(sessionId)
      setRows(r.screenings || [])
    } catch (e) {
      setErr(e.message)
    }
  }, [sessionId])

  useEffect(() => {
    load()
  }, [load, refreshKey])

  if (err) return <p className="notice err">{err}</p>
  if (!rows) return <p className="muted small">Loading…</p>
  if (!rows.length)
    return <p className="muted small">No earlier screenings in this browser session.</p>

  return (
    <table className="mini-table">
      <thead>
        <tr>
          <th>When</th>
          <th>Estimate</th>
          <th>Band</th>
          <th className="num">Answered</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((r, i) => (
          <tr key={i}>
            <td>{timeAgo(r.ts)}</td>
            <td>{pct(r.probability)}</td>
            <td style={{ color: bandColor(r.band), fontWeight: 700 }}>{r.band}</td>
            <td className="num">{Math.round((r.completeness ?? 1) * 21)}/21</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
