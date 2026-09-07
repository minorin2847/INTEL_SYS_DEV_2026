import React, { useEffect, useState } from 'react'

// Light / Dark / System. Persists to localStorage and stamps data-theme on <html>;
// "system" removes the attribute so prefers-color-scheme takes over.
const OPTIONS = [
  ['system', 'Auto', '◐'],
  ['light', 'Light', '☀'],
  ['dark', 'Dark', '☾'],
]

function apply(mode) {
  const root = document.documentElement
  if (mode === 'system') root.removeAttribute('data-theme')
  else root.setAttribute('data-theme', mode)
}

export default function ThemeToggle() {
  const [mode, setMode] = useState(() => {
    try {
      return localStorage.getItem('cb-theme') || 'system'
    } catch {
      return 'system'
    }
  })

  useEffect(() => {
    apply(mode)
    try {
      localStorage.setItem('cb-theme', mode)
    } catch {
      /* private mode — ignore */
    }
  }, [mode])

  return (
    <div className="theme-toggle" role="group" aria-label="Colour theme">
      {OPTIONS.map(([value, label, glyph]) => (
        <button
          key={value}
          type="button"
          className={`theme-toggle__btn${mode === value ? ' is-active' : ''}`}
          aria-pressed={mode === value}
          title={`${label} theme`}
          onClick={() => setMode(value)}
        >
          <span aria-hidden="true">{glyph}</span>
          <span className="theme-toggle__label">{label}</span>
        </button>
      ))}
    </div>
  )
}
