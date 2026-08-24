#!/usr/bin/env python3
"""Create portable technical and visual-review evidence for a rendered video."""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any


@dataclass
class Check:
    name: str
    status: str
    expected: str
    actual: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path, help="Rendered video to verify")
    parser.add_argument("--out", type=Path, required=True, help="New evidence directory")
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Seconds between overview samples (default: 1)",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        help="Optional JSON shot manifest with stable IDs and timing",
    )
    parser.add_argument("--width", type=int, help="Expected video width")
    parser.add_argument("--height", type=int, help="Expected video height")
    parser.add_argument("--fps", type=float, help="Expected frame rate")
    parser.add_argument("--duration", type=float, help="Expected duration in seconds")
    parser.add_argument(
        "--duration-tolerance",
        type=float,
        default=0.15,
        help="Allowed duration difference in seconds (default: 0.15)",
    )
    parser.add_argument(
        "--require-audio",
        action="store_true",
        help="Fail when the rendered file has no audio stream",
    )
    return parser.parse_args()


def run(command: list[str], *, allow_failure: bool = False) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode != 0 and not allow_failure:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"Command failed ({result.returncode}): {' '.join(command)}\n{detail}")
    return result


def tool_version(tool: str) -> str:
    result = run([tool, "-version"])
    return result.stdout.splitlines()[0].strip()


def frame_rate(stream: dict[str, Any]) -> float:
    value = stream.get("avg_frame_rate") or stream.get("r_frame_rate") or "0/1"
    try:
        return float(Fraction(value))
    except (ValueError, ZeroDivisionError):
        return 0.0


def media_duration(metadata: dict[str, Any], video_stream: dict[str, Any]) -> float:
    candidates = [metadata.get("format", {}).get("duration"), video_stream.get("duration")]
    for value in candidates:
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return 0.0


def safe_id(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-.")
    if not cleaned:
        raise ValueError(f"Shot ID cannot be converted into a safe filename: {value!r}")
    return cleaned


def extract_frame(video: Path, timestamp: float, destination: Path) -> None:
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            f"{timestamp:.6f}",
            "-i",
            str(video),
            "-frames:v",
            "1",
            "-update",
            "1",
            "-y",
            str(destination),
        ]
    )


def extract_overview_frames(
    video: Path, frames_dir: Path, interval: float, duration: float
) -> list[Path]:
    frames_dir.mkdir(parents=True)
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(video),
            "-vf",
            f"fps=1/{interval}",
            "-start_number",
            "0",
            "-y",
            str(frames_dir / "sample-%04d.png"),
        ]
    )
    frames = sorted(frames_dir.glob("sample-*.png"))
    last_regular_time = max(0.0, (len(frames) - 1) * interval)
    if duration > 0 and duration - last_regular_time > 0.10:
        final_path = frames_dir / f"sample-{len(frames):04d}.png"
        extract_frame(video, max(0.0, duration - 0.05), final_path)
        frames.append(final_path)
    return frames


def create_contact_sheet(frames_dir: Path, frame_count: int, destination: Path) -> None:
    if frame_count < 1:
        raise RuntimeError("No overview frames were extracted")
    columns = min(5, frame_count)
    rows = math.ceil(frame_count / columns)
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-framerate",
            "1",
            "-i",
            str(frames_dir / "sample-%04d.png"),
            "-vf",
            f"scale=320:-2,tile={columns}x{rows}:padding=8:margin=8:color=0x181818",
            "-frames:v",
            "1",
            "-y",
            str(destination),
        ]
    )


def create_shot_contact_sheet(frames_dir: Path, frame_count: int, destination: Path) -> None:
    if frame_count < 1:
        return
    shot_frames = sorted(frames_dir.glob("*.png"))
    with tempfile.TemporaryDirectory(prefix="shot-sheet-", dir=frames_dir.parent) as temporary:
        sequence_dir = Path(temporary)
        for index, source in enumerate(shot_frames):
            shutil.copyfile(source, sequence_dir / f"sample-{index:04d}.png")
        create_contact_sheet(sequence_dir, frame_count, destination)


def load_manifest(path: Path | None, duration: float) -> tuple[dict[str, Any] | None, list[str]]:
    if path is None:
        return None, []
    data = json.loads(path.read_text(encoding="utf-8"))
    shots = data.get("shots")
    if not isinstance(shots, list):
        raise ValueError("Shot manifest must contain a 'shots' list")

    warnings: list[str] = []
    previous_end = 0.0
    seen: set[str] = set()
    for index, shot in enumerate(shots):
        if not isinstance(shot, dict):
            raise ValueError(f"Shot {index + 1} must be an object")
        shot_id = str(shot.get("id", ""))
        safe_id(shot_id)
        if shot_id in seen:
            raise ValueError(f"Duplicate shot ID: {shot_id}")
        seen.add(shot_id)
        try:
            start = float(shot["start"])
            end = float(shot["end"])
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(f"Shot {shot_id} needs numeric start and end values") from error
        if start < 0 or end <= start or end > duration + 0.15:
            raise ValueError(f"Shot {shot_id} has an invalid range: {start} to {end}")
        if index and start > previous_end + 0.02:
            warnings.append(f"Gap before {shot_id}: {previous_end:.3f}s to {start:.3f}s")
        if index and start < previous_end - 0.02:
            warnings.append(f"Overlap at {shot_id}: starts {start:.3f}s before {previous_end:.3f}s")
        previous_end = max(previous_end, end)
    return data, warnings


def extract_shot_frames(
    video: Path, manifest: dict[str, Any] | None, destination: Path, duration: float
) -> list[dict[str, Any]]:
    if manifest is None:
        return []
    destination.mkdir(parents=True)
    evidence: list[dict[str, Any]] = []
    for shot_index, shot in enumerate(manifest["shots"], 1):
        shot_id = str(shot["id"])
        start = float(shot["start"])
        end = min(float(shot["end"]), duration)
        requested = shot.get("review_times", [])
        review_times = [float(value) for value in requested]
        timestamps = [("start", start), ("end", max(start, end - 0.05))]
        timestamps.extend((f"review-{index:02d}", value) for index, value in enumerate(review_times, 1))
        for moment_index, (label, timestamp) in enumerate(timestamps, 1):
            if timestamp < start or timestamp > end:
                raise ValueError(
                    f"Review time {timestamp:.3f}s is outside shot {shot_id}: {start:.3f}s to {end:.3f}s"
                )
            filename = (
                f"shot-{shot_index:04d}-{safe_id(shot_id)}-"
                f"{moment_index:02d}-{label}-{timestamp:08.3f}s.png"
            )
            extract_frame(video, timestamp, destination / filename)
            evidence.append({"shot_id": shot_id, "label": label, "time": timestamp, "file": filename})
    return evidence


def run_diagnostics(video: Path, has_audio: bool) -> tuple[str, dict[str, int], list[str]]:
    video_result = run(
        [
            "ffmpeg",
            "-hide_banner",
            "-i",
            str(video),
            "-map",
            "0:v:0",
            "-vf",
            "blackdetect=d=0.20:pix_th=0.10,freezedetect=n=-60dB:d=2",
            "-an",
            "-f",
            "null",
            "-",
        ],
        allow_failure=True,
    )
    logs = ["# Video diagnostics\n", video_result.stderr]
    failures: list[str] = []
    if video_result.returncode != 0:
        failures.append("Video diagnostic pass failed to run")

    silence_count = 0
    if has_audio:
        audio_result = run(
            [
                "ffmpeg",
                "-hide_banner",
                "-i",
                str(video),
                "-map",
                "0:a:0",
                "-af",
                "silencedetect=n=-50dB:d=1",
                "-vn",
                "-f",
                "null",
                "-",
            ],
            allow_failure=True,
        )
        logs.extend(["\n# Audio diagnostics\n", audio_result.stderr])
        if audio_result.returncode != 0:
            failures.append("Audio diagnostic pass failed to run")
        silence_count = len(re.findall(r"silence_start:", audio_result.stderr))

    counts = {
        "black_segments": len(re.findall(r"black_start:", video_result.stderr)),
        "freeze_segments": len(re.findall(r"freeze_start:", video_result.stderr)),
        "silence_segments": silence_count,
    }
    return "".join(logs), counts, failures


def add_check(checks: list[Check], name: str, passed: bool, expected: str, actual: str) -> None:
    checks.append(Check(name, "PASS" if passed else "FAIL", expected, actual))


def build_report(
    video: Path,
    checks: list[Check],
    frame_count: int,
    shot_count: int,
    diagnostics: dict[str, int],
    manifest_warnings: list[str],
    tool_versions: dict[str, str],
) -> str:
    rows = "\n".join(
        f"| {check.name} | {check.status} | {check.expected} | {check.actual} |" for check in checks
    )
    warnings = manifest_warnings or ["None."]
    warning_lines = "\n".join(f"- {warning}" for warning in warnings)
    technical_status = "PASS" if all(check.status == "PASS" for check in checks) else "FAIL"
    return f"""# Video pre-verification report

- Render: `{video}`
- Generated: {datetime.now(timezone.utc).isoformat()}
- Technical gate: **{technical_status}**
- Visual gate: **PENDING AGENT REVIEW**

## Technical checks

| Check | Result | Expected | Actual |
| --- | --- | --- | --- |
{rows}

## Evidence

- Overview frames: {frame_count}
- Stable-ID shot frames: {shot_count}
- Contact sheet: `contact-sheet.png`
- Stable-ID shot contact sheet: {"`shot-contact-sheet.png`" if shot_count else "not generated because no manifest was supplied"}
- Machine-readable result: `verification.json`
- Complete diagnostic output: `diagnostics.log`

## Diagnostic flags

- Black segments: {diagnostics['black_segments']}
- Frozen segments of at least 2 seconds: {diagnostics['freeze_segments']}
- Silent audio segments of at least 1 second: {diagnostics['silence_segments']}

These flags require interpretation. A deliberate black frame, hold, or silent beat is not automatically a defect.

## Shot-manifest warnings

{warning_lines}

## Toolchain

- {tool_versions['ffmpeg']}
- {tool_versions['ffprobe']}

## Human handoff gate

Do not hand the render to a human reviewer until an agent has watched the complete playback, inspected `contact-sheet.png`, checked all stable-ID shot frames, completed `visual-review.md`, and resolved or disclosed every failure.
"""


def visual_review_template(video: Path) -> str:
    return f"""# Visual and playback review

- Render: `{video}`
- Reviewer:
- Review date:
- Viewer or browser used:
- Status: pending

## Required pass

- [ ] Watch the actual rendered file from start to finish with sound.
- [ ] Inspect `contact-sheet.png` for continuity, blank frames, clipping, visual drift, and unintended jumps.
- [ ] Inspect `shot-contact-sheet.png` and every image in `shot-frames/` for shot entry, exit, and requested review moments.
- [ ] Compare hook, beat jobs, attention path, proof, captions, CTA, and final state with the approved direction artifacts.
- [ ] Check readable type, safe zones, contrast, crop, depth, camera, overlays, and disclosure legibility.
- [ ] Listen for clicks, cut-off words, unintended silence, masking, bad levels, and synchronization errors.
- [ ] Interpret every diagnostic flag in `diagnostics.log`.
- [ ] Re-render and repeat invalidated checks after material fixes.

## Findings

| Severity | Time or stable ID | Observable problem | Required correction | Acceptance check | Status |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |

## Gate decision

- Technical gate: see `verification-report.md`
- Visual gate: pending
- Ready for human review: no
- Open limitations:
"""


def verify_video(args: argparse.Namespace) -> bool:
    video = args.video.expanduser().resolve()
    out = args.out.expanduser().resolve()
    if not video.is_file():
        raise SystemExit(f"Video does not exist: {video}")
    if out.exists():
        raise SystemExit(f"Refusing to overwrite existing evidence directory: {out}")
    if args.interval <= 0:
        raise SystemExit("--interval must be greater than zero")
    if args.duration_tolerance < 0:
        raise SystemExit("--duration-tolerance cannot be negative")
    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool) is None:
            raise SystemExit(f"Required tool is not available on PATH: {tool}")

    out.mkdir(parents=True)
    metadata_result = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_streams",
            "-show_format",
            "-of",
            "json",
            str(video),
        ]
    )
    metadata = json.loads(metadata_result.stdout)
    (out / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    video_streams = [stream for stream in metadata.get("streams", []) if stream.get("codec_type") == "video"]
    audio_streams = [stream for stream in metadata.get("streams", []) if stream.get("codec_type") == "audio"]
    if not video_streams:
        raise RuntimeError("Rendered file contains no video stream")
    stream = video_streams[0]
    width = int(stream.get("width", 0))
    height = int(stream.get("height", 0))
    fps = frame_rate(stream)
    duration = media_duration(metadata, stream)
    has_audio = bool(audio_streams)

    checks: list[Check] = []
    add_check(checks, "Video stream", True, "present", f"{stream.get('codec_name', 'unknown')} video")
    add_check(
        checks,
        "Dimensions",
        (args.width is None or width == args.width) and (args.height is None or height == args.height),
        (
            f"{args.width if args.width is not None else '*'}x"
            f"{args.height if args.height is not None else '*'}"
            if args.width is not None or args.height is not None
            else "record only"
        ),
        f"{width}x{height}",
    )
    add_check(
        checks,
        "Frame rate",
        args.fps is None or abs(fps - args.fps) <= 0.05,
        f"{args.fps:.3f} fps" if args.fps is not None else "record only",
        f"{fps:.3f} fps",
    )
    add_check(
        checks,
        "Duration",
        args.duration is None or abs(duration - args.duration) <= args.duration_tolerance,
        (
            f"{args.duration:.3f}s ± {args.duration_tolerance:.3f}s"
            if args.duration is not None
            else "record only"
        ),
        f"{duration:.3f}s",
    )
    add_check(
        checks,
        "Audio stream",
        not args.require_audio or has_audio,
        "present" if args.require_audio else "optional",
        f"{len(audio_streams)} stream(s)",
    )

    manifest_path = args.manifest.expanduser().resolve() if args.manifest else None
    manifest, manifest_warnings = load_manifest(manifest_path, duration)
    if manifest is not None:
        (out / "shot-manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )

    frames = extract_overview_frames(video, out / "frames", args.interval, duration)
    create_contact_sheet(out / "frames", len(frames), out / "contact-sheet.png")
    shot_evidence = extract_shot_frames(video, manifest, out / "shot-frames", duration)
    create_shot_contact_sheet(
        out / "shot-frames", len(shot_evidence), out / "shot-contact-sheet.png"
    )
    diagnostic_log, diagnostic_counts, diagnostic_failures = run_diagnostics(video, has_audio)
    (out / "diagnostics.log").write_text(diagnostic_log, encoding="utf-8")
    add_check(
        checks,
        "Diagnostic execution",
        not diagnostic_failures,
        "all passes completed",
        "; ".join(diagnostic_failures) if diagnostic_failures else "completed",
    )

    versions = {"ffmpeg": tool_version("ffmpeg"), "ffprobe": tool_version("ffprobe")}
    passed = all(check.status == "PASS" for check in checks)
    result = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "video": str(video),
        "technical_gate": "pass" if passed else "fail",
        "visual_gate": "pending",
        "media": {
            "width": width,
            "height": height,
            "fps": fps,
            "duration": duration,
            "video_codec": stream.get("codec_name"),
            "audio_streams": len(audio_streams),
        },
        "sampling": {"interval_seconds": args.interval, "overview_frames": len(frames)},
        "shot_evidence": shot_evidence,
        "manifest_warnings": manifest_warnings,
        "diagnostics": diagnostic_counts,
        "checks": [check.__dict__ for check in checks],
        "tool_versions": versions,
    }
    (out / "verification.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    (out / "verification-report.md").write_text(
        build_report(
            video,
            checks,
            len(frames),
            len(shot_evidence),
            diagnostic_counts,
            manifest_warnings,
            versions,
        ),
        encoding="utf-8",
    )
    (out / "visual-review.md").write_text(visual_review_template(video), encoding="utf-8")
    print(f"Technical gate {'passed' if passed else 'failed'}: {out}")
    return passed


def main() -> None:
    try:
        passed = verify_video(parse_args())
    except (RuntimeError, ValueError, json.JSONDecodeError) as error:
        print(f"Verification failed: {error}", file=sys.stderr)
        raise SystemExit(2) from error
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
