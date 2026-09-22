# Mathematical notation

How mathematics is written in anything the user reads. The medium decides the form, and there
are two media with different limits.

A chat client renders markdown in a proportional font. Unicode subscripts render small, collide
with emphasis markers, and nothing aligns into columns, so a derivation written inline becomes
harder to read than the source it came from. A web page has no such limit and should typeset
properly.

## The rule in chat

**Every displayed equation, derivation, and matrix goes in a fenced code block** with no
language tag. Markdown does not process inside a fence, the font is monospace, and columns
align. This is not a preference about density. It is the only way matrices render at all.

## Inside a code block

- **No markdown emphasis.** No asterisks, no bold. They appear literally.
- **Subscripts with an underscore**: `u_1`, `x_i`, `lambda_max`. Never `uᵢ`.
- **Superscripts with a caret**: `A^T`, `x^2`, `(X^T X)^{-1}`. Never `Aᵀ` or `x²`.
- **Sums written out**: `sum_{i=1..m}`. Never a bare sigma with a unicode index.
- **Align multi-step derivations on the equals sign**, one step per line, with the
  justification for each step either trailing the line or given in prose underneath.
- **Matrices as aligned grids** with square brackets, padded so the columns line up.
- Greek letters may stay as single characters (`alpha`, `lambda`, or the unicode letter) when
  unambiguous. It is the sub and superscripts that break, not the letters.

## Outside a code block

- Inline mathematics is for short names only, wrapped in backticks: `rank(A)`, `null(T)`,
  `S` perp. Anything with an index, an exponent, or more than one operator gets a fence.
- Never bold a variable to distinguish a vector. State the convention once, in prose, and
  rely on it: lowercase for vectors, uppercase for matrices, Greek for scalars.

## In a web artifact, use real typesetting

The plain-text convention above is a workaround for a rendering limit that a web page does not
have. A page carrying mathematics typesets it, and the fenced-block rules do not apply there.

Prefer MathJax over KaTeX in a published artifact. Artifact content policies commonly allow
external scripts from a short CDN list while blocking external stylesheets and font files,
which KaTeX needs for both. MathJax's SVG build is a single self-contained script that needs
neither.

```
<script>window.MathJax = { tex:{...}, svg:{ fontCache:'global' } };</script>
<script id="MathJax-script" async
  src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-svg.js"></script>
```

Define macros in the `tex.macros` config rather than repeating long expressions, and set a
monospace fallback style for the pre-typeset state so a blocked script degrades to readable
source rather than raw braces. MathJax skips `pre` and `code` by default, so any genuinely
tabular block still renders as plain text.

A page that will also be read on paper carries a further constraint. An `overflow` container
clips rather than scrolls when printed, and typeset mathematics cannot wrap, so a long
expression in a narrow column runs off the edge. See the printing section of `artifacts.md`.

## Diagrams

When the geometry is the content rather than an illustration of it, draw it. See
`artifacts.md` for when an artifact is warranted; a quick inline visual is usually enough.

## Example

```
Least squares, from the orthogonality of the residual.

  y - X w   orthogonal to   col(X)
  X^T (y - X w)  =  0
  X^T X w        =  X^T y

When rank(X) = d, X^T X is invertible and

  w  =  (X^T X)^{-1} X^T y
```
