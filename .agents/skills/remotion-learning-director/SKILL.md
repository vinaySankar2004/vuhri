---
name: remotion-learning-director
description: Direct, build, verify, and publish videos that teach a concept through meaningful motion. Use for vuhri learning videos, especially when an approved artifact brief or companion interactive lesson already exists. Do not use for promotional videos or footage-only editing.
---

# Remotion Learning Director

Turn a learning objective into a watchable, technically correct video whose motion explains sequence, ownership, state, causality, or comparison. `direct-video` supplies the direction artifacts, renderer choice, verification, and revision protocol. This skill adds the instructional layer.

## Start from the brief

If no approved artifact brief exists, use `direct-learning-artifact` first. Reuse what the brief, the companion lesson, and the active space already decided about purpose, audience, duration, visual language, narration, and delivery. Ask at most one focused question, and only when its answer would change the result and cannot be inferred safely.

## Direct for learning

Write the direction brief, beat sheet, and shot plan beside the artifact brief, with these constraints:

- Give each beat one conceptual job and state the learner inference it should produce.
- Use movement to reveal a relationship or state change, never only to decorate.
- Keep technical terms exact while explaining them in short spoken sentences.
- Coordinate narration, captions, and the active visual. Never make the learner read a paragraph while tracking animation.
- Prefer code-native diagrams, labels, packets, gates, timelines, and state transitions for software systems.
- Keep the companion lesson's visual language unless the user asks for a new one.
- Add a prediction, pause, contrast, or retrieval cue when it helps without breaking the flow.
- Cover meaningful drawbacks and failure states, not only the happy path.

Use specialist review perspectives internally when they expose a real instructional or visual risk. Do not add approval gates the user has already passed.

## Build

Follow `direct-video`'s rendering reference. Keep captions inside safe margins and away from the active diagram. Build the requested audio. If narration or music cannot be produced, report the limitation instead of substituting a different experience.

## Verify

Run `direct-video`'s verification on the complete render. Also confirm that the central learning objective and the important failure states survived the edit, and that narration, captions, and animation match the beat sheet. Enjoyment or assisted viewing is not evidence of understanding, so keep the planned independent check for a later session.

## Deliver

Give the learner a clickable link to the finished video or the lesson that embeds it, never a command to run. To embed it in a learning website, use `build-web-artifact`, then `verify-web-artifact`.
