import { go, href } from '../lib/route.js'
import SearchBox from './SearchBox.jsx'

const NAV = [
  ['types', 'Diabetes types'],
  ['symptoms', 'Symptom finder'],
  ['paths', 'Trace a link'],
]

// Left-hand rail: wordmark, numbered chapters, and a search that is always at hand.
export default function Header({ view }) {
  return (
    <header className="rail">
      <a href={href('home')} className="brand" aria-label="Glyco Atlas — home">
        <span className="brand__mark">
          <svg viewBox="0 0 48 48" aria-hidden="true" className="brand__logo">
            <circle className="ring" cx="24" cy="24" r="21" />
            <path className="spoke" d="M24 24 11 14M24 24l15-8M24 24 16 39M24 24l12 14" />
            <circle className="sat" cx="11" cy="14" r="3.5" /><circle className="sat" cx="39" cy="16" r="3.5" />
            <circle className="sat" cx="16" cy="39" r="3.5" /><circle className="sat" cx="36" cy="38" r="3.5" />
            <circle className="hub" cx="24" cy="24" r="7" />
          </svg>
          <span className="brand__name">Glyco<em>Atlas</em></span>
        </span>
        <p className="brand__tag">A field guide to diabetes, charted from Vinmec articles.</p>
      </a>
      <nav className="nav" aria-label="Main">
        {NAV.map(([v, label], i) => (
          <a key={v} href={href(v)} className="nav__link" aria-current={view === v ? 'page' : undefined}>
            <span className="num" aria-hidden="true">0{i + 1}</span>{label}
          </a>
        ))}
      </nav>
      {view !== 'home' && (
        <div className="rail__search">
          <span className="eyebrow">Look up</span>
          <SearchBox size="sm" placeholder="drug, symptom, food…" onSelect={(e) => go('entity', e.name)} />
        </div>
      )}
    </header>
  )
}
