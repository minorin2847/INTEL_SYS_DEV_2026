// HTTP wrapper around the customer-behaviour API.
// Dev: BASE is "/api" and Vite proxies it to the FastAPI service on :8000.
// Prod: set VITE_API_BASE at build time to the API's public URL.

const BASE = (import.meta.env.VITE_API_BASE || '/api').replace(/\/$/, '')

export class ApiError extends Error {
  constructor(kind, message, payload) {
    super(message)
    this.kind = kind
    this.payload = payload
  }
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
    return errs.map((e) => `${(e.loc || []).slice(1).join('.')}: ${e.msg}`).join('; ')
  }
  return 'The API rejected the input.'
}

async function request(path, { method = 'GET', body } = {}) {
  let res
  try {
    res = await fetch(BASE + path, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: body === undefined ? undefined : JSON.stringify(body),
    })
  } catch {
    throw new ApiError('network', `Cannot reach the API (${BASE}). Is it running on :8000?`)
  }
  const text = await res.text()
  const data = text ? safeJson(text) : null
  if (res.status === 422) throw new ApiError('validation', humanizeValidation(data), data)
  if (!res.ok) {
    const detail = data && data.detail ? data.detail : res.statusText
    throw new ApiError('http', `API error ${res.status}: ${detail}`, data)
  }
  return data
}

export const api = {
  health: () => request('/healthz'),
  questions: () => request('/questions'),
  samples: () => request('/samples'),
  modelInfo: () => request('/model-info'),
  predict: (payload) => request('/predict', { method: 'POST', body: payload }),
}
