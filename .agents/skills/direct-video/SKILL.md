---
name: direct-video
description: Direct or revise an editable video system for any topic, producing a direction brief, stable-ID beat sheet, shot plan, and change-scoped revision instructions. Use when hooks, narrative structure, visual choreography, or reusable motion language need deliberate design before a Remotion or other frame-based build. Do not use for footage-only editing or a small settled animation tweak.
---

# Direct Video

Turn an idea, script, or existing cut into inspectable direction that another person or build system can execute and revise without regenerating the whole video.

## Choose the route

- For a new direction, produce a direction brief, beat sheet, and shot plan.
- For a full video, approve those direction artifacts before loading the relevant production skill and building.
- For a revision, identify the smallest stable target, patch it, and invalidate only its downstream dependents.
- For library work, extract candidates from a finished video, then promote only the patterns that survive another use or an explicit cross-topic test.
- For marketing, ads, product films, launch clips, or landing-page motion, load the `remotion-marketing-director` adapter after the general direction layer.

Do not force every project through every stage. Reuse answers already present in the request, source material, or approved brief. Pause only at decisions whose answer would change the concept, hook, or visual thesis.

## Guide people who do not speak video

Assume the user can describe their product, idea, audience, taste, and reaction, but may not know video terminology. Read [guided direction](references/guided-direction.md) for a new video when the user has not supplied a professional brief.

Own the translation from ordinary language to direction. Do not ask a blank question such as "What visual style do you want?" Present a recommended interpretation and, only when useful, one meaningfully different alternative. Explain the visible consequence of each choice without requiring the user to name lenses, easing curves, edit rhythms, or animation techniques.

## Direct through edit surfaces

Use the templates in `assets/` when their structure fits. Keep each artifact readable without the codebase.

1. Lock the editorial contract: audience, desired effect, single core claim, truth or source constraints, duration, format, and delivery context.
2. Choose the angle, hook mechanism, and narrative movement. Read [narrative direction](references/narrative-direction.md) for this work.
3. Define one visual thesis that can carry the piece on mute. A visual thesis states the changing relationship the viewer will watch, not a style label.
4. Divide the argument into beats with stable IDs such as `B01`. Give each beat one job and explicit entry and exit states.
5. Choreograph shots inside each beat with IDs such as `B03.S02`. Read [shot grammar](references/shot-grammar.md) and the [directing dictionary](references/directing-dictionary.md) before writing the shot plan.
6. Map narration words, music events, and sound cues to visible events. Exact frame numbers belong in the production plan, not the conceptual brief.
7. Audit the direction before build. A muted viewer should follow the main relationship, the spoken track should work without reading the screen, and every motion event should change meaning, attention, state, or rhythm.

Read [duration and quality](references/duration-and-quality.md) before promising scope or writing a detailed timeline. Every interval must have an intentional job, including holds and silence. Sample the final video at least once per second for short work and at every shot boundary for longer work.

Keep source-backed facts, user choices, and creative proposals distinguishable. References may inform a mechanism, pacing idea, or motion property. Do not copy another creator's recognizable sequence or visual identity.

## Compile direction into production

Treat the shot plan as an intermediate representation between direction and implementation. Preserve its stable IDs in scene names, data, review stills, and revision notes.

When building with Remotion, load `remotion-best-practices` and the creation, markup, caption, audio, rendering, or other references it routes to. Use a specialized director skill when the format requires one. The direction layer defines what the viewer should perceive and when. The production layer chooses components, coordinates, springs, and rendering mechanics.

Do not hide timing, narration, or scene order inside a large component. Keep the build data-addressable so a request such as "hold B04.S01 for half a second longer" has a narrow implementation surface.

## Revise without collateral change

Read [revision protocol](references/revision-protocol.md) whenever the user dislikes part of a direction or render. Restate the requested delta, target the smallest IDs, preserve protected properties, and recheck only affected dependencies plus the whole-video seams.

## Grow the arsenal from evidence

Read [library system](references/library-system.md) when adding a motion primitive, composition pattern, hook entry, style system, or example. Keep semantics separate from implementation. A useful library answers what a pattern communicates, what state it requires, what it changes, when it fails, and which implementations are available.

The library has three confidence levels:

- `candidate`: observed once or proposed.
- `proven`: used successfully in two meaningfully different contexts.
- `core`: stable API, documented failure conditions, rendered tests, and intentional maintenance ownership.

Large catalogs without rendered examples are inventories, not a directing system.

Read [learning loop](references/learning-loop.md) after a verified revision, a repeated failure, or a new reusable success. Store a project-specific correction in the project. Promote it into shared guidance only when evidence shows the lesson generalizes.

Use `scripts/init_video_project.py` when a new sustained video project needs the full staged workspace. Read [workspace architecture](references/workspace-architecture.md) before initializing it. The script creates the edit surfaces, source ledger, production folders, review records, and project memory without asking the user to design the filesystem.

## Verify the result

For direction-only work, check contract coverage, continuity, timing plausibility, source integrity, visual legibility, and revision addressability.

For a built video, read [observability and pre-verification](references/observability-and-verification.md). Run the portable verifier against the actual complete render and preserve its evidence. Inspect the complete playback with sound, the generated contact sheet, representative frames from every beat, every stable-ID shot boundary, transitions, and audio synchronization. Compare the result against the direction artifacts and complete the visual-review record before human handoff.

Do not treat an automated technical pass as a visual pass. Fix material defects, rerender, and create a fresh evidence run. Report unresolved mismatches instead of silently changing the direction.
