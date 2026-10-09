# Lesson log

Use this format:

```markdown
## YYYY-MM-DD: short title

- Evidence:
- Proposed change:
- Scope and exclusions:
- Status: proposed
```

## 2026-10-09: Read pages without side effects, inside the extension's tab group

- Evidence: Guiding an AWS console session through Claude in Chrome, the agent could not see
  the person's tabs until the page was opened in the extension's own tab group and they worked
  there. Reading an IAM policy editor with a script that called the editor library's setup
  function replaced the editor and its unsaved text with mangled JSON. Nothing was saved, and
  a reload recovered it.
- Proposed change: In `method/browsers.md`, note that the extension sees only its own tab group,
  and require reading through page text, the accessibility tree, or screenshots, never through
  a page's own scripts.
- Scope and exclusions: Applies to both browsers. Inspecting a page with plain DOM reads is
  still allowed.
- Status: accepted

## 2026-10-08: Fall back to Claude in Chrome when the built-in browser fails

- Evidence: An AWS root sign-in in the desktop app's Browser pane passed the email and
  password, then ended at the passkey step with a message that the prompt was cancelled. The
  person's Safari completed the passkey, but its old AWS cookies made the console return a
  `400 Bad Request` until a private window was used. A review of the third-party
  `claude-for-safari` skill (SDLLL, MIT) found it is AppleScript running page JavaScript in
  Safari. It needs a Safari setting that opens every tab to any app with Automation access,
  plus up to three more macOS permissions. Computer use can see browsers but not act in them.
  The learner chose Chrome over Safari once told Chrome can use Apple passkeys, and asked for
  a public rule used only when the pane fails.
- Proposed change: Add `method/browsers.md` with the order (pane first, Claude in Chrome on a
  recorded failure) and a list of observed failures, route to it from `AGENTS.md`, and record
  the rejected Safari route in `DECISIONS.md`.
- Scope and exclusions: No custom browser code or vendored skill. Confirmed the same day: the
  AWS root sign-in that failed in the pane worked in Chrome.
- Status: accepted

## 2026-10-03: Consolidate rules, roles, and housekeeping

- Evidence: Rules had spread across four homes that drifted apart. The repository, `local/`, an
  agent-only memory of 21 files that other agents could not see, and two Remotion skills
  installed for one agent only. `PROFILE.md` had not changed since 2026-09-14 while newer
  preferences contradicted it. The learner is sharing vuhri with non-technical people who are
  wary of an agent's reach, and asked for space awareness, plain update prompts, and alignment
  after updates.
- Proposed change: Make `AGENTS.md` a routing file under a word budget, `method/artifacts.md`
  the single map for visual work, and `method/housekeeping.md` the home for roles, scope,
  updates, disk space, and consolidation, backed by `npm run housekeeping`, `MIGRATIONS.md`,
  and the `consolidate` skill. Move personal rules into `local/preferences/`.
- Scope and exclusions: Mac-wide cleanup stays on request. Nothing is deleted without a yes,
  and removal always goes through the Trash.
- Status: accepted

## 2026-10-03: Adopt brag's techniques without its runtime

- Evidence: A review of the third-party `brag` launch-video skill (latent-spaces/brag, MIT)
  found useful planning rules and one small audio script, while its runtime pulled an unpinned
  CLI with default-on telemetry and bundled music with unsettled credit terms.
- Proposed change: Add format presets, mid-transition frames, reading-time flags, and a poster
  check to the verifier; add `bake_poster.py` and the optional `analyze_music_cues.py`; add
  rendering, audio-direction, and product-intake references.
- Scope and exclusions: Its numeric rules stay candidate until vuhri's own renders confirm them.
  No Hyperframes, tone presets, or bundled media.
- Status: accepted

## 2026-10-03: Build a deck as local outputs from one outline

- Evidence: For a one-hour family tutorial, a hosted slide artifact was rejected. The learner
  wanted decks as the repository's own work: a PDF to share, a click-through page whose arrow
  keys play animations for live talks, and a video that follows the same deck. One outline
  produced all three plus presenter notes in the time available, and printing the
  click-through page kept the PDF in step with it.
- Proposed change: Add a slide decks section to `method/artifacts.md` naming the outputs, the
  single outline, vuhri's design tokens, the verification, and keeping only `final/` at
  project end.
- Scope and exclusions: Applies to decks and talks. A deck skill with a reusable
  click-through template waits until a second deck shows what varies.
- Status: accepted

## 2026-10-03: Render video without Remotion when its dependencies are absent

- Evidence: Remotion dependencies had been cleared from the local projects, and the talk was
  under an hour away. A page that draws any frame from a time value, captured frame by frame
  in headless Chromium and encoded with ffmpeg, produced a verified four-minute cut keyed by
  beat IDs. Narration from the built-in macOS voice was aligned by re-rendering beats longer
  rather than speeding the voice.
- Proposed change: Note in the video section of `method/artifacts.md` that this renderer is
  acceptable when Remotion is unavailable, with the same beat IDs and verifier.
- Scope and exclusions: Remotion stays the default for sustained video work. The built-in
  voice is provisional, and a public master needs a reviewed voice and a listening pass.
- Status: accepted

## 2026-09-21: Write mathematics for the medium it is read in

- Evidence: A projection derivation written inline in chat mixed unicode subscripts with
  emphasis markers. The learner screenshotted it, said matrix and summation notation was hard
  to read that way, and asked for a fix that would hold permanently. The same content in a
  fenced block, and later typeset on a web page, was legible without further explanation.
- Proposed change: Add `method/math-notation.md`, load it from the constitution beside the
  writing method, and link it from `method/writing.md`. Fenced code blocks in chat with ASCII
  sub and superscripts; real typesetting in a web artifact.
- Scope and exclusions: Applies to any user-visible derivation, matrix, or multi-step
  algebra. It does not govern code, and it does not require typesetting where a sentence
  would do.
- Status: accepted

## 2026-09-21: Treat a growing annotated document as append-only

- Evidence: The learner asked to keep one course notebook on a tablet, annotate it, and have
  new units added to that same file as they were taught, then raised the case of a correction
  landing on a page he had already written on. Regenerating the document would have destroyed
  a term of annotation invisibly.
- Proposed change: Add `scripts/splice-notes-pdf.py` and an accumulating-documents section to
  `method/artifacts.md`. One HTML source renders both the live page and the export and can
  render a named subset of itself; new sections are spliced into the returned file; the
  contents page is replaceable and every other page is not.
- Scope and exclusions: Applies to artifacts read over months and annotated outside the
  system. A one-off explainer is still regenerated freely. The approach accumulates errata
  pages rather than keeping the document pristine, which is the intended trade.
- Status: accepted

## 2026-09-21: Verify an artifact against print, not only against the screen

- Evidence: Exporting a working page produced three defects invisible on screen: typeset
  mathematics clipped past the page edge, a callout drawn on top of a card because CSS grid
  mis-fragments across a page break, and a near-blank page where a short tail orphaned. Only
  one was reported by the learner; the other two were found by inspecting every page.
- Proposed change: Add a printing section to `method/artifacts.md`. Interactive controls are
  replaced by the static result they would produce, nothing depends on scrolling, tall
  containers use block layout when printing, and every rendered page is inspected after any
  content change.
- Scope and exclusions: Applies to artifacts intended to be read away from the browser. It
  does not require a print stylesheet for a screen-only tool.
- Status: accepted

## 2026-08-24: Make video direction addressable

- Evidence: The MCP learning video reached a verified result, but its brief and storyboard identified scenes only by time and title. The learner then asked for deeper direction, granular control, reusable hook and motion vocabulary, and local changes that do not regenerate unaffected work.
- Proposed change: Add a general video direction layer with stable beat and shot IDs, explicit state transitions, a scoped revision protocol, and evidence-based library promotion. Keep learning-specific behavior in the Remotion learning adapter.
- Scope and exclusions: Applies to code-directed video and substantial creative revisions. It does not require the full workflow for footage-only editing or a small settled animation tweak.
- Status: accepted

## 2026-08-24: Guide non-editors and separate marketing direction

- Evidence: The learner stated that neither they nor an expected user should need video-creation or editing knowledge. They asked the system to direct every second, support marketing, ads, quick animations, premium frontend-inspired depth and 3D, preserve a clear ICM workspace, and prevent verified mistakes from recurring.
- Proposed change: Add novice-guided recommendations, duration bands, per-second review, a marketing Remotion adapter, frontend-to-video motion guidance, a staged project initializer, and scoped failure memory with regression checks.
- Scope and exclusions: Applies to sustained code-directed marketing and general video work. It does not promise rapid one-pass polish for videos longer than 90 seconds, infer unsupported marketing claims, or promote one-off taste feedback into shared rules.
- Status: accepted

## 2026-08-24: Preserve video verification evidence before human review

- Evidence: The learner asked for visual observability and agent-side pre-verification so a person reviews a technically and visually inspected result instead of finding basic defects through repeated feedback. They also required the workflow to run in Codex, Cursor, Claude Code, or another coding-agent environment.
- Proposed change: Add an agent-independent verifier that records media metadata, overview and final frames, stable-ID shot-boundary frames, contact sheets, decode diagnostics, and separate technical and visual gate states. Bundle the verifier into every sustained video workspace and test both passing and failing media contracts.
- Scope and exclusions: Applies to code-directed rendered video. It detects observable technical and visual risks but does not claim that black frames, static holds, or silence are defects without direction-aware review, and it does not replace human taste review.
- Status: accepted
