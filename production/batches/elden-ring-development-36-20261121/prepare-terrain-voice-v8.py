"""Produce and independently review only the revised terrain narration, on CPU."""
import argparse
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import sys
import tempfile

sys.dont_write_bytecode = True
os.environ["CUDA_VISIBLE_DEVICES"] = ""

from make_approved_voice_v2 import DEFAULT_OUTPUT, QWEN, pcm, read, save, sha


TAKE = "07-1"
SENTENCES = (
    "처음엔 높이맵을 검토했습니다.",
    "격자에 있는 점마다 높이를 정해서 지형을 만드는 방식입니다.",
)
ENGLISH = (
    "The team first considered a heightmap.",
    "A heightmap shapes terrain by assigning a height to each point on a grid.",
)
TEXT = " ".join(SENTENCES)
DEFAULT_DESTINATION = DEFAULT_OUTPUT.parent / "pc-review-v8" / "terrain-voice"
OLD_SHA = "bdbe758c9c7dac8e43eb8a42e02d11811f6c9497507a68e5ba2ba8c4a15001bc"


def limit_cpu():
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    kernel.SetPriorityClass.argtypes = (wintypes.HANDLE, wintypes.DWORD)
    kernel.GetProcessAffinityMask.argtypes = (
        wintypes.HANDLE, ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_size_t),
    )
    kernel.SetProcessAffinityMask.argtypes = (wintypes.HANDLE, ctypes.c_size_t)
    handle = kernel.GetCurrentProcess()
    allowed, system = ctypes.c_size_t(), ctypes.c_size_t()
    if not kernel.SetPriorityClass(handle, 0x00004000):
        raise ctypes.WinError(ctypes.get_last_error())
    if not kernel.GetProcessAffinityMask(handle, ctypes.byref(allowed), ctypes.byref(system)):
        raise ctypes.WinError(ctypes.get_last_error())
    available = [1 << bit for bit in range(allowed.value.bit_length()) if allowed.value & (1 << bit)]
    limit = sum(available[-4:])
    if not kernel.SetProcessAffinityMask(handle, limit):
        raise ctypes.WinError(ctypes.get_last_error())
    print(f"CPU worker below normal priority on {len(available[-4:])} logical processors", flush=True)


def identity():
    sys.path.insert(0, str(QWEN))
    import render_narration as engine

    baseline = read(DEFAULT_OUTPUT / "voice-identity-v2.json")
    old = DEFAULT_OUTPUT / "approved-voice" / f"{TAKE}.wav"
    if sha(old) != OLD_SHA:
        raise ValueError("Original 07-1 audio changed")
    checks = {
        "engineSha256": sha(QWEN / "render_narration.py"),
        "referenceSha256": sha(engine.REFERENCE),
        "referenceTextSha256": sha(engine.REFERENCE_TEXT_PATH),
        "model": engine.MODEL_DIR.name,
    }
    if any(baseline.get(key) != value for key, value in checks.items()):
        raise ValueError("Approved speaker or generation engine changed")
    return engine, {"originalTakeSha256": OLD_SHA, **checks, "device": "cpu",
                    "dtype": "float32", "sceneBatchSize": 1, "maxNewTokens": 4096,
                    "narrationKo": TEXT, "narrationEn": " ".join(ENGLISH)}


def render(engine, info, destination, raw):
    if raw.exists():
        existing = read(destination / "generation.json")
        if existing["identity"] != info or existing["take"] != pcm(raw):
            raise ValueError("Existing replacement belongs to a different voice identity")
        print(f"Using existing scoped raw WAV: {raw}", flush=True)
        return
    with tempfile.TemporaryDirectory(prefix="render-", dir=destination) as staging:
        candidate = Path(staging) / raw.name
        engine.CHUNK_DIR = candidate.parent
        engine.INFERENCE_DEVICE = "cpu"
        engine.MAX_RENDER_ATTEMPTS = info.get("maxAttempts", 1)
        engine.MAX_NEW_TOKENS = 4096
        engine.load_tts_dependencies()
        engine.render_chunks([engine.RenderItem(TAKE, TEXT, candidate)], batch_size=1)
        wav = pcm(candidate)
        if wav["samples"] > 252000:
            raise ValueError("New narration cannot fit its existing eleven-second beat")
        samples, sample_rate = engine.sf.read(candidate, dtype="float32")
        tail_ratio = engine._tail_ratio(samples, sample_rate)
        decay_ms = engine._tail_decay_ms(samples, sample_rate)
        ending = {"tailRatio": tail_ratio, "decayMs": decay_ms,
                  "passes": bool(engine._passes_quality(tail_ratio, decay_ms))}
        candidate.replace(raw)
        save(destination / "generation.json", {"identity": info, "take": wav, "ending": ending})
    print(f"Scoped replacement raw WAV: {raw}", flush=True)


def sentence_intervals(words, normalize):
    ranges = []
    index = 0
    for ko, en in zip(SENTENCES, ENGLISH, strict=True):
        target = normalize(ko)
        text = ""
        onset = index
        while index < len(words) and len(text) < len(target):
            text += normalize(words[index]["text"])
            index += 1
        if text != target or index <= onset:
            raise ValueError("The exact two sentences lack independent whole-word timestamp edges")
        start, end = words[onset]["start"], words[index - 1]["end"]
        if ranges and start < ranges[-1]["end"]:
            raise ValueError("Sentence boundary overlaps")
        ranges.append({"ko": ko, "en": en, "start": start, "end": end})
    if index != len(words):
        raise ValueError("Unexpected whole-word readback remainder")
    return ranges


def review(destination, raw, info):
    from review_approved_voice_v2 import listen_to, load_transcriber, normalize

    existing = read(destination / "generation.json")
    if existing["identity"] != info or existing["take"] != pcm(raw):
        raise ValueError("Narration changed between generation and review")
    result = listen_to(load_transcriber("cpu"), raw, TEXT, "source")
    report = destination / "07-1-source-review.json"
    result["identity"] = info
    result["sampleRate"] = existing["take"]["sampleRate"]
    result["samples"] = existing["take"]["samples"]
    result["approvedForEdit"] = False
    try:
        if normalize(result["recognized"]) != normalize(TEXT):
            raise ValueError("Independent transcription differs from the exact revised narration")
        result["sentenceIntervals"] = sentence_intervals(result["timestamped"], normalize)
        if result["levels"]["peakLevelDbfs"] >= -.02:
            raise ValueError("Narration needs a clipping review")
        if result["levels"]["speechHalfMedianChangeDb"] <= -6:
            raise ValueError("Narration needs a sustained late-level review")
        if "ending" in existing:
            result["ending"] = existing["ending"]
            if not result["ending"]["passes"]:
                raise ValueError("Narration needs a clean ending")
        result["approvedForEdit"] = True
    finally:
        save(report, result)
    print(json.dumps({"raw": str(raw), "review": str(report), "intervals": result["sentenceIntervals"]},
                     ensure_ascii=False), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("check", "render", "review"))
    parser.add_argument("--destination", type=Path, default=DEFAULT_DESTINATION)
    parser.add_argument("--ending-attempts", type=int, choices=(1, 3), default=1)
    args = parser.parse_args()
    engine, info = identity()
    if args.ending_attempts > 1:
        info["maxAttempts"] = args.ending_attempts
    if args.operation == "check":
        print(json.dumps(info, ensure_ascii=False, indent=2))
        return
    limit_cpu()
    destination = args.destination.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    raw = destination / f"{TAKE}.wav"
    lock = destination / "07-1-cpu-worker.lock"
    with lock.open("x", encoding="utf-8") as marker:
        marker.write(str(os.getpid()))
    try:
        if args.operation == "render":
            render(engine, info, destination, raw)
        else:
            review(destination, raw, info)
    finally:
        lock.unlink()


if __name__ == "__main__":
    main()
