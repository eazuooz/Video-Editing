"""Render the approved balanced narration and an editor-ready SRT subtitle file.

The official Chatterbox Multilingual demo accepts at most 300 characters per
request, so this script sends short narration chunks, joins the generated WAVs,
and creates sentence-level SRT timings from their actual durations.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from shutil import copy2

import numpy as np
import soundfile as sf
from gradio_client import Client, handle_file


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "narration" / "jump-physics.script.json"
REFERENCE = ROOT / "shared" / "voice-reference" / "reference-15-35s.wav"
CHUNK_DIR = ROOT / "shared" / "output" / "narration" / "chunks"
OUTPUT_DIR = ROOT / "shared" / "output" / "narration"
OUTPUT_AUDIO = OUTPUT_DIR / "jump-physics-balanced.wav"
OUTPUT_SRT = OUTPUT_DIR / "jump-physics-balanced.srt"

MAX_CHARS = 260
GAP_SECONDS = 0.35
SEED = 240726

# 02-balanced everywhere by default; 03-brisk (higher exaggeration, lower
# cfg_weight -> faster, more emphatic delivery) for the Zangief screw
# piledriver (08) and Smash Bros jump-squat (09) scenes, per the sample
# comparison in shared/audio-samples/jump-physics/.
BALANCED_TONE = {"exaggeration_input": 0.50, "temperature_input": 0.70, "cfgw_input": 0.50}
BRISK_TONE = {"exaggeration_input": 0.80, "temperature_input": 0.80, "cfgw_input": 0.35}
BRISK_SCENE_IDS = {"08", "09"}


def tone_for_scene(scene_id: str) -> dict:
    return BRISK_TONE if scene_id in BRISK_SCENE_IDS else BALANCED_TONE


@dataclass
class Chunk:
    scene_id: str
    lines: list[str]

    @property
    def text(self) -> str:
        return "\n\n".join(self.lines)


def load_chunks() -> list[Chunk]:
    script = json.loads(SCRIPT_PATH.read_text(encoding="utf-8"))
    chunks: list[Chunk] = []

    for scene in script["scenes"]:
        current: list[str] = []
        for line in scene["lines"]:
            candidate = "\n\n".join([*current, line])
            if current and len(candidate) > MAX_CHARS:
                chunks.append(Chunk(scene["id"], current))
                current = [line]
            else:
                current.append(line)
        if current:
            chunks.append(Chunk(scene["id"], current))

    return chunks


def format_timestamp(seconds: float) -> str:
    milliseconds = round(max(seconds, 0) * 1000)
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    whole_seconds, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02}:{minutes:02}:{whole_seconds:02},{milliseconds:03}"


def wrap_caption(text: str, width: int = 24) -> str:
    words = text.split()
    rows: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and len(candidate) > width:
            rows.append(current)
            current = word
        else:
            current = candidate
    if current:
        rows.append(current)
    return "\n".join(rows)


def render_chunks(chunks: list[Chunk]) -> list[Path]:
    CHUNK_DIR.mkdir(parents=True, exist_ok=True)
    client = Client("ResembleAI/Chatterbox-Multilingual-TTS")
    chunk_paths: list[Path] = []

    for number, chunk in enumerate(chunks, start=1):
        destination = CHUNK_DIR / f"{number:02d}-scene-{chunk.scene_id}.wav"
        if destination.exists() and destination.stat().st_size > 0:
            chunk_paths.append(destination)
            print(f"Reusing {destination.name}")
            continue

        tone = tone_for_scene(chunk.scene_id)
        generated_path = client.predict(
            text_input=chunk.text,
            language_id="ko",
            audio_prompt_path_input=handle_file(REFERENCE),
            seed_num_input=SEED,
            api_name="/generate_tts_audio",
            **tone,
        )
        copy2(generated_path, destination)
        chunk_paths.append(destination)
        tone_name = "brisk" if tone is BRISK_TONE else "balanced"
        print(f"Generated {destination.name} ({tone_name}): {len(chunk.text)} characters")

    return chunk_paths


def join_audio_and_write_srt(chunks: list[Chunk], chunk_paths: list[Path]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    audio_parts: list[np.ndarray] = []
    captions: list[tuple[float, float, str]] = []
    cursor = 0.0
    sample_rate: int | None = None

    for index, (chunk, path) in enumerate(zip(chunks, chunk_paths)):
        audio, rate = sf.read(path, always_2d=False)
        if sample_rate is None:
            sample_rate = rate
        elif rate != sample_rate:
            raise RuntimeError(f"Unexpected sample rate in {path}: {rate}")

        audio = np.asarray(audio, dtype=np.float32)
        if audio.ndim == 2:
            audio = audio.mean(axis=1)
        duration = len(audio) / rate
        audio_parts.append(audio)

        total_weight = sum(len(line.replace(" ", "")) for line in chunk.lines)
        line_cursor = cursor
        for line in chunk.lines:
            weight = len(line.replace(" ", "")) / total_weight
            line_duration = duration * weight
            captions.append((line_cursor, line_cursor + line_duration, line))
            line_cursor += line_duration
        cursor += duration

        if index < len(chunks) - 1:
            audio_parts.append(np.zeros(round(rate * GAP_SECONDS), dtype=np.float32))
            cursor += GAP_SECONDS

    if sample_rate is None:
        raise RuntimeError("No audio chunks were generated.")

    sf.write(OUTPUT_AUDIO, np.concatenate(audio_parts), sample_rate, subtype="PCM_16")

    with OUTPUT_SRT.open("w", encoding="utf-8") as srt:
        for index, (start, end, text) in enumerate(captions, start=1):
            srt.write(
                f"{index}\n{format_timestamp(start)} --> {format_timestamp(end)}\n"
                f"{wrap_caption(text)}\n\n"
            )

    print(f"Created {OUTPUT_AUDIO}")
    print(f"Created {OUTPUT_SRT}")


def main() -> None:
    if not REFERENCE.exists():
        raise FileNotFoundError(f"Missing reference audio: {REFERENCE}")
    chunks = load_chunks()
    print(f"Rendering {len(chunks)} chunks.")
    paths = render_chunks(chunks)
    join_audio_and_write_srt(chunks, paths)


if __name__ == "__main__":
    main()
