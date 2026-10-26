import { articles } from '../lib/labels.js'

// How many articles back a fact. The bar uses a log scale (1 → 150 articles),
// the number next to it is the real value.
export default function SupportMeter({ support, source }) {
  if (source === 'curated') {
    return <span className="pill" title="General medical classification added by hand, not counted from articles">reference</span>
  }
  const pct = Math.min(100, (Math.log10(support + 1) / Math.log10(151)) * 100)
  return (
    <span className="meter" title={`Stated in ${articles(support)}`}>
      <span className="meter__track" aria-hidden="true">
        <span className="meter__fill" style={{ width: `${pct}%` }} />
      </span>
      <span className="meter__value">{articles(support)}</span>
    </span>
  )
}
