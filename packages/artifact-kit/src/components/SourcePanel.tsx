type Source = {
  label: string
  detail?: string
}

type SourcePanelProps = {
  sources: Source[]
  note?: string
}

export function SourcePanel({sources, note}: SourcePanelProps) {
  return (
    <details className="source-panel">
      <summary>Sources and assumptions</summary>
      <ul>
        {sources.map((source) => (
          <li key={`${source.label}-${source.detail ?? ''}`}>
            <strong>{source.label}</strong>
            {source.detail ? <span>{source.detail}</span> : null}
          </li>
        ))}
      </ul>
      {note ? <p>{note}</p> : null}
    </details>
  )
}

