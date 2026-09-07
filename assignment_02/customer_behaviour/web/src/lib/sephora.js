// Small presentational maps for the Sephora customer-behaviour client.
// No logic — just labels / glyphs so the UI reads nicely.

export const CATEGORY_GLYPH = {
  Cleansers: '🧼',
  'Eye Care': '👁️',
  'High Tech Tools': '🔌',
  'Lip Balms & Treatments': '💋',
  Masks: '🧖',
  'Mini Size': '🧴',
  Moisturizers: '💧',
  'Self Tanners': '🌤️',
  Sunscreen: '☀️',
  Treatments: '🧪',
  'Value & Gift Sets': '🎁',
  Wellness: '🌿',
}

export const SKIN_TYPE_GLYPH = {
  dry: '🏜️',
  combination: '🔀',
  normal: '🙂',
  oily: '💦',
}

export function priceTier(p) {
  if (p == null || Number.isNaN(Number(p))) return null
  const n = Number(p)
  if (n < 25) return 'budget'
  if (n < 55) return 'mid-range'
  return 'premium'
}

export function titleCase(s) {
  return String(s || '')
    .replace(/[_-]+/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase())
}

// /samples example row -> flat values map for the form
export function exampleToValues(ex, defaults = {}) {
  const out = { ...defaults }
  for (const [k, v] of Object.entries(ex)) {
    if (k.startsWith('_')) continue
    out[k] = v ?? ''
  }
  return out
}
