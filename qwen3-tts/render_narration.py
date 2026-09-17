"""Render a project's narration locally with Qwen3-TTS voice cloning.

The script is resumable: valid per-line or per-scene WAV files are reused after
an interruption, then joined into one edit-ready WAV and a timing-accurate SRT.

Project-specific paths come from projects/<slug>/project.json.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "projects" / "jump-physics" / "script" / "narration.ko.json"
REFERENCE = ROOT / "shared" / "voice-reference" / "reference-15-35s.wav"
REFERENCE_TEXT_PATH: Path | None = (
    ROOT / "shared" / "voice-reference" / "reference-15-35s.ko.txt"
)
MODEL_DIR = ROOT / "qwen3-tts" / "models" / "Qwen3-TTS-12Hz-1.7B-Base"
OUTPUT_DIR = ROOT / "shared" / "output" / "narration" / "qwen3-1.7b-balanced-v1"
CHUNK_DIR = OUTPUT_DIR / "chunks"
FINAL_WAV = OUTPUT_DIR / "jump-physics-qwen3-balanced.wav"
FINAL_SRT = OUTPUT_DIR / "jump-physics-qwen3-balanced.srt"
TIMING_JSON = OUTPUT_DIR / "jump-physics-qwen3-balanced.timing.json"
LANGUAGE = "Korean"
RENDER_MODE = "scene"


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
LINE_GAP_SECONDS = 0.28
SCENE_GAP_SECONDS = 0.72
EXAMPLE_SECONDS = 0.0  # opt-in via manifest; preserve older project timing
NARRATION_PLACEMENT = "after-example-meme-overlays-explanation"


def narration_lead_seconds() -> float:
    return 0.0 if NARRATION_PLACEMENT in {"continuous-across-example-and-explanation", "continuous-across-all-three-segments"} else EXAMPLE_SECONDS

# Qwen3-TTS occasionally predicts the end-of-audio token before a sentence's
# trailing decay (e.g. "-니다.") has finished, clipping it mid-sound. This is
# stochastic per sample (do_sample=True), not a per-sentence bug, so a
# regenerate-until-clean loop reliably fixes it. tail_ratio = RMS of the last
# 50ms over RMS of the whole clip; a real ending decays toward silence
# (ratio well under 0.05 in testing), a clipped one stays loud (0.15+).
TAIL_RATIO_THRESHOLD = 0.07
MAX_RENDER_ATTEMPTS = 3
MAX_NEW_TOKENS = 1024

# tail_ratio alone misses a subtler failure: the model stops right as the
# syllable's amplitude was already naturally low, so the clip reads "quiet at
# the end" even though it was cut off mid-decay. A real trailing consonant or
# breath fades out over tens to ~150ms+ (median measured here: ~106ms); an
# abrupt EOS-triggered stop can collapse in under 20ms while still passing the
# loudness-only check. tail_decay_ms measures how long the last local peak
# takes to fall to 10% of itself.
DECAY_MS_THRESHOLD = 70.0

# Speech does not have to start or end on a zero crossing, so a raw chunk
# butted directly against the silence gap around it steps instantly from 0 to
# whatever amplitude the chunk happened to start/end at -- an audible click.
# A short linear fade at both edges of every chunk removes that regardless of
# what the model produced, independent of the tail_ratio content check above
# (which catches missing content, not this splice noise).
FADE_SECONDS = 0.006


@dataclass(frozen=True)
class Job:
    scene_id: str
    scene_title: str
    line_number: int
    text: str

    @property
    def path(self) -> Path:
        return CHUNK_DIR / f"{self.scene_id}-{self.line_number:02d}.wav"


@dataclass(frozen=True)
class RenderItem:
    key: str
    text: str
    path: Path


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
    global SCRIPT_PATH, REFERENCE, REFERENCE_TEXT_PATH, MODEL_DIR, OUTPUT_DIR, CHUNK_DIR
    global FINAL_WAV, FINAL_SRT, TIMING_JSON, LANGUAGE, RENDER_MODE
    global LINE_GAP_SECONDS, SCENE_GAP_SECONDS, TAIL_RATIO_THRESHOLD
    global EXAMPLE_SECONDS, NARRATION_PLACEMENT
    global DECAY_MS_THRESHOLD, MAX_RENDER_ATTEMPTS, MAX_NEW_TOKENS, FADE_SECONDS

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
    EXAMPLE_SECONDS = float(manifest.get("editing", {}).get("exampleSeconds", 0))
    NARRATION_PLACEMENT = manifest.get("editing", {}).get("narrationPlacement", "after-example-meme-overlays-explanation")
    if NARRATION_PLACEMENT not in {"after-example-meme-overlays-explanation", "continuous-across-example-and-explanation", "continuous-across-all-three-segments"}:
        raise ValueError(f"Unsupported narration placement: {NARRATION_PLACEMENT}")
    if not 0 <= EXAMPLE_SECONDS <= 120:
        raise ValueError("editing.exampleSeconds must be between 0 and 120")
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
    reference_text = tts.get("referenceText")
    REFERENCE_TEXT_PATH = _repo_path(str(reference_text)) if reference_text else None
    MODEL_DIR = _repo_path(str(tts["model"]))
    OUTPUT_DIR = _repo_path(str(tts["outputDir"]))
    CHUNK_DIR = OUTPUT_DIR / "chunks"
    stem = str(tts["filenameStem"])
    FINAL_WAV = OUTPUT_DIR / f"{stem}.wav"
    FINAL_SRT = OUTPUT_DIR / f"{stem}.srt"
    TIMING_JSON = OUTPUT_DIR / f"{stem}.timing.json"
    LANGUAGE = str(tts.get("language", "Korean"))
    RENDER_MODE = str(tts.get("renderMode", "line"))
    if RENDER_MODE not in {"line", "scene"}:
        raise ValueError("tts.renderMode must be either 'line' or 'scene'")
    LINE_GAP_SECONDS = float(tts.get("lineGapSeconds", LINE_GAP_SECONDS))
    SCENE_GAP_SECONDS = float(tts.get("sceneGapSeconds", SCENE_GAP_SECONDS))
    TAIL_RATIO_THRESHOLD = float(
        tts.get("tailRatioThreshold", TAIL_RATIO_THRESHOLD)
    )
    DECAY_MS_THRESHOLD = float(tts.get("tailDecayMsThreshold", DECAY_MS_THRESHOLD))
    MAX_RENDER_ATTEMPTS = int(tts.get("maxRenderAttempts", MAX_RENDER_ATTEMPTS))
    MAX_NEW_TOKENS = int(tts.get("maxNewTokens", MAX_NEW_TOKENS))
    FADE_SECONDS = float(tts.get("edgeFadeSeconds", FADE_SECONDS))


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


def build_render_items(jobs: list[Job]) -> list[RenderItem]:
    if RENDER_MODE == "line":
        return [
            RenderItem(
                key=f"{job.scene_id}-{job.line_number:02d}",
                text=job.text,
                path=job.path,
            )
            for job in jobs
        ]

    grouped: dict[str, list[Job]] = {}
    for job in jobs:
        grouped.setdefault(job.scene_id, []).append(job)
    return [
        RenderItem(
            key=f"{scene_id}-scene",
            text=" ".join(job.text for job in scene_jobs),
            path=CHUNK_DIR / f"{scene_id}-scene.wav",
        )
        for scene_id, scene_jobs in grouped.items()
    ]


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
    normal_decay = (
        tail_ratio <= TAIL_RATIO_THRESHOLD and decay_ms >= DECAY_MS_THRESHOLD
    )
    # A very quiet terminal consonant can legitimately close faster than the
    # general decay threshold.  Accept that only when both the absolute tail
    # ratio and the measured decay are still safely away from a hard cut.
    quiet_natural_close = tail_ratio <= 0.025 and decay_ms >= 35.0
    return normal_decay or quiet_natural_close


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


def render_chunks(items: list[RenderItem], batch_size: int, force_scenes: set[str] | None = None) -> None:
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA GPU is required for local Qwen3-TTS inference.")
    if not REFERENCE.exists():
        raise FileNotFoundError(f"Reference audio not found: {REFERENCE}")
    if not MODEL_DIR.exists():
        raise FileNotFoundError(f"Model not found: {MODEL_DIR}")
    if REFERENCE_TEXT_PATH is not None and not REFERENCE_TEXT_PATH.exists():
        raise FileNotFoundError(f"Reference transcript not found: {REFERENCE_TEXT_PATH}")

    force_scenes = force_scenes or set()
    pending = [item for item in items if item.key.split('-')[0] in force_scenes or needs_render(item.path)]
    for item in pending:
        if item.key.split('-')[0] in force_scenes and valid_wav(item.path):
            stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
            previous = item.path.with_name(f"{item.path.stem}-previous-{stamp}.wav")
            shutil.copy2(item.path, previous)
            print(f"Preserved previous take: {previous}", flush=True)
    if not pending:
        print("All narration chunks already exist and have clean endings; reusing them.")
        return

    CHUNK_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Rendering {len(pending)} narration chunks locally (batch size {batch_size}).")
    model = Qwen3TTSModel.from_pretrained(
        str(MODEL_DIR), device_map="cuda:0", dtype=torch.bfloat16
    )
    # Build the voice identity prompt once, then reuse it for every batch.
    reference_text = (
        REFERENCE_TEXT_PATH.read_text(encoding="utf-8").strip()
        if REFERENCE_TEXT_PATH is not None
        else None
    )
    if reference_text:
        print(f"Using transcript-assisted voice cloning: {REFERENCE_TEXT_PATH}")
        voice_prompt = model.create_voice_clone_prompt(
            ref_audio=str(REFERENCE),
            ref_text=reference_text,
            x_vector_only_mode=False,
        )
    else:
        print("Using speaker-vector-only voice cloning (no reference transcript).")
        voice_prompt = model.create_voice_clone_prompt(
            ref_audio=str(REFERENCE), x_vector_only_mode=True
        )

    def generate_one(text: str) -> tuple[np.ndarray, int]:
        wavs, sr = model.generate_voice_clone(
            text=[text],
            language=LANGUAGE,
            voice_clone_prompt=voice_prompt,
            non_streaming_mode=True,
            max_new_tokens=MAX_NEW_TOKENS,
        )
        return wavs[0], sr

    for index in range(0, len(pending), batch_size):
        batch = pending[index : index + batch_size]
        wavs, sample_rate = model.generate_voice_clone(
            text=[item.text for item in batch],
            language=LANGUAGE,
            voice_clone_prompt=voice_prompt,
            non_streaming_mode=True,
            max_new_tokens=MAX_NEW_TOKENS,
        )
        if len(wavs) != len(batch):
            raise RuntimeError(f"Expected {len(batch)} WAVs, got {len(wavs)}")
        for item, wav in zip(batch, wavs, strict=True):
            best_wav = wav
            best_tail, best_decay = _tail_ratio(wav, sample_rate), _tail_decay_ms(wav, sample_rate)
            best_score = _badness(best_tail, best_decay)
            attempts = 1
            sf.write(item.path, best_wav, sample_rate)
            print(
                f"Checked {item.key} attempt 1: "
                f"tail={best_tail:.3f}, decay={best_decay:.0f}ms",
                flush=True,
            )
            while not _passes_quality(best_tail, best_decay) and attempts < MAX_RENDER_ATTEMPTS:
                attempts += 1
                retry_wav, retry_sr = generate_one(item.text)
                retry_tail, retry_decay = _tail_ratio(retry_wav, retry_sr), _tail_decay_ms(retry_wav, retry_sr)
                retry_score = _badness(retry_tail, retry_decay)
                if retry_score < best_score:
                    best_wav, best_tail, best_decay, best_score = retry_wav, retry_tail, retry_decay, retry_score
                    sf.write(item.path, best_wav, retry_sr)
                print(
                    f"Checked {item.key} attempt {attempts}: "
                    f"tail={retry_tail:.3f}, decay={retry_decay:.0f}ms",
                    flush=True,
                )
            status = (
                "clean"
                if _passes_quality(best_tail, best_decay)
                else f"best of {attempts} (tail={best_tail:.3f}, decay={best_decay:.0f}ms)"
            )
            print(
                f"Rendered {item.key} "
                f"({len(best_wav) / sample_rate:.2f}s, {status}): {item.text[:24]}",
                flush=True,
            )


def _line_weight(text: str) -> float:
    spoken = re.sub(r"[^0-9A-Za-z가-힣]", "", text)
    return max(1.0, float(len(spoken)))


def _line_boundaries(wav: np.ndarray, sr: int, lines: list[str]) -> list[float]:
    """Place subtitle boundaries at quiet valleys near text-length estimates."""
    duration = len(wav) / sr
    if len(lines) <= 1:
        return [0.0, duration]

    weights = np.asarray([_line_weight(line) for line in lines], dtype=np.float64)
    targets = np.cumsum(weights)[:-1] / weights.sum() * duration
    window = max(1, round(sr * 0.025))
    hop = max(1, round(sr * 0.010))
    starts = np.arange(0, max(1, len(wav) - window + 1), hop)
    envelope = np.asarray([_rms(wav[start : start + window]) for start in starts])
    if len(envelope) >= 7:
        envelope = np.convolve(envelope, np.ones(7) / 7, mode="same")
    times = (starts + window / 2) / sr

    boundaries = [0.0]
    min_segment = min(1.25, duration / (len(lines) * 2.5))
    for index, target in enumerate(targets):
        remaining = len(lines) - index - 1
        low = boundaries[-1] + min_segment
        high = duration - remaining * min_segment
        radius = max(1.6, duration * 0.08)
        mask = (times >= max(low, target - radius)) & (
            times <= min(high, target + radius)
        )
        candidates = np.where(mask)[0]
        if not len(candidates):
            boundary = min(high, max(low, float(target)))
        else:
            local = envelope[candidates]
            energy = local / max(float(np.percentile(envelope, 80)), 1e-6)
            distance = np.abs(times[candidates] - target) / radius
            best = candidates[int(np.argmin(energy + distance * 0.12))]
            boundary = float(times[best])
        boundaries.append(boundary)
    boundaries.append(duration)
    return boundaries


def assemble_outputs(jobs: list[Job]) -> None:
    pieces: list[np.ndarray] = []
    srt_entries: list[dict[str, object]] = []
    position = 0.0
    sample_rate: int | None = None

    if RENDER_MODE == "scene":
        assemble_scene_outputs(jobs)
        return

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

        if narration_lead_seconds() and (job_index == 0 or jobs[job_index - 1].scene_id != job.scene_id):
            lead_samples = round(narration_lead_seconds() * sample_rate)
            pieces.append(np.zeros(lead_samples, dtype=np.float32))
            position += lead_samples / sample_rate

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
                "example_seconds": EXAMPLE_SECONDS,
                "narration_placement": NARRATION_PLACEMENT,
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


def assemble_scene_outputs(jobs: list[Job]) -> None:
    pieces: list[np.ndarray] = []
    srt_entries: list[dict[str, object]] = []
    grouped: dict[str, list[Job]] = {}
    for job in jobs:
        grouped.setdefault(job.scene_id, []).append(job)

    position = 0.0
    sample_rate: int | None = None
    entry_index = 1
    scene_items = list(grouped.items())
    for scene_index, (scene_id, scene_jobs) in enumerate(scene_items):
        path = CHUNK_DIR / f"{scene_id}-scene.wav"
        if not valid_wav(path):
            raise FileNotFoundError(f"Missing or invalid scene chunk: {path}")
        wav, sr = _read_mono(path)
        if sample_rate is None:
            sample_rate = sr
        elif sample_rate != sr:
            raise RuntimeError(f"Sample-rate mismatch in {path}: {sr} != {sample_rate}")
        wav = _apply_edge_fades(wav, sr)
        boundaries = _line_boundaries(wav, sr, [job.text for job in scene_jobs])
        if narration_lead_seconds():
            lead_samples = round(narration_lead_seconds() * sr)
            pieces.append(np.zeros(lead_samples, dtype=np.float32))
            position += lead_samples / sr
        pieces.append(wav)
        for line_index, job in enumerate(scene_jobs):
            srt_entries.append(
                {
                    "index": entry_index,
                    "scene_id": job.scene_id,
                    "scene_title": job.scene_title,
                    "text": job.text,
                    "start": position + boundaries[line_index],
                    "end": position + boundaries[line_index + 1],
                }
            )
            entry_index += 1

        duration = len(wav) / sr
        position += duration
        if scene_index != len(scene_items) - 1:
            pieces.append(np.zeros(round(SCENE_GAP_SECONDS * sr), dtype=np.float32))
            position += SCENE_GAP_SECONDS

    if sample_rate is None:
        raise RuntimeError("The narration script contained no renderable scenes.")

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
                "render_mode": RENDER_MODE,
                "example_seconds": EXAMPLE_SECONDS,
                "narration_placement": NARRATION_PLACEMENT,
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
    parser.add_argument("--force-scenes", default="", help="Comma-separated scene IDs to regenerate after content review; previous takes are preserved")
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
    force_scenes = {value.strip().zfill(2) for value in args.force_scenes.split(',') if value.strip()}
    unknown = force_scenes - {job.scene_id for job in jobs}
    if unknown:
        raise ValueError(f"Unknown forced scene IDs: {sorted(unknown)}")
    if args.dry_run:
        print(f"Dry run passed: {len(jobs)} narration lines")
        return
    load_tts_dependencies()
    items = build_render_items(jobs)
    effective_batch_size = 1 if RENDER_MODE == "scene" else args.batch_size
    print(f"Render mode: {RENDER_MODE} ({len(items)} synthesis jobs)")
    render_chunks(items, effective_batch_size, force_scenes)
    assemble_outputs(jobs)


if __name__ == "__main__":
    main()
