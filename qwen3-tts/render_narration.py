"""Render the jump-physics narration locally with Qwen3-TTS voice cloning.

The script is resumable: valid per-line WAV files are reused after an
interruption, then joined into one edit-ready WAV and a timing-accurate SRT.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
from qwen_tts import Qwen3TTSModel


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "narration" / "jump-physics.script.json"
REFERENCE = ROOT / "shared" / "voice-reference" / "reference-15-35s.wav"
MODEL_DIR = ROOT / "qwen3-tts" / "models" / "Qwen3-TTS-12Hz-0.6B-Base"
OUTPUT_DIR = ROOT / "shared" / "output" / "narration" / "qwen3-balanced"
CHUNK_DIR = OUTPUT_DIR / "chunks"
FINAL_WAV = OUTPUT_DIR / "jump-physics-qwen3-balanced.wav"
FINAL_SRT = OUTPUT_DIR / "jump-physics-qwen3-balanced.srt"
TIMING_JSON = OUTPUT_DIR / "jump-physics-qwen3-balanced.timing.json"

# Small pauses make adjacent generated lines sound like a single narration,
# while preserving a clean cut point for the video editor.
LINE_GAP_SECONDS = 0.22
SCENE_GAP_SECONDS = 0.65

# Qwen3-TTS occasionally predicts the end-of-audio token before a sentence's
# trailing decay (e.g. "-니다.") has finished, clipping it mid-sound. This is
# stochastic per sample (do_sample=True), not a per-sentence bug, so a
# regenerate-until-clean loop reliably fixes it. tail_ratio = RMS of the last
# 50ms over RMS of the whole clip; a real ending decays toward silence
# (ratio well under 0.05 in testing), a clipped one stays loud (0.15+).
TAIL_RATIO_THRESHOLD = 0.08
MAX_RENDER_ATTEMPTS = 5


@dataclass(frozen=True)
class Job:
    scene_id: str
    scene_title: str
    line_number: int
    text: str

    @property
    def path(self) -> Path:
        return CHUNK_DIR / f"{self.scene_id}-{self.line_number:02d}.wav"


def timestamp(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    seconds, milliseconds = divmod(milliseconds, 1_000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def load_jobs() -> list[Job]:
    payload = json.loads(SCRIPT_PATH.read_text(encoding="utf-8"))
    jobs: list[Job] = []
    for scene in payload["scenes"]:
        for line_number, text in enumerate(scene["lines"], start=1):
            text = text.strip()
            if text:
                jobs.append(Job(scene["id"], scene["title"], line_number, text))
    return jobs


def valid_wav(path: Path) -> bool:
    if not path.exists() or path.stat().st_size < 100:
        return False
    try:
        return sf.info(path).frames > 0
    except RuntimeError:
        return False


def _rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(x**2))) if len(x) else 0.0


def _tail_ratio(wav: np.ndarray, sr: int) -> float:
    whole = _rms(wav)
    if whole == 0:
        return 0.0
    return _rms(wav[-int(sr * 0.05):]) / whole


def _read_mono(path: Path) -> tuple[np.ndarray, int]:
    wav, sr = sf.read(path, dtype="float32", always_2d=False)
    if wav.ndim == 2:
        wav = wav.mean(axis=1)
    return wav, sr


def needs_render(path: Path) -> bool:
    if not valid_wav(path):
        return True
    wav, sr = _read_mono(path)
    return _tail_ratio(wav, sr) > TAIL_RATIO_THRESHOLD


def render_chunks(jobs: list[Job], batch_size: int) -> None:
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA GPU is required for local Qwen3-TTS inference.")
    if not REFERENCE.exists():
        raise FileNotFoundError(f"Reference audio not found: {REFERENCE}")
    if not MODEL_DIR.exists():
        raise FileNotFoundError(f"Model not found: {MODEL_DIR}")

    pending = [job for job in jobs if needs_render(job.path)]
    if not pending:
        print("All narration chunks already exist and have clean endings; reusing them.")
        return

    CHUNK_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Rendering {len(pending)} narration chunks locally (batch size {batch_size}).")
    model = Qwen3TTSModel.from_pretrained(
        str(MODEL_DIR), device_map="cuda:0", dtype=torch.bfloat16
    )
    # Build the voice identity prompt once, then reuse it for every batch.
    voice_prompt = model.create_voice_clone_prompt(
        ref_audio=str(REFERENCE), x_vector_only_mode=True
    )

    def generate_one(text: str) -> tuple[np.ndarray, int]:
        wavs, sr = model.generate_voice_clone(
            text=[text],
            language="Korean",
            voice_clone_prompt=voice_prompt,
            non_streaming_mode=True,
        )
        return wavs[0], sr

    for index in range(0, len(pending), batch_size):
        batch = pending[index : index + batch_size]
        wavs, sample_rate = model.generate_voice_clone(
            text=[job.text for job in batch],
            language="Korean",
            voice_clone_prompt=voice_prompt,
            non_streaming_mode=True,
        )
        if len(wavs) != len(batch):
            raise RuntimeError(f"Expected {len(batch)} WAVs, got {len(wavs)}")
        for job, wav in zip(batch, wavs, strict=True):
            best_wav, best_ratio, attempts = wav, _tail_ratio(wav, sample_rate), 1
            while best_ratio > TAIL_RATIO_THRESHOLD and attempts < MAX_RENDER_ATTEMPTS:
                attempts += 1
                retry_wav, retry_sr = generate_one(job.text)
                retry_ratio = _tail_ratio(retry_wav, retry_sr)
                if retry_ratio < best_ratio:
                    best_wav, best_ratio = retry_wav, retry_ratio
            sf.write(job.path, best_wav, sample_rate)
            status = "clean" if best_ratio <= TAIL_RATIO_THRESHOLD else f"best of {attempts}, still soft-clipped ({best_ratio:.3f})"
            print(
                f"Rendered {job.scene_id}-{job.line_number:02d} "
                f"({len(best_wav) / sample_rate:.2f}s, {status}): {job.text[:24]}"
            )


def assemble_outputs(jobs: list[Job]) -> None:
    pieces: list[np.ndarray] = []
    srt_entries: list[dict[str, object]] = []
    position = 0.0
    sample_rate: int | None = None

    for job_index, job in enumerate(jobs):
        if not valid_wav(job.path):
            raise FileNotFoundError(f"Missing or invalid chunk: {job.path}")
        wav, sr = sf.read(job.path, dtype="float32", always_2d=False)
        if wav.ndim == 2:
            wav = wav.mean(axis=1)
        if sample_rate is None:
            sample_rate = sr
        elif sample_rate != sr:
            raise RuntimeError(f"Sample-rate mismatch in {job.path}: {sr} != {sample_rate}")

        start = position
        duration = len(wav) / sample_rate
        end = start + duration
        pieces.append(wav)
        srt_entries.append(
            {
                "index": job_index + 1,
                "scene_id": job.scene_id,
                "scene_title": job.scene_title,
                "text": job.text,
                "start": start,
                "end": end,
            }
        )

        is_last = job_index == len(jobs) - 1
        next_scene = None if is_last else jobs[job_index + 1].scene_id
        gap_seconds = 0.0 if is_last else (
            SCENE_GAP_SECONDS if next_scene != job.scene_id else LINE_GAP_SECONDS
        )
        if gap_seconds:
            pieces.append(np.zeros(round(gap_seconds * sample_rate), dtype=np.float32))
            position = end + gap_seconds
        else:
            position = end

    if sample_rate is None:
        raise RuntimeError("The narration script contained no renderable lines.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sf.write(FINAL_WAV, np.concatenate(pieces), sample_rate)
    srt = "\n\n".join(
        f"{entry['index']}\n{timestamp(float(entry['start']))} --> "
        f"{timestamp(float(entry['end']))}\n{entry['text']}"
        for entry in srt_entries
    )
    FINAL_SRT.write_text(srt + "\n", encoding="utf-8")
    TIMING_JSON.write_text(
        json.dumps(
            {
                "sample_rate": sample_rate,
                "duration_seconds": position,
                "entries": srt_entries,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Created {FINAL_WAV}")
    print(f"Created {FINAL_SRT}")
    print(f"Duration: {position:.2f}s")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-size", type=int, default=2)
    args = parser.parse_args()
    if args.batch_size < 1:
        raise ValueError("--batch-size must be at least 1")

    jobs = load_jobs()
    render_chunks(jobs, args.batch_size)
    assemble_outputs(jobs)


if __name__ == "__main__":
    main()
