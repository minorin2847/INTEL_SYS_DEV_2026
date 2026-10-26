import { api } from '../lib/api.js'
import { go, href } from '../lib/route.js'
import { nfc, relVerb } from '../lib/labels.js'
import { useAsync } from '../lib/useAsync.js'
import { Empty, ErrorNote, Spinner } from './Feedback.jsx'
import SearchBox from './SearchBox.jsx'
import TypePill from './TypePill.jsx'

const EXAMPLES = [
  ['Thừa cân, béo phì', 'Thận'],
  ['Metformin', 'Hạ đường huyết'],
  ['Đái tháo đường thai kỳ', 'Mắt'],
]

// How are two entities connected? Shortest chains of facts between them.
export default function PathFinder({ from, to }) {
  const set = (key, value) => go('paths', null, { from, to, [key]: value })
  const ready = from && to && from !== to
  const result = useAsync(() => (ready ? api.paths(from, to) : Promise.resolve(null)), [from, to])

  return (
    <div className="stack">
      <div>
        <h1>Trace a link</h1>
        <p className="lead">Pick two entities to see the shortest chains of facts that link them, for example from a risk factor to the organ it ends up damaging.</p>
      </div>
      <section className="card path-form">
        <Endpoint label="From" value={from} onSelect={(e) => set('from', e.name)} />
        <span className="path-form__arrow" aria-hidden="true">→</span>
        <Endpoint label="To" value={to} onSelect={(e) => set('to', e.name)} />
      </section>

      {!from && !to && (
        <div className="card">
          <h2>Try</h2>
          <div className="chips">
            {EXAMPLES.map(([a, b]) => (
              <a key={a + b} className="chip" href={href('paths', null, { from: a, to: b })}>{a} → {b}</a>
            ))}
          </div>
        </div>
      )}
      {from && to && from === to && <ErrorNote error={{ message: 'Choose two different entities.' }} />}
      {ready && result.loading && <Spinner label="Searching the graph…" />}
      <ErrorNote error={result.error} />
      {ready && result.data && (
        <section className="card" aria-live="polite">
          <h2>{result.data.length ? `${result.data.length} shortest chain${result.data.length > 1 ? 's' : ''}` : 'No connection'}</h2>
          {result.data.length === 0 && <Empty>These entities are not connected within four steps.</Empty>}
          <ol className="paths">
            {result.data.map((p, i) => (
              <li key={i} className="path">
                {p.nodes.map((n, j) => (
                  <span key={n.name} className="path__step">
                    {j > 0 && <span className="path__rel">{relVerb(p.relations[j - 1], p.forward[j - 1])}</span>}
                    <a href={href('entity', n.name)} className="path__node">{nfc(n.name)}</a>
                  </span>
                ))}
              </li>
            ))}
          </ol>
          <p className="hint">Each step is one fact from the graph, read from left to right.</p>
        </section>
      )}
    </div>
  )
}

function Endpoint({ label, value, onSelect }) {
  return (
    <div className="endpoint">
      <span className="field__label">{label}</span>
      {value ? (
        <div className="endpoint__value">
          <a href={href('entity', value)}>{value}</a>
        </div>
      ) : (
        <span className="endpoint__value endpoint__value--empty">Not chosen</span>
      )}
      <SearchBox size="sm" label={`${label} entity`} placeholder={value ? 'Change…' : 'Search…'} onSelect={onSelect} />
    </div>
  )
}
