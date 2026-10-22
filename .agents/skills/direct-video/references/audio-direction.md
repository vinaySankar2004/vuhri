# Audio direction

Plan sound with the picture, not after it. Rules marked candidate are adapted from the [brag](https://github.com/latent-spaces/brag) project (MIT) and become firm only after vuhri's own verified renders support them.

## Plan

Decide the audio role at the script stage: narration, a music bed, sparse effects, or intentional silence. Map each important word, music change, and effect to a visible event in the beat sheet. A muted viewer should still follow the video, and a listener should still follow the narration.

## Sources and rights

- Record every track and effect with its source, licence, and attribution in `_config/brand.md`.
- Download sounds when a video needs them, into that project. CC0 libraries such as Kenney's need no credit; CC BY music needs credit in the delivery notes.
- A commercial track the user supplies may be muted or claimed on public platforms. Say so before using it.
- A built-in system voice is provisional. A public master needs a reviewed voice and a full listening pass, including how names are pronounced.

## Voice

Checked 2026-10-20 against model cards, licences and the [Artificial Analysis arena](https://artificialanalysis.ai/text-to-speech/leaderboard).

- **macOS voices never go in a published video.** Apple's licence limits system voices, Premium voices and Personal Voice to personal, non-commercial use.
- **Free voices that are safe for commercial use and run locally on Apple Silicon through [mlx-audio](https://github.com/Blaizzy/mlx-audio):**
  - [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M): Apache-2.0, about 330 MB, fast, 54 preset voices, and pronunciation fixes in IPA.
  - [Ming-3.0-tts-0.5B](https://huggingface.co/inclusionAI/Ming-3.0-tts-0.5B): MIT, about 3 GB, ranked highest of the clean-licence models, with emotion and pace instructions and number handling.
  - [Chatterbox](https://github.com/resemble-ai/chatterbox): MIT, about 2.6 GB, clones a voice from about 10 seconds of audio, and watermarks its output inaudibly.
- **Not safe for commercial use:** F5-TTS and XTTS-v2 weights, Voxtral TTS, the ElevenLabs free tier, and `edge-tts`. Check any other model's weights licence separately from its code licence.
- Keep the chosen voice, its settings and its pronunciation fixes in the project's `_config/brand.md`, so every video sounds the same.

## Music and effects (candidate)

- Keep a music bed around 0.3 to 0.4 of full volume, never above 0.5, and duck it to about 0.12 to 0.15 under narration.
- Keep effects between 0.55 and 0.85, softer for restrained tones.
- Start an effect up to 0.1 seconds before its element first appears, so sound and motion land together.
- In a staggered set, accent only the first, last, or strongest item unless the rhythm is the point.
- Match the gesture: card sounds for card reveals, clicks for simulated taps, one short impact for a payoff. Use warm, dull sounds for anything repeated, because bright ones fatigue.
- Mix effects and music as one piece. Nothing harsh, and small repeated sounds stay in the background.

## Beat timing (candidate)

When music timing matters, find its beats:

```bash
python3 .agents/skills/direct-video/scripts/analyze_music_cues.py track.mp3 \
  --output-json 03_script/output/cues.json --output-md 03_script/output/cues.md
```

It needs the libraries in `scripts/requirements-audio.txt` and explains how to install them when they are missing. Then:

- Move a major reveal at most 0.15 seconds toward a strong cue, and a small entrance at most 0.10 seconds toward a beat.
- Lock one to three moments in a short video. Readability and story win over any lock.
- At fast tempos, land sequential lines of text on every other beat, or bring them in quickly and hold the set.

## Music-reactive visuals (candidate)

Remotion's `@remotion/media-utils` provides per-frame audio data. Let loudness or bass gently modulate something already on screen, such as glow, depth, or a card's presence. Never add waveform bars, equalizers, music notes, strobing, or pulsing text.
