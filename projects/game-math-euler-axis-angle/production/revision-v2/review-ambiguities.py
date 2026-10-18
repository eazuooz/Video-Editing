"""One finite, unprompted ASR check of six already flagged complete contexts.

This never synthesizes, changes source PCM, or recognizes all26 scenes again.
Listening and pronunciation approval remain separate and pending.
"""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import time
import uuid

import numpy as np
import psutil
import soundfile as sf

ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / "projects/game-math-euler-axis-angle"
OUT = PROJECT / "production/local/revision-v2/ambiguity-review"
VOICE = ROOT / "shared/output/narration/game-math-euler-axis-angle/teaching-rules-v2"
LEASE = ROOT / "shared/output/GPU_HANDOFF.json"
RANGES = [
    ("01", 6.55, 19.15, "overview: interpolation term in complete adjacent sentences"),
    ("03", 0.0, 9.45, "complete world/body coordinate definitions"),
    ("04", 0.0, 7.40, "complete initial alignment and heading example"),
    ("05", 46.55, None, "last two approved sentences and full PCM tail"),
    ("12", 19.0, 35.38, "negative-pitch sum and complete following consequence"),
    ("15", 0.0, 35.02, "wrap branch setup and complete inside-range contrast"),
]


def read(file):
    return json.loads(file.read_text(encoding="utf-8"))


def sha(file):
    return hashlib.sha256(file.read_bytes()).hexdigest()


def relative(file):
    return file.relative_to(ROOT).as_posix()


def selected():
    assert read(ROOT / "shared/publishing/video-production-control.json")["selectedVideo"] == PROJECT.name


def save(data):
    (OUT / "results.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    selected()
    prior = read(PROJECT / "production/local/revision-v2/voice-review-execution.json")
    assert prior["status"] == "ASR-ready-for-direct-full-text-review" and prior["exitCode"] == 0
    assert not LEASE.exists(), "Preserve any other GPU lease"
    free = int(subprocess.check_output(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"], text=True).splitlines()[0])
    assert free >= 5000, free
    OUT.mkdir(parents=True, exist_ok=True)
    inputs = []
    for scene, start, end, purpose in RANGES:
        source = VOICE / "chunks" / f"{scene}-scene.wav"
        raw, rate = sf.read(source, dtype="float32")
        assert rate == 24000 and raw.ndim == 1
        a, b = round(start * rate), len(raw) if end is None else min(len(raw), round(end * rate))
        samples = raw[a:b]
        clip = OUT / f"{scene}-complete-context.wav"
        if clip.exists():
            kept, kept_rate = sf.read(clip, dtype="float32")
            assert kept_rate == rate and np.array_equal(kept, samples), "Preserve a different existing clip"
        else:
            sf.write(clip, samples, rate, subtype="FLOAT")
        inputs.append({"scene": scene, "source": relative(source), "sourceSha256": sha(source),
                       "sourceStartSample": a, "sourceEndSampleExclusive": b,
                       "sourceIn": a / rate, "sourceOutExclusive": b / rate,
                       "clip": relative(clip), "clipSha256": sha(clip), "sampleRate": rate,
                       "samplesPreservedExactly": True, "purpose": purpose})
    local_model = ROOT / "qwen3-tts/models/whisper-large-v3-turbo"
    model_id = str(local_model) if (local_model / "model.safetensors").exists() else "openai/whisper-large-v3-turbo"
    report = {"schemaVersion": 1, "slug": PROJECT.name, "status": "running-finite-context-ASR",
              "scope": "six flagged complete contexts only; no expected-text prompt; original PCM unchanged",
              "model": model_id, "scenes": inputs,
              "humanListening": "pending", "sourcePronunciation": "pending"}
    if (OUT / "results.json").exists():
        old = read(OUT / "results.json")
        if old.get("status") == "complete-independent-context-evidence":
            assert [{k: v for k, v in s.items() if k not in ("recognized", "words")} for s in old["scenes"]] == inputs
            print("Reused identical completed context evidence", flush=True)
            return
    token = str(uuid.uuid4())
    process = psutil.Process()
    owned = {"token": token, "project": PROJECT.name, "state": "tts_running",
             "coordinator": {"pid": os.getpid(), "createTime": process.create_time()},
             "purpose": "one finite ASR batch: six flagged complete contexts", "foreignProcessesPaused": []}
    with LEASE.open("x", encoding="utf-8") as handle:
        json.dump(owned, handle)
    try:
        save(report)
        import torch
        from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
        torch.set_num_threads(2)
        model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id, dtype=torch.float16, low_cpu_mem_usage=True,
                                                       use_safetensors=True, local_files_only=True,
                                                       attn_implementation="eager").to("cuda:0")
        processor = AutoProcessor.from_pretrained(model_id, local_files_only=True)
        transcribe = pipeline("automatic-speech-recognition", model=model, tokenizer=processor.tokenizer,
                              feature_extractor=processor.feature_extractor, dtype=torch.float16, device="cuda:0")
        for record in inputs:
            selected()
            print("Recognizing flagged complete context", record["scene"], flush=True)
            result = transcribe(str(ROOT / record["clip"]), generate_kwargs={"language": "korean", "task": "transcribe"},
                                return_timestamps="word")
            record["recognized"], record["words"] = result["text"], result["chunks"]
            save(report)
        report.update(status="complete-independent-context-evidence", completedAt=time.time())
        save(report)
    except BaseException as error:
        report.update(status="failed", error=repr(error))
        save(report)
        raise
    finally:
        if LEASE.exists() and read(LEASE).get("token") == token:
            LEASE.unlink()


if __name__ == "__main__":
    main()
