# Learning artifacts

An artifact exists to support a defined learning action. Visual novelty alone is insufficient.

## Decision

Before building, state the concept, learning objective, learner action, misconception or difficulty, reason for the format, source basis, and success evidence. Prefer a small example, trace, sketch, or table when it can do the job.

## Lifecycle

```text
learning need
  -> brief
  -> build
  -> technical verification
  -> instructional verification
  -> learner use
  -> revision or archive
```

Useful states are `draft`, `built`, `technically-verified`, `instructionally-verified`, `used`, `revised`, and `archived`.

## Interactive websites

Build from the shared artifact kit when its primitives fit. Keep domain logic local to the artifact. Promote a new shared component only after real reuse or a clear repeated need.

Verification has four lanes:

- Build integrity
- Interaction integrity
- Visual and accessibility integrity
- Instructional integrity

Run the application in a real browser. Exercise expected paths, incorrect actions, reset, edge cases, keyboard use, responsive layouts, and browser errors. Confirm that the displayed state and feedback match the underlying concept.

## Video

Educational direction and technical Remotion construction are separate concerns. The general `direct-video` skill defines editable direction artifacts and stable revision targets. The `remotion-learning-director` skill adds the learning objective, misconception, prediction or retrieval moment, source requirements, and companion learning check. Official Remotion skills handle technical creation and rendering.

Rendered video verification should inspect frames, pacing, captions, audio, clipping, synchronization, accuracy, distracting motion, and alignment with the approved beat sheet and shot plan. Run technical checks against the actual exported media and preserve metadata, sampled frames, stable-ID shot frames, contact sheets, diagnostics, and a visual-review record. Automated checks do not stand in for agent playback and visual inspection.
