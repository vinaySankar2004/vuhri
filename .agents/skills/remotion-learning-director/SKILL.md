---
name: remotion-learning-director
description: Direct, build, verify, and publish Remotion videos that teach a concept through meaningful motion. Use for HubToLearn learning videos, especially when an approved artifact brief or companion interactive lesson already exists. Do not use for ordinary promotional videos or footage-only editing.
---

# Remotion Learning Director

Turn a learning objective into a watchable, technically correct video whose motion explains sequence, ownership, state, causality, or comparison. Treat the installed `remotion-video-director` as a creative toolbox and `remotion-best-practices` as the implementation authority. Adapt both to the learner and the approved brief instead of following their default interviews mechanically.

## Start from evidence

Read `local/NOW.md`, the active session, the relevant artifact brief, and the companion artifact when they exist. Reuse established choices about purpose, audience, duration, visual language, narration, and delivery.

If no approved brief exists, use `direct-learning-artifact` before building. If the brief already answers the production questions, do not ask them again. Ask at most one focused question only when the missing answer would materially change the result and cannot be inferred safely.

## Direct for learning

Create or update a concise creative brief and storyboard beside the artifact brief. Borrow useful scene planning, pacing, and review ideas from `remotion-video-director`, with these adaptations:

- Give each beat one conceptual job.
- Use movement to reveal a relationship or state change. Avoid motion that only decorates the frame.
- Keep technical terms exact while explaining them in short, spoken sentences.
- Coordinate narration, captions, and the active visual. Do not make the learner read a paragraph while also tracking animation.
- Prefer code-native diagrams, labels, packets, gates, timelines, and state transitions when teaching software systems.
- Preserve visual language from the companion lesson unless the user asks for a new direction.
- Include a prediction, pause, contrast, or retrieval cue when it improves learning without interrupting the video’s flow.
- Cover meaningful drawbacks and failure states, not only the happy path.

Do not require an invented expert panel or repeated approval gates when the user has already approved the direction. Use specialist review perspectives internally when they expose a real instructional or visual risk.

## Build with official Remotion guidance

Load `remotion-best-practices` and every reference it routes to for the active work, including creation, markup, captions, and rendering when applicable. When creative advice conflicts with official Remotion mechanics, follow the official guidance.

Keep these production invariants:

- Drive timeline motion from the current frame and video configuration. Do not use browser-time CSS animation for rendered motion.
- Keep scene timing, copy, captions, and theme tokens in clear data structures rather than one large component.
- Use deterministic assets and behavior.
- Keep captions inside safe margins and away from the active diagram.
- Preserve user changes and avoid unrelated refactors.
- Build the requested audio treatment when feasible. If narration or music cannot be produced, report that limitation instead of silently substituting a different experience.

## Verify the actual video

An exported file is not enough. Before delivery:

1. Run project checks and render the complete requested composition.
2. Probe the rendered file for duration, dimensions, frame rate, codecs, and audio presence.
3. Extract representative stills from every beat, inspect them visually, and fix clipping, overlap, weak contrast, unsafe captions, dead frames, or misleading diagrams.
4. Check narration, captions, and animation timing against the storyboard.
5. Confirm the central learning objective and important failure states survived the edit.
6. Re-render and re-inspect after material fixes.

Do not claim learner understanding from enjoyment or assisted viewing. Preserve the intended independent follow-up check in the active session.

## Publish for the learner

When the video belongs to an existing learning website, use `build-web-artifact` to embed it, then `verify-web-artifact` to exercise the changed experience. Projects with `.openai/hosting.json` must use the Sites building and hosting workflows.

The user should receive a clickable HTTPS URL to the finished experience and, when useful, a direct clickable video URL. Never make the learner run a command to watch or inspect the result. Update the active session and `local/NOW.md` with the exact continuation point.
