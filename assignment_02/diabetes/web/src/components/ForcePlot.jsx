import { useMemo, useState } from 'react'

/**
 * Interactive additive force plot for a single prediction.
 *
 * Reads like the classic SHAP force plot: the estimate f(x) sits in the middle,
 * red segments to its left are the answers pushing the estimate UP, blue segments
 * to its right are the answers pulling it DOWN. Segment length is proportional to
 * how much that answer moved the estimate. Hover any segment for detail.
 *
 * props:
 *   factors   [{feature, label, value}]  signed contributions (all of them)
 *   baseValue number   the model's average output (starting point)
 *   output    number   the predicted probability for this person
 *   describe  fn(feature) -> string | null   the person's answer, for the tooltip
 */
export default function ForcePlot({ factors, baseValue, output, describe }) {
  const [tip, setTip] = useState(null)

  const model = useMemo(() => {
    const W = 860
    const H = 128
    const padY = 34
    const barH = 30

    const clean = (factors || []).filter((f) => Math.abs(f.value) > 1e-6)
    // keep the 12 biggest, roll the rest into one "other answers" segment
    const sorted = [...clean].sort((a, b) => Math.abs(b.value) - Math.abs(a.value))
    const top = sorted.slice(0, 12)
    const rest = sorted.slice(12)
    if (rest.length) {
      const v = rest.reduce((s, f) => s + f.value, 0)
      if (Math.abs(v) > 1e-6)
        top.push({ feature: '__other__', label: `${rest.length} smaller factors`, value: v })
    }

    const rawSum = top.reduce((s, f) => s + f.value, 0)
    const targetSpan = output - baseValue
    const scale = Math.abs(rawSum) > 1e-9 ? targetSpan / rawSum : 1

    const pos = top.filter((f) => f.value > 0).sort((a, b) => a.value - b.value)
    const neg = top.filter((f) => f.value < 0).sort((a, b) => a.value - b.value) // most negative first
    const sumPos = pos.reduce((s, f) => s + f.value * scale, 0)
    const sumNeg = neg.reduce((s, f) => s + Math.abs(f.value) * scale, 0)

    const leftEdge = output - sumPos
    const rightEdge = output + sumNeg
    const baseTick = output - sumPos + sumNeg // ~= baseValue

    let lo = Math.min(leftEdge, baseValue, output) - 0.06
    let hi = Math.max(rightEdge, baseValue, output) + 0.06
    lo = Math.max(0, lo)
    hi = Math.min(1, hi)
    if (hi - lo < 0.05) {
      hi = Math.min(1, hi + 0.05)
      lo = Math.max(0, lo - 0.05)
    }
    const x = (v) => ((v - lo) / (hi - lo)) * W

    // build red run: far-left -> output, small segment first
    const segs = []
    let cursor = leftEdge
    for (const f of pos) {
      const w = f.value * scale
      segs.push({ ...f, x0: x(cursor), x1: x(cursor + w), fill: '#e5544b', side: 'up' })
      cursor += w
    }
    // blue run: output -> far-right, most-negative (largest) first so it sits by f(x)
    cursor = output
    for (const f of neg) {
      const w = Math.abs(f.value) * scale
      segs.push({ ...f, x0: x(cursor), x1: x(cursor + w), fill: '#4c8bf5', side: 'down' })
      cursor += w
    }

    return { W, H, padY, barH, segs, x, baseTick, output, lo, hi }
  }, [factors, baseValue, output])

  const { W, H, padY, barH, segs, x, baseTick } = model

  function move(e, s) {
    const ans = s.feature !== '__other__' && describe ? describe(s.feature) : null
    setTip({
      cx: e.clientX,
      cy: e.clientY,
      label: s.label,
      line: `${s.value > 0 ? 'Raises' : 'Lowers'} the estimate by ${Math.abs(
        Math.round(s.value * 100),
      )} points`,
      ans,
    })
  }

  return (
    <div className="forceplot" onMouseLeave={() => setTip(null)}>
      <svg viewBox={`0 0 ${W} ${H}`} width="100%" height={H} preserveAspectRatio="xMidYMid meet">
        {/* base marker */}
        <line x1={x(baseTick)} x2={x(baseTick)} y1={padY - 12} y2={padY + barH + 12} stroke="#98a2b3" strokeWidth="1" strokeDasharray="3 3" />
        <text x={x(baseTick)} y={padY - 16} textAnchor="middle" fontSize="11" fill="#667085">
          average {Math.round(baseTick * 100)}%
        </text>

        {/* segments */}
        {segs.map((s, i) => (
          <g key={i} onMouseMove={(e) => move(e, s)}>
            <rect
              x={Math.min(s.x0, s.x1)}
              y={padY}
              width={Math.max(2, Math.abs(s.x1 - s.x0))}
              height={barH}
              fill={s.fill}
              stroke="#fff"
              strokeWidth="1"
            />
          </g>
        ))}

        {/* output marker */}
        <line x1={x(model.output)} x2={x(model.output)} y1={padY - 20} y2={padY + barH + 20} stroke="#1c2333" strokeWidth="2" />
        <text x={x(model.output)} y={padY + barH + 34} textAnchor="middle" fontSize="14" fontWeight="700" fill="#1c2333">
          this estimate {Math.round(model.output * 100)}%
        </text>
      </svg>

      <div className="legend">
        <span><span className="sw" style={{ background: '#e5544b' }} />answers raising the estimate</span>
        <span><span className="sw" style={{ background: '#4c8bf5' }} />answers lowering it</span>
        <span className="muted">hover a block for detail</span>
      </div>

      {tip && (
        <div
          className="fp-tooltip"
          style={{ left: Math.min(tip.cx + 14, window.innerWidth - 250), top: tip.cy + 14 }}
        >
          <strong>{tip.label}</strong>
          <div>{tip.line}</div>
          {tip.ans && <div className="muted" style={{ color: '#cbd5e1' }}>Your answer: {tip.ans}</div>}
        </div>
      )}
    </div>
  )
}
