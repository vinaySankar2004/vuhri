# Learning loop

Use verified outcomes to improve future direction without turning every preference or isolated failure into a universal rule.

## Record failures at the right layer

After a material correction, record:

- failure ID and date;
- affected beat, shot, component, or stage;
- what a viewer experienced;
- root cause layer: contract, angle, script, beat, shot, component, asset, render, or platform;
- correction;
- regression check;
- evidence that the correction worked;
- scope: project-only, pattern candidate, or shared rule candidate.

Examples:

- A caption covering a CTA is a project failure until the safe-zone logic is shown to fail elsewhere.
- A gate opening before its authority is named can update the `Gate` primitive's failure conditions after a second relevant example or explicit cross-topic test.
- "The user disliked blue" remains project feedback. It is not a design rule.

## Learn only from reviewed outcomes

Do not learn patterns from raw generated output. Early outputs contain unresolved mistakes. Use approved direction, verified renders, revision ledgers, and explicit user feedback as evidence.

## Promotion path

1. Record the correction in `memory/failures.md` for the project.
2. Add a candidate lesson to `memory/lessons.md` when it may generalize.
3. Test it in a meaningfully different video or controlled micro-composition.
4. Update the relevant primitive, pattern, style system, script, or skill only after the test supports it.
5. Attach a regression check so the same failure becomes observable, not merely remembered.

Prefer a narrow fix in the closest responsible layer. Shared instructions should not accumulate one-off taste decisions.
