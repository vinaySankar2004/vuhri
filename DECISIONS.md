# Decisions

This file records choices that should remain stable until new evidence justifies changing them.

## 2026-08-24

### Use vahri as the public identity

The project, repository, package scope, and user-facing studio use the lowercase name `vahri`. The local directory rename is intentionally deferred until after this session.

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

Video direction is a reusable domain beyond education. A general `direct-video` skill owns the editorial contract, hook, narrative movement, visual thesis, stable-ID beat sheet, shot plan, revision protocol, and library governance. vahri's `remotion-learning-director` remains a thin adapter that adds instructional evidence, misconceptions, learning cues, and companion checks.

### Grow the motion library from rendered evidence

The video arsenal distinguishes semantic primitives, composition patterns, style systems, and proven examples. New entries begin as candidates. They become stable only after reuse or an explicit cross-topic test, documented failure conditions, and rendered verification.

## 2026-08-23

### Begin with the inquiry

vahri answers or teaches first. It does not force a course, mode, or onboarding ritual onto an ordinary question.

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
