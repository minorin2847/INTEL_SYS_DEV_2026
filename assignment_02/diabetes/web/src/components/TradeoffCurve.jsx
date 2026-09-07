// Recall (cases caught) vs flag rate (share referred), with the current cut marked.
export default function TradeoffCurve({ curve, current }) {
  const W = 520
  const H = 300
  const m = { l: 52, r: 16, t: 14, b: 44 }
  const iw = W - m.l - m.r
  const ih = H - m.t - m.b
  const x = (v) => m.l + v * iw
  const y = (v) => m.t + (1 - v) * ih

  const pts = [...(curve || [])].sort((a, b) => a.flag_rate - b.flag_rate)
  const d = pts.map((p, i) => `${i ? 'L' : 'M'}${x(p.flag_rate)},${y(p.recall)}`).join(' ')

  const ticks = [0, 0.25, 0.5, 0.75, 1]

  return (
    <svg viewBox={`0 0 ${W} ${H}`} width="100%" height={H} role="img" aria-label="trade-off curve">
      {ticks.map((t) => (
        <g key={t}>
          <line x1={x(t)} x2={x(t)} y1={m.t} y2={m.t + ih} stroke="#eef1f5" />
          <line x1={m.l} x2={m.l + iw} y1={y(t)} y2={y(t)} stroke="#eef1f5" />
          <text x={x(t)} y={H - 24} textAnchor="middle" fontSize="11" fill="#667085">
            {Math.round(t * 100)}%
          </text>
          <text x={m.l - 8} y={y(t) + 4} textAnchor="end" fontSize="11" fill="#667085">
            {Math.round(t * 100)}%
          </text>
        </g>
      ))}
      <path d={d} fill="none" stroke="#2f6feb" strokeWidth="2.5" />

      {current && (
        <g>
          <circle cx={x(current.flag_rate)} cy={y(current.recall)} r="6" fill="#c0392b" />
          <text
            x={x(current.flag_rate)}
            y={y(current.recall) - 12}
            textAnchor="middle"
            fontSize="12"
            fontWeight="700"
            fill="#c0392b"
          >
            current
          </text>
        </g>
      )}

      <text x={m.l + iw / 2} y={H - 6} textAnchor="middle" fontSize="12" fill="#1c2333">
        share of people referred
      </text>
      <text
        x={-(m.t + ih / 2)}
        y={14}
        transform="rotate(-90)"
        textAnchor="middle"
        fontSize="12"
        fill="#1c2333"
      >
        share of true cases caught
      </text>
    </svg>
  )
}
