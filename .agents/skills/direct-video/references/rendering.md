# Rendering

Choose the renderer by what the video needs. Both share the same direction artifacts, stable IDs, and verifier.

## Choose

| Renderer | Use when | Cost |
| --- | --- | --- |
| Remotion | Complex or sustained animation, 3D through `@remotion/three`, caption tooling, Studio review, reusable React components | An `npm install` per project, often hundreds of megabytes. Remove `node_modules` when the project ends. |
| HTML frame renderer | A video that follows a deck, text and diagram motion, or anything one page can draw | A headless browser and ffmpeg, shared across projects |

For Remotion, load Remotion's `remotion-best-practices` skill when it is installed, otherwise read [the Remotion docs](https://www.remotion.dev/docs). Its guidance on mechanics wins over creative advice.

The HTML frame renderer is a page that draws any frame from a time value, captured frame by frame in headless Chromium and encoded with ffmpeg. It has produced a verified narrated talk video. Turn it into a reusable tool on its next use, once a second video shows what varies.

## Determinism

- Every frame is a pure function of time and scene data. No browser-time animation, timers, or unseeded randomness.
- Wait for fonts, images, and video frames to load before capturing each frame.
- Keep timing, copy, and theme in data keyed by beat and shot IDs, never buried inside a component.

## Capture speed

Capture is usually the slowest step of the HTML renderer, and headless Chromium often draws on the CPU even when a GPU exists. Enable the platform's GPU backend for ANGLE and confirm the reported renderer changed. Pipe frames into ffmpeg instead of writing images to disk, and split long videos across a few browser instances. Measure before and after: these notes come from one contributor's measurements on one machine.

## Formats and encoding

- Presets: landscape 1920x1080, vertical 1080x1920, square 1080x1080, all at 30 fps. Compose each format separately rather than cropping one, and pass `--format` to the verifier.
- Deliver H.264 in `yuv420p`, AAC audio, and `-movflags +faststart`. Keep film grain subtle, because it inflates file size sharply.
- Narrated delivery targets about -16 LUFS integrated loudness with true peak at or below -1 dBFS. Measure with `ffmpeg -i final.mp4 -af ebur128=peak=true -f null -`.

## Poster

Most platforms use frame 0 as the thumbnail. Pick the strongest settled frame, with text fully in and nothing mid-transition, then run:

```bash
python3 tools/bake_poster.py render.mp4 --at 3.2 --out final.mp4
```

It writes `final.jpg` and replaces frame 0 only, so duration and sync are unchanged. Verify the baked file with `--poster final.jpg`.
