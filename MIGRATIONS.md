# Migrations

Changes that require an existing `local/` to be aligned. After an update, `npm run housekeeping` lists every entry newer than `aligned_through` in `local/settings/housekeeping.json`. Apply them oldest first. Make mechanical changes directly, ask before changing the person's own content, explain what is new in everyday words, then run `npm run housekeeping -- --aligned`.

Maintainers add an entry whenever a change alters the shape of `local/`, such as a template, settings file, folder, or file format, and set `aligned_through` in `templates/local/settings/housekeeping.json` to the entry's date. Paths below are relative to `local/`.

## 2026-10-03: Housekeeping settings and one home for preferences

- `settings/housekeeping.json` now holds the role, kept items, and alignment date. The update adds it with `role` set to `user`; change it only if this person develops vuhri.
- Standing preferences live one per file under `preferences/`, each indexed by one line in `PROFILE.md` with its evidence in the file. Offer to move any preference held elsewhere, such as an agent's private memory, into that shape.
- `PROFILE.md` is read at every session start, so keep it under 400 words. `npm run check:context` enforces this and the 450-word limit on `NOW.md`.
