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

- `characters/`: one style file per character, the look applied to any skeleton;
- `motion/`: recorded or generated motion, with source and licence per file;
- `renders/`: clips, rebuildable from the two above.

Add an asset only when a job uses it, and record its source and licence when it arrives.

## Modules

- Characters: [characters](references/characters.md). A character style plus a motion becomes
  a flat 2D figure on a transparent background.

Add a module, such as product shots, when the first job needs it: one reference, one script,
proven on that job. Do not build modules ahead of a need.

## Keep it fast

A clip should take minutes, not hours. Reuse a style and a motion before making new ones;
render at the video's size, never larger; use the Workbench engine for flat looks and move to
Eevee or Cycles only when light is the point.

## Verify

Lay out the rendered frames one at a time around every key moment with `direct-video`'s
`frame_grid.sh` before the clip goes into a video, then verify the finished video as usual.
Record each fault and its fix in the video project's `memory/failures.md`.
