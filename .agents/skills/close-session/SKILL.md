---
name: close-session
description: Close a sustained session. Bring the session record, NOW.md, and every document the session touched current and concise, then commit and push local/ if it is a Git repository. Use when the user says "close the session", or that they are done, stopping, or wrapping up, or when a sustained piece of work reaches a natural end.
---

# Close a session

A session is closed when a later session can resume from the files alone. Quick inquiries need none of this. Do not run it for a question answered in a few turns. An incognito session leaves no record by definition, so it is never closed this way.

## Update the record first

Write the session record before committing anything. Record what was demonstrated, the conditions, help used, and the date. Keep it under 900 words. Preserve original attempts.

Then bring `local/NOW.md` current. It is loaded at the start of every session, so its length is a standing cost on every future session.

- Budget: 450 words, enforced by `npm run check:context`, which also holds `PROFILE.md` to 400.
- It holds what is live: the active space and its exact continuation point, what was most recently completed, and open threads that need an action.
- Move detail into the space, session record, or knowledge note it belongs to, and link to it. Do not restate a fact that already sits one link away.
- Delete items that resolved. A finished thread is not context.
- Convert relative dates to absolute ones.

## Freshness pass

The same discipline applies to every document the session created or edited: space `CONTEXT.md` files, procedures, preferences, `PROFILE.md`, and anything linking to them. For each one:

- It states the current status. Rewrite status lines the session changed, and delete what resolved.
- Each fact lives in one place. Replace a repeat with a link.
- It stays as short as `method/writing.md` asks. If a `CONTEXT.md` has grown past what a reader needs to resume, split it.

An explicit user rule from the session goes into `local/` once, where it belongs.

## Tidy up

Offer to move to the Trash anything this session downloaded or generated that is no longer needed, as `method/housekeeping.md` describes. Offer the deep clean once if housekeeping reports it due.

## Checkpoint

If `local/` is its own Git repository, commit it at close without asking, once the freshness pass is done. Its contents are personal by definition, so the question is only whether the writing is accurate. Commit only this session's work, since other sessions may have changes in the same tree.

Only the maintainer commits to the public vuhri repository (see `method/housekeeping.md`). Show what changed there and get a yes before committing.

Run the checks the change earns. Method, script, or skill changes in the public repository call for `npm run check`. A `local/` commit calls for `npm run check:privacy` and `npm run check:context`. Never force-add ignored content.

Follow `.agents/skills/commit-changes/SKILL.md` for message style, staging, and the rules on amending and history. Do not create tags.

## Push

Most users' `local/` is a plain folder, so the freshness pass is the whole close for them. When `local/` is a Git repository with a remote, push it after the commit, so the closed session is backed up and can resume on another machine. Push the public repository only when the user asks. Report what is committed locally and what has reached the remote, and do not describe one as the other.

## Report

One short paragraph: what the session established, where it stopped, and the state of both repositories. The files carry the detail. The handoff does not repeat them.
