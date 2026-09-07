import React from 'react'

// Dropdown of real Sephora reviews from /samples. Selecting one fills the whole form.
export default function ExamplePicker({ examples, onPick }) {
  if (!examples?.length) return null
  return (
    <label className="picker">
      <span className="picker__lbl">Load a real review</span>
      <select
        defaultValue=""
        onChange={(e) => {
          const i = Number(e.target.value)
          if (Number.isInteger(i) && examples[i]) onPick(examples[i])
          e.target.selectedIndex = 0
        }}
      >
        <option value="" disabled>
          choose…
        </option>
        {examples.map((ex, i) => (
          <option key={i} value={i}>
            {ex._label}
          </option>
        ))}
      </select>
    </label>
  )
}
