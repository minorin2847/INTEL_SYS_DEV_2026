import { useState } from 'react'
import { api } from '../lib/api.js'
import { href } from '../lib/route.js'
import { articles, nfc, relHeading } from '../lib/labels.js'
import { useAsync } from '../lib/useAsync.js'
import { Empty, ErrorNote, Spinner } from './Feedback.jsx'
import FactGroup from './FactGroup.jsx'
import MinSupport from './MinSupport.jsx'
import NeighbourGraph from './NeighbourGraph.jsx'
import TypePill from './TypePill.jsx'

// Everything the graph knows about one entity: its facts grouped by relation,
// a drawing of its neighbourhood, and the articles that mention it.
export default function EntityView({ name, compactHeader = false }) {
  const [minSupport, setMinSupport] = useState(2)
  const { data, error, loading } = useAsync(() => api.entity(name, minSupport), [name, minSupport])
  const mentions = useAsync(() => api.articles(name, 6), [name])

  if (error) {
    return (
      <div className="card">
        <ErrorNote error={error} />
        {error.kind === 'not_found' && <p><a href={href('home')}>Back to search</a></p>}
      </div>
    )
  }
  if (!data) return <Spinner label={`Loading ${name}…`} />

  const groups = groupFacts(data.facts, name)
  return (
    <div className="stack">
      <header className={`entity-head ${compactHeader ? 'entity-head--compact' : ''}`}>
        <div className="entity-head__title">
          {!compactHeader && <h1>{nfc(data.name)}</h1>}
          <TypePill type={data.type} />
        </div>
        <dl className="kv">
          <div><dt>Mentioned in</dt><dd>{articles(data.mentioned_in)}</dd></div>
          <div><dt>Facts shown</dt><dd>{data.facts.length}</dd></div>
          {data.threshold && <div><dt>Diagnostic threshold</dt><dd>{data.threshold}</dd></div>}
        </dl>
        <MinSupport value={minSupport} onChange={setMinSupport} />
      </header>
      <p className="hint">
        Each fact was extracted from Vinmec articles; the bar shows how many different articles state it. “Reference” facts
        (drug classes, organs) are general medical classifications added by hand.
      </p>

      <div className={`entity-grid ${loading ? 'is-refreshing' : ''}`}>
        <div className="stack">
          {groups.length === 0 && (
            <div className="card"><Empty>No facts reach this level of evidence. Choose “All facts” to see weaker ones.</Empty></div>
          )}
          {groups.map((g) => <FactGroup key={g.key} title={g.title} facts={g.facts} focus={name} />)}
        </div>
        <aside className="stack entity-grid__side">
          {data.facts.length > 0 && (
            <section className="card">
              <h2>Neighbourhood</h2>
              <NeighbourGraph name={data.name} type={data.type} facts={data.facts} />
            </section>
          )}
          <section className="card">
            <h2>Articles mentioning it</h2>
            {mentions.loading && <Spinner />}
            <ErrorNote error={mentions.error} />
            {mentions.data && mentions.data.length === 0 && <Empty>No article mentions this entity.</Empty>}
            {mentions.data && (
              <ul className="source-list">
                {mentions.data.map((a) => (
                  <li key={a.url}>
                    <a href={a.url} target="_blank" rel="noreferrer">{a.title}</a>
                    {a.date && <span className="source-list__date">{a.date.slice(0, 10)}</span>}
                  </li>
                ))}
              </ul>
            )}
          </section>
        </aside>
      </div>
    </div>
  )
}

function groupFacts(facts, focus) {
  const map = new Map()
  for (const f of facts) {
    const dir = f.subject === focus ? 'out' : 'in'
    const key = `${f.relation}:${dir}`
    if (!map.has(key)) map.set(key, { key, title: relHeading(f.relation, dir), facts: [], weight: 0 })
    const g = map.get(key)
    g.facts.push(f)
    g.weight += f.support + 1
  }
  return [...map.values()].sort((a, b) => b.weight - a.weight)
}
