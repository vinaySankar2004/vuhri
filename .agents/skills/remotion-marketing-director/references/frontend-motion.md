# Frontend motion

Use strong frontend design as a visual system, then translate it into a timed argument. Do not reproduce a webpage scroll or copy another site's recognizable sequence.

## Reference research pass

When the direction is open, study a small, varied reference set:

- one reference for brand world or atmosphere;
- one for composition and typography;
- one for motion rhythm and transition continuity;
- one for product demonstration or conversion clarity;
- one technical example when 3D, shaders, unusual compositing, or a new dependency is proposed.

For each source, record the property being studied and the project decision it influences. Several references may inform one original system. One reference should not determine the whole sequence.

## Extract the design language

From a reference page, screenshot, Figma file, or codebase, record:

- composition grid and dominant silhouette;
- typography roles and scale contrast;
- color roles, gradients, and material treatment;
- corner, border, stroke, shadow, and glow language;
- depth cues and layer order;
- focal product or interface object;
- motion curves, stagger, camera restraint, and transition continuity;
- which property supports the message and which is decorative.

Use an inspiration ledger from `direct-video`. Study properties from several references instead of cloning one source.

## Translate interaction into time

Web interaction lets a user choose the pace. Video owns the pace. Convert:

- scroll progression -> chapter or camera progression;
- hover -> focus, proof, or annotation moment;
- card stack -> ordered reveal or comparison;
- sticky section -> held stage while evidence changes;
- page transition -> semantic state change;
- cursor movement -> guided attention only when pointer intent matters;
- responsive layout -> separately composed aspect-ratio variants.

Do not animate every possible interaction. Select the few states that prove the product or build the desired feeling.

## Depth modes

### Layered 2.5D

Use HTML, SVG, images, or video planes with shared perspective, z separation, occlusion, shadow, light, and parallax. This is the default for polished interface and landing-page motion because text stays crisp and revision remains cheap.

### True 3D

Use real geometry when the viewer needs to understand material, volume, rotation, assembly, spatial relationship, or physical product behavior. In Remotion, `@remotion/three` integrates React Three Fiber with frame-driven rendering through `useCurrentFrame()`.

### Hybrid

Use a 3D product or environment as the hero and keep headlines, proof, captions, UI, and CTA in 2D layers. This preserves clarity while giving the film tangible depth.

## Depth rules

- Use depth to express hierarchy, relationship, or tangibility.
- Preserve a shared vanishing point for related planes.
- Use occlusion, scale, shadow, light, and focus consistently.
- Keep important text on stable readable planes. Avoid deep or constantly rotating text.
- Give one layer priority. Excessive z separation makes the eye refocus repeatedly.
- Prefer restrained camera movement. Move the product or camera only when the new angle reveals information.
- Keep large peripheral motion and repeated oscillation low.
- Provide a non-motion cue for every important state change.

These rules align with [Apple's motion guidance](https://developer.apple.com/design/human-interface-guidelines/motion), [Apple's spatial depth guidance](https://developer.apple.com/design/human-interface-guidelines/spatial-layout/), and [Motion's explanation of web perspective and 3D transforms](https://motion.dev/docs/3d-transforms).

## Remotion implementation notes

- Use [Remotion's `@remotion/three`](https://www.remotion.dev/docs/three) for React Three Fiber scenes.
- Animate Three.js markup declaratively from the current frame. Do not use the ordinary React Three Fiber `useFrame()` loop inside rendered video.
- Pass explicit canvas dimensions.
- Use `layout="none"` for Remotion sequences inside `ThreeCanvas`.
- Configure the recommended Chromium `angle` renderer for Three.js rendering.
- Keep UI and caption layers outside the 3D canvas when possible.
- Verify textures, shadows, antialiasing, camera clipping, and representative frames on the actual render path.

## Quality risks

- Landing-page beauty replaces offer clarity.
- Camera movement delays product recognition.
- Glass and glow reduce text contrast.
- Everything floats, so depth no longer communicates hierarchy.
- A desktop composition is cropped into vertical instead of recomposed.
- The product appears to perform an action it cannot actually perform.
- Render cost grows while the visible improvement remains small.
