# Library system

Use this reference to grow a reusable arsenal without turning one successful video into a rigid house style.

## Four library layers

### Semantic primitives

Small verbs that communicate a change: reveal, trace, gate, compare, transform, accumulate, rank, focus, balance, fracture, resolve, and hand off.

Each entry records:

- communicative job;
- required state in;
- state change;
- attention path;
- useful variants;
- failure conditions;
- compatible subjects and layouts;
- available implementations.

### Composition patterns

Reusable combinations of primitives, such as a protocol trace, layered reveal, before-and-after transformation, decision matrix, accumulating proof stack, annotated product walkthrough, or causal chain.

Patterns define roles and sequence. They should not freeze copy, colors, or a recognizable visual identity.

### Style systems

Tokens and motion behavior that make a video coherent: color roles, type scale, spacing, stroke language, corner language, camera restraint, spring families, timing scale, texture, caption treatment, and audio behavior.

A style system can be swapped without changing the semantic beat plan.

### Proven examples

Rendered compositions used as references, tests, and sources for extraction. Examples do not become templates automatically. Record what worked, what was specific to the topic, and what should not be copied.

## Registry entry

```markdown
## Gate

- Level: candidate | proven | core
- Communicates: A proposal cannot continue until an authority changes state.
- State in: Subject moving toward a visible boundary; authority named.
- State change: Boundary changes from blocking to permitting.
- Attention: Subject -> authority -> boundary -> subject.
- Variants: approval, authorization, validation, threshold, rate limit.
- Fails when: The authority is unnamed, the gate opens before the decision, or color is the only state cue.
- Implementations: Remotion 2D rail gate; UI modal approval; physical barrier metaphor.
- Evidence: Links to rendered examples and review notes.
```

## Promotion rule

Promote a candidate to `proven` after two meaningfully different uses or one use plus an explicit cross-topic test. Promote to `core` only after its API is stable, failure conditions are documented, reduced-motion behavior exists where relevant, and rendered tests cover its variants.

Prefer source-owned components whose code can be inspected and adapted. The Remotion ecosystem currently includes copy-owned libraries and template collections such as [Onda](https://github.com/degueba/onda), [Remocn](https://github.com/remocn/remocn), [Remotion Templates by RVE](https://github.com/reactvideoeditor/remotion-templates), and the [official Remotion resource index](https://www.remotion.dev/docs/resources). Treat them as implementation research. Review licenses and dependencies before adopting code.

## Inspiration ledger

For every inspiration, record:

- source URL and creator;
- the exact property being studied, such as pacing, transition continuity, caption behavior, or camera restraint;
- an observation stated without copying protected text or assets;
- the project decision it influenced;
- whether the influence is semantic, stylistic, or technical.

Build a vocabulary from observed properties. Do not build a style clone from a creator's finished sequence.
