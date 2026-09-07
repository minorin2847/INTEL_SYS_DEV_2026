export default function Collapsible({ summary, children, open = false }) {
  return (
    <details className="collapsible" open={open}>
      <summary>{summary}</summary>
      <div className="spacer" />
      {children}
    </details>
  )
}
