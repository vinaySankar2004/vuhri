type LegendItem = {
  label: string
  description: string
  tone: 'idle' | 'active' | 'complete' | 'warning'
}

type StateLegendProps = {
  items: LegendItem[]
}

export function StateLegend({items}: StateLegendProps) {
  return (
    <div className="state-legend" aria-label="State legend">
      {items.map((item) => (
        <div className="legend-item" key={item.label}>
          <span className={`legend-swatch ${item.tone}`} aria-hidden="true" />
          <span>
            <strong>{item.label}</strong>
            <small>{item.description}</small>
          </span>
        </div>
      ))}
    </div>
  )
}

