#!/usr/bin/env python3
"""Regression tests for portable rendered-video verification."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from verify_video import verify_video


def make_video(path: Path) -> None:
    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "lavfi",
            "-i",
            "testsrc2=size=320x180:rate=30:duration=2",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=880:sample_rate=48000:duration=2",
            "-shortest",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-y",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def arguments(video: Path, out: Path, manifest: Path | None = None, width: int = 320) -> argparse.Namespace:
    return argparse.Namespace(
        video=video,
        out=out,
        interval=1.0,
        manifest=manifest,
        width=width,
        height=180,
        fps=30.0,
        duration=2.0,
        duration_tolerance=0.15,
        require_audio=True,
    )


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "ffmpeg is required")
class VideoVerificationTest(unittest.TestCase):
    def test_creates_machine_and_visual_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            video = root / "sample.mp4"
            manifest = root / "shots.json"
            out = root / "evidence"
            make_video(video)
            manifest.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "shots": [
                            {"id": "B01.S01", "start": 0, "end": 1, "review_times": [0.5]},
                            {"id": "B01.S02", "start": 1, "end": 2, "review_times": [1.5]},
                        ],
                    }
                ),
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                passed = verify_video(arguments(video, out, manifest))

            self.assertTrue(passed)
            required = [
                "metadata.json",
                "verification.json",
                "verification-report.md",
                "visual-review.md",
                "diagnostics.log",
                "contact-sheet.png",
                "shot-contact-sheet.png",
                "shot-manifest.json",
            ]
            self.assertEqual([name for name in required if not (out / name).is_file()], [])
            self.assertEqual(len(list((out / "frames").glob("*.png"))), 3)
            self.assertEqual(len(list((out / "shot-frames").glob("*.png"))), 6)

            result = json.loads((out / "verification.json").read_text(encoding="utf-8"))
            self.assertEqual(result["technical_gate"], "pass")
            self.assertEqual(result["visual_gate"], "pending")
            self.assertEqual(result["media"]["width"], 320)
            self.assertEqual(result["media"]["audio_streams"], 1)

    def test_expected_metadata_mismatch_fails_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            video = root / "sample.mp4"
            out = root / "evidence"
            make_video(video)

            with redirect_stdout(StringIO()):
                passed = verify_video(arguments(video, out, width=1920))

            self.assertFalse(passed)
            result = json.loads((out / "verification.json").read_text(encoding="utf-8"))
            self.assertEqual(result["technical_gate"], "fail")
            dimensions = next(check for check in result["checks"] if check["name"] == "Dimensions")
            self.assertEqual(dimensions["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
