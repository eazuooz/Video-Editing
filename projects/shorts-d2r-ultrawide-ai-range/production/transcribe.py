"""Cache one complete CPU or explicitly selected CUDA Whisper transcription per voice/mix file hash.

No job runs on import. The model receives no expected-text prompt. Reusing a
successful cache preserves the raw recognition even if editorial text changes.
"""
from pathlib import Path
import argparse
import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import time
import unicodedata
import wave

P = Path(__file__).resolve().parents[1]
R = P.parents[1]
from audio_revision import L, VOICE, REVISION, normalize_speech, guard as revision_guard
DEFAULT_VOICE = (
    "projects/shorts-d2r-ultrawide-ai-range/production/local/audio-v1/voice/"
    "interior.wav"
)


def read(path):
    return json.loads(Path(path).read_text(encoding="utf8"))


def sha(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def normalized(text):
    return normalize_speech(text, read(P / "script/clauses.json").get("pronunciationAliases", {}))


def repository_path(value):
    path = Path(value)
    return path if path.is_absolute() else R / path


def relative(path):
    try:
        return Path(path).resolve().relative_to(R.resolve()).as_posix()
    except ValueError:
        return str(Path(path).resolve())


def narration_input(project):
    source = repository_path(project["paths"]["script"])
    document = read(source)
    lines = [line for scene in document["scenes"] for line in scene["lines"]]
    if not lines or any(not isinstance(line, str) or not line.strip() for line in lines):
        raise RuntimeError("Narration must contain nonempty scene lines.")
    expected = " ".join(lines)
    text_path = P / "script/narration.ko.txt"
    if text_path.exists():
        raw = text_path.read_text(encoding="utf8").strip()
        if normalized(raw) != normalized(expected):
            raise RuntimeError("Narration JSON and narration.ko.txt differ.")
        expected = raw
    return source, expected


def ffmpeg_path():
    configured = os.environ.get("YAMYAM_FFMPEG")
    candidate = Path(configured) if configured else Path(
        "C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/"
        "Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/"
        "ffmpeg-9.0-full_build/bin/ffmpeg.exe"
    )
    if candidate.is_file():
        return candidate
    found = shutil.which("ffmpeg")
    if not found:
        raise RuntimeError("FFmpeg not found; set YAMYAM_FFMPEG to its executable.")
    return Path(found)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("role", choices=["voice", "mix"])
    args = parser.parse_args(argv)
    revision_guard()
    control=read(R/'shared/publishing/video-production-control.json')
    if P.name not in control.get('scopedBatchAuthorizations',{}).get('explicit-ten-distinctive-shorts-20261025',{}).get('slugs',[]):
        raise RuntimeError('Selected authorized Short changed; do not start ASR.')
    project = read(P / "project.json")
    voice = VOICE
    source = voice if args.role == "voice" else L / "final-mix.m4a"
    script_path, expected = narration_input(project)
    digest = sha(source)
    output = L / f"asr-{args.role}-{digest[:12]}.json"
    if output.exists():
        prior = read(output)
        if (prior.get("sha256") != digest or prior.get("role") != args.role
                or not prior.get("fullInput") or not prior.get("chunks")):
            raise RuntimeError("Existing ASR cache is incomplete or belongs to another input.")
        print(json.dumps({
            "output": relative(output), "cached": True,
            "rawAsrPreserved": True,
            "currentExpectedNormalizedMatch": normalized(expected) == normalized(prior["text"]),
        }, ensure_ascii=False))
        return
    report_temporary = output.with_suffix(".partial.json")
    if report_temporary.exists():
        raise RuntimeError("A prior incomplete ASR report needs inspection before starting another full run.")

    # Offline loading prevents a metadata network request or an accidental new model.
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["OMP_NUM_THREADS"] = "3"
    os.environ["MKL_NUM_THREADS"] = "3"
    ffmpeg = ffmpeg_path()
    os.environ["PATH"] = str(ffmpeg.parent) + os.pathsep + os.environ.get("PATH", "")
    L.mkdir(parents=True, exist_ok=True)
    wav = L / f"asr-{args.role}-{digest[:12]}-16k.wav"
    if not wav.exists():
        temporary = wav.with_name(wav.stem + ".partial.wav")
        if temporary.exists():
            raise RuntimeError("An incomplete ASR conversion exists; inspect it before retrying.")
        subprocess.run([
            str(ffmpeg), "-v", "error", "-n", "-i", str(source),
            "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(temporary),
        ], check=True)
        temporary.replace(wav)
    with wave.open(str(wav), "rb") as audio:
        if audio.getframerate() != 16000 or audio.getnchannels() != 1:
            raise RuntimeError("ASR conversion must be mono16k PCM.")
        measured_seconds = audio.getnframes() / audio.getframerate()
        if measured_seconds <= 0:
            raise RuntimeError("ASR conversion contains no audio samples.")

    import torch
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

    torch.set_num_threads(3)
    torch.set_num_interop_threads(1)
    dedicated = R / "qwen3-tts/models/whisper-large-v3-turbo"
    model_id = str(dedicated) if (dedicated / "config.json").exists() else "openai/whisper-large-v3-turbo"
    device = os.environ.get("YAMYAM_ASR_DEVICE", "cpu")
    if device not in ("cpu", "cuda"):
        raise RuntimeError("Unsupported ASR device")
    if device == "cuda":
        revision_guard()
        if not torch.cuda.is_available():
            raise RuntimeError("Requested CUDA ASR is unavailable")
        if (R / "shared/output/GPU_HANDOFF.json").exists():
            raise RuntimeError("Foreign GPU voice lease is active")
        free, usage = map(int, subprocess.check_output([
            "nvidia-smi", "--query-gpu=memory.free,utilization.gpu",
            "--format=csv,noheader,nounits"], text=True).strip().split(","))
        if free < 4800 or usage >= 35:
            raise RuntimeError("GPU not available for serial ASR")
    started = time.monotonic()
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, dtype=torch.float32, attn_implementation="eager", local_files_only=True,
    ).to(device)
    processor = AutoProcessor.from_pretrained(model_id, local_files_only=True)
    recognize = pipeline(
        "automatic-speech-recognition", model=model, tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor, dtype=torch.float32, device=device,
    )
    print("Transcribing complete " + args.role + " on " + device + ",3 CPU threads", flush=True)
    recognized = recognize(
        str(wav), generate_kwargs={"language": "korean", "task": "transcribe"},
        return_timestamps="word",
    )
    if not recognized.get("text") or not recognized.get("chunks"):
        raise RuntimeError("Complete ASR returned no usable text/word timestamps.")
    report = {
        "schemaVersion": 1, "role": args.role, "input": relative(source),
        "sha256": digest, "fullInput": True,
        "inputDurationSeconds": measured_seconds,
        "model": model_id, "device": device, "cpuThreads": 3,
        "expectedTextPromptUsed": False, "rawRecognitionUnmodified": True,
        "normalizationAliases": read(P / "script/clauses.json").get("pronunciationAliases", {}),
        "text": recognized["text"], "chunks": recognized["chunks"],
        "expected": expected, "expectedSource": relative(script_path),
        "expectedSourceSha256": sha(script_path),
        "normalizedMatch": normalized(expected) == normalized(recognized["text"]),
        "similarity": difflib.SequenceMatcher(
            None, normalized(expected), normalized(recognized["text"]), autojunk=False,
        ).ratio(),
        "elapsedSeconds": round(time.monotonic() - started, 3),
        "humanListening": "pending",
    }
    if sha(source) != digest:
        raise RuntimeError("Source changed during ASR; current recognition cannot be assigned to the earlier hash.")
    report_temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    report_temporary.replace(output)
    print(json.dumps({
        "output": relative(output), "text": report["text"],
        "similarity": report["similarity"], "humanListening": "pending",
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
