---
name: commit-changes
description: Create a careful Git checkpoint when the user asks to commit, save, checkpoint, or commit and push repository work. Inspect scope, protect private data, run proportionate checks, and report the resulting state. A commit request does not imply permission to push, amend, force-push, or create a remote.
---

# Commit changes

Make the repository easier to understand and resume. Preserve the user's work and authorization boundaries. Only the `maintainer` role commits to the public vuhri repository; a user's commits stay in their own `local/` (see `method/housekeeping.md`).

## Inspect before staging

Read the repository instructions. Inspect the current branch, status, staged diff, unstaged diff, and relevant untracked files. Treat pre-existing or unrelated changes as the user's work. Include them only when the requested commit clearly covers them.

Check for private learner data, credentials, generated output, large binaries, and accidental tool state. In vuhri, run `npm run check:privacy` when available. Never force-add ignored content merely to make the working tree appear clean.

## Commit only this session's work

Several sessions may run at once, often in the same space and the same files. A plain "commit" means this session's changes only.

- Stage the paths this session created or edited, never `git add .` or `-A`. Commit everything only when the user says so explicitly.
- A file other sessions also changed gets hunk-level staging. Stage only this session's hunks. Build a patch from `git diff <file>`, keep this session's hunks, and apply it with `git apply --cached`. Then confirm with `git diff --cached` that nothing foreign went in.
- If a hunk mixes this session's lines with another session's, or context was summarized and ownership is unclear, ask before staging it.
- Report what was left unstaged, so the other sessions' work is visibly untouched.

## Form the checkpoint

Group one coherent change per commit when practical. Stage explicit paths unless every visible change is clearly within scope. Review the staged diff or summary before committing.

Run checks proportionate to the changed files and repository risk. Use the repository's full check before a release or broad foundation change. Do not bypass hooks or checks merely to complete the commit.

Follow the repository's established message style. Otherwise use a concise imperative subject, with a conventional type such as `feat`, `fix`, `docs`, `test`, `refactor`, or `chore` when it clarifies intent. Add a body only when the reason or consequence is not evident from the diff.

Create a new commit. Do not amend, rewrite history, squash, or change authorship unless the user explicitly requests it.

## Push only when authorized

A request to commit is local. Push only when the user also asks to push or has clearly established that the requested checkpoint should be synchronized now.

Before pushing, inspect the remote and upstream. Use an ordinary push. Never force-push unless the user explicitly requests the history rewrite and the exact target is verified.

If no remote exists, do not create one until repository ownership and visibility are established by the user or clear project context. If the remote advanced, fetch and inspect the divergence rather than overwriting it.

## Verify and report

After committing, report the short hash, subject, checks run, and any changes left outside the commit. After pushing, fetch or inspect the tracking state and confirm whether local `HEAD` equals the upstream branch. Ignored private state may remain locally and must not be described as remotely synchronized.
