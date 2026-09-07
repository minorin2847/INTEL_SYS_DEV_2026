// Tiny inline line chart. points: [{x, y}], with x,y already numeric.
export default function Sparkline({ points, width = 260, height = 54, marker }) {
  if (!points || points.length < 2) return null
  const xs = points.map((p) => p.x)
  const ys = points.map((p) => p.y)
  const minX = Math.min(...xs)
  const maxX = Math.max(...xs)
  const minY = Math.min(...ys)
  const maxY = Math.max(...ys)
  const sx = (x) => ((x - minX) / (maxX - minX || 1)) * (width - 6) + 3
  const sy = (y) => height - 4 - ((y - minY) / (maxY - minY || 1)) * (height - 8)
  const d = points.map((p, i) => `${i ? 'L' : 'M'}${sx(p.x)},${sy(p.y)}`).join(' ')
  return (
    <svg width={width} height={height} role="img" aria-label="trend">
      <path d={d} fill="none" stroke="#2f6feb" strokeWidth="2" />
      {marker != null && (
        <circle cx={sx(marker.x)} cy={sy(marker.y)} r="4" fill="#c0392b" />
      )}
    </svg>
  )
}
