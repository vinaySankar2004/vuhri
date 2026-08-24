type PredictionPromptProps = {
  question: string
  choices: string[]
  selected?: string
  onSelect: (choice: string) => void
}

export function PredictionPrompt({
  question,
  choices,
  selected,
  onSelect,
}: PredictionPromptProps) {
  return (
    <fieldset className="prediction-prompt">
      <legend>{question}</legend>
      <div className="prediction-choices">
        {choices.map((choice) => (
          <button
            className={selected === choice ? 'choice selected' : 'choice'}
            key={choice}
            onClick={() => onSelect(choice)}
            type="button"
            aria-pressed={selected === choice}
          >
            {choice}
          </button>
        ))}
      </div>
    </fieldset>
  )
}

