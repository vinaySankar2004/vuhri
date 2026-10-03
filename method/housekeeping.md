# Housekeeping

Keep the workspace safe, current, small, and consistent without making the person manage it. Many people using vuhri are not technical and are wary of an agent with access to their computer. Earn that trust by staying in bounds and asking plainly.

## Session start

In a normal session where `local/` exists, run `npm run housekeeping` once. It reports large items and, for a user, whether a newer version of vuhri exists. Raise its findings after handling the first request, in one short message, never as a block in front of it. Skip housekeeping entirely in an incognito session.

## Roles

`local/settings/housekeeping.json` sets `role`. A missing file means `user`.

- `maintainer` develops vuhri and may commit and push the public repository through `commit-changes`.
- `user` never commits, pushes, or edits the public repository's files. Their `local/` is theirs.

## Stay inside the folder

Work inside the vuhri folder. Do not read, change, install, or download anything outside it unless the person asks for that specific thing. Put downloads and generated files inside the folder, in the project they serve, unless the person names a place.

Download what a task needs when it needs it, not in advance. When the task ends, offer to remove what it no longer needs.

## Updates

For a user, the housekeeping run checks for a newer version at most once a day. When one exists, ask in everyday words, for example: "A newer version of vuhri is ready. Want me to update it now?" Never mention Git, pulling, or branches. On a yes, run `npm run housekeeping -- --update`. If it reports that vuhri's own files were changed locally, do not force anything. Explain in a sentence that the update has to wait, and leave everything as it is.

An update is finished only when the person's `local/` matches the new conventions. The update adds any new template files without overwriting theirs, then lists what changed and every pending entry in `MIGRATIONS.md`. Apply those entries as that file says, and tell the person what is new in a sentence or two. A housekeeping run that reports pending entries without an update, for example after a long gap, gets the same treatment.

When a maintainer's change alters the shape of `local/`, they add a `MIGRATIONS.md` entry in the same commit.

## Disk space

The run lists dependencies, build output, and caches over 50 MB, renders and evidence over 100 MB, any other file over 100 MB, session copies under `.claude/worktrees/`, and the folder's total size.

When something is worth raising, say what it is, how big it is, whether it can be recreated and how long that takes, and what removing it changes. Group similar items into one question. For example: "Two video projects hold 350 MB of downloaded building blocks. They come back with one command in about a minute when you next edit those videos. Want me to clear them?"

- Remove only on a yes, by exact path, and only by moving to the Trash. Say it can be restored until the Trash is emptied.
- Never suggest removing originals or inputs, the only copy of anything, `final/` outputs, or the evidence of an active project.
- When the person says to keep something, record it with `npm run housekeeping -- --keep <path>`. It is raised again only if it grows by half.
- Session copies under `.claude/worktrees/` may belong to other running sessions. Report their size; leave removal to the person or the app.

Clean up after work too. Remove the scratch a session created, such as frames, temporary renders, and check screenshots, once the output it produced is verified. When a project ends, offer to keep only its `final/` folder. When someone hands over a file to keep, copy it into `local/`, confirm the copy is identical, and offer to move the original to the Trash.

## Deep clean

Rules and notes drift as lessons land in different places and threads finish. When housekeeping reports a deep clean is due (never done, more than 30 days, or five lessons accepted since the last one), offer it once in everyday words, for example: "It has been a while since vuhri's rules and notes were tidied. Want me to do a clean-up pass?" On a yes, run the `consolidate` skill. A user's pass covers only their own `local/`.
