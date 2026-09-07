export const pct = (x, digits = 0) =>
  x == null || Number.isNaN(x) ? '--' : `${(x * 100).toFixed(digits)}%`

export const points = (x) =>
  x == null ? '--' : `${x >= 0 ? '+' : ''}${Math.round(x * 100)}`

export const bandColor = (band) =>
  ({ Low: '#1a8a4a', Moderate: '#b7791f', High: '#c0392b' }[band] || '#556')

export const bandTint = (band) =>
  ({ Low: '#e6f4ec', Moderate: '#fbf0dc', High: '#fbe7e4' }[band] || '#eef')

export function timeAgo(ts) {
  const d = new Date(ts * 1000)
  const diff = (Date.now() - d.getTime()) / 1000
  if (diff < 60) return 'just now'
  if (diff < 3600) return `${Math.floor(diff / 60)} min ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)} h ago`
  return d.toLocaleString()
}

// short human sentence for a modifiable what-if factor (row label)
export function whatifSentence(f) {
  const map = {
    Smoker: 'If you had never smoked regularly',
    HvyAlcoholConsump: 'If you were not a heavy drinker',
    PhysActivity: 'If you were physically active',
    Fruits: 'If you ate fruit daily',
    Veggies: 'If you ate vegetables daily',
    BMI: 'At a lower BMI',
  }
  return map[f.feature] || `If ${f.label} were at its healthier value`
}

// imperative phrase for a counterfactual change, with its concrete target
export function cfPhrase(c) {
  if (c.feature === 'BMI') return `reach a BMI of about ${Math.round(c.to)}`
  return (
    {
      Smoker: 'stop smoking',
      HvyAlcoholConsump: 'cut back from heavy drinking',
      PhysActivity: 'become physically active',
      Fruits: 'eat fruit daily',
      Veggies: 'eat vegetables daily',
    }[c.feature] || `set ${c.label} to its healthier value`
  )
}

// collapse repeated changes to the same feature (e.g. two BMI steps) into one,
// keeping the final target value
export function dedupeChanges(changes) {
  const byFeat = new Map()
  for (const c of changes || []) byFeat.set(c.feature, { ...(byFeat.get(c.feature) || {}), ...c })
  return [...byFeat.values()]
}
