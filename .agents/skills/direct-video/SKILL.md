---
name: direct-video
description: Direct, render, verify, or revise a video built in code, from a short loop to a long explainer, through a direction brief, stable-ID beat sheet, shot plan, and change-scoped revisions. Use for any new code-built video, a video that follows a deck, or a revision that should leave unaffected work alone. Do not use for footage-only editing or a small settled animation tweak.
---

# Direct Video

Turn an idea, script, deck, or existing cut into direction that another person or build can execute and revise without regenerating the whole video.

## Size the work

Match the process to the job, as the table in `method/artifacts.md` sets out:

- Loop or sting, 2 to 6 seconds: one shot sentence with its job and exit condition, then build.
- Short video, 6 to 45 seconds: a direction brief, beat sheet, and shot plan from `assets/`, approved before building. Add a design board when the look is still open.
- Longer video, 45 seconds and up: the staged workspace from `scripts/init_video_project.py` and a design board approved before production. Read [workspace architecture](references/workspace-architecture.md) and the design board section of [guided direction](references/guided-direction.md). Past 90 seconds, build and verify in chapters.
- Revision: the [revision protocol](references/revision-protocol.md).

Load an adapter after the direction layer: `remotion-learning-director` for teaching, `remotion-marketing-director` for marketing, ads, product films, and launch clips. Reuse answers already given. Pause only at decisions that change the concept, hook, or visual thesis.

## Guide people who do not speak video

Assume the user can describe their product, idea, audience, taste, and reaction, but not video terminology. Read [guided direction](references/guided-direction.md) for a new video without a professional brief. Recommend an interpretation in plain language and explain the visible consequence of each choice. Never ask a blank question such as "What visual style do you want?"

## Direct

1. Lock the editorial contract: audience, desired effect, single core claim, source constraints, duration, format, and delivery context.
2. Choose the angle, hook mechanism, and narrative movement from [narrative direction](references/narrative-direction.md).
3. Define one visual thesis that carries the piece on mute: the changing relationship the viewer watches, not a style label.
4. Divide the argument into beats with stable IDs such as `B01`, each with one job and explicit entry and exit states.
5. Choreograph shots such as `B03.S02` with [shot grammar](references/shot-grammar.md) and the [directing dictionary](references/directing-dictionary.md).
6. Plan sound with the picture using [audio direction](references/audio-direction.md).
7. Audit before building. A muted viewer follows the main relationship, the spoken track works without reading the screen, every motion event changes meaning, attention, state, or rhythm, and every interval has a job. [Duration and quality](references/duration-and-quality.md) covers time budgets and reading time.

Keep source-backed facts, user choices, and creative proposals distinguishable. Study references for a property such as pacing or camera restraint. Never copy a creator's recognizable sequence or visual identity.

## Build

Choose the renderer and follow its rules in [rendering](references/rendering.md). Treat the shot plan as the interface between direction and code: preserve its IDs in scene names, data, review stills, and revision notes, and keep timing, copy, and narration in data so a request such as "hold B04.S01 half a second longer" has a narrow surface.

## Verify

Read [observability and pre-verification](references/observability-and-verification.md). Run the verifier against the complete render. Inspect the full playback with sound, both contact sheets, every shot boundary and transition frame, and the reading-time flags. Complete the visual-review record before human handoff. An automated pass never stands in for a visual pass. Fix material defects, rerender, and create a fresh evidence run. Report mismatches with the direction instead of silently changing it.

## Grow the arsenal

Add motion primitives, patterns, and style systems through the [library system](references/library-system.md): entries start as `candidate` and earn `proven` or `core` from rendered evidence. After a verified revision, a repeated failure, or a reusable success, apply the [learning loop](references/learning-loop.md). A large catalog without rendered examples is an inventory, not a directing system.
