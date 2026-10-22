---
name: build-in-blender
description: Make motion and 3D in Blender, run headless from scripts, and hand the result to a video as a transparent clip. Use when a character must move like a real one (a kick, a celebration, a wave), when an object needs real light, depth or physics (a product turning, a coin falling), or when the user asks for Blender. Do not use for charts, text, numbers or UI motion; those stay in Remotion through `direct-video`.
---

# Build in Blender

Blender does motion and 3D; Remotion assembles the video. Every Blender job is a script run
headless, so it is repeatable, and every job saves its `.blend` so a person can open it, adjust
it, or learn from it.

## Run it

```bash
/Applications/Blender.app/Contents/MacOS/Blender -b --python <script.py> -- <args>
```

Install once with `brew install --cask blender`. Scripts live in `scripts/`; check the
version a script was written for before trusting an API call (written on Blender 5.2).

## The contract with a video

A Blender job produces one folder:

- a PNG sequence with a transparent background, `0001.png` onward, at the video's frame rate;
- `meta.json` with what the video needs to line things up: frame rate, frame count, and any
  key moment in frames and output pixels (a foot's contact, a product's settle);
- `scene.blend`, the scene that rendered it.

The video plays the sequence and places its own data-driven elements from `meta.json`. Renders
are rebuildable and are never committed.

## The asset library

Assets live in `local/blender/`, indexed in its `README.md`:

- `characters/`: one design file per character, built into its `.blend`;
- `motion/`: recordings with source and licence, pose layers, and the motions built from them;
- `renders/`: clips, rebuildable from the two above.

Built `.blend` files are rebuildable from the design files and recordings, so they are not
committed; a `.blend` someone has edited by hand becomes a source and is.

Add an asset only when a job uses it, and record its source and licence when it arrives.

## Modules

- Characters: [characters](references/characters.md). A designed character, a motion retargeted
  onto it, and a shot of the two: three parts, each its own script and file.

Add a module, such as product shots, when the first job needs it: one reference and its scripts,
proven on that job. Do not build modules ahead of a need.

## Keep it fast

A clip should take minutes, not hours. Reuse a character and a motion before making new ones;
render at the video's size, never larger; use the Workbench engine for flat looks and move to
Eevee or Cycles only when light is the point.

## Verify

Lay out the rendered frames one at a time around every key moment with `direct-video`'s
`frame_grid.sh` before the clip goes into a video, then verify the finished video as usual.
Record each fault and its fix in the video project's `memory/failures.md`.
