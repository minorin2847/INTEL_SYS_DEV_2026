// Hash routing so every view is a shareable URL:
//   #/  ·  #/entity/<name>  ·  #/types/<name>  ·  #/symptoms  ·  #/paths?from=..&to=..
import { useEffect, useState } from 'react'

export function parseHash(hash = window.location.hash) {
  const [path, query = ''] = hash.replace(/^#/, '').split('?')
  const parts = path.split('/').filter(Boolean).map(decodeURIComponent)
  return { view: parts[0] || 'home', arg: parts[1] || null, params: Object.fromEntries(new URLSearchParams(query)) }
}

export function href(view, arg, params) {
  let h = `#/${view === 'home' ? '' : view}`
  if (arg) h += `/${encodeURIComponent(arg)}`
  if (params) {
    const q = new URLSearchParams(Object.entries(params).filter(([, v]) => v)).toString()
    if (q) h += `?${q}`
  }
  return h
}

export const go = (view, arg, params) => { window.location.hash = href(view, arg, params) }

export function useRoute() {
  const [route, setRoute] = useState(parseHash)
  useEffect(() => {
    const onChange = () => { setRoute(parseHash()); window.scrollTo({ top: 0 }) }
    window.addEventListener('hashchange', onChange)
    return () => window.removeEventListener('hashchange', onChange)
  }, [])
  return route
}
