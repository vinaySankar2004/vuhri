# HubToLearn

HubToLearn is a local, repo-based learning system for Codex and compatible coding agents. It can handle a quick question, a sustained topic, a course, an exam, a paper, a project, or a practice track.

The public repository holds the teaching method, reusable skills, artifact foundations, templates, checks, and accepted lessons. Personal goals, sources, attempts, assessments, memory, and generated learning artifacts stay in `local/`, which Git ignores.

## Start

```bash
npm install
npm run setup
```

Then open this folder in Codex and ask a question. HubToLearn should begin with the inquiry. It creates structure only when continuity, evidence, sources, or artifacts make that structure useful.

Run the artifact studio with:

```bash
npm run dev
```

Run all repository checks with:

```bash
npm run check
```

## Where to look

- `AGENTS.md` contains the operating constitution.
- `VISION.md` defines the product and its boundaries.
- `DECISIONS.md` records settled design choices.
- `method/` explains the learner model, context, interaction, sources, artifacts, and writing.
- `.agents/skills/` contains reusable workflows.
- `templates/local/` is the public template for private learner state.
- `apps/artifact-studio/` hosts local interactive artifacts.
- `packages/artifact-kit/` contains reusable learning interface components.
- `lessons/` records proposed and accepted improvements.

## Privacy

`local/` is excluded from the public repository. `npm run check:privacy` fails if Git begins tracking anything inside it. Raw course material, assessments, results, and personal memory must stay there.

If private backup is needed, `local/` can later become its own private Git repository.

