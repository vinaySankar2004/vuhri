---
name: build-web-artifact
description: Build or materially revise an interactive learning website from an approved artifact brief. Use the shared artifact kit, preserve private evidence boundaries, and prepare the result for independent verification. Do not mark the artifact verified.
---

# Build a web learning artifact

Read the approved `artifact-brief.md`, `method/artifacts.md`, and the relevant source and space contracts. If the brief lacks a learner action, success evidence, or source basis, return to direction before building.

Use `packages/artifact-kit` components when they fit. Keep concept-specific state and logic inside the artifact. Add a shared primitive only after a demonstrated reusable need, and keep that promotion separate from private learner content.

Build for observable behavior:

- Instructions state what the learner should do.
- State changes are visible and correct.
- Predictions or attempts are captured before answers appear when the brief requires them.
- Feedback is specific.
- Reset and replay restore all relevant state.
- Keyboard use, reduced motion, readable contrast, and small screens are supported.
- Simplifications and sources remain visible.

Add unit tests for concept logic and important state transitions. Run the build and tests. Leave the artifact in `built` state and hand it to `verify-web-artifact`.

