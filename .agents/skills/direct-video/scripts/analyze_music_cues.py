#!/usr/bin/env python3
"""Find the beat grid and strongest landing moments in a music track.

Writes a JSON cue file and a short Markdown summary for the script and shot plan.
Optional: it needs the libraries in requirements-audio.txt, which are installed
only when a video needs beat timing.

Adapted from latent-spaces/brag, skills/brag/scripts/analyze_music_cues.py at
commit cb89b9f (https://github.com/latent-spaces/brag). Changes: dependency
check with install instructions, wording.

MIT License

Copyright (c) 2026 Shunit Haviv Hakimi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

try:
    import librosa
    import numpy as np
except ImportError:
    librosa = None
    np = None

REQUIREMENTS = Path(__file__).with_name("requirements-audio.txt")
MISSING_DEPENDENCIES = 3

HOP_LENGTH = 512
FRAME_LENGTH = 2048
BASS_N_FFT = 4096
BASS_MIN_HZ = 30.0
BASS_MAX_HZ = 180.0


def _as_float(value: Any) -> float:
    array = np.asarray(value)
    if array.size == 0:
        return 0.0
    return float(array.reshape(-1)[0])


def _finite_round(value: float, digits: int = 4) -> float:
    if not math.isfinite(value):
        return 0.0
    return round(float(value), digits)


def _normalize(values: Any) -> Any:
    values = np.asarray(values, dtype=float)
    values = np.nan_to_num(values, nan=0.0, posinf=0.0, neginf=0.0)
    if values.size == 0:
        return values
    values = np.maximum(values, 0.0)
    high = np.percentile(values, 98)
    if high <= 1e-12:
        high = np.max(values)
    if high <= 1e-12:
        return np.zeros_like(values)
    return np.clip(values / high, 0.0, 1.0)


def _feature_at(feature: Any, frame: int) -> float:
    if feature.size == 0:
        return 0.0
    index = int(np.clip(frame, 0, feature.size - 1))
    return float(feature[index])


def _local_contrast(onset_norm: Any, frame: int, sr: int) -> float:
    radius = max(1, int(round(0.5 * sr / HOP_LENGTH)))
    start = max(0, frame - radius)
    end = min(onset_norm.size, frame + radius + 1)
    local = onset_norm[start:end]
    if local.size == 0:
        return 0.0
    median = float(np.median(local))
    return max(0.0, _feature_at(onset_norm, frame) - median)


def _score_frame(frame: int, onset: Any, contrast: Any, rms: Any, bass: Any) -> dict[str, float]:
    onset_value = _feature_at(onset, frame)
    contrast_value = _feature_at(contrast, frame)
    rms_value = _feature_at(rms, frame)
    bass_value = _feature_at(bass, frame)
    intensity = 0.45 * onset_value + 0.25 * contrast_value + 0.20 * rms_value + 0.10 * bass_value
    return {
        "intensity": float(np.clip(intensity, 0.0, 1.0)),
        "onsetStrength": onset_value,
        "localOnsetContrast": contrast_value,
        "rms": rms_value,
        "bassEnergy": bass_value,
    }


def _features(score: dict[str, float]) -> dict[str, float]:
    return {
        key: _finite_round(score[key])
        for key in ("onsetStrength", "localOnsetContrast", "rms", "bassEnergy")
    }


def _dedupe_cues(cues: list[dict[str, Any]], min_gap: float = 0.18) -> list[dict[str, Any]]:
    accepted: list[dict[str, Any]] = []
    for cue in sorted(cues, key=lambda item: item["intensity"], reverse=True):
        if all(abs(cue["time"] - existing["time"]) >= min_gap for existing in accepted):
            accepted.append(cue)
    return sorted(accepted, key=lambda item: item["time"])


def _compact_times(items: list[dict[str, Any]], max_items: int = 48) -> str:
    text = ", ".join(f"{item['time']:.2f}" for item in items[:max_items])
    if len(items) > max_items:
        text += f", ... (+{len(items) - max_items} more)"
    return text or "none"


def _format_cue(cue: dict[str, Any]) -> str:
    return f"{cue['time']:.2f}s ({cue['intensity']:.2f}, {cue['kind']})"


def analyze_track(
    input_path: Path, window_start: float, window_duration: float, top_cues: int, sr: int
) -> tuple[dict[str, Any], str]:
    y, actual_sr = librosa.load(input_path, sr=sr, mono=True)
    duration = float(librosa.get_duration(y=y, sr=actual_sr))
    window_end = min(duration, window_start + window_duration)

    onset_env = librosa.onset.onset_strength(y=y, sr=actual_sr, hop_length=HOP_LENGTH)
    onset_norm = _normalize(onset_env)
    contrast_norm = _normalize(
        np.array([_local_contrast(onset_norm, frame, actual_sr) for frame in range(onset_norm.size)])
    )
    rms_norm = _normalize(
        librosa.feature.rms(y=y, frame_length=FRAME_LENGTH, hop_length=HOP_LENGTH)[0]
    )
    spectrum = np.abs(librosa.stft(y, n_fft=BASS_N_FFT, hop_length=HOP_LENGTH))
    frequencies = librosa.fft_frequencies(sr=actual_sr, n_fft=BASS_N_FFT)
    bass_mask = (frequencies >= BASS_MIN_HZ) & (frequencies <= BASS_MAX_HZ)
    bass = np.mean(spectrum[bass_mask], axis=0) if np.any(bass_mask) else np.zeros(spectrum.shape[1])
    bass_norm = _normalize(bass)

    tempo, beat_frames = librosa.beat.beat_track(
        y=y, sr=actual_sr, onset_envelope=onset_env, hop_length=HOP_LENGTH, units="frames"
    )
    beat_frames = np.asarray(beat_frames, dtype=int)
    beat_times = librosa.frames_to_time(beat_frames, sr=actual_sr, hop_length=HOP_LENGTH)

    beats: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    for frame, time in zip(beat_frames, beat_times):
        score = _score_frame(frame, onset_norm, contrast_norm, rms_norm, bass_norm)
        beat = {
            "time": _finite_round(float(time)),
            "intensity": _finite_round(score["intensity"]),
            "features": _features(score),
        }
        beats.append(beat)
        candidates.append({**beat, "kind": "strong_beat"})

    onset_frames = librosa.onset.onset_detect(
        onset_envelope=onset_env, sr=actual_sr, hop_length=HOP_LENGTH, backtrack=False, units="frames"
    )
    for frame in np.asarray(onset_frames, dtype=int):
        score = _score_frame(frame, onset_norm, contrast_norm, rms_norm, bass_norm)
        candidates.append(
            {
                "time": _finite_round(
                    float(librosa.frames_to_time(frame, sr=actual_sr, hop_length=HOP_LENGTH))
                ),
                "intensity": _finite_round(score["intensity"]),
                "kind": "onset_peak",
                "features": _features(score),
            }
        )

    strong = [cue for cue in _dedupe_cues(candidates) if cue["intensity"] >= 0.45]
    strong_cues = sorted(
        sorted(strong, key=lambda cue: cue["intensity"], reverse=True)[:64],
        key=lambda cue: cue["time"],
    )

    data = {
        "schemaVersion": 1,
        "source": {"filename": input_path.name, "trackStem": input_path.stem},
        "duration": _finite_round(duration, 3),
        "tempo": _finite_round(_as_float(tempo), 2),
        "analysis": {
            "sampleRate": actual_sr,
            "hopLength": HOP_LENGTH,
            "windowStart": _finite_round(window_start, 3),
            "windowDuration": _finite_round(window_duration, 3),
            "windowEnd": _finite_round(window_end, 3),
        },
        "scoring": {
            "intensityFormula": "0.45*onset_strength + 0.25*local_onset_contrast + 0.20*rms + 0.10*bass_energy",
            "normalization": "Per-track 98th percentile scaled to 0-1, then clamped.",
            "strongCueMinimumIntensity": 0.45,
            "strongCueMaxCount": 64,
        },
        "beats": beats,
        "strongCues": strong_cues,
    }

    window_beats = [beat for beat in beats if window_start <= beat["time"] <= window_end]
    window_cues = [cue for cue in strong_cues if window_start <= cue["time"] <= window_end]
    top = sorted(window_cues, key=lambda cue: cue["intensity"], reverse=True)[:top_cues]
    markdown = "\n".join(
        [
            f"# Music cues: {input_path.stem}",
            "",
            f"- Track: `{input_path.name}`",
            f"- Duration: {duration:.2f}s",
            f"- Estimated tempo: {_as_float(tempo):.2f} BPM",
            f"- Planning window: {window_start:.2f}s to {window_end:.2f}s",
            "",
            "## Beat grid",
            "",
            _compact_times(window_beats),
            "",
            "## Strongest cues",
            "",
            "\n".join(f"- {_format_cue(cue)}" for cue in top) or "- none",
            "",
            "## Use",
            "",
            "Timing hints only. See `references/audio-direction.md` for how far a reveal may move toward a cue.",
            "",
        ]
    )
    return data, markdown


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("input", type=Path, help="Audio file")
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    parser.add_argument("--window-start", type=float, default=0.0)
    parser.add_argument("--window-duration", type=float, default=25.0)
    parser.add_argument("--top-cues", type=int, default=10)
    parser.add_argument("--sr", type=int, default=44100)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if librosa is None:
        print(
            "Beat analysis needs librosa, which is installed only when a video needs it.\n"
            "Install it into a virtual environment, then rerun this script with that Python:\n"
            "  python3 -m venv .venv-audio\n"
            f"  .venv-audio/bin/pip install -r {REQUIREMENTS}\n"
            "Remove .venv-audio when the video is finished.",
            file=sys.stderr,
        )
        raise SystemExit(MISSING_DEPENDENCIES)
    if not args.input.is_file():
        raise SystemExit(f"Audio file does not exist: {args.input}")

    data, markdown = analyze_track(
        args.input, args.window_start, args.window_duration, args.top_cues, args.sr
    )
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    args.output_md.write_text(markdown, encoding="utf-8")
    print(f"Wrote {args.output_json} and {args.output_md}")


if __name__ == "__main__":
    main()
