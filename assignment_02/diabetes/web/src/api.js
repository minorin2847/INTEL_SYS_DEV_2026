// HTTP wrapper around the diabetes screening API.
// Dev: BASE is "/api" and Vite proxies it to the FastAPI service.
// Prod: set VITE_API_BASE at build time to the API's public URL.

const BASE = (import.meta.env.VITE_API_BASE || '/api').replace(/\/$/, '')

async function request(path, { method = 'GET', body, headers } = {}) {
  let res
  try {
    res = await fetch(BASE + path, {
      method,
      headers: { 'Content-Type': 'application/json', ...(headers || {}) },
      body: body === undefined ? undefined : JSON.stringify(body),
    })
  } catch (e) {
    throw new ApiError('network', `Cannot reach the API (${BASE}). Is it running?`)
  }
  const text = await res.text()
  const data = text ? safeJson(text) : null
  if (res.status === 422) {
    throw new ApiError('validation', humanizeValidation(data), data)
  }
  if (!res.ok) {
    const detail = data && data.detail ? data.detail : res.statusText
    throw new ApiError('http', `API error ${res.status}: ${detail}`, data)
  }
  return data
}

function safeJson(t) {
  try {
    return JSON.parse(t)
  } catch {
    return null
  }
}

function humanizeValidation(data) {
  const errs = data && data.detail
  if (Array.isArray(errs) && errs.length) {
    return errs
      .map((e) => `${(e.loc || []).slice(1).join('.')}: ${e.msg}`)
      .join('; ')
  }
  return 'The API rejected the input.'
}

export class ApiError extends Error {
  constructor(kind, message, payload) {
    super(message)
    this.kind = kind
    this.payload = payload
  }
}

export const api = {
  health: () => request('/healthz'),
  questions: () => request('/questions'),
  predict: (payload, include = 'explain,similar,whatif,counterfactual', { log = true } = {}) =>
    request(
      `/predict?include=${encodeURIComponent(include)}${log ? '' : '&log=false'}`,
      { method: 'POST', body: payload },
    ),
  history: (session, limit = 50) =>
    request(`/history?session=${encodeURIComponent(session)}&limit=${limit}`),
  metrics: () => request('/metrics'),
  thresholdCurve: (split = 'val', grid = 49) =>
    request(`/threshold-curve?split=${split}&grid=${grid}`),
  thresholdRecommend: (objective = 'recall', target = 0.9) =>
    request(`/threshold-recommend?objective=${objective}&target=${target}`),
  getConfig: () => request('/config'),
  setThresholds: (moderate_cut, high_cut, adminKey) =>
    request('/config/thresholds', {
      method: 'POST',
      body: { moderate_cut, high_cut },
      headers: { 'X-Admin-Key': adminKey },
    }),
}
