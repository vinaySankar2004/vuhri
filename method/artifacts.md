# Artifacts

An artifact is anything vuhri builds to be seen: a web page, a document, a deck, or a video. It earns its place only when a smaller explanation cannot do the job. Personal artifacts and their evidence live under `local/artifacts/`.

## Choose the smallest fit

| Job | Build | Route | Done when |
| --- | --- | --- | --- |
| Show something during a conversation | A sentence, table, trace, or sketch in chat | Answer directly; mathematics follows [math-notation.md](math-notation.md) | It reads clearly where it is shown |
| Let someone see or manipulate a concept | An interactive page | `build-web-artifact`, then `verify-web-artifact` | All four lanes pass in a real browser |
| Notes read and annotated over months | An accumulating document | [Accumulating documents](#accumulating-documents) | Every new page is inspected in print |
| A talk | A deck set from one outline | [Slide decks](#slide-decks) | Every slide stepped, every printed page inspected |
| A loop, sting, or micro-animation | One shot, 2 to 6 seconds | `direct-video`: one shot sentence, then build | Verifier and visual pass |
| A short video | Beats and shots, 6 to 45 seconds | `direct-video` brief, beat sheet, and shot plan, then build | One frame per second and every boundary reviewed |
| A longer video | A staged workspace, 45 seconds and up | `direct-video` with `init_video_project.py` and a design board; chapters past 90 seconds | Board approved, then each section reviewed |
| A change to any of these | The smallest stable target | The medium's revision rules; for video, the revision protocol | The change and its seams are rechecked |

For learning, start with `direct-learning-artifact` whatever the medium. It may conclude that a chat answer is enough. Learning videos add `remotion-learning-director`; marketing, ads, and launch clips add `remotion-marketing-director`.

An artifact is unfinished until it has been exercised in its actual format: clicked through in a browser, printed and inspected page by page, or played with sound.

## Learning artifacts

Before building, state the concept, learning objective, learner action, misconception or difficulty, reason for the format, source basis, and success evidence. Track state as `draft`, `built`, `technically-verified`, `instructionally-verified`, `used`, `revised`, or `archived`.

## Interactive websites

Build from the shared artifact kit when its primitives fit. Keep domain logic local to the artifact. Promote a new shared component only after real reuse or a clear repeated need. `verify-web-artifact` defines the four verification lanes.

## Accumulating documents

Some artifacts are read over months rather than used once. A course or project notebook grows
a section at a time, and the learner annotates their copy and inserts pages of their own.

The copy they annotate is the only place their work exists, so the document is never
regenerated. A new section is rendered alone and spliced into the file they return.

**Ownership decides what may be rewritten.** The contents page belongs to the document and is
replaced when it goes stale. Every other page belongs to the learner once delivered, so a
correction is an inserted page, not a replacement. A clean document is worth less than a term
of their annotation.

- Keep one source file that produces both the live page and the export, so the two cannot drift.
- Give that source a way to render a named subset of itself, which makes a clean splice possible.
- Inspect the returned file before placing anything. Their inserted pages mean the layout
  cannot be assumed.
- Keep the filename stable for the life of the document.
- Assume every returned page is marked. Tablet exports often flatten ink into the page, so an
  annotation count of zero proves nothing. Replacing any page needs their confirmation.

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

## Slide decks

A deck is built locally as the user's own work, not in a hosted slide tool. One outline with
stable slide IDs feeds every output, so they cannot drift.

- `presentation.html` is the live version: one self-contained page where the arrow keys play
  each slide's builds, then advance. It is as close to a video as a click-through can be.
- `deck.pdf` is printed from that page in a mode that shows every build at once. It is the
  copy to share.
- `video.mp4`, when wanted, follows the outline's order and parts. Narrate it when people
  will watch without the presenter.
- Presenter notes, when asked for, hold the script and a checklist.

Use vuhri's design tokens in `apps/artifact-studio/src/styles.css` unless the user names
another system. Before handing a deck over, step every slide forwards and back in a real
browser and inspect every printed page. Keep the outputs in the project's `final/` folder.

## Video

`direct-video` owns direction, rendering, verification, and revision for every video, with an adapter for learning or marketing constraints. A video that follows a deck takes the outline's slide IDs as its beat IDs.
