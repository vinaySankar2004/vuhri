type StepControlsProps = {
  step: number
  total: number
  onBack: () => void
  onNext: () => void
  onReset: () => void
}

export function StepControls({
  step,
  total,
  onBack,
  onNext,
  onReset,
}: StepControlsProps) {
  return (
    <div className="step-controls" aria-label="Artifact steps">
      <button onClick={onBack} type="button" disabled={step <= 0}>
        Back
      </button>
      <div className="step-position" aria-live="polite">
        <span>Step</span>
        <strong>{step + 1}</strong>
        <span>of {total}</span>
      </div>
      <button onClick={onNext} type="button" disabled={step >= total - 1}>
        Next
      </button>
      <button className="quiet" onClick={onReset} type="button">
        Reset
      </button>
    </div>
  )
}

