#!/usr/bin/env python3
"""Regression tests for the video project workspace initializer."""

from __future__ import annotations

import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from init_video_project import STAGES, create_project


class VideoProjectInitializerTest(unittest.TestCase):
    def test_creates_complete_marketing_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "campaign"
            with redirect_stdout(StringIO()):
                create_project(target, "Campaign", "marketing", ["vertical", "square"])

            required = [
                "CONTEXT.md",
                "project.json",
                "_config/brief.md",
                "_config/brand.md",
                "_config/platform.md",
                "_config/quality-bar.md",
                "01_research/sources/.gitkeep",
                "06_production/src/.gitkeep",
                "06_production/assets/.gitkeep",
                "06_production/out/.gitkeep",
                "07_review/shot-manifest.json",
                "07_review/runs/.gitkeep",
                "tools/verify_video.py",
                "tools/bake_poster.py",
                "memory/decisions.md",
                "memory/failures.md",
                "memory/lessons.md",
                "library/candidates.md",
            ]
            required.extend(f"{stage['folder']}/CONTEXT.md" for stage in STAGES)
            required.extend(f"{stage['folder']}/output/.gitkeep" for stage in STAGES)

            missing = [relative for relative in required if not (target / relative).exists()]
            self.assertEqual(missing, [])

            metadata = json.loads((target / "project.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["title"], "Campaign")
            self.assertEqual(metadata["kind"], "marketing")
            self.assertEqual(metadata["status"], "active")

            manifest = json.loads(
                (target / "07_review" / "shot-manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(manifest, {"schema_version": 1, "shots": []})
            self.assertIn(
                "Create portable technical and visual-review evidence",
                (target / "tools" / "verify_video.py").read_text(encoding="utf-8"),
            )
            platform = (target / "_config" / "platform.md").read_text(encoding="utf-8")
            self.assertIn("vertical: 9:16, 1080x1920, 30 fps", platform)
            self.assertIn("square: 1:1, 1080x1080, 30 fps", platform)

            for stage in STAGES:
                context = target / str(stage["folder"]) / "CONTEXT.md"
                line_count = len(context.read_text(encoding="utf-8").splitlines())
                self.assertLessEqual(line_count, 80, context)

    def test_refuses_to_overwrite_existing_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "existing"
            target.mkdir()
            sentinel = target / "keep.txt"
            sentinel.write_text("preserve", encoding="utf-8")

            with self.assertRaises(SystemExit):
                create_project(target, "Existing", "general")

            self.assertEqual(sentinel.read_text(encoding="utf-8"), "preserve")


if __name__ == "__main__":
    unittest.main()
