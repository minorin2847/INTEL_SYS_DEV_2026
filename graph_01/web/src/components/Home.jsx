import { useState } from 'react'
import { api } from '../lib/api.js'
import { go, href } from '../lib/route.js'
import { TYPES, fmtInt, nfc, typeClass } from '../lib/labels.js'
import { useAsync } from '../lib/useAsync.js'
import { ErrorNote, Spinner } from './Feedback.jsx'
import SearchBox from './SearchBox.jsx'
import { DIABETES_TYPES } from './TypesView.jsx'

const QUICK = ['Metformin', 'HbA1c', 'Bệnh võng mạc', 'Khát nhiều', 'Thừa cân, béo phì', 'Đồ ngọt, bánh kẹo']
const roman = ['i', 'ii', 'iii', 'iv', 'v', 'vi']

export default function Home() {
  const stats = useAsync(() => api.stats(), [])
  const [kind, setKind] = useState(null)
  const entries = useAsync(() => (kind ? api.search('', kind, 100) : Promise.resolve([])), [kind])
  return (
    <div className="stack stack--lg">
      <section className="hero">
        <span className="eyebrow"><b>Vol. 1</b> · Charted from Vinmec</span>
        <h1>An atlas of what we <em>know</em> about diabetes.</h1>
        <p className="lead">
          Symptoms, causes, complications, tests, drugs and diet advice, mapped from
          {stats.data ? ` ${fmtInt(stats.data.articles)} ` : ' '}Vinmec health articles. Every entry cites the articles behind it.
        </p>
        <SearchBox size="lg" placeholder="Look up a drug, symptom, food…" onSelect={(e) => go('entity', e.name)} />
        <div className="chips chips--center">
          {QUICK.map((q) => <a key={q} className="chip" href={href('entity', q)}>{q}</a>)}
        </div>
      </section>

      <ErrorNote error={stats.error} />
      {stats.data && (
        <section className="tiles" aria-label="Atlas size">
          <Tile value={stats.data.facts} label="facts" />
          <Tile value={stats.data.nodes.reduce((s, n) => s + n.n, 0)} label="entries" />
          <Tile value={stats.data.articles} label="sources" />
          <Tile value={stats.data.relations.length} label="link kinds" />
        </section>
      )}

      <section className="stack">
        <h2 className="section-title"><span className="eyebrow">Part I</span>Begin with a type</h2>
        <div className="cards">
          {DIABETES_TYPES.map((t, i) => (
            <a key={t.name} href={href('types', t.name)} className="card--link">
              <span className="num" aria-hidden="true">{roman[i]}.</span>
              <strong>{t.short}</strong>
              <span className="card__note">{t.note}</span>
            </a>
          ))}
        </div>
      </section>

      {stats.data && (
        <section className="stack">
          <h2 className="section-title"><span className="eyebrow">Part II</span>Legend of entries</h2>
          <div className="chips">
            {stats.data.nodes.map((n) => (
              <button key={n.name} type="button" className={`chip ${typeClass(n.name)}`} aria-pressed={kind === n.name}
                onClick={() => setKind(kind === n.name ? null : n.name)}>
                <span className="dot" aria-hidden="true" />{TYPES[n.name]?.plural || n.name} · {n.n}
              </button>
            ))}
          </div>
          {kind && (
            <div className={`legend-list ${typeClass(kind)}`} aria-live="polite">
              {entries.loading && <Spinner />}
              <ErrorNote error={entries.error} />
              <ul>
                {entries.data?.map((e) => (
                  <li key={e.name}><a href={href('entity', e.name)}>{nfc(e.name)}</a></li>
                ))}
              </ul>
            </div>
          )}
        </section>
      )}

      <details className="how">
        <summary>Surveyor’s notes: how this atlas was compiled</summary>
        <ol>
          <li>Diabetes articles were collected from the vinmec.com sitemap and filtered by how often they really discuss diabetes.</li>
          <li>Each article was split into sections. A section heading such as “Triệu chứng” or “Điều trị” decides what kind of fact may be read from it.</li>
          <li>Mentions of known symptoms, drugs, tests, foods… were matched in those sections and counted per article.</li>
          <li>A fact is kept only when at least two different articles state it (or an official Vinmec disease page does).</li>
        </ol>
        <p>On a random sample of 50 facts, 48 were correct. Reading material only — not medical advice.</p>
      </details>
    </div>
  )
}

function Tile({ value, label }) {
  return (
    <div className="tile">
      <span className="tile__value">{fmtInt(value)}</span>
      <span className="tile__label">{label}</span>
    </div>
  )
}
