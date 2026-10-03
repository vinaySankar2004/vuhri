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

from bake_poster import bake_poster
from verify_video import reading_floor, verify_video


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


def arguments(
    video: Path,
    out: Path,
    manifest: Path | None = None,
    width: int | None = 320,
    **overrides: object,
) -> argparse.Namespace:
    values = {
        "video": video,
        "out": out,
        "interval": 1.0,
        "manifest": manifest,
        "width": width,
        "height": 180,
        "fps": 30.0,
        "duration": 2.0,
        "duration_tolerance": 0.15,
        "require_audio": True,
        "format": None,
        "poster": None,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def check(out: Path, name: str) -> dict[str, str]:
    result = json.loads((out / "verification.json").read_text(encoding="utf-8"))
    return next(item for item in result["checks"] if item["name"] == name)


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

    def test_format_preset_sets_expected_dimensions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            video = root / "sample.mp4"
            out = root / "evidence"
            make_video(video)

            with redirect_stdout(StringIO()):
                passed = verify_video(
                    arguments(video, out, width=None, height=None, fps=None, format="vertical")
                )

            self.assertFalse(passed)
            self.assertEqual(check(out, "Dimensions")["expected"], "1080x1920")
            self.assertEqual(check(out, "Frame rate")["status"], "PASS")

    def test_samples_transitions_and_flags_short_text(self) -> None:
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
                            {
                                "id": "B01.S01",
                                "start": 0,
                                "end": 1.2,
                                "text": [{"id": "B01.S01.T01", "words": 6, "settled": 0.2, "exit": 1.0}],
                            },
                            {
                                "id": "B01.S02",
                                "start": 0.8,
                                "end": 2,
                                "text": [{"id": "B01.S02.T01", "words": 2, "settled": 1.0, "exit": 1.9}],
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                passed = verify_video(arguments(video, out, manifest))

            self.assertTrue(passed)
            transition = list((out / "shot-frames").glob("*transition-to-B01.S02*"))
            self.assertEqual(len(transition), 1)
            self.assertIn("0001.000s", transition[0].name)
            result = json.loads((out / "verification.json").read_text(encoding="utf-8"))
            self.assertEqual(len(result["reading_flags"]), 1)
            self.assertTrue(result["reading_flags"][0].startswith("B01.S01.T01"))
            self.assertEqual(reading_floor(3), 0.8)
            self.assertAlmostEqual(reading_floor(6), 1.8)

    def test_baked_poster_matches_frame_zero(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            video = root / "sample.mp4"
            baked = root / "final.mp4"
            make_video(video)
            with redirect_stdout(StringIO()):
                poster = bake_poster(video, 1.0, baked)
                passed = verify_video(arguments(video=baked, out=root / "good", poster=poster))
            self.assertTrue(passed)
            self.assertEqual(check(root / "good", "Poster frame")["status"], "PASS")

            other = root / "other.jpg"
            subprocess.run(
                ["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i",
                 "color=c=red:size=320x180", "-frames:v", "1", "-y", str(other)],
                check=True,
            )
            with redirect_stdout(StringIO()):
                passed = verify_video(arguments(video=video, out=root / "bad", poster=other))
            self.assertFalse(passed)
            self.assertEqual(check(root / "bad", "Poster frame")["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
