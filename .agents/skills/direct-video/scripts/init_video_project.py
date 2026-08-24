#!/usr/bin/env python3
"""Create an inspectable, staged video project workspace."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import date
from pathlib import Path


STAGES = [
    {
        "folder": "00_intake",
        "title": "Intake",
        "job": "Turn the user's ordinary-language request into a project contract without requiring video jargon.",
        "inputs": "Conversation, supplied assets, `_config/brief.md`, and `_config/brand.md`.",
        "process": [
            "Record the product, topic, audience, desired change, destination, constraints, and known assets.",
            "Mark unknown facts, permissions, claims, platform choices, and material taste decisions.",
            "Recommend a duration band and production mode in plain language.",
            "Present the project contract only if a high-leverage choice still needs confirmation.",
        ],
        "audit": [
            "The user is not asked to supply professional video terminology.",
            "Business facts, user choices, and director recommendations are distinguishable.",
            "Unknown claims and rights are visible rather than assumed.",
        ],
        "output": "output/project-contract.md",
    },
    {
        "folder": "01_research",
        "title": "Research",
        "job": "Collect only the source, market, platform, product, and inspiration evidence needed for this video.",
        "inputs": "`../00_intake/output/project-contract.md`, files in `sources/`, and relevant `_config/` records.",
        "process": [
            "Verify product behavior, claims, platform constraints, destination consistency, and rights-sensitive assets.",
            "Study references by property, such as composition, depth, pacing, proof, or caption behavior.",
            "Record source URL, creator, authority, access date, and the project decision each source may influence.",
            "If research is unnecessary, write a skip record explaining why.",
        ],
        "audit": [
            "No factual or performance claim lacks a source or explicit provisional label.",
            "Inspiration observations do not request copying a creator's recognizable sequence.",
            "Time-sensitive platform guidance includes an access date.",
        ],
        "output": "output/research-brief.md",
    },
    {
        "folder": "02_direction",
        "title": "Direction",
        "job": "Choose the angle, hook mechanism, visual thesis, style system, duration, and non-negotiable moments.",
        "inputs": "The project contract, research brief, `_config/brand.md`, and `_config/quality-bar.md`.",
        "process": [
            "Write one recommended direction and at most one materially different alternative when needed.",
            "Define the hook contract, governing narrative movement, visual thesis, emotional movement, and exclusions.",
            "Choose 2D, 2.5D, 3D, or hybrid production based on what the visual must communicate.",
            "Save the approved or clearly marked provisional direction.",
        ],
        "audit": [
            "The direction can be understood by a non-editor.",
            "The visual thesis describes a meaningful changing relationship, not a style adjective.",
            "Duration fits the quality envelope or the exception is explicit.",
        ],
        "output": "output/direction-brief.md",
    },
    {
        "folder": "03_script",
        "title": "Script and audio plan",
        "job": "Write the spoken, on-screen, and audio argument that the approved direction needs.",
        "inputs": "The direction brief, research brief, and project brand and quality configuration.",
        "process": [
            "Write narration, on-screen copy, claims, disclosure language, and CTA as separate tracks.",
            "Read spoken lines aloud for timing and natural phrasing.",
            "Map important words, pauses, music changes, and sound cues to intended visual events.",
            "For silent or music-only work, record the visual and audio plan instead of inventing narration.",
        ],
        "audit": [
            "The spoken track works without requiring the viewer to read paragraphs.",
            "On-screen copy remains readable for its planned duration.",
            "The script delivers the direction's promise and contains no unsupported claim.",
        ],
        "output": "output/script-and-audio.md",
    },
    {
        "folder": "04_beats",
        "title": "Beat sheet",
        "job": "Turn the approved direction and script into stable-ID conceptual beats.",
        "inputs": "The direction brief and script or audio plan.",
        "process": [
            "Assign stable IDs such as `B01` without tying them to file order.",
            "Give each beat one job, question in, state in, action chain, state out, and handoff.",
            "Create a second-level time ledger for work up to 45 seconds.",
            "Check total timing against the target duration and required holds.",
        ],
        "audit": [
            "Every beat advances the governing narrative movement.",
            "Each state out supports the next state in.",
            "Every interval has an intentional job, including holds and silence.",
        ],
        "output": "output/beat-sheet.md",
    },
    {
        "folder": "05_shots",
        "title": "Shot plan",
        "job": "Choreograph every beat into stable-ID shots with explicit attention, camera, depth, audio, and exit conditions.",
        "inputs": "The beat sheet, direction brief, script or audio plan, and approved assets.",
        "process": [
            "Assign IDs such as `B03.S02` and write one shot sentence for each.",
            "Record elements, initial state, action order, attention path, camera, audio anchors, duration, and exit condition.",
            "Name candidate semantic primitives and implementation risks.",
            "Map protected properties that later revisions should preserve.",
        ],
        "audit": [
            "The viewer has one primary attention target at a time.",
            "Camera and depth changes reveal information or strengthen the intended feeling.",
            "Every shot is independently addressable for revision and review.",
        ],
        "output": "output/shot-plan.md",
    },
    {
        "folder": "06_production",
        "title": "Production",
        "job": "Build the approved shot plan as deterministic, data-addressable video code and assets.",
        "inputs": "The shot plan, beat sheet, script, direction, `_config/`, and licensed assets.",
        "process": [
            "Load the relevant production skill and current official implementation guidance.",
            "Preserve beat and shot IDs in scene names, data, filenames, and review stills.",
            "Keep timing, copy, theme, captions, and asset references in clear data structures.",
            "Render a complete rough cut before polishing isolated scenes.",
        ],
        "audit": [
            "The build covers every approved beat and shot.",
            "Renders are deterministic and platform dimensions are correct.",
            "Unapproved direction changes are reported instead of hidden in code.",
        ],
        "output": "output/ with rendered media, metadata, contact sheets, and build notes",
    },
    {
        "folder": "07_review",
        "title": "Review",
        "job": "Verify technical, visual, audio, platform, factual, and persuasive quality against the direction artifacts.",
        "inputs": "Production output plus all approved upstream artifacts.",
        "process": [
            "Run `tools/verify_video.py` against the actual rendered file and preserve the evidence in a new `runs/` folder.",
            "Inspect the complete playback, contact sheet, one-second samples for short work, and stable-ID shot-boundary frames.",
            "Check attention, continuity, safe zones, captions, audio, claims, proof, CTA, crops, and direction alignment.",
            "Write failures as observable deltas with target IDs and acceptance tests.",
        ],
        "audit": [
            "Every pass claim links to an actual check or inspected evidence.",
            "The result is compared with the approved direction, not aesthetic taste alone.",
            "Open failures and limitations are visible.",
        ],
        "output": "output/verification-report.md",
    },
    {
        "folder": "08_revisions",
        "title": "Revisions",
        "job": "Apply the smallest approved deltas, preserve unaffected work, and close verified corrections.",
        "inputs": "Review report, user feedback, revision ledger, and affected upstream and production artifacts.",
        "process": [
            "Translate feedback into target IDs, allowed changes, protected properties, invalidated dependencies, and acceptance checks.",
            "Patch the closest responsible layer instead of regenerating the full video.",
            "Re-render affected regions and inspect seams, then run any invalidated whole-video checks.",
            "Record verified failures and lessons in `memory/` at the narrowest valid scope.",
        ],
        "audit": [
            "The requested delta is satisfied without collateral changes.",
            "Affected dependencies and seams were rechecked.",
            "A repeated failure now has an observable regression check.",
        ],
        "output": "output/revision-ledger.md",
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="New project directory to create")
    parser.add_argument("--title", help="Human-readable project title")
    parser.add_argument(
        "--kind",
        choices=("general", "marketing", "learning"),
        default="general",
        help="Project adapter to record in the workspace",
    )
    return parser.parse_args()


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def stage_context(stage: dict[str, object]) -> str:
    process = "\n".join(
        f"{index}. {item}" for index, item in enumerate(stage["process"], start=1)
    )
    audit = "\n".join(f"- [ ] {item}" for item in stage["audit"])
    return f"""# Stage: {stage['title']}

## Job

{stage['job']}

## Inputs

{stage['inputs']}

## Process

{process}

## Audit

{audit}

## Output

`{stage['output']}`
"""


def root_context(title: str, kind: str) -> str:
    routes = "\n".join(
        f"| {stage['title']} | `{stage['folder']}/CONTEXT.md` | {stage['job']} |"
        for stage in STAGES
    )
    return f"""# {title}

Kind: `{kind}`

This workspace directs, builds, verifies, and revises one video project through inspectable stage outputs. Read only the current stage, its declared inputs, and the relevant shared configuration.

## Task routing

| Task | Stage | Job |
| --- | --- | --- |
{routes}

## Shared records

- `_config/brief.md`: stable project contract and current constraints.
- `_config/brand.md`: brand assets, rules, permissions, and exclusions.
- `_config/platform.md`: placements, formats, safe zones, and access-dated sources.
- `_config/quality-bar.md`: duration envelope and verification floor.
- `memory/decisions.md`: approved choices that should remain stable.
- `memory/failures.md`: observed failures, corrections, evidence, and regression checks.
- `memory/lessons.md`: candidate generalizations awaiting tests.
- `library/candidates.md`: reusable primitives and patterns extracted from verified work.
- `07_review/shot-manifest.json`: portable stable-ID timing for visual evidence.
- `07_review/runs/`: immutable per-render technical and visual-review evidence.
- `tools/verify_video.py`: agent-independent rendered-video pre-verification.

## Operating rules

- Preserve stable beat and shot IDs across stages and revisions.
- Keep source facts, user choices, director recommendations, and test results distinguishable.
- Do not advance past a material unresolved decision. Do not pause for implementation details the user cannot reasonably judge.
- Learn from approved direction, verified renders, and explicit feedback. Do not treat raw output as a reference standard.
- Fix an error in the closest responsible layer and add a regression check before promoting a shared rule.
"""


def create_project(target: Path, title: str, kind: str) -> None:
    target = target.expanduser().resolve()
    if target.exists():
        raise SystemExit(f"Refusing to overwrite existing path: {target}")

    target.mkdir(parents=True)
    created = date.today().isoformat()

    write_text(target / "CONTEXT.md", root_context(title, kind))
    write_text(
        target / "project.json",
        json.dumps(
            {"title": title, "kind": kind, "created": created, "status": "active"},
            indent=2,
        ),
    )
    write_text(
        target / "_config" / "brief.md",
        f"""# Project brief

- Title: {title}
- Kind: {kind}
- Created: {created}
- Status: active
- Audience and viewing context:
- Desired change:
- Product, topic, or offer:
- Core claim:
- Destination action:
- Duration and placements:
- Source, claim, rights, and privacy constraints:
- Delivery target:
""",
    )
    write_text(
        target / "_config" / "brand.md",
        """# Brand system

- Brand name:
- Voice:
- Logo and asset locations:
- Colors and typography:
- Material and depth language:
- Motion character:
- Required disclosures:
- Prohibited treatments:
- Asset ownership and license notes:
""",
    )
    write_text(
        target / "_config" / "platform.md",
        """# Platform configuration

| Placement | Aspect ratio | Duration | Safe zones | Audio and caption rules | Source and access date |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |

Recheck platform guidance before production because specifications and policies change.
""",
    )
    write_text(
        target / "_config" / "quality-bar.md",
        """# Quality bar

- Default rapid high-polish envelope: 2 to 45 seconds.
- Extended mode: 45 to 90 seconds with sections and more review.
- Long-form mode: more than 90 seconds with modular sequences.
- Every interval has an intentional job, including holds and silence.
- Every short video receives one-second sampling plus shot-boundary review.
- Every factual, product, performance, or customer claim is supported or marked provisional.
- Every revision preserves unaffected stable IDs and protected properties.
""",
    )

    for stage in STAGES:
        folder = target / str(stage["folder"])
        write_text(folder / "CONTEXT.md", stage_context(stage))
        write_text(folder / "output" / ".gitkeep", "")

    write_text(target / "01_research" / "sources" / ".gitkeep", "")
    write_text(target / "06_production" / "src" / ".gitkeep", "")
    write_text(target / "06_production" / "assets" / ".gitkeep", "")
    write_text(target / "06_production" / "out" / ".gitkeep", "")
    write_text(
        target / "07_review" / "shot-manifest.json",
        json.dumps({"schema_version": 1, "shots": []}, indent=2),
    )
    write_text(target / "07_review" / "runs" / ".gitkeep", "")
    verifier_source = Path(__file__).with_name("verify_video.py")
    if not verifier_source.is_file():
        raise RuntimeError(f"Missing bundled verifier: {verifier_source}")
    verifier_target = target / "tools" / "verify_video.py"
    verifier_target.parent.mkdir(parents=True)
    shutil.copy2(verifier_source, verifier_target)
    write_text(
        target / "memory" / "decisions.md",
        "# Decisions\n\nRecord approved choices, their rationale, date, and affected IDs.\n",
    )
    write_text(
        target / "memory" / "failures.md",
        """# Failures

## Template

- ID:
- Date:
- Affected IDs:
- Viewer experience:
- Root cause layer:
- Correction:
- Regression check:
- Verification evidence:
- Scope: project-only | pattern candidate | shared rule candidate
""",
    )
    write_text(
        target / "memory" / "lessons.md",
        """# Lessons

Record only candidate generalizations supported by reviewed outcomes. Link each lesson to failures, verified renders, user feedback, and cross-topic tests.
""",
    )
    write_text(
        target / "library" / "candidates.md",
        """# Library candidates

Record semantic primitives, composition patterns, style systems, and examples extracted from verified work. New entries remain candidates until reuse or an explicit cross-topic test supports promotion.
""",
    )

    print(f"Created {kind} video workspace: {target}")


def main() -> None:
    args = parse_args()
    title = args.title or args.target.name.replace("-", " ").replace("_", " ").title()
    create_project(args.target, title, args.kind)


if __name__ == "__main__":
    main()
