# Learning artifacts

An artifact exists to support a defined learning action. Visual novelty alone is insufficient.

## Decision

Before building, state the concept, learning objective, learner action, misconception or difficulty, reason for the format, source basis, and success evidence. Prefer a small example, trace, sketch, or table when it can do the job.

## Lifecycle

```text
learning need
  -> brief
  -> build
  -> technical verification
  -> instructional verification
  -> learner use
  -> revision or archive
```

Useful states are `draft`, `built`, `technically-verified`, `instructionally-verified`, `used`, `revised`, and `archived`.

## Interactive websites

Build from the shared artifact kit when its primitives fit. Keep domain logic local to the artifact. Promote a new shared component only after real reuse or a clear repeated need.

Verification has four lanes:

- Build integrity
- Interaction integrity
- Visual and accessibility integrity
- Instructional integrity

Run the application in a real browser. Exercise expected paths, incorrect actions, reset, edge cases, keyboard use, responsive layouts, and browser errors. Confirm that the displayed state and feedback match the underlying concept.

## Accumulating documents

Some artifacts are read over months rather than used once. A course or project notebook grows
a section at a time, and the learner annotates their copy and inserts pages of their own.

The copy they annotate is the only place their work exists. Regenerating the whole document
destroys it silently, so a new section is rendered on its own and spliced into the file they
return. Their pages are copied through untouched, never rebuilt.

**Ownership decides what may be rewritten.** The contents page belongs to the document and is
replaced whenever it goes stale. Every other page belongs to the learner from the moment it is
delivered. A correction to a section already issued is therefore an inserted page, not a
replacement of the original, and the document accumulates errata rather than staying pristine.
That is the correct trade: a clean document is worth less than a term of their annotation.

- Keep one source file that produces both the live page and the export, so the two cannot drift.
- Give that source a way to render a named subset of itself, which is what makes a clean splice
  possible.
- Inspect the returned file before placing anything. The learner's own inserted pages mean the
  layout cannot be assumed.
- Keep the filename stable for the life of the document.
- A destructive option, such as replacing a stale contents page, needs their confirmation that
  the pages being discarded are unmarked.

`scripts/splice-notes-pdf.py` implements this for an HTML source and a PDF export.

## Printing

An artifact meant to be read on paper or on a tablet must transfer completely, apart from its
interactivity. Replace each interactive control with the static equivalent it would have
produced: a selector becomes every option shown together, a manipulable figure becomes one
worked state with its readout.

Three failures recur and none are visible without looking at every rendered page.

- An `overflow` container clips instead of scrolling. Nothing may depend on scrolling.
- Typeset mathematics carries a fixed width and cannot wrap. Scale display equations to their
  container and write anything long as display rather than inline.
- CSS grid mis-fragments across a page break in some engines and overlaps content. Containers
  tall enough to break should use block layout when printing.

Re-render and inspect every page after any content change, because new content moves every
page break after it.

## Video

Educational direction and technical Remotion construction are separate concerns. The general `direct-video` skill defines editable direction artifacts and stable revision targets. The `remotion-learning-director` skill adds the learning objective, misconception, prediction or retrieval moment, source requirements, and companion learning check. Official Remotion skills handle technical creation and rendering.

Rendered video verification should inspect frames, pacing, captions, audio, clipping, synchronization, accuracy, distracting motion, and alignment with the approved beat sheet and shot plan. Run technical checks against the actual exported media and preserve metadata, sampled frames, stable-ID shot frames, contact sheets, diagnostics, and a visual-review record. Automated checks do not stand in for agent playback and visual inspection.
