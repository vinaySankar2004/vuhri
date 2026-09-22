# Decisions

This file records choices that should remain stable until new evidence justifies changing them.

## 2026-09-21

### Let the medium decide how mathematics is written

A chat client renders markdown in a proportional font, where unicode subscripts collide with
emphasis markers and nothing aligns, so a derivation written inline is harder to read than its
source. Displayed equations and matrices go in fenced code blocks there. A web page has no such
limit and typesets properly. The rules are recorded in `method/math-notation.md`, which is
loaded from the constitution alongside the writing method.

### Treat a growing annotated document as append-only

A notebook read across months is annotated by the learner, who also inserts pages of their own.
That copy is the only place their work exists, so the document is never regenerated. New
sections are rendered alone and spliced into the file they return. The contents page belongs to
the document and may be replaced; every other page belongs to the learner once delivered, which
makes a correction an inserted page rather than a rewrite. One HTML source produces both the
live page and the export so the two cannot drift, and it must be able to render a named subset
of itself. `scripts/splice-notes-pdf.py` implements this.

### Require an artifact to survive printing

An artifact meant for paper or a tablet must transfer completely apart from its interactivity,
with each control replaced by the static result it would have produced. Overflow containers
clip rather than scroll, typeset mathematics cannot wrap, and CSS grid mis-fragments across a
page break. Every rendered page is inspected after any content change, because new content
moves every page break after it.

## 2026-09-16

### Allow incognito sessions

A session declared incognito in the user's first message runs with no read or write access to `local/` or to memory stored outside the repository, and leaves no trace of having happened. The mode is one way. It cannot be declared retroactively, because a mid-session switch would require deleting work already recorded, and it cannot be lifted, because a session that can rejoin memory is not private. The agent never asks for it or offers it, so an undeclared session is always a normal one. Incognito is scoped to questions, reading, and discussion rather than production work, and it does not relax writing or teaching standards.

## 2026-08-24

### Use vuhri as the public identity

The project, repository, package scope, and user-facing studio use the lowercase name `vuhri`. The local directory rename is intentionally deferred until after this session.

### Make video pre-verification portable and evidence-backed

Every built video must pass a pre-human verification stage against the actual render. The shared boundary is Python 3, `ffmpeg`, `ffprobe`, plain JSON, Markdown, and PNG files so Codex, Cursor, Claude Code, or a person at a terminal can run the same checks. Each run preserves media metadata, interval frames, the final frame, stable-ID shot frames, contact sheets, black, freeze, and silence diagnostics, and an explicit visual-review record. An automated pass never implies a visual pass.

### Direct for non-editors by default

Video workflows assume the user can describe the idea, audience, product, taste, and reaction without knowing production terminology. The director recommends duration, hook, visual thesis, production mode, shot density, camera behavior, audio treatment, and platform variants in plain language. The user is asked only for business, truth, source, permission, or taste decisions that cannot be inferred safely.

### Add a marketing adapter without weakening the general core

The `remotion-marketing-director` skill adds campaign objective, offer, proof, CTA, platform research, variant testing, claims, rights, and frontend-inspired 2.5D or 3D direction. The general `direct-video` skill remains format-neutral, and the learning adapter remains responsible for instructional evidence and checks.

### Declare a rapid video quality envelope

The default rapid high-polish envelope is 2 to 45 seconds. Work from 45 to 90 seconds uses an extended workflow with sections and more review. Longer work uses modular long-form production. The boundary controls process and promises; it does not claim that longer videos cannot be excellent.

### Learn from verified outcomes at the closest layer

Sustained video projects use staged edit surfaces plus local decisions, failures, lessons, and library candidates. Raw generated output is not a reference standard. A correction stays project-specific until reuse or a deliberate cross-topic test supports a broader rule, and every promoted failure lesson includes a regression check.

### Separate general video direction from learning adaptation

Video direction is a reusable domain beyond education. A general `direct-video` skill owns the editorial contract, hook, narrative movement, visual thesis, stable-ID beat sheet, shot plan, revision protocol, and library governance. vuhri's `remotion-learning-director` remains a thin adapter that adds instructional evidence, misconceptions, learning cues, and companion checks.

### Grow the motion library from rendered evidence

The video arsenal distinguishes semantic primitives, composition patterns, style systems, and proven examples. New entries begin as candidates. They become stable only after reuse or an explicit cross-topic test, documented failure conditions, and rendered verification.

## 2026-08-23

### Begin with the inquiry

vuhri answers or teaches first. It does not force a course, mode, or onboarding ritual onto an ordinary question.

### Use spaces for durable continuity

A space can represent an inquiry, topic, course, exam, paper, project, or practice track. A course is one possible context, not the root abstraction.

### Keep public method and private learner state separate

The shared repository contains reusable teaching behavior and foundations. `local/` contains personal sources, attempts, assessments, memory, and artifacts.

### Store structured evidence by default

Meaningful learning sessions store concise evidence. Raw transcripts are not duplicated by default.

### Keep inferred preferences tentative

Explicit preferences take effect immediately. Inferred preferences begin as candidates, retain counterevidence, and become stronger only through confirmation or repeated use.

### Track capability with conditions

Capability records state what the learner demonstrated, in which context, with what help, and how recently. Initial versions use descriptive states instead of unsupported percentages.

### Treat artifacts as instructional software

An artifact begins with a learning brief. Interactive websites require build, interaction, visual, accessibility, and instructional checks in a real browser.

### Reuse before expanding the artifact kit

The shared kit grows from components that prove useful in real artifacts. The repository does not predict a full component catalog in advance.

### Verify Codex first

Codex is the active test environment. Other agents receive compatibility through `AGENTS.md`, plain files, and Agent Skills conventions. Tool-specific infrastructure is added only after a demonstrated need.
