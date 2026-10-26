import { useEffect, useState } from 'react'
import { api } from './lib/api.js'
import { useRoute } from './lib/route.js'
import EntityView from './components/EntityView.jsx'
import Header from './components/Header.jsx'
import Home from './components/Home.jsx'
import PathFinder from './components/PathFinder.jsx'
import SymptomChecker from './components/SymptomChecker.jsx'
import TypesView from './components/TypesView.jsx'

export default function App() {
  const { view, arg, params } = useRoute()
  const [offline, setOffline] = useState(null)

  useEffect(() => {
    api.health().then(() => setOffline(null)).catch((e) => setOffline(e.message))
  }, [])

  useEffect(() => {
    document.title = arg ? `${arg} · Glyco Atlas` : 'Glyco Atlas — a field guide to diabetes'
  }, [arg])

  return (
    <div className="app">
      <a className="skip-link" href="#main">Skip to content</a>
      <Header view={view} />
      <div className="main">
        {offline && (
          <div className="banner" role="alert">
            <span>{offline}</span>
            <button type="button" className="btn btn--ghost btn--sm" onClick={() => setOffline(null)}>Dismiss</button>
          </div>
        )}
        <main id="main" className="page">
          {view === 'entity' && arg && <EntityView key={arg} name={arg} />}
          {view === 'types' && <TypesView name={arg} />}
          {view === 'symptoms' && <SymptomChecker />}
          {view === 'paths' && <PathFinder from={params.from} to={params.to} />}
          {!['entity', 'types', 'symptoms', 'paths'].includes(view) && <Home />}
        </main>
        <footer className="footer">
          Charted from public Vinmec health articles · Neo4j graph · Reading material only, not medical advice.
        </footer>
      </div>
    </div>
  )
}
