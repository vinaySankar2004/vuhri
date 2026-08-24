# Context map

vahri uses spaces for durable working context and shared concept records for knowledge that crosses spaces.

## Spaces

A space can represent an inquiry, topic, course, exam, paper, project, or practice track. Type helps routing but does not impose a complete folder tree.

Every durable space has a concise `CONTEXT.md` that states its purpose, level, current target, constraints, source priority, current position, relationships, and open threads when those fields apply.

Folders appear when they gain content. A small space may have only `CONTEXT.md` and `sessions/`. A large space may add sources, targets, attempts, assessments, artifacts, misconceptions, and an archive.

## Concepts and targets

Reusable concepts live under `local/knowledge/`. A space links to those concepts and records context-specific targets.

For example, binary search may require loop-invariant proofs in a university exam and search-on-answer recognition in interview practice. Evidence and expectations remain scoped even when the underlying concept is shared.

## Relationships

Use ordinary Markdown links to express relationships such as prerequisite, assessed by, applied in, contrasts with, source for, attempted in, misunderstood in, or artifact for. Add small metadata fields only when they improve routing or deterministic checks.

## Progressive loading

Load context in this order and stop when enough is known:

1. Root teaching rules
2. `local/NOW.md`
3. Relevant space context and index
4. Relevant learner records
5. Relevant concept records
6. Specific sources, attempts, assessments, or artifacts

An unrelated quick inquiry should not inherit yesterday's active topic.

## Lifecycle

Spaces may be active, paused, completed, or archived. Archived spaces remain searchable but do not load by default. Preserve links when splitting, merging, renaming, or reopening spaces.
