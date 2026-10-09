# vuhri

vuhri is a local-first workspace for learning and directed creation with coding agents. It supports quick questions, durable learning spaces, interactive explanations, and editable videos for education, marketing, and other topics.

Intent, sources, direction, implementation, verification, and reusable lessons remain in inspectable files. Personal learning records and generated artifacts stay private under `local/`.

## Start

```bash
npm install
npm run setup
```

Open the folder in Claude Code, Codex, Cursor, or another coding agent that follows repository instructions, then begin with the actual inquiry or creative request. vuhri adds structure only when continuity, evidence, sources, direction, or production make it useful.

Each session starts with `npm run housekeeping`, which reports large files and, for people who use vuhri without developing it, whether an update is ready. The agent asks before changing anything.

Run the local artifact studio with:

```bash
npm run dev
```

Run the complete repository check with:

```bash
npm run check
```

## Repository map

- `AGENTS.md` contains the operating constitution.
- `VISION.md` defines the product and its boundaries.
- `DECISIONS.md` records settled design choices.
- `MIGRATIONS.md` lists changes an existing `local/` must be aligned to after an update.
- `method/` contains the learning, context, source, browser, artifact, writing, and housekeeping methods.
- `.agents/skills/` contains reusable direction, production, verification, and repository workflows.
- `templates/local/` is the public template for private working state.
- `apps/artifact-studio/` hosts local interactive artifacts.
- `packages/artifact-kit/` contains reusable learning interface components.
- `lessons/` records improvements grounded in actual use.

## Privacy

Git ignores `local/`. `npm run check:privacy` fails if Git begins tracking personal sources, attempts, assessments, memory, or generated private artifacts.

If private backup is needed, `local/` can become a separate private repository.
