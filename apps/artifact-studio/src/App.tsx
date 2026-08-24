import {useState} from 'react'
import {
  ArtifactShell,
  PredictionPrompt,
  SourcePanel,
  StateLegend,
  StepControls,
  clampStep,
} from '@hubtolearn/artifact-kit'

const states = [
  {
    title: 'Begin at course A',
    copy: 'A enters the current DFS path. It is active but not complete.',
    nodes: ['active', 'idle', 'idle'],
  },
  {
    title: 'Follow A to B',
    copy: 'B joins the same active path. A remains active while its call waits.',
    nodes: ['active', 'active', 'idle'],
  },
  {
    title: 'Finish B',
    copy: 'B has no remaining dependency. It leaves the path and becomes complete.',
    nodes: ['active', 'complete', 'idle'],
  },
  {
    title: 'Follow A to C',
    copy: 'C becomes active. Reaching completed B from here would be safe.',
    nodes: ['active', 'complete', 'active'],
  },
  {
    title: 'Finish the search',
    copy: 'Every node is complete. No edge returned to a node in the active path.',
    nodes: ['complete', 'complete', 'complete'],
  },
]

export function App() {
  const [step, setStep] = useState(0)
  const [prediction, setPrediction] = useState<string>()
  const current = states[step]

  function reset() {
    setStep(0)
    setPrediction(undefined)
  }

  return (
    <>
      <nav className="studio-nav" aria-label="Artifact Studio navigation">
        <a className="brand" href="#top" aria-label="HubToLearn Artifact Studio home">
          <span className="brand-mark" aria-hidden="true">H</span>
          <span>HubToLearn</span>
        </a>
        <div className="nav-status">
          <span className="status-dot" aria-hidden="true" />
          Local artifact studio
        </div>
      </nav>

      <div id="top">
        <ArtifactShell
          eyebrow="Artifact kit preview"
          title="Build explanations you can touch."
          description="This studio hosts small learning tools with visible state, deliberate interaction, and a check outside the interface."
          objective="Predict how DFS state changes, then explain why a completed node is safe to revisit."
          aside={
            <>
              <div className="aside-card">
                <p className="aside-label">What good means</p>
                <ul className="principle-list">
                  <li>The learner acts before the answer appears.</li>
                  <li>State changes remain visible.</li>
                  <li>Reset restores the entire activity.</li>
                  <li>Sources and simplifications stay close.</li>
                </ul>
              </div>
              <SourcePanel
                sources={[
                  {label: 'Preview only', detail: 'A small directed acyclic graph'},
                  {label: 'Model', detail: 'Three-state DFS cycle detection'},
                ]}
                note="A real artifact would link its authoritative concept sources and learner evidence."
              />
            </>
          }
        >
          <section className="demo-card" aria-labelledby="demo-title">
            <div className="demo-heading">
              <div>
                <p className="section-kicker">Directed graph · DFS trace</p>
                <h2 id="demo-title">{current.title}</h2>
              </div>
              <span className="demo-badge">Component preview</span>
            </div>

            <div className="graph-stage" aria-label="Graph with courses A, B, and C">
              <svg className="edges" viewBox="0 0 620 240" aria-hidden="true">
                <path d="M 185 120 C 260 40, 355 40, 430 82" />
                <path d="M 185 120 C 260 200, 355 200, 430 158" />
              </svg>
              {['A', 'B', 'C'].map((node, index) => (
                <div
                  className={`graph-node node-${node.toLowerCase()} ${current.nodes[index]}`}
                  key={node}
                  aria-label={`Course ${node}: ${current.nodes[index]}`}
                >
                  <span>Course</span>
                  <strong>{node}</strong>
                  <small>{current.nodes[index]}</small>
                </div>
              ))}
            </div>

            <p className="state-copy" aria-live="polite">{current.copy}</p>

            <StateLegend
              items={[
                {label: 'Unvisited', description: 'not entered', tone: 'idle'},
                {label: 'Visiting', description: 'on current path', tone: 'active'},
                {label: 'Visited', description: 'fully complete', tone: 'complete'},
              ]}
            />

            <StepControls
              step={step}
              total={states.length}
              onBack={() => setStep((value) => clampStep(value - 1, states.length))}
              onNext={() => setStep((value) => clampStep(value + 1, states.length))}
              onReset={reset}
            />
          </section>

          <PredictionPrompt
            question="If C points to completed B, is that edge a cycle?"
            choices={['Yes, B was seen before', 'No, B has left the active path']}
            selected={prediction}
            onSelect={setPrediction}
          />

          {prediction ? (
            <div className={prediction.startsWith('No') ? 'feedback correct' : 'feedback revise'} aria-live="polite">
              <span>{prediction.startsWith('No') ? 'Ready to explain' : 'Look at the active path'}</span>
              <p>
                {prediction.startsWith('No')
                  ? 'Correct. A completed node can be shared by several paths. Only an edge to an active node closes a DFS cycle.'
                  : 'Seen before is insufficient. A cycle requires B to remain active in the current recursion path.'}
              </p>
            </div>
          ) : null}
        </ArtifactShell>
      </div>
    </>
  )
}

