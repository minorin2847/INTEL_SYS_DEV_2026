const OPTIONS = [
  [0, 'All facts'],
  [2, '2+ articles'],
  [3, '3+ articles'],
  [5, '5+ articles'],
  [10, '10+ articles'],
]

// Lets the reader hide weakly documented facts. Reference facts are always shown.
export default function MinSupport({ value, onChange }) {
  return (
    <label className="field field--inline">
      <span className="field__label">Show facts stated in</span>
      <select className="field__control" value={value} onChange={(e) => onChange(Number(e.target.value))}>
        {OPTIONS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
      </select>
    </label>
  )
}
