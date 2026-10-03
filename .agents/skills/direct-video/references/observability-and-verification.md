# Observability and pre-verification

Treat verification evidence as part of the video, not as disposable agent output. A human reviewer should receive a render that has already survived a technical pass, an agent playback pass, and an agent visual pass.

## Portable contract

Keep the verification layer independent of any one coding-agent harness. Codex, Cursor, Claude Code, and a person at a terminal should be able to run the same command and inspect the same files.

The portable boundary is:

- a rendered media file;
- a plain JSON shot manifest with stable IDs and seconds;
- Python 3 plus `ffmpeg` and `ffprobe` on `PATH`;
- PNG evidence, JSON metadata, Markdown reports, and raw diagnostic logs on disk.

An agent-specific image viewer or browser may inspect the PNG files. It must not be the only place where evidence exists. Record the viewer used in `visual-review.md`.

## Run the gate

New staged projects contain `tools/verify_video.py`. Run it against the actual exported file, not only a Studio preview:

```bash
python3 tools/verify_video.py 06_production/out/final.mp4 \
  --out 07_review/runs/2026-08-24T120000Z \
  --manifest 07_review/shot-manifest.json \
  --format vertical --duration 15 --require-audio --poster 06_production/out/final.jpg
```

`--format` sets the expected size and 30 fps; `--width`, `--height`, and `--fps` override it. `--poster` checks that frame 0 matches the poster written by `bake_poster.py`.

Use one-second overview sampling for work up to 45 seconds. For longer work, choose a documented interval and preserve shot-boundary sampling through the manifest.

The verifier refuses to overwrite a prior evidence directory. Each rerender gets a new run so regression evidence stays inspectable.

## Shot manifest

Use seconds in the portable manifest. Preserve the same IDs used in the beat sheet, shot plan, scene data, and revision ledger.

```json
{
  "schema_version": 1,
  "shots": [
    {
      "id": "B01.S01",
      "start": 0,
      "end": 2.4,
      "review_times": [0.6, 1.8],
      "text": [{"id": "B01.S01.T01", "words": 5, "settled": 0.5, "exit": 2.3}]
    },
    {"id": "B01.S02", "start": 2.1, "end": 4.0}
  ]
}
```

The verifier extracts every shot's entry and exit plus optional internal moments. Consecutive shots whose ranges overlap are joined by a transition, and the middle of each overlap is sampled. Optional `text` entries give each readable line's word count and settled and exit times, and lines that leave before the reading floor in [duration and quality](duration-and-quality.md) are flagged. Gaps are reported for interpretation. Invalid ranges, invalid text timings, and duplicate IDs stop the run.

## Evidence produced

Every run contains:

- `metadata.json`: raw media and stream metadata;
- `verification.json`: machine-readable checks and gate status;
- `verification-report.md`: concise technical result and handoff condition;
- `frames/`: interval samples from the full timeline plus the final state;
- `shot-frames/`: stable-ID entry, exit, requested review, and mid-transition frames;
- `contact-sheet.png`: a fast visual scan of the complete timeline;
- `shot-contact-sheet.png`: a fast stable-ID boundary scan when a manifest is supplied;
- `diagnostics.log`: raw black, freeze, and silence detector output;
- `visual-review.md`: the agent playback and visual-review record.

Black, freeze, silence, and reading-time detections are flags, not automatic creative failures. A hold or pause may be intentional. The agent must interpret each flag against the direction and audio plan.

## Agent visual pass

The actual video remains the authority. The contact sheet finds discontinuities quickly but cannot prove motion quality, timing, audio quality, or synchronization.

Before human handoff:

1. Watch the complete rendered file with sound.
2. Inspect the overview and shot contact sheets with the environment's image viewer or in a browser.
3. Inspect stable-ID frames at every shot boundary.
4. Compare the render with the direction brief, beat sheet, shot plan, script, platform settings, and quality bar.
5. Write observable findings with times or stable IDs, severity, correction, and acceptance check.
6. Fix material defects, rerender, and create a new verification run.
7. Change `visual-review.md` to pass only when every failure is fixed or explicitly disclosed.

For frontend-inspired work, also inspect perspective consistency, text crispness, z-order, lighting continuity, browser chrome, crop, safe zones, and whether depth ever competes with the offer or proof.

## Gate states

- Technical pass: required metadata matches and every diagnostic pass ran.
- Visual pass: an agent completed playback, contact-sheet, and shot-boundary review.
- Ready for human review: both gates pass and open limitations are disclosed.

Do not call a render pre-verified while `visual_gate` or the Markdown review remains pending. Automated checks reduce avoidable back and forth. They do not replace editorial judgment.
