"""Check each new Shorts voice take with the existing local Whisper model."""
import argparse
import difflib
import json
from pathlib import Path
import re
import sys
import time
import unicodedata
import wave

import numpy as np

from make_approved_voice_v2 import DEFAULT_OUTPUT, MIN_FREE, QWEN, busy, pinned_plan, resource_guard, save, sha

ASR_REVISION = "41f01f3fe87f28c78e2fbf8b568835947dd65ed9"
MODEL = Path.home() / ".cache/huggingface/hub/models--openai--whisper-large-v3-turbo/snapshots" / ASR_REVISION


def normalize(text):
    text = unicodedata.normalize("NFKC", text).lower()
    # Whisper may write the same proper name in Hangul, Latin, or both.
    text = re.sub(r"(?<![a-z])elden\s*(?:ring(?![a-z])|링)", "엘든 링", text)
    text = re.sub(r"(?<![a-z])from\s*software(?![a-z])", "프롬 소프트웨어", text)
    return re.sub("[^가-힣a-z0-9]", "", text)


def metrics(path):
    with wave.open(str(path), "rb") as wav:
        samples = np.frombuffer(wav.readframes(wav.getnframes()), dtype="<i2").astype(np.float32) / 32768
        rate = wav.getframerate()
    frame_width = rate // 25
    frames = samples[:samples.size // frame_width * frame_width].reshape(-1, frame_width)
    level = 20 * np.log10(np.maximum(np.sqrt(np.mean(frames ** 2, axis=1)), 1.e-6))
    gate = max(float(np.max(level)) - 26, -50)
    active = level[level >= gate]
    if not active.size:
        raise ValueError(f"No active speech: {path.name}")
    midpoint = active.size // 2
    delta = float(np.median(active[midpoint:]) - np.median(active[:midpoint])) if midpoint else None
    return {"seconds": len(samples) / rate, "peakLevelDbfs": round(float(20 * np.log10(np.max(np.abs(samples)))), 2),
            "activeMedianDbfs": round(float(np.median(active)), 2),
            "speechHalfMedianChangeDb": round(delta, 2) if delta is not None else None,
            "activeSeconds": round(active.size * .04, 2)}


def load_transcriber(device):
    import torch
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

    torch.set_num_threads(4)
    if device == "cuda:0":
        total = torch.cuda.get_device_properties(0).total_memory
        torch.cuda.set_per_process_memory_fraction(min(1.0, 6 * 1024 ** 3 / total), 0)
    dtype = torch.float32 if device == "cpu" else torch.float16
    model = AutoModelForSpeechSeq2Seq.from_pretrained(str(MODEL), dtype=dtype, low_cpu_mem_usage=True,
                                                     local_files_only=True, attn_implementation="sdpa").to(device)
    processor = AutoProcessor.from_pretrained(str(MODEL), local_files_only=True)
    return pipeline("automatic-speech-recognition", model=model, tokenizer=processor.tokenizer,
                    feature_extractor=processor.feature_extractor, dtype=dtype, device=device)


def reserve_asr():
    guard = resource_guard()
    if reason := busy(guard, MIN_FREE):
        raise RuntimeError(f"Local Whisper resources are busy: {reason}")
    sys.path.insert(0, str(QWEN))
    from gpu_handoff_guard import schedule_gpu_handoff

    schedule_gpu_handoff("elden-ring-development-36-approved-voice-qa", "cuda:0",
                         minimum_free_mib=MIN_FREE)


def compare(expected, recognized):
    left, right = normalize(expected), normalize(recognized)
    matcher = difflib.SequenceMatcher(None, left, right, autojunk=False)
    return round(matcher.ratio(), 4), [
        (kind, left[a:b], right[c:d]) for kind, a, b, c, d in matcher.get_opcodes() if kind != "equal"
    ]


def compare_source(expected, review):
    comparisons = [compare(expected, review["recognized"])]
    alternate = review.get("independentReadback")
    if alternate and alternate["sha256"] == review["sha256"]:
        comparisons.append(compare(expected, alternate["recognized"]))
    return max(comparisons, key=lambda comparison: comparison[0])


def listen_to(transcriber, path, expected, kind):
    options = {"language": "korean", "task": "transcribe"}
    if kind == "source":
        spoken = transcriber(str(path), generate_kwargs=options, return_timestamps="word")
    else:
        # Source-take word boundaries have already anchored captions. Checking the
        # complete final mix needs the independent utterances, not new timing guides.
        spoken = transcriber(str(path), generate_kwargs={**options, "max_new_tokens": 160},
                             return_timestamps=False, chunk_length_s=30, stride_length_s=2)
    score, edits = compare(expected, spoken["text"])
    segments = [
        {"text": s["text"], "start": s["timestamp"][0], "end": s["timestamp"][1]}
        for s in spoken.get("chunks", []) if s["timestamp"][0] is not None and s["timestamp"][1] is not None
        and s["timestamp"][1] > s["timestamp"][0]
    ]
    result = {"sha256": sha(path), "model": f"whisper-large-v3-turbo/{ASR_REVISION}", "expected": expected,
              "recognized": spoken["text"], "similarity": score, "differences": edits,
              "timestampType": "positive-whole-word" if kind == "source" else "full-content-readback",
              "timestamped": segments, "humanReview": "pending"}
    if kind == "source":
        result["levels"] = metrics(path)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--mode", choices=("source", "mix", "both"), default="source")
    parser.add_argument("--device", choices=("cpu", "cuda:0"), default="cpu")
    parser.add_argument("--watch", action="store_true")
    parser.add_argument("--only", nargs="*", default=[])
    args = parser.parse_args()
    plan = pinned_plan()
    selection = []
    if args.mode in {"source", "both"}:
        selection += [("source", f"{ep['id']}-{n}", args.output / "approved-voice" / f"{ep['id']}-{n}.wav", utterance)
                      for ep in plan for n, utterance in enumerate(ep["narrationKo"])]
    if args.mode in {"mix", "both"}:
        selection += [("mix", ep["id"], args.output / ep["id"] / "captioned.mp4", " ".join(ep["narrationKo"])) for ep in plan]
    if args.only:
        selection = [item for item in selection if item[1] in args.only]
    for kind in {item[0] for item in selection}:
        (args.output / f"voice-qa-{kind}").mkdir(exist_ok=True, parents=True)
    stop = time.monotonic() + 7200
    transcriber = None
    pending = {(kind, key) for kind, key, _, _ in selection}
    source_paths = {key: path for kind, key, path, _ in selection if kind == "source"}
    verified_times = {}
    while pending:
        source_round = False
        for kind, key, path, expected in selection:
            job = (kind, key)
            if not path.is_file():
                continue
            changed = path.stat().st_mtime_ns
            if job not in pending:
                if verified_times.get(job) == changed:
                    continue
                pending.add(job)
            if kind == "mix" and any(k == "source" and source_paths[n].is_file() for k, n in pending):
                source_round = True
                break
            if kind == "mix" and not (path.parent / "verification.json").is_file():
                continue
            proof = args.output / f"voice-qa-{kind}" / f"{key}.json"
            if proof.is_file() and json.loads(proof.read_text(encoding="utf-8"))["sha256"] == sha(path):
                pending.remove(job)
                verified_times[job] = changed
                continue
            if kind == "source":
                try:
                    with wave.open(str(path), "rb") as audio:
                        completed = len(audio.readframes(audio.getnframes())) == audio.getnframes() * 2
                except (wave.Error, EOFError, PermissionError):
                    completed = False
                if not completed:
                    continue
            if transcriber is None:
                if args.device == "cuda:0":
                    reserve_asr()
                transcriber = load_transcriber(args.device)
            result = listen_to(transcriber, path, expected, kind)
            if path.stat().st_mtime_ns != changed:
                continue
            save(proof, result)
            pending.remove(job)
            verified_times[job] = changed
            print(f"{key} {kind} ASR {result['similarity']:.3f}", flush=True)
        if not pending or not args.watch:
            break
        if time.monotonic() >= stop:
            raise RuntimeError("Audio review timed out waiting for remaining files")
        time.sleep(1 if source_round else 12)
    print(f"{len(selection) - len(pending)}/{len(selection)} {args.mode} files reviewed.", flush=True)


if __name__ == "__main__":
    main()
