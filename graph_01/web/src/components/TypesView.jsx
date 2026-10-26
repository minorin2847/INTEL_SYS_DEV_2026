import { href } from '../lib/route.js'
import EntityView from './EntityView.jsx'

export const DIABETES_TYPES = [
  { name: 'Đái tháo đường', short: 'Diabetes (general)', note: 'Facts from articles that do not name a specific type.' },
  { name: 'Đái tháo đường type 1', short: 'Type 1', note: 'Autoimmune: the body destroys its own insulin-producing cells; usually starts young.' },
  { name: 'Đái tháo đường type 2', short: 'Type 2', note: 'The body stops responding well to insulin; linked to weight, age and lifestyle.' },
  { name: 'Đái tháo đường thai kỳ', short: 'Gestational', note: 'High blood sugar that appears during pregnancy.' },
  { name: 'Tiền đái tháo đường', short: 'Prediabetes', note: 'Blood sugar above normal but below the diabetes threshold.' },
]

// One tab per diabetes type; the content is the normal entity page of that type.
export default function TypesView({ name }) {
  const current = DIABETES_TYPES.find((t) => t.name === name) || DIABETES_TYPES[2]
  return (
    <div className="stack">
      <div>
        <h1>Diabetes types</h1>
        <p className="lead">Compare what Vinmec articles say about each type of diabetes.</p>
      </div>
      <nav className="tabs" aria-label="Diabetes type">
        {DIABETES_TYPES.map((t) => (
          <a key={t.name} href={href('types', t.name)} className="tabs__tab" aria-current={t.name === current.name ? 'page' : undefined}>
            {t.short}
          </a>
        ))}
      </nav>
      <p className="hint"><strong>{current.name}.</strong> {current.note}</p>
      <EntityView key={current.name} name={current.name} compactHeader />
    </div>
  )
}
