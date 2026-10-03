#!/usr/bin/env python3
"""Regression tests for the optional music cue analyzer."""

from __future__ import annotations

import json
import math
import struct
import subprocess
import sys
import tempfile
import unittest
import wave
from pathlib import Path

import analyze_music_cues

SCRIPT = Path(__file__).with_name("analyze_music_cues.py")


def write_click_track(path: Path, bpm: float = 120.0, seconds: float = 8.0, rate: int = 22050) -> None:
    period = 60.0 / bpm
    frames = bytearray()
    for index in range(int(seconds * rate)):
        since_click = (index / rate) % period
        sample = math.sin(2 * math.pi * 1000 * since_click) * math.exp(-since_click * 60) if since_click < 0.05 else 0.0
        frames += struct.pack("<h", int(sample * 30000))
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(rate)
        output.writeframes(bytes(frames))


class MusicCueTest(unittest.TestCase):
    def run_script(self, root: Path, audio: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(audio), "--output-json", str(root / "cues.json"),
             "--output-md", str(root / "cues.md"), "--window-duration", "8"],
            text=True, capture_output=True, check=False,
        )

    @unittest.skipIf(analyze_music_cues.librosa is not None, "librosa is installed")
    def test_explains_missing_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result = self.run_script(root, root / "missing.wav")
            self.assertEqual(result.returncode, analyze_music_cues.MISSING_DEPENDENCIES)
            self.assertIn("requirements-audio.txt", result.stderr)
            self.assertFalse((root / "cues.json").exists())

    @unittest.skipIf(analyze_music_cues.librosa is None, "librosa is not installed")
    def test_finds_tempo_of_click_track(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            audio = root / "clicks.wav"
            write_click_track(audio)
            result = self.run_script(root, audio)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads((root / "cues.json").read_text(encoding="utf-8"))
            self.assertAlmostEqual(data["tempo"], 120.0, delta=3.0)
            gaps = [b["time"] - a["time"] for a, b in zip(data["beats"], data["beats"][1:])]
            self.assertAlmostEqual(sum(gaps) / len(gaps), 0.5, delta=0.03)


if __name__ == "__main__":
    unittest.main()
