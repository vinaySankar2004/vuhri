# Revision protocol

Use this when feedback targets part of a direction or render.

## Translate feedback into a delta

Record:

- target IDs;
- observed problem;
- requested viewer effect;
- properties allowed to change;
- properties that must remain fixed;
- evidence, reference, or timestamp supplied by the user;
- acceptance check.

"Make it punchier" is not yet a production delta. A useful translation might be: "In `B01.S02`, shorten the anticipation, move the first contradiction before the second spoken sentence, and preserve the current typography and final hook claim."

If several translations are plausible and would produce materially different videos, present the alternatives before editing.

## Scope the invalidation

Use this dependency order:

`editorial contract -> angle -> script -> beat -> shot -> component -> render -> publication`

A change invalidates itself and the artifacts to its right that depend on it. It does not automatically invalidate siblings or upstream decisions.

Examples:

- A color adjustment in `B04.S01` requires a local component change, seam review, and render inspection.
- A new line of narration may change caption timing, shot duration, downstream audio positions, and total duration.
- A new core claim invalidates the angle, script, beat sheet, source check, shot plan, and build.

## Protect continuity

Before editing, list the properties that should remain stable, such as duration, palette, motif, camera logic, character identity, caption treatment, audio bed, or all unaffected beat IDs.

After editing, verify:

- the target acceptance check;
- the transition into and out of the changed region;
- audio and caption synchronization;
- total duration and platform constraints;
- any dependency explicitly marked by the revision.

Do not use a full regeneration when a targeted patch can satisfy the request.

## Revision ledger entry

```markdown
### R004

- Targets: B03.S02, B03.A01
- Problem: The gate opens before the narration establishes who owns it.
- Delta: Delay the opening until the word "approval" and hold the closed state longer.
- Preserve: Scene duration, copy, palette, packet path, adjacent beats.
- Acceptance: A first-time viewer can name the host as the approval owner before the packet continues.
- Status: proposed | built | verified | rejected
```
