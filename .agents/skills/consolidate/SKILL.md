---
name: consolidate
description: Deep-clean vuhri's rules and working notes so each rule has one home, nothing is stale or contradictory, wording stays lean, and the files every session loads stay small. Use when housekeeping reports a deep clean due and the person agrees, or when they ask to tidy, clean up, consolidate, or review the rules.
---

# Consolidate rules and notes

Rules drift as lessons land in whichever file was open at the time, and notes go stale as work finishes. This pass restores one home per rule and fresh working context. A user consolidates only their own `local/`; public files are the maintainer's.

## Inventory

Read every place a rule can live:

- Public: `AGENTS.md`, `method/`, `.agents/skills/`, `DECISIONS.md`, `MIGRATIONS.md`, `lessons/log.md`, `templates/`.
- Personal: `local/PROFILE.md`, `local/preferences/`, `local/settings/`, and the constraints in each space's `CONTEXT.md`.
- Any agent-private memory. It should hold only a pointer to `local/`.
- Working context: `local/NOW.md`, each space's open threads and current position, and `local/artifacts/index.md`.

## Classify

For each rule, decide where it belongs, then flag what is wrong with it:

- Belongs: everyone goes to `method/` or a skill; this person to `local/preferences/`; one space to that space; a machine fact to `local/settings/environment.md`.
- Duplicated: keep the most specific home and link from the others.
- Stale: it describes a tool, file, or decision that no longer exists. Delete it rather than annotating it.
- Contradicted: the later explicit statement wins. Keep the earlier one's evidence in the record if it still informs scope.
- Unenforced: a rule that keeps failing deserves a check, not more words.
- Finished or bloated: resolved threads leave the working context, and wordy passages are cut to what a reader needs.

## Propose, then apply

Show a migration map: rule, current home, target home, reason. Apply it on approval. Update every link to a moved rule. When a change alters the shape of `local/`, add a `MIGRATIONS.md` entry.

## Verify

- `npm run check` passes, including the word budgets in `scripts/check-context.mjs`.
- Walk test: from `AGENTS.md`, any task reaches its governing file within two reads.
- Record the date as `last_consolidation` in `local/settings/housekeeping.json`. Add a lesson only if a rule's meaning changed.
