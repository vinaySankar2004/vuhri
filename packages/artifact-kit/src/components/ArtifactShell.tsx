import type {ReactNode} from 'react'

type ArtifactShellProps = {
  eyebrow?: string
  title: string
  description: string
  objective?: string
  children: ReactNode
  aside?: ReactNode
}

export function ArtifactShell({
  eyebrow = 'Learning artifact',
  title,
  description,
  objective,
  children,
  aside,
}: ArtifactShellProps) {
  return (
    <main className="artifact-shell">
      <header className="artifact-header">
        <div className="artifact-heading-copy">
          <p className="artifact-eyebrow">{eyebrow}</p>
          <h1>{title}</h1>
          <p className="artifact-description">{description}</p>
        </div>
        {objective ? (
          <div className="artifact-objective" aria-label="Learning objective">
            <span>Objective</span>
            <p>{objective}</p>
          </div>
        ) : null}
      </header>

      <div className={aside ? 'artifact-layout with-aside' : 'artifact-layout'}>
        <section className="artifact-workspace">{children}</section>
        {aside ? <aside className="artifact-aside">{aside}</aside> : null}
      </div>
    </main>
  )
}

