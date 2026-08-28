"""Render a project's narration locally with Qwen3-TTS voice cloning.

The script is resumable: valid per-line WAV files are reused after an
interruption, then joined into one edit-ready WAV and a timing-accurate SRT.

Project-specific paths come from projects/<slug>/project.json.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "projects" / "jump-physics" / "script" / "narration.ko.json"
REFERENCE = ROOT / "shared" / "voice-reference" / "reference-15-35s.wav"
MODEL_DIR = ROOT / "qwen3-tts" / "models" / "Qwen3-TTS-12Hz-0.6B-Base"
OUTPUT_DIR = ROOT / "shared" / "output" / "narration" / "qwen3-balanced"
CHUNK_DIR = OUTPUT_DIR / "chunks"
FINAL_WAV = OUTPUT_DIR / "jump-physics-qwen3-balanced.wav"
FINAL_SRT = OUTPUT_DIR / "jump-physics-qwen3-balanced.srt"
TIMING_JSON = OUTPUT_DIR / "jump-physics-qwen3-balanced.timing.json"
LANGUAGE = "Korean"


def load_tts_dependencies() -> None:
    """Import the GPU/audio stack only for a real render, not for --dry-run."""
    global np, sf, torch, Qwen3TTSModel

    import numpy as np_module
    import soundfile as sf_module
    import torch as torch_module
    from qwen_tts import Qwen3TTSModel as model_class

    np = np_module
    sf = sf_module
    torch = torch_module
    Qwen3TTSModel = model_class

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

# tail_ratio alone misses a subtler failure: the model stops right as the
# syllable's amplitude was already naturally low, so the clip reads "quiet at
# the end" even though it was cut off mid-decay. A real trailing consonant or
# breath fades out over tens to ~150ms+ (median measured here: ~106ms); an
# abrupt EOS-triggered stop can collapse in under 20ms while still passing the
# loudness-only check. tail_decay_ms measures how long the last local peak
# takes to fall to 10% of itself.
DECAY_MS_THRESHOLD = 50.0

# Speech does not have to start or end on a zero crossing, so a raw chunk
# butted directly against the silence gap around it steps instantly from 0 to
# whatever amplitude the chunk happened to start/end at -- an audible click.
# A short linear fade at both edges of every chunk removes that regardless of
# what the model produced, independent of the tail_ratio content check above
# (which catches missing content, not this splice noise).
FADE_SECONDS = 0.012


@dataclass(frozen=True)
class Job:
    scene_id: str
    scene_title: str
    line_number: int
    text: str

    @property
    def path(self) -> Path:
        return CHUNK_DIR / f"{self.scene_id}-{self.line_number:02d}.wav"


def _repo_path(relative: str) -> Path:
    """Resolve a manifest path and reject paths outside this repository."""
    resolved = (ROOT / relative).resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as error:
        raise ValueError(f"Project path escapes the repository: {relative}") from error
    return resolved


def configure_project(project: str) -> None:
    """Load all project-specific input and output paths from its manifest."""
    global SCRIPT_PATH, REFERENCE, MODEL_DIR, OUTPUT_DIR, CHUNK_DIR
    global FINAL_WAV, FINAL_SRT, TIMING_JSON, LANGUAGE

    manifest_path = ROOT / "projects" / project / "project.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Project manifest not found: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("slug") != project:
        raise ValueError(
            f"Manifest slug {manifest.get('slug')!r} does not match project {project!r}"
        )

    paths = manifest.get("paths", {})
    tts = manifest.get("tts", {})
    required = {
        "paths.script": paths.get("script"),
        "tts.reference": tts.get("reference"),
        "tts.model": tts.get("model"),
        "tts.outputDir": tts.get("outputDir"),
        "tts.filenameStem": tts.get("filenameStem"),
    }
    missing = [key for key, value in required.items() if not value]
    if missing:
        raise KeyError(f"Missing project settings: {', '.join(missing)}")

    SCRIPT_PATH = _repo_path(str(paths["script"]))
    REFERENCE = _repo_path(str(tts["reference"]))
    MODEL_DIR = _repo_path(str(tts["model"]))
    OUTPUT_DIR = _repo_path(str(tts["outputDir"]))
    CHUNK_DIR = OUTPUT_DIR / "chunks"
    stem = str(tts["filenameStem"])
    FINAL_WAV = OUTPUT_DIR / f"{stem}.wav"
    FINAL_SRT = OUTPUT_DIR / f"{stem}.srt"
    TIMING_JSON = OUTPUT_DIR / f"{stem}.timing.json"
    LANGUAGE = str(tts.get("language", "Korean"))


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


def _tail_decay_ms(wav: np.ndarray, sr: int) -> float:
    window = int(sr * 0.4)
    tail = wav[-window:] if len(wav) >= window else wav
    if len(tail) == 0:
        return float("inf")
    env = np.abs(tail)
    smooth_win = max(1, int(sr * 0.005))
    smooth = np.convolve(env, np.ones(smooth_win) / smooth_win, mode="same")
    if smooth.max() < 1e-4:
        return float("inf")
    peak_idx = int(np.argmax(smooth))
    peak_val = smooth[peak_idx]
    after = smooth[peak_idx:]
    below = np.where(after < peak_val * 0.10)[0]
    return float(below[0] / sr * 1000) if len(below) else float("inf")


def _passes_quality(tail_ratio: float, decay_ms: float) -> bool:
    return tail_ratio <= TAIL_RATIO_THRESHOLD and decay_ms >= DECAY_MS_THRESHOLD


def _badness(tail_ratio: float, decay_ms: float) -> float:
    """Lower is better; <=1.0 on both axes means it passes."""
    return max(tail_ratio / TAIL_RATIO_THRESHOLD, DECAY_MS_THRESHOLD / max(decay_ms, 1.0))


def _read_mono(path: Path) -> tuple[np.ndarray, int]:
    wav, sr = sf.read(path, dtype="float32", always_2d=False)
    if wav.ndim == 2:
        wav = wav.mean(axis=1)
    return wav, sr


def _apply_edge_fades(wav: np.ndarray, sr: int, seconds: float = FADE_SECONDS) -> np.ndarray:
    n = min(int(sr * seconds), len(wav) // 2)
    if n <= 1:
        return wav
    wav = wav.copy()
    ramp = np.linspace(0.0, 1.0, n, dtype=np.float32)
    wav[:n] *= ramp
    wav[-n:] *= ramp[::-1]
    return wav


def needs_render(path: Path) -> bool:
    if not valid_wav(path):
        return True
    wav, sr = _read_mono(path)
    return not _passes_quality(_tail_ratio(wav, sr), _tail_decay_ms(wav, sr))


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
            language=LANGUAGE,
            voice_clone_prompt=voice_prompt,
            non_streaming_mode=True,
        )
        return wavs[0], sr

    for index in range(0, len(pending), batch_size):
        batch = pending[index : index + batch_size]
        wavs, sample_rate = model.generate_voice_clone(
            text=[job.text for job in batch],
            language=LANGUAGE,
            voice_clone_prompt=voice_prompt,
            non_streaming_mode=True,
        )
        if len(wavs) != len(batch):
            raise RuntimeError(f"Expected {len(batch)} WAVs, got {len(wavs)}")
        for job, wav in zip(batch, wavs, strict=True):
            best_wav = wav
            best_tail, best_decay = _tail_ratio(wav, sample_rate), _tail_decay_ms(wav, sample_rate)
            best_score = _badness(best_tail, best_decay)
            attempts = 1
            while not _passes_quality(best_tail, best_decay) and attempts < MAX_RENDER_ATTEMPTS:
                attempts += 1
                retry_wav, retry_sr = generate_one(job.text)
                retry_tail, retry_decay = _tail_ratio(retry_wav, retry_sr), _tail_decay_ms(retry_wav, retry_sr)
                retry_score = _badness(retry_tail, retry_decay)
                if retry_score < best_score:
                    best_wav, best_tail, best_decay, best_score = retry_wav, retry_tail, retry_decay, retry_score
            sf.write(job.path, best_wav, sample_rate)
            status = (
                "clean"
                if _passes_quality(best_tail, best_decay)
                else f"best of {attempts} (tail={best_tail:.3f}, decay={best_decay:.0f}ms)"
            )
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
        wav = _apply_edge_fades(wav, sample_rate)

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
    parser.add_argument(
        "--project",
        default="jump-physics",
        help="Project slug under projects/ (default: jump-physics)",
    )
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate the manifest and script without loading the TTS model",
    )
    args = parser.parse_args()
    if args.batch_size < 1:
        raise ValueError("--batch-size must be at least 1")

    configure_project(args.project)
    print(f"Project: {args.project}")
    print(f"Script:  {SCRIPT_PATH}")
    print(f"Output:  {OUTPUT_DIR}")
    jobs = load_jobs()
    if args.dry_run:
        print(f"Dry run passed: {len(jobs)} narration lines")
        return
    load_tts_dependencies()
    render_chunks(jobs, args.batch_size)
    assemble_outputs(jobs)


if __name__ == "__main__":
    main()
