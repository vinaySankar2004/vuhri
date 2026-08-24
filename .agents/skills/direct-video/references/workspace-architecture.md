# Workspace architecture

Use the staged workspace for a sustained video project, not for a tiny settled edit.

Create it with:

```bash
python3 scripts/init_video_project.py /absolute/path/to/new-project --title "Project title" --kind marketing
```

The initializer refuses to overwrite an existing path.

## Stages

```text
video-project/
|-- CONTEXT.md
|-- project.json
|-- _config/
|   |-- brief.md
|   |-- brand.md
|   |-- platform.md
|   `-- quality-bar.md
|-- 00_intake/
|-- 01_research/
|   `-- sources/
|-- 02_direction/
|-- 03_script/
|-- 04_beats/
|-- 05_shots/
|-- 06_production/
|   |-- src/
|   |-- assets/
|   `-- out/
|-- 07_review/
|   |-- shot-manifest.json
|   `-- runs/
|-- 08_revisions/
|-- tools/
|   `-- verify_video.py
|-- library/
`-- memory/
    |-- decisions.md
    |-- failures.md
    `-- lessons.md
```

Every numbered folder contains a stage contract and an output edit surface. The direction stages separate business intent, sources, direction, script, beats, and shots so a correction can begin at the closest responsible layer.

The review stage is a portable observability boundary. `shot-manifest.json` connects stable direction IDs to rendered seconds. Each verifier run preserves metadata, sampled frames, stable-ID boundary frames, a contact sheet, diagnostics, and review records. Read [observability and pre-verification](observability-and-verification.md) before human handoff.

## Learning boundary

Project memory stores verified local evidence. It does not teach future work from every generated output.

- `decisions.md` protects choices that should remain stable.
- `failures.md` connects observed problems to fixes and regression checks.
- `lessons.md` holds possible generalizations until another use or deliberate test supports them.
- `library/candidates.md` tracks reusable motion language and components without prematurely stabilizing APIs.

This mirrors the ICM principle that stages communicate through inspectable files while keeping stable reference material separate from per-run work.
