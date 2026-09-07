import React from 'react'

// One labelled input, driven by a /questions field spec.
// type: "choice" | "number" | "text" | "textarea"
export default function Field({ f, value, onChange, invalid }) {
  const wide = f.type === 'textarea' || f.type === 'text'
  return (
    <label className={`field${wide ? ' field--wide' : ''}${invalid ? ' field--invalid' : ''}`}>
      <span className="field__label">
        {f.label}
        {f.required && <span className="req" title="required">*</span>}
      </span>

      {f.type === 'choice' && (
        <select value={value ?? ''} onChange={(e) => onChange(f.field, e.target.value)}>
          <option value="">— not set —</option>
          {f.options.map((o) => (
            <option key={o} value={o}>{o}</option>
          ))}
        </select>
      )}

      {f.type === 'number' && (
        <input
          type="number" step="any" min={f.min} max={f.max} inputMode="decimal"
          value={value ?? ''}
          onChange={(e) => onChange(f.field, e.target.value)}
        />
      )}

      {f.type === 'text' && (
        <input
          type="text"
          value={value ?? ''}
          onChange={(e) => onChange(f.field, e.target.value)}
        />
      )}

      {f.type === 'textarea' && (
        <textarea
          rows={5}
          placeholder="What was your experience with the product?"
          value={value ?? ''}
          onChange={(e) => onChange(f.field, e.target.value)}
        />
      )}

      {f.note && <span className="field__note">{f.note}</span>}
    </label>
  )
}
