# Lesson log

Use this format:

```markdown
## YYYY-MM-DD: short title

- Evidence:
- Proposed change:
- Scope and exclusions:
- Status: proposed
```

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
