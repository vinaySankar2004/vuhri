#!/usr/bin/env python3
"""Make a chosen frame the video's first frame, so every thumbnail shows it.

Most players and sharing platforms use frame 0 as the idle thumbnail and ignore
cover metadata. This extracts the frame at --at as a poster image and draws it
over frame 0 only, so duration, frame count, and audio timing stay unchanged.
Adapted from the poster step in latent-spaces/brag (MIT).
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("video", type=Path, help="Rendered video")
    parser.add_argument("--at", type=float, required=True, help="Seconds of a settled, postable frame")
    parser.add_argument("--out", type=Path, required=True, help="New video with the poster as frame 0")
    parser.add_argument("--poster", type=Path, help="Poster image path (default: --out with .jpg)")
    return parser.parse_args()


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"Command failed ({result.returncode}): {' '.join(command)}\n{detail}")
    return result


def probe(video: Path) -> dict[str, float]:
    data = json.loads(
        run(
            [
                "ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
                "-show_entries", "stream=nb_read_frames:format=duration", "-of", "json", str(video),
            ]
        ).stdout
    )
    return {
        "frames": float(data["streams"][0]["nb_read_frames"]),
        "duration": float(data["format"]["duration"]),
    }


def bake_poster(video: Path, at: float, out: Path, poster: Path | None = None) -> Path:
    video = video.expanduser().resolve()
    out = out.expanduser().resolve()
    poster = (poster or out.with_suffix(".jpg")).expanduser().resolve()
    if not video.is_file():
        raise SystemExit(f"Video does not exist: {video}")
    if out == video:
        raise SystemExit("--out must differ from the input so the original render is kept")
    for path in (out, poster):
        if path.exists():
            raise SystemExit(f"Refusing to overwrite: {path}")
    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool) is None:
            raise SystemExit(f"Required tool is not available on PATH: {tool}")

    source = probe(video)
    if not 0 <= at < source["duration"]:
        raise SystemExit(f"--at {at}s is outside the video (0 to {source['duration']:.3f}s)")

    out.parent.mkdir(parents=True, exist_ok=True)
    poster.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{at:.6f}", "-i", str(video),
         "-frames:v", "1", "-q:v", "2", "-update", "1", str(poster)])
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(video), "-i", str(poster),
         "-filter_complex", "[0:v][1:v]overlay=0:0:enable='eq(n,0)'[v]",
         "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
         "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", str(out)])

    baked = probe(out)
    if baked["frames"] != source["frames"]:
        raise RuntimeError(f"Frame count changed: {source['frames']:.0f} to {baked['frames']:.0f}")
    print(f"Poster {poster.name} is frame 0 of {out} ({baked['frames']:.0f} frames, {baked['duration']:.3f}s)")
    return poster


def main() -> None:
    args = parse_args()
    try:
        bake_poster(args.video, args.at, args.out, args.poster)
    except RuntimeError as error:
        print(f"Poster bake failed: {error}", file=sys.stderr)
        raise SystemExit(2) from error


if __name__ == "__main__":
    main()
