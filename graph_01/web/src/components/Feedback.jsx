// Small shared states: loading, error, empty.

export function Spinner({ label = 'Loading…' }) {
  return (
    <p className="status" role="status">
      <span className="spinner" aria-hidden="true" />
      {label}
    </p>
  )
}

export function ErrorNote({ error }) {
  if (!error) return null
  return <p className="error-note" role="alert">{error.message || String(error)}</p>
}

export function Empty({ children }) {
  return <p className="empty">{children}</p>
}
