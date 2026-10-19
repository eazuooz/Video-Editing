"""One hash-cached complete CPU ASR pass for the new intro or final mix.

No expected-text prompt is sent to Whisper. Existing body recognition is not
changed. Importing this module starts no model or media work.
"""
from pathlib import Path
import argparse
import difflib
import hashlib
import json
import os
import re
import subprocess
import time
import unicodedata
import wave

R = Path(__file__).resolve().parents[4]
P = Path(__file__).resolve().parents[2]
L = P / "production/local/intro-v2"
MANIFEST = P / "production/intro-v2/tts-manifest.json"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf8"))


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def repository_path(value):
    path = Path(value)
    return path if path.is_absolute() else R / path


def relative(path):
    return Path(path).resolve().relative_to(R.resolve()).as_posix()


def normalized(text):
    return re.sub(r"[^0-9a-z가-힣]", "", unicodedata.normalize("NFC", text).lower())


def script_lines(path):
    document = read(path)
    lines = [line for scene in document["scenes"] for line in scene["lines"]]
    if not lines or any(not isinstance(line, str) or not line.strip() for line in lines):
        raise RuntimeError("Expected nonempty spoken intro/body lines.")
    return lines


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("role", choices=["intro", "mix"])
    parser.add_argument("--expected", help="Optional repository-relative full narration JSON for revised mix.")
    args = parser.parse_args(argv)
    manifest = read(MANIFEST)
    if manifest.get("slug") != P.name or manifest.get("revision") != "zombie-quiet-intro-v2":
        raise RuntimeError("Use this selected intro manifest only.")
    tts = manifest["tts"]
    source = (repository_path(tts["outputDir"]) / (tts["filenameStem"] + ".wav")
              if args.role == "intro" else L / "final-mix.m4a")
    intro_script = repository_path(manifest["paths"]["script"])
    script_paths = [repository_path(args.expected)] if args.expected else [intro_script]
    if args.role == "mix" and not args.expected:
        script_paths.append(P / "script/narration.ko.json")
    expected = " ".join(line for path in script_paths for line in script_lines(path))
    digest = sha(source)
    output = L / f"asr-{args.role}-{digest[:12]}.json"
    if output.exists():
        prior = read(output)
        if (prior.get("sha256") != digest or prior.get("role") != args.role
                or not prior.get("fullInput") or not prior.get("chunks")
                or not prior.get("rawRecognitionUnmodified")):
            raise RuntimeError("Prior ASR cache is incomplete or belongs to another input.")
        print(json.dumps({"output": relative(output), "cached": True,
                          "rawAsrPreserved": True,
                          "currentExpectedNormalizedMatch": normalized(expected) == normalized(prior["text"])},
                         ensure_ascii=False))
        return
    report_temporary = output.with_suffix(".partial.json")
    if report_temporary.exists():
        raise RuntimeError("Inspect the incomplete ASR report before attempting another pass.")
    os.environ.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1",
                      OMP_NUM_THREADS="3", MKL_NUM_THREADS="3")
    ffmpeg = Path(os.environ.get("YAMYAM_FFMPEG", str(Path(
        "C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/"
        "Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/"
        "ffmpeg-9.0-full_build/bin/ffmpeg.exe"))))
    if not ffmpeg.is_file():
        raise RuntimeError("FFmpeg not found; configure YAMYAM_FFMPEG explicitly.")
    os.environ["PATH"] = str(ffmpeg.parent) + os.pathsep + os.environ.get("PATH", "")
    L.mkdir(parents=True, exist_ok=True)
    wav = L / f"asr-{args.role}-{digest[:12]}-16k.wav"
    if not wav.exists():
        temporary = wav.with_name(wav.stem + ".partial.wav")
        if temporary.exists():
            raise RuntimeError("Inspect the incomplete ASR conversion before retrying.")
        subprocess.run([str(ffmpeg), "-v", "error", "-n", "-i", str(source),
                        "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(temporary)], check=True)
        temporary.replace(wav)
    with wave.open(str(wav), "rb") as audio:
        if audio.getframerate() != 16000 or audio.getnchannels() != 1:
            raise RuntimeError("ASR conversion must be mono16k PCM.")
        seconds = audio.getnframes() / audio.getframerate()
        if seconds <= 0:
            raise RuntimeError("ASR conversion contains no audio samples.")
    import torch
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

    torch.set_num_threads(3)
    torch.set_num_interop_threads(1)
    dedicated = R / "qwen3-tts/models/whisper-large-v3-turbo"
    # Same previously validated offline Hugging Face cache as body recognition.
    model_path = dedicated if (dedicated / "config.json").exists() else "openai/whisper-large-v3-turbo"
    started = time.monotonic()
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        str(model_path), dtype=torch.float32, attn_implementation="eager", local_files_only=True,
    ).to("cpu")
    processor = AutoProcessor.from_pretrained(str(model_path), local_files_only=True)
    recognize = pipeline("automatic-speech-recognition", model=model, tokenizer=processor.tokenizer,
                         feature_extractor=processor.feature_extractor, dtype=torch.float32, device="cpu")
    print("Transcribing complete " + args.role + " on CPU,3threads", flush=True)
    recognized = recognize(str(wav), generate_kwargs={"language": "korean", "task": "transcribe"},
                           return_timestamps="word")
    if not recognized.get("text") or not recognized.get("chunks"):
        raise RuntimeError("Complete ASR returned no usable full text/word timestamps.")
    if sha(source) != digest:
        raise RuntimeError("Source changed during ASR; preserve recognition as unassigned staging.")
    report = {
        "schemaVersion": 1, "role": args.role, "revision": "zombie-quiet-intro-v2",
        "input": relative(source), "sha256": digest, "fullInput": True,
        "inputDurationSeconds": seconds, "model": str(model_path), "device": "cpu", "cpuThreads": 3,
        "expectedTextPromptUsed": False, "rawRecognitionUnmodified": True,
        "text": recognized["text"], "chunks": recognized["chunks"], "expected": expected,
        "expectedSources": [{"path": relative(path), "sha256": sha(path)} for path in script_paths],
        "normalizedMatch": normalized(expected) == normalized(recognized["text"]),
        "similarity": difflib.SequenceMatcher(None, normalized(expected),
                                              normalized(recognized["text"]), autojunk=False).ratio(),
        "elapsedSeconds": round(time.monotonic() - started, 3), "humanListening": "pending",
    }
    report_temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    report_temporary.replace(output)
    print(json.dumps({"output": relative(output), "text": report["text"],
                      "similarity": report["similarity"], "humanListening": "pending"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
