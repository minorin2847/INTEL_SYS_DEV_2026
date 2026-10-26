import { useEffect, useId, useRef, useState } from 'react'
import { api } from '../lib/api.js'
import { nfc, typeClass, typeLabel } from '../lib/labels.js'

// Accessible combobox over /entities. `onSelect(entity)` is called with {name, type}.
export default function SearchBox({ onSelect, placeholder = 'Search a symptom, drug, food, test…', label = 'Search the graph', size = 'md', type, autoFocus }) {
  const [q, setQ] = useState('')
  const [items, setItems] = useState([])
  const [open, setOpen] = useState(false)
  const [active, setActive] = useState(-1)
  const [loading, setLoading] = useState(false)
  const listId = useId()
  const inputRef = useRef(null)

  useEffect(() => {
    if (!open) return
    const ctrl = new AbortController()
    const t = setTimeout(() => {
      setLoading(true)
      api.search(q, type, 8, ctrl.signal)
        .then((r) => { setItems(r); setActive(r.length ? 0 : -1) })
        .catch((e) => e.name !== 'AbortError' && setItems([]))
        .finally(() => setLoading(false))
    }, 150)
    return () => { clearTimeout(t); ctrl.abort() }
  }, [q, open, type])

  const choose = (item) => {
    if (!item) return
    onSelect(item)
    setQ('')
    setOpen(false)
    inputRef.current?.blur()
  }

  const onKeyDown = (e) => {
    if (e.key === 'ArrowDown') { e.preventDefault(); setOpen(true); setActive((i) => Math.min(i + 1, items.length - 1)) }
    else if (e.key === 'ArrowUp') { e.preventDefault(); setActive((i) => Math.max(i - 1, 0)) }
    else if (e.key === 'Enter') { e.preventDefault(); choose(items[active]) }
    else if (e.key === 'Escape') { setOpen(false) }
  }

  const expanded = open && (items.length > 0 || (!loading && q))
  return (
    <div className={`search search--${size}`}>
      <label className="visually-hidden" htmlFor={`${listId}-input`}>{label}</label>
      <svg className="search__icon" viewBox="0 0 20 20" aria-hidden="true"><circle cx="9" cy="9" r="6" /><path d="m14 14 4 4" /></svg>
      <input
        id={`${listId}-input`}
        ref={inputRef}
        className="search__input"
        role="combobox"
        aria-expanded={!!expanded}
        aria-controls={listId}
        aria-autocomplete="list"
        aria-activedescendant={active >= 0 && expanded ? `${listId}-${active}` : undefined}
        autoComplete="off"
        spellCheck="false"
        autoFocus={autoFocus}
        placeholder={placeholder}
        value={q}
        onChange={(e) => { setQ(e.target.value); setOpen(true) }}
        onFocus={() => setOpen(true)}
        onBlur={() => setTimeout(() => setOpen(false), 120)}
        onKeyDown={onKeyDown}
      />
      {expanded && (
        <ul className="search__list" id={listId} role="listbox">
          {items.map((it, i) => (
            <li
              key={it.name}
              id={`${listId}-${i}`}
              role="option"
              aria-selected={i === active}
              className="search__option"
              onMouseDown={(e) => { e.preventDefault(); choose(it) }}
              onMouseEnter={() => setActive(i)}
            >
              <span className={`dot ${typeClass(it.type)}`} aria-hidden="true" />
              <span className="search__name">{nfc(it.name)}</span>
              <span className="search__type">{typeLabel(it.type)}</span>
            </li>
          ))}
          {!items.length && <li className="search__empty">No entity matches “{q}”.</li>}
        </ul>
      )}
    </div>
  )
}
