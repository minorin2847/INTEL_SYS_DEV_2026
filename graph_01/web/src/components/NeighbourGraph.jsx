import { href } from '../lib/route.js'
import { nfc, relHeading, typeClass, typeLabel } from '../lib/labels.js'

const W = 640
const H = 420
const MAX = 12

// Radial drawing of the 1-hop neighbourhood: the entity in the centre,
// its strongest neighbours around it. Every neighbour links to its own page.
export default function NeighbourGraph({ name, type, facts }) {
  const seen = new Map()
  for (const f of facts) {
    const out = f.subject === name
    const other = out ? f.object : f.subject
    if (!seen.has(other)) {
      seen.set(other, { name: other, type: out ? f.object_type : f.subject_type, rel: relHeading(f.relation, out ? 'out' : 'in'), support: f.support })
    }
  }
  const nodes = [...seen.values()].sort((a, b) => b.support - a.support).slice(0, MAX)
  const hidden = seen.size - nodes.length
  const cx = W / 2
  const cy = H / 2
  const rx = W / 2 - 110
  const ry = H / 2 - 50
  const placed = nodes.map((n, i) => {
    const a = (2 * Math.PI * i) / nodes.length - Math.PI / 2
    return { ...n, x: cx + rx * Math.cos(a), y: cy + ry * Math.sin(a) }
  })

  return (
    <figure className="graph">
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`${name} and ${nodes.length} directly connected entities`}>
        {placed.map((n) => (
          <line key={`l-${n.name}`} x1={cx} y1={cy} x2={n.x} y2={n.y} className="graph__edge" />
        ))}
        {placed.map((n) => (
          <a key={n.name} href={href('entity', n.name)} className={`graph__node ${typeClass(n.type)}`}>
            <title>{`${n.rel}: ${n.name} (${typeLabel(n.type)})`}</title>
            <rect x={n.x - 8} y={n.y - 8} width="16" height="16" />
            <text x={n.x} y={n.y + (n.y < cy ? -18 : 30)} textAnchor="middle">{short(n.name)}</text>
          </a>
        ))}
        <g className={`graph__center ${typeClass(type)}`}>
          <rect x={cx - 15} y={cy - 15} width="30" height="30" />
          <text x={cx} y={cy + 40} textAnchor="middle">{short(name, 26)}</text>
        </g>
      </svg>
      <figcaption>
        Chart of direct links{hidden > 0 ? ` (strongest ${nodes.length} of ${seen.size})` : ''}. Click a diamond to open it.
      </figcaption>
    </figure>
  )
}

const short = (s, n = 18) => {
  s = nfc(s)
  return s.length > n ? `${s.slice(0, n - 1)}…` : s
}
