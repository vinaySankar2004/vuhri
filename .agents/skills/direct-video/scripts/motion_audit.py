"""Frame-by-frame motion audit for a rendered video.

Flags three kinds of motion fault that a contact sheet cannot show:
- flicker: a region changes, then changes back on the next frame (A, B, A);
- pop: a region changes far more in one frame than in the frames around it;
- hard cut: the whole frame changes at once;
- oscillation: a region's brightness keeps reversing direction within a few frames, the
  signature of a strobe even when it never returns exactly to an earlier frame.

Usage: python motion_audit.py video.mp4 [--manifest shot-manifest.json] [--fps 30]
Needs numpy and ffmpeg. Prints flagged times, grouped, with the stable shot ID when a
manifest is given.
"""

import argparse
import json
import subprocess
import sys

import numpy as np

W, H = 135, 240  # one eighth of 1080x1920
TILES_X, TILES_Y = 6, 10


def frames(path: str):
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={W}:{H},format=gray", "-f", "rawvideo", "-"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    size = W * H
    while True:
        buf = proc.stdout.read(size)
        if len(buf) < size:
            break
        yield np.frombuffer(buf, dtype=np.uint8).reshape(H, W).astype(np.float32)


def tile_means(diff: np.ndarray) -> np.ndarray:
    th, tw = H // TILES_Y, W // TILES_X
    return diff[: th * TILES_Y, : tw * TILES_X].reshape(TILES_Y, th, TILES_X, tw).mean(axis=(1, 3))


def shot_at(manifest, t):
    if not manifest:
        return ""
    ids = [s["id"] for s in manifest["shots"] if s["start"] <= t < s["end"]]
    return "/".join(ids)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--manifest")
    ap.add_argument("--fps", type=float, default=30)
    ap.add_argument("--tile", type=float, default=6.0, help="tile change (0-255) that counts as motion")
    ap.add_argument("--amp", type=float, default=1.5, help="tile brightness step that counts in oscillation")
    args = ap.parse_args()
    manifest = json.load(open(args.manifest)) if args.manifest else None

    fs = list(frames(args.video))
    if len(fs) < 3:
        print("too few frames")
        return 1
    d1 = [np.zeros((TILES_Y, TILES_X))] + [tile_means(np.abs(fs[i] - fs[i - 1])) for i in range(1, len(fs))]
    whole = np.array([np.abs(fs[i] - fs[i - 1]).mean() if i else 0 for i in range(len(fs))])

    flags = []
    # Oscillation: per tile, count direction reversals of mean brightness in a 9-frame window.
    means = np.stack([f[: (H // TILES_Y) * TILES_Y, : (W // TILES_X) * TILES_X]
                      .reshape(TILES_Y, H // TILES_Y, TILES_X, W // TILES_X).mean(axis=(1, 3)) for f in fs])
    step = np.diff(means, axis=0)
    moving = np.abs(step) > args.amp
    sign = np.sign(step) * moving
    for i in range(0, len(step) - 9):
        win = sign[i : i + 9]
        reversals = np.zeros((TILES_Y, TILES_X))
        prev = np.zeros((TILES_Y, TILES_X))
        for row in win:
            flip = (row != 0) & (prev != 0) & (row != prev)
            reversals += flip
            prev = np.where(row != 0, row, prev)
        hit = reversals >= 3
        if hit.any():
            flags.append((i + 4, "oscillation", int(hit.sum()), float(np.abs(step[i : i + 9]).max())))
    for i in range(2, len(fs) - 1):
        a, b = d1[i], d1[i + 1]
        back = tile_means(np.abs(fs[i + 1] - fs[i - 1]))
        flick = (a > args.tile) & (b > args.tile) & (back < 0.35 * np.minimum(a, b))
        if flick.any():
            flags.append((i, "flicker", int(flick.sum()), float(a.max())))
        lo, hi = max(1, i - 6), min(len(fs), i + 7)
        neighbourhood = np.stack([d1[j] for j in range(lo, hi) if j != i])
        typical = np.median(neighbourhood, axis=0)
        pop = (a > args.tile * 2) & (a > 5 * (typical + 0.5))
        if pop.any():
            flags.append((i, "pop", int(pop.sum()), float(a.max())))
        if whole[i] > 25:
            flags.append((i, "hard cut", 0, float(whole[i])))

    if not flags:
        print("No flicker, pops or hard cuts found.")
        return 0
    flags.sort(key=lambda x: (x[1], x[0]))
    last = None
    for i, kind, tiles, size in flags:
        t = i / args.fps
        key = (kind, i)
        if last and last[0] == kind and i - last[1] <= 3:
            last = key
            continue
        print(f"{t:7.2f}s  frame {i:5d}  {kind:8s}  tiles={tiles:2d}  change={size:5.1f}  {shot_at(manifest, t)}")
        last = key
    return 0


if __name__ == "__main__":
    sys.exit(main())
