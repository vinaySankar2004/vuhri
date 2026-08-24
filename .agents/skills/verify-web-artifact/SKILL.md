---
name: verify-web-artifact
description: Verify a built learning website by running checks, exercising it in a real browser, and reviewing technical, interaction, visual, accessibility, and instructional correctness. Use after building or materially changing a web artifact.
---

# Verify a web learning artifact

Read the artifact brief, `method/artifacts.md`, and the built artifact. Create a report from `templates/verification-report/verification-report.md`.

Run the repository's mechanical checks first. Then open the artifact in a real browser and collect evidence. A production build or type check alone is not browser verification.

Read [the verification lanes](references/verification-lanes.md) for the required review. Derive artifact-specific adversarial cases from the brief, concept, state model, and likely learner mistakes.

The report records commands, browser paths, viewports, screenshots, failures, fixes, reruns, instructional findings, and remaining uncertainty. Use `fail` while any required path is broken or the concept is misrepresented. Use `pass-with-follow-up` only when the remaining item does not undermine the learning objective.

Do not claim the artifact improved learning until a learner uses it and produces the stated success evidence.

