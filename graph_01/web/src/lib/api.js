// HTTP wrapper around the Diabetes KG API.
// Dev: BASE is "/api" and Vite proxies it to the FastAPI service.
// Prod: set VITE_API_BASE at build time to the API's public URL.

const BASE = (import.meta.env.VITE_API_BASE || '/api').replace(/\/$/, '')

export class ApiError extends Error {
  constructor(kind, message) {
    super(message)
    this.kind = kind // 'network' | 'unavailable' | 'not_found' | 'http'
  }
}

async function request(path, { method = 'GET', body, signal } = {}) {
  let res
  try {
    res = await fetch(BASE + path, {
      method,
      signal,
      headers: body ? { 'Content-Type': 'application/json' } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    })
  } catch (e) {
    if (e.name === 'AbortError') throw e
    throw new ApiError('network', 'Cannot reach the API. Start it with: uvicorn api.main:app --port 8000')
  }
  const data = await res.json().catch(() => null)
  if (res.status === 503) throw new ApiError('unavailable', 'The Neo4j database is not running. Start it with: docker start neo4j-diabetes')
  if (res.status === 404) throw new ApiError('not_found', data?.detail || 'Not found.')
  if (!res.ok) throw new ApiError('http', data?.detail || `API error ${res.status}`)
  return data
}

const qs = (params) => {
  const s = new URLSearchParams()
  Object.entries(params).forEach(([k, v]) => v !== undefined && v !== null && v !== '' && s.set(k, v))
  return s.toString()
}

export const api = {
  health: () => request('/health'),
  stats: () => request('/stats'),
  search: (q, type, limit = 8, signal) => request(`/entities?${qs({ q, type, limit })}`, { signal }),
  entity: (name, minSupport = 0) => request(`/entities/${encodeURIComponent(name)}?${qs({ min_support: minSupport })}`),
  articles: (name, limit = 6) => request(`/entities/${encodeURIComponent(name)}/articles?${qs({ limit })}`),
  evidence: ({ subject, relation, object }) => request(`/evidence?${qs({ subject, relation, object })}`),
  symptomCheck: (symptoms, minSupport = 1) =>
    request('/symptom-check', { method: 'POST', body: { symptoms, min_support: minSupport } }),
  paths: (source, target) => request(`/paths?${qs({ source, target })}`),
}
