import { typeClass, typeLabel } from '../lib/labels.js'

export default function TypePill({ type }) {
  return (
    <span className={`pill pill--type ${typeClass(type)}`}>
      <span className="dot" aria-hidden="true" />
      {typeLabel(type)}
    </span>
  )
}
