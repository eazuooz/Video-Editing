"""Current, isolated audio preparation for the selected video revision.

No stage generates TTS, downloads a model, claims human listening, touches a GPU,
or changes a project manifest, shared controller, research queue or other job.
Invoke stages explicitly; importing this module does no work.

    python audio_pipeline.py assemble
    python audio_pipeline.py recognize
    python audio_pipeline.py compare
    python audio_pipeline.py split --review <repository-relative review.json>
    python audio_pipeline.py caption-input --plan <repository-relative edit-plan.json>
    python audio_pipeline.py mix --plan <repository-relative edit-plan.json>
    python audio_pipeline.py recognize-final --encoded-file <captioned.mp4>

Raw manifest (default production/local/reference-preserving-v2/voice/raw-inputs.json):
    {"sources": [{"path": "repo/relative.mp3", "sha256": "..."}],
     "joinSilenceSeconds": 0.2}
Source order is narration order. Originals remain untouched. Source paths may
also be absolute paths within this repository. All persistent media is ignored
local output; only this implementation belongs in Git.

Split review is an internal complete-text review, not another user approval:
    {"audioSha256": "...", "comparisonSha256": "...",
     "fullTextDirectlyCompared": true, "notes": "..."}

Mix plan: fps=60, totalFrames, optional introFrames=120/outroFrames=600,
scenes=[{id, voiceStart OR voiceStartFrame, startFrame, endFrame}], and cuts.
Scene chunks are placed intact with no stretching or speech fades. Optional
audio.music={path,sha256,licenseRecord,title,artist}; no unverified track fallback.
Independent-gameplay cuts can retain source audio using sourceFile, sourceStart,
startFrame, frames, sourceSha256 and sourceAudioEnabled=true. Source music and
commentary selection remain the scene editor's responsibility. Optional audio
settings: targetLufs=-16, voicePeakDbfs=-2.5, musicLufs=-31, gameRmsDbfs=-33,
matchSceneRms=false, sceneSpeechRmsDbfs=-20, preserveGameAudio=true.

Outputs: shared/output/narration/<slug>/reference-preserving-v2 contains source
assembly, the one cached full source ASR, comparison, chunks/asr, paragraph/word
timing and split evidence. Mix stems/report/AAC are in production/local/
reference-preserving-v2/edit. Existing incompatible outputs are never replaced.
Choose a distinct revision/output directory if changed inputs need a new take.
caption-input emits the sibling caption_pipeline.py schema. It uses the intact
scene PCM's measured duration and global origin, and selects paragraph words
with their scene-local timestamps. plan.captionAliases can map display tokens
to pronunciation tokens; spelling in the video remains canonical.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import difflib
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import uuid

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[4]
PROJECT = Path(__file__).resolve().parents[2]
SLUG = PROJECT.name
REVISION = Path(__file__).resolve().parent.name
SCRIPT = PROJECT / "script" / REVISION
LOCAL = PROJECT / "production" / "local" / REVISION
NARRATION = ROOT / "shared" / "output" / "narration" / SLUG / REVISION
RATE = 24000


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def relative(path):
    return Path(path).resolve().relative_to(ROOT.resolve()).as_posix()


def repo_path(value):
    path = Path(value)
    path = (path if path.is_absolute() else ROOT / path).resolve()
    path.relative_to(ROOT.resolve())
    return path


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".writing")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def canonical_signature(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def output_cache(path, signature, files=()):
    """An existing receipt either matches exactly or remains preserved."""
    if not Path(path).exists():
        return None
    receipt = read(path)
    if receipt.get("inputSignature") != signature:
        raise ValueError(f"Preserved output has different inputs: {relative(path)}; use a new revision/output directory")
    for item in files or receipt.get("outputs", []):
        path_to_check = repo_path(item["path"])
        if not path_to_check.is_file() or sha(path_to_check) != item["sha256"]:
            raise ValueError(f"Existing output missing/changed: {item['path']}; recover it before reuse")
    return receipt


def require_new(*paths):
    for path in paths:
        if Path(path).exists():
            raise FileExistsError(f"Preserve existing unregistered output: {path}")


def tool(name):
    configured = os.environ.get("VIDEO_" + name.upper()) or os.environ.get(name.upper() + "_BINARY")
    candidates = [Path(configured)] if configured else []
    installed = shutil.which(name)
    if installed:
        candidates.append(Path(installed))
    candidates += [ROOT / "motion-canvas" / "node_modules" / "@ffmpeg-installer" / "win32-x64" / (name + ".exe")]
    winget = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages"
    if winget.is_dir():
        candidates += sorted(winget.glob("Gyan.FFmpeg*/ffmpeg*/bin/" + name + ".exe"))
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    raise FileNotFoundError(f"Set VIDEO_{name.upper()} to the installed {name} executable; this pipeline never downloads tools")


def run_ff(args, log):
    process = subprocess.run(
        [tool("ffmpeg"), "-hide_banner", "-nostdin", "-v", "info", "-threads", "4",
         "-filter_threads", "1", "-filter_complex_threads", "1", "-n", *map(str, args)],
        cwd=ROOT, capture_output=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    Path(log).parent.mkdir(parents=True, exist_ok=True)
    Path(log).write_bytes(process.stderr)
    if process.returncode:
        raise RuntimeError(process.stderr.decode("utf-8", errors="replace")[-4000:])
    return process.stderr.decode("utf-8", errors="replace")


def artifact(path):
    return {"path": relative(path), "sha256": sha(path), "bytes": Path(path).stat().st_size}


@contextmanager
def stage_lock(directory, stage):
    """Only our own lock is removed; even stale foreign locks are left alone."""
    directory.mkdir(parents=True, exist_ok=True)
    lock = directory / "audio-pipeline.lock.json"
    token = uuid.uuid4().hex
    control = ROOT / "shared" / "publishing" / "video-production-control.json"
    policy = read(control)
    record = {"token": token, "pid": os.getpid(), "stage": stage, "startedAt": now(),
              "project": SLUG, "revision": REVISION, "controlSha256": sha(control),
              "observedControlMode": policy.get("mode"), "foreignProcessesPaused": [], "device": "cpu"}
    with lock.open("x", encoding="utf-8") as handle:
        json.dump(record, handle, ensure_ascii=False, indent=2)
    try:
        yield record
    finally:
        if lock.exists() and read(lock).get("token") == token:
            lock.unlink()


def scripts():
    ko_file, en_file = SCRIPT / "narration.ko.json", SCRIPT / "narration.en.json"
    spoken_file = SCRIPT / "narration.tts.ko.json"
    ko, en = read(ko_file), read(en_file)
    spoken = read(spoken_file) if spoken_file.exists() else ko
    expected_ids = [scene["id"] for scene in ko["scenes"]]
    if not expected_ids or len(expected_ids) != len(set(expected_ids)) or not all(re.fullmatch(r"[A-Za-z0-9_-]+", str(value)) for value in expected_ids):
        raise ValueError("Narration scene IDs must be nonempty and unique")
    for collection in (en, spoken):
        if [scene["id"] for scene in collection["scenes"]] != expected_ids:
            raise ValueError("KO/EN/pronunciation scene IDs or order differ")
    for a, b, c in zip(ko["scenes"], en["scenes"], spoken["scenes"]):
        if not a["lines"] or len(a["lines"]) != len(b["lines"]) or len(a["lines"]) != len(c["lines"]):
            raise ValueError(f"KO/EN/pronunciation paragraph counts differ: {a['id']}")
        if not all(isinstance(line, str) and line.strip() for scene in (a, b, c) for line in scene["lines"]):
            raise ValueError("Empty/non-text narration paragraph")
    files = [artifact(ko_file), artifact(en_file)]
    if spoken_file.exists():
        files.append(artifact(spoken_file))
    return ko, en, spoken, files


def alignment_helpers():
    sys.path.insert(0, str(ROOT / "qwen3-tts"))
    from align_project_subtitles import align_characters, normalized
    return align_characters, normalized


def assemble(manifest):
    specification = read(manifest)
    if not specification.get("sources"):
        raise ValueError("raw-inputs.json must contain ordered, hashed sources")
    gap = float(specification.get("joinSilenceSeconds", .2))
    if not math.isfinite(gap) or gap < 0 or gap > 2:
        raise ValueError("Declared join silence must be 0..2 seconds")
    sources = []
    for source in specification["sources"]:
        path = repo_path(source["path"])
        if not path.is_file() or sha(path) != source["sha256"].lower():
            raise ValueError(f"Source missing/hash mismatch: {path}")
        sources.append(artifact(path))
    inputs = {"sources": sources, "joinSilenceSamples": round(gap * RATE), "sampleRate": RATE,
              "decode": "ffmpeg mono pcm_f32le; order unchanged; no speech edits or time stretch"}
    signature = canonical_signature(inputs)
    receipt_path, full_path = NARRATION / "source-assembly.json", NARRATION / "narration-source.wav"
    if output_cache(receipt_path, signature):
        print("Reusing unchanged source assembly")
        return
    require_new(full_path)
    parts, placements, position, outputs = [], [], 0, []
    for index, source in enumerate(sources):
        if index and inputs["joinSilenceSamples"]:
            parts.append(np.zeros(inputs["joinSilenceSamples"], dtype=np.float32))
            position += inputs["joinSilenceSamples"]
        decoded = NARRATION / "decoded-sources" / f"{index + 1:03d}-{source['sha256'][:12]}.wav"
        decoded.parent.mkdir(parents=True, exist_ok=True)
        require_new(decoded)
        run_ff(["-i", repo_path(source["path"]), "-vn", "-ac", "1", "-ar", RATE, "-c:a", "pcm_f32le", decoded],
               NARRATION / "logs" / f"decode-source-{index + 1:03d}.log")
        audio, rate = sf.read(decoded, dtype="float32")
        if rate != RATE or audio.ndim != 1 or not len(audio) or not np.isfinite(audio).all():
            raise ValueError(f"Invalid decoded source: {decoded}")
        parts.append(audio)
        placements.append({"source": source, "decoded": artifact(decoded), "startSample": position,
                           "endSample": position + len(audio), "samples": len(audio)})
        position += len(audio)
        outputs.append(artifact(decoded))
    full = np.concatenate(parts)
    sf.write(full_path, full, RATE, subtype="FLOAT")
    restored, rate = sf.read(full_path, dtype="float32")
    if rate != RATE or not np.array_equal(restored, full):
        raise ValueError("Float source assembly failed exact sample reconstruction")
    outputs.append(artifact(full_path))
    save(receipt_path, {"inputSignature": signature, "createdAt": now(), "inputs": inputs,
                       "placements": placements, "outputs": outputs, "samples": len(full),
                       "durationSeconds": len(full) / RATE, "sampleRate": RATE,
                       "sha256": sha(full_path), "originalBytesRetained": True,
                       "decodedSamplesPreserved": True, "timeStretch": False, "humanListening": "pending"})
    print(f"Assembled {len(full) / RATE:.3f}s from {len(sources)} preserved source files")


def full_asr(audio_path, cache_path, *, final=False):
    local_model = ROOT / "qwen3-tts" / "models" / "whisper-large-v3-turbo"
    current_audio = artifact(audio_path)
    if Path(cache_path).exists():
        cached = read(cache_path)
        recorded = cached.get("inputs", {})
        if recorded.get("audio") != current_audio or recorded.get("timestampGranularity") != ("segment" if final else "word"):
            raise ValueError("Preserve an existing ASR for different audio; use a distinct revision/output directory")
        if cached.get("inputSignature") != canonical_signature(recorded) or cached.get("audio_sha256") != current_audio["sha256"]:
            raise ValueError("ASR cache identity/signature is inconsistent")
        if recorded.get("device") != "cpu" or recorded.get("expectedPrompt") is not None or not cached.get("completeAudioSubmitted"):
            raise ValueError("Existing ASR does not satisfy this pipeline's full, unprompted CPU recognition contract")
        print("Reusing unchanged complete ASR; model loading and recognition skipped")
        return cached
    model_id = str(local_model) if (local_model / "config.json").is_file() else "openai/whisper-large-v3-turbo"
    config_path = local_model / "config.json"
    if not config_path.is_file():
        # This helper only inspects the existing Hugging Face cache. It performs
        # no request and never reads or prints credentials.
        from huggingface_hub import try_to_load_from_cache
        cached_config = try_to_load_from_cache(model_id, "config.json")
        config_path = Path(cached_config) if isinstance(cached_config, str) else None
    inputs = {"audio": current_audio, "model": relative(local_model) if model_id != "openai/whisper-large-v3-turbo" else model_id,
              "modelConfigSha256": sha(config_path) if config_path and config_path.is_file() else None, "device": "cpu",
              "threads": 4, "language": "korean", "task": "transcribe",
              "timestampGranularity": "segment" if final else "word", "expectedPrompt": None,
              "boundedRecognition": {"chunkSeconds":30,"strideSeconds":[5,5],"batchSize":1,"numBeams":1}}
    signature = canonical_signature(inputs)
    cached = output_cache(cache_path, signature)
    if cached:
        print("Reusing unchanged complete ASR; no new recognition")
        return cached
    import torch
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
    torch.set_num_threads(4)
    model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id, dtype=torch.float32,
                                                    attn_implementation="eager", local_files_only=True)
    processor = AutoProcessor.from_pretrained(model_id, local_files_only=True)
    recognizer = pipeline("automatic-speech-recognition", model=model, tokenizer=processor.tokenizer,
                          feature_extractor=processor.feature_extractor, dtype=torch.float32, device="cpu")
    print("Recognizing the complete current audio once on CPU4, without a supplied prompt", flush=True)
    result = recognizer(str(audio_path), generate_kwargs={"language": "korean", "task": "transcribe", "num_beams":1},
                        chunk_length_s=30, stride_length_s=(5,5), batch_size=1,
                        return_timestamps=True if final else "word")
    record = {"inputSignature": signature, "createdAt": now(), "inputs": inputs,
              "audio_sha256": inputs["audio"]["sha256"], "text": result["text"],
              "segments" if final else "words": result["chunks"], "completeAudioSubmitted": True,
              "scope": "complete current final encoded mix" if final else "complete current source narration",
              "noExpectedPrompt": True, "newRecognitionPasses": 1, "device": "cpu", "cpuThreads": 4,
              "foreignProcessesPaused": [], "fullTextDirectReview": "pending", "humanListening": "pending"}
    save(cache_path, record)
    return record


def compare(cache_path, output_path):
    ko, _en, spoken, script_files = scripts()
    _, normalized = alignment_helpers()
    actual = read(cache_path)
    display_text = " ".join(line for scene in ko["scenes"] for line in scene["lines"])
    spoken_text = " ".join(line for scene in spoken["scenes"] for line in scene["lines"])
    a, b = normalized(spoken_text), normalized(actual["text"])
    matcher = difflib.SequenceMatcher(None, a, b, autojunk=False)
    record = {"createdAt": now(), "audioSha256": actual["audio_sha256"], "asrSha256": sha(cache_path),
              "scriptInputs": script_files, "displayText": display_text, "expectedSpokenText": spoken_text,
              "recognized": actual["text"], "normalizedSimilarity": matcher.ratio(),
              "differences": [{"kind": op, "expected": a[i:j], "recognized": b[k:l],
                               "expectedCharacterRange": [i, j], "recognizedCharacterRange": [k, l]}
                              for op, i, j, k, l in matcher.get_opcodes() if op != "equal"],
              "reviewStatus": "pending direct comparison of complete text; score is not approval",
              "humanListening": "pending"}
    save(output_path, record)
    print(f"Comparison written; similarity {matcher.ratio():.4f}, complete direct review pending")


def db(value):
    return float(20 * np.log10(max(float(value), 1e-12)))


def rms(audio):
    return float(np.sqrt(np.mean(np.square(audio, dtype=np.float64)))) if len(audio) else 0.0


def safe_boundary(audio, rate, previous_end, next_start, *, override=None, silence_dbfs=-42, minimum_pause=.05):
    """Check a low-energy pause near aligned sentence ends, never split by text length.

    Word timestamps are estimates. A narrow +/-120ms tolerance permits their
    small boundary errors, while requiring an actual >=50ms low-energy run.
    The report distinguishes this signal check from listening/phoneme approval.
    """
    target = (previous_end + next_start) / 2
    lo = max(0, round((min(previous_end, next_start) - .12) * rate))
    hi = min(len(audio), round((max(previous_end, next_start) + .12) * rate))
    hop = max(1, round(rate * .005))
    width = max(hop, round(rate * .01))
    threshold = 10 ** (silence_dbfs / 20)
    values = []
    for sample in range(lo, hi - width + 1, hop):
        block = audio[sample:sample + width]
        values.append((sample, rms(block), float(np.max(np.abs(block)))))
    runs, current = [], []
    for point in values:
        if point[1] <= threshold and point[2] <= threshold * 4:
            current.append(point)
        else:
            if current:
                runs.append(current)
                current = []
    if current:
        runs.append(current)
    runs = [run for run in runs if (run[-1][0] + width - run[0][0]) / rate >= minimum_pause]
    if not runs:
        raise ValueError(f"No verified low-energy scene pause near {target:.3f}s; inspect full context, do not cut a word or stretch audio")
    if override is None:
        selected = min(runs, key=lambda run: abs((run[0][0] + run[-1][0] + width) / (2 * rate) - target))
        cut = round((selected[0][0] + selected[-1][0] + width) / 2)
    else:
        cut = round(float(override) * rate)
        candidates = [run for run in runs if run[0][0] + width // 2 <= cut <= run[-1][0] + width // 2]
        if not candidates:
            raise ValueError("Requested boundary override is outside a verified low-energy pause")
        selected = candidates[0]
    return cut, {"cutSample": cut, "cutSeconds": cut / rate, "alignedPreviousEnd": previous_end,
                 "alignedNextStart": next_start, "pauseStart": selected[0][0] / rate,
                 "pauseEnd": (selected[-1][0] + width) / rate, "minimumPauseSeconds": minimum_pause,
                 "maximumWindowRmsDbfs": db(max(point[1] for point in selected)),
                 "silenceThresholdDbfs": silence_dbfs, "analysisWindowMs": 10, "analysisHopMs": 5,
                 "signalPauseCheckPassed": True, "semanticBoundaryListening": "pending",
                 "contextForListening": [max(0, target - 1.5), min(len(audio) / rate, target + 1.5)]}


def split(review_path, overrides_path=None):
    ko, en, spoken, script_files = scripts()
    raw, cache = NARRATION / "narration-source.wav", NARRATION / "whole-source-asr.json"
    comparison_path = NARRATION / "whole-source-comparison.json"
    review, comparison, recognition = read(review_path), read(comparison_path), read(cache)
    digest = sha(raw)
    if recognition["audio_sha256"] != digest or comparison["audioSha256"] != digest:
        raise ValueError("ASR/comparison does not match the current assembled audio")
    if comparison["scriptInputs"] != script_files or comparison["asrSha256"] != sha(cache):
        raise ValueError("Comparison is stale for the current scripts or ASR")
    if review.get("audioSha256") != digest or review.get("comparisonSha256") != sha(comparison_path) or review.get("fullTextDirectlyCompared") is not True:
        raise ValueError("Record direct comparison of the complete current source ASR before scene splitting")
    overrides = read(overrides_path) if overrides_path else {}
    override_rows = {row["afterScene"]: row for row in overrides.get("boundaries", [])}
    inputs = {"sourceSha256": digest, "asrSha256": sha(cache), "scripts": script_files,
              "comparisonReview": artifact(review_path), "boundaryOverrides": overrides,
              "boundaryPolicy": "word-aligned plus >=50ms waveform low-energy pause; no time stretch"}
    signature = canonical_signature(inputs)
    receipt_path = NARRATION / "scene-split-review.json"
    if output_cache(receipt_path, signature):
        print("Reusing unchanged split/timing outputs")
        return
    align_characters, normalized = alignment_helpers()
    audio, rate = sf.read(raw, dtype="float32")
    if rate != RATE or audio.ndim != 1:
        raise ValueError("Expected mono float source at 24kHz")
    expected = " ".join(line for scene in spoken["scenes"] for line in scene["lines"])
    starts, ends, coverage = align_characters(expected, recognition["words"], len(audio) / rate)
    bounds, boundaries, cursor = [0], [], 0
    for scene in spoken["scenes"][:-1]:
        cursor += sum(len(normalized(line)) for line in scene["lines"])
        override = override_rows.get(scene["id"])
        if override and (not override.get("fullContextReviewed") or not override.get("reason")):
            raise ValueError("Boundary overrides need an actual contextual review and reason")
        boundary, evidence = safe_boundary(audio, rate, float(ends[cursor - 1]), float(starts[cursor]),
                                          override=override["cutSeconds"] if override else None)
        if boundary <= bounds[-1] or boundary >= len(audio):
            raise ValueError("Scene boundaries must be strictly increasing inside the audio")
        bounds.append(boundary)
        boundaries.append({"afterScene": scene["id"], **evidence})
    bounds.append(len(audio))
    chunks, asr_dir = NARRATION / "chunks", NARRATION / "asr"
    chunks.mkdir(exist_ok=True)
    asr_dir.mkdir(exist_ok=True)
    outputs, scene_rows, entries, reconstructed, cursor = [], [], [], [], 0
    for scene, translation, tts_scene, lo, hi in zip(ko["scenes"], en["scenes"], spoken["scenes"], bounds, bounds[1:]):
        destination, word_file = chunks / f"{scene['id']}-scene.wav", asr_dir / f"{scene['id']}.json"
        require_new(destination, word_file)
        sf.write(destination, audio[lo:hi], rate, subtype="FLOAT")
        back, check_rate = sf.read(destination, dtype="float32")
        if check_rate != rate or not np.array_equal(back, audio[lo:hi]):
            raise ValueError("Split output failed exact decoded sample preservation")
        reconstructed.append(back)
        words = []
        for word in recognition["words"]:
            begin, end = word["timestamp"]
            if begin is None or end is None:
                continue
            # Assign each recognized word once by its endpoint; original full
            # timestamps remain available for investigating ASR boundary errors.
            if lo / rate < end <= hi / rate + 1e-7:
                words.append({"text": word["text"], "timestamp": [max(0, begin - lo / rate), min((hi - lo) / rate, end - lo / rate)],
                              "sourceTimestamp": [begin, end]})
        local_spoken = " ".join(tts_scene["lines"])
        _local_starts, _local_ends, local_coverage = align_characters(local_spoken, words, (hi - lo) / rate)
        save(word_file, {"scene": scene["id"], "audio_sha256": sha(destination), "text": " ".join(word["text"].strip() for word in words),
                         "words": words, "derivedFrom": {"path": relative(cache), "sha256": sha(cache), "startSample": lo, "endSample": hi},
                         "newRecognitionPass": False, "scriptMatchCoverage": local_coverage, "humanListening": "pending"})
        paragraphs = []
        for paragraph, (line, english, pronounced) in enumerate(zip(scene["lines"], translation["lines"], tts_scene["lines"]), 1):
            length = len(normalized(pronounced))
            if not length:
                raise ValueError("Pronunciation paragraph has no alignable characters")
            start, end = float(starts[cursor]), float(ends[cursor + length - 1])
            if start < lo / rate - .12 or end > hi / rate + .12:
                raise ValueError("Aligned paragraph exceeds the verified source scene boundary")
            local_begin = max(0, start - lo / rate)
            local_end = min((hi - lo) / rate, end - lo / rate)
            entry = {"index": len(entries) + 1, "scene_id": scene["id"], "scene_title": scene["title"], "paragraph": paragraph,
                     "text": line, "english": english, "spokenText": pronounced,
                     "start": lo / rate if paragraph == 1 else start, "voice_start": start, "end": end,
                     "sourceSceneOrigin": lo / rate, "sceneLocalStart": local_begin, "sceneLocalEnd": local_end,
                     "alignment": "complete-source-word-timestamps-matched-to-pronunciation-script"}
            entries.append(entry)
            paragraphs.append({"paragraph": paragraph, "text": line, "english": english, "spokenText": pronounced,
                               "start": local_begin, "end": local_end})
            cursor += length
        scene_rows.append({"id": scene["id"], "title": scene["title"], "path": relative(destination), "sha256": sha(destination),
                           "startSample": lo, "endSample": hi, "samples": hi - lo, "sampleRate": rate,
                           "duration": (hi - lo) / rate, "sourceOrigin": lo / rate,
                           "paragraphStarts": [row["start"] for row in paragraphs], "paragraphs": paragraphs,
                           "wordFile": relative(word_file), "asrCoverage": local_coverage})
        outputs.extend([artifact(destination), artifact(word_file)])
    if not np.array_equal(np.concatenate(reconstructed), audio):
        raise ValueError("Concatenated scene PCM differs from the assembled source")
    timing_path = NARRATION / "narration.timing.json"
    scenes_path = NARRATION / "source-scene-timings.json"
    save(timing_path, {"sample_rate": rate, "duration_seconds": len(audio) / rate,
                       "render_mode": "continuous-cloud-source-split-at-verified-signal-pauses", "entries": entries})
    save(scenes_path, {"inputSignature": signature, "sampleRate": rate, "sourceSha256": digest, "scenes": scene_rows})
    outputs.extend([artifact(timing_path), artifact(scenes_path)])
    save(receipt_path, {"inputSignature": signature, "createdAt": now(), "inputs": inputs, "outputs": outputs,
                       "matchingCoverage": coverage, "boundaries": boundaries, "scenes": scene_rows,
                       "decodedSourceReconstructionIdentical": True, "discardedSamples": 0, "repeatedSamples": 0,
                       "timeStretch": False, "newRecognitionPasses": 0, "humanListening": "pending"})
    print(f"Split {len(scene_rows)} scenes; exact decoded sample reconstruction verified")


def mask_words(length, rate, words):
    mask = np.zeros(length, dtype=bool)
    for word in words:
        begin, end = word["timestamp"]
        if begin is not None and end is not None:
            mask[max(0, round(begin * rate)):min(length, round(end * rate))] = True
    return mask


def caption_input(plan_path, output_dir):
    """Bridge actual scene PCM and words to the paired-caption builder."""
    plan = read(plan_path)
    ko, _en, _spoken, script_files = scripts()
    split_record = read(NARRATION / "scene-split-review.json")
    timing = read(NARRATION / "source-scene-timings.json")
    scene_origins = {scene["id"]: (float(scene["voiceStartFrame"]) / 60 if "voiceStartFrame" in scene else float(scene["voiceStart"]))
                     for scene in plan["scenes"]}
    if [scene["id"] for scene in timing["scenes"]] != [scene["id"] for scene in ko["scenes"]] or set(scene_origins) != {scene["id"] for scene in ko["scenes"]}:
        raise ValueError("Caption plan, scripts and measured scene timing differ")
    if split_record["inputs"]["scripts"] != script_files:
        raise ValueError("Current script differs from the reviewed word alignment")
    paragraphs = []
    for scene in timing["scenes"]:
        audio_path = repo_path(scene["path"])
        source_asr = read(repo_path(scene["wordFile"]))
        if sha(audio_path) != scene["sha256"] or source_asr["audio_sha256"] != scene["sha256"]:
            raise ValueError("Current scene PCM no longer matches its derived ASR")
        rows = scene["paragraphs"]
        for index, paragraph in enumerate(rows):
            lower = (rows[index - 1]["end"] + paragraph["start"]) / 2 if index else -1
            upper = (paragraph["end"] + rows[index + 1]["start"]) / 2 if index + 1 < len(rows) else scene["duration"] + .001
            words = [word for word in source_asr["words"] if lower < word["timestamp"][1] <= upper]
            if not words:
                raise ValueError(f"No measured words for paragraph {scene['id']}/{index + 1}")
            # Whisper sometimes emits a zero-length leading fragment (e.g.
            # 'De' immediately before 'facto'). Retain all text by grouping it
            # with the following measured phrase, never inventing a new time.
            grouped, merges, pending = [], [], None
            for word in words:
                item = dict(word)
                begin, end = item["timestamp"]
                if end == begin:
                    if pending is not None:
                        raise ValueError("Consecutive zero-duration fragments require contextual review")
                    pending = item
                    continue
                if pending is not None:
                    if abs(pending["timestamp"][1] - begin) > .002:
                        raise ValueError("Untimed ASR fragment is not adjacent to a measured phrase")
                    merges.append({"fragment": pending, "following": item,
                                   "policy": "same measured phrase interval; complete text retained"})
                    item["text"] = pending["text"] + item["text"]
                    pending = None
                if grouped and begin < grouped[-1]["timestamp"][1] - .002:
                    previous = grouped.pop()
                    if begin < previous["timestamp"][0] or end < previous["timestamp"][0]:
                        raise ValueError("Reversed ASR phrase order requires contextual review")
                    merges.append({"overlapping": [previous, item],
                                   "policy": "group complete adjacent phrase in union of measured intervals; no invented word time"})
                    item = {"text": previous["text"] + item["text"],
                            "timestamp": [previous["timestamp"][0], max(previous["timestamp"][1], end)]}
                grouped.append(item)
            if pending is not None:
                raise ValueError("Trailing untimed fragment needs complete-context review")
            words = grouped
            paragraphs.append({"id": f"{scene['id']}-p{index + 1:02d}", "scene": scene["id"], "line": index,
                               "start": scene_origins[scene["id"]], "duration": scene["duration"],
                               "ko": paragraph["text"], "en": paragraph["english"], "words": words,
                               "audioFile": scene["path"], "audioFileSha256": scene["sha256"],
                               "wordSelection": "paragraph endpoint intervals from full-source script-matched ASR; timestamps retain scene origin",
                               "audioFileScope": "intact scene PCM; no extra paragraph extraction or ASR"})
            if merges:
                paragraphs[-1]["measuredPhraseGrouping"] = merges
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / "caption-input.json"
    save(destination, {"fps": 60, "scriptKo": relative(SCRIPT / "narration.ko.json"),
                       "scriptEn": relative(SCRIPT / "narration.en.json"), "paragraphs": paragraphs,
                       "aliases": plan.get("captionAliases", {}), "bodyEndFrame": int(plan["totalFrames"]) - int(plan.get("outroFrames", 600)),
                       "minCoverage": .93, "sourceSplitReviewSha256": sha(NARRATION / "scene-split-review.json"),
                       "measuredPlanSha256": sha(plan_path), "humanListening": "pending"})
    print(f"Prepared {len(paragraphs)} measured paragraphs for caption_pipeline.py: {relative(destination)}")


def loudness(path, log, target=-16, peak=-2.5):
    message = run_ff(["-i", path, "-af", f"loudnorm=I={target}:TP={peak}:LRA=11:print_format=json", "-f", "null", "-"], log)
    return json.loads(message[message.rfind("{"):message.rfind("}") + 1])


def finite_db(value, name):
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"Non-finite {name}; inspect speech rather than normalizing silence")
    return number


def loop_music(audio, required_samples, rate, crossfade_seconds=1):
    """Repeat only licensed background music, with equal-power joins."""
    if len(audio) <= 2 * rate:
        raise ValueError("Background music must exceed two seconds")
    if len(audio) >= required_samples:
        return audio[:required_samples].copy(), 0
    fade = min(round(crossfade_seconds * rate), len(audio) // 4)
    blend = np.linspace(0, np.pi / 2, fade, endpoint=True)
    output = audio.copy()
    joins = 0
    while len(output) < required_samples:
        crossing = output[-fade:] * np.cos(blend)[:, None] + audio[:fade] * np.sin(blend)[:, None]
        output = np.concatenate((output[:-fade], crossing, audio[fade:]))
        joins += 1
    return output[:required_samples], joins


def mix(plan_path, output_dir):
    plan = read(plan_path)
    ko, _en, _spoken, script_files = scripts()
    fps, frames = int(plan.get("fps", 60)), int(plan["totalFrames"])
    if fps != 60 or frames <= 0:
        raise ValueError("Current long-form audio requires a measured 60fps plan")
    if [scene["id"] for scene in plan["scenes"]] != [scene["id"] for scene in ko["scenes"]]:
        raise ValueError("Measured edit plan scene order differs from the current script")
    settings = plan.get("audio", {})
    split_receipt = read(NARRATION / "scene-split-review.json")
    for item in split_receipt["outputs"]:
        if sha(repo_path(item["path"])) != item["sha256"]:
            raise ValueError("A split PCM/timing input changed; preserve and review the correction")
    duration, count = frames / fps, frames * (RATE // fps)
    signature_inputs = {"plan": artifact(plan_path), "splitReceipt": artifact(NARRATION / "scene-split-review.json"),
                        "scripts": script_files, "audioSettings": settings, "pipelineSha256": sha(Path(__file__))}
    if settings.get("music"):
        music = settings["music"]
        music_path = repo_path(music["path"])
        if sha(music_path) != music["sha256"].lower() or not repo_path(music["licenseRecord"]).is_file():
            raise ValueError("Music bytes/license record do not match the measured plan")
        signature_inputs["music"] = artifact(music_path)
        signature_inputs["musicLicense"] = artifact(repo_path(music["licenseRecord"]))
    signature = canonical_signature(signature_inputs)
    receipt_path = output_dir / "audio-build.json"
    if output_cache(receipt_path, signature):
        print("Reusing unchanged measured mix")
        return
    output_dir.mkdir(parents=True, exist_ok=True)
    names = ("narration-timed.wav", "narration-stem.wav", "game-stem.wav", "music-stem.wav", "final-mix.wav", "final-mix.m4a")
    require_new(*(output_dir / name for name in names))
    voice, occupied, reports = np.zeros(count, np.float32), np.zeros(count, bool), []
    intro = int(plan.get("introFrames", 120))
    outro = int(plan.get("outroFrames", 600))
    if intro < 0 or outro < 0 or intro + outro >= frames:
        raise ValueError("Invalid branding/membership timing")
    for scene in plan["scenes"]:
        path = NARRATION / "chunks" / f"{scene['id']}-scene.wav"
        recognition = read(NARRATION / "asr" / f"{scene['id']}.json")
        if sha(path) != recognition["audio_sha256"]:
            raise ValueError("Stale scene ASR/chunk")
        audio, rate = sf.read(path, dtype="float32")
        if rate != RATE or audio.ndim != 1:
            raise ValueError("Expected mono24k scene source")
        start_seconds = float(scene["voiceStartFrame"]) / fps if "voiceStartFrame" in scene else float(scene["voiceStart"])
        start, end = round(start_seconds * rate), round(start_seconds * rate) + len(audio)
        if abs(start / rate - start_seconds) > .51 / rate:
            raise ValueError("Voice placement is not sample-aligned")
        if start < intro * (RATE // fps) or end > (frames - outro) * (RATE // fps):
            raise ValueError("Voice intrudes into branding/membership or exceeds the output")
        if start < int(scene["startFrame"]) * (RATE // fps) or end > int(scene["endFrame"]) * (RATE // fps):
            raise ValueError(f"Full unchanged source PCM does not fit scene {scene['id']}; extend its timing")
        if occupied[start:end].any():
            raise ValueError("Narration scene placements overlap")
        speech = mask_words(len(audio), rate, recognition["words"])
        if not speech.any():
            raise ValueError("Scene has no timestamped speech for continuity measurement")
        level = db(rms(audio[speech]))
        gain_db = float(settings.get("sceneSpeechRmsDbfs", -20)) - level if settings.get("matchSceneRms", False) else 0.0
        scaled = audio * np.float32(10 ** (gain_db / 20))
        voice[start:end] = scaled
        occupied[start:end] = True
        windows = []
        for index in range(0, len(audio), rate // 2):
            active = speech[index:index + rate]
            if active.sum() >= rate // 4:
                values = audio[index:index + rate][active]
                windows.append({"sceneLocalStart": index / rate, "timelineStart": start_seconds + index / rate,
                                "sourceSpeechDbfs": db(rms(values)), "afterFixedGainDbfs": db(rms(values)) + gain_db})
        reports.append({"scene": scene["id"], "sourceSha256": sha(path), "sourceSamples": len(audio),
                        "voiceStartSample": start, "voiceEndSample": end, "sourceSpeechRmsDbfs": level,
                        "fixedGainDb": gain_db, "windows": windows, "sourcePcmOverwritten": False,
                        "voiceFades": False, "timeStretch": False})
    timed = output_dir / "narration-timed.wav"
    sf.write(timed, voice, RATE, subtype="FLOAT")
    if not np.array_equal(sf.read(timed, dtype="float32")[0], voice):
        raise ValueError("Timed float narration changed samples")
    target, peak = float(settings.get("targetLufs", -16)), float(settings.get("voicePeakDbfs", -2.5))
    if not -24 <= target <= -12 or not -6 <= peak <= -1:
        raise ValueError("Narration level/peak target outside the supported production range")
    measured = loudness(timed, output_dir / "voice-measure.log", target, peak)
    global_gain = target - finite_db(measured["input_i"], "source integrated loudness")
    finite_db(measured["input_tp"], "source peak")
    limiter_ceiling = 10 ** (peak / 20)
    # loudnorm is measurement-only on the voice bus. A constant gain and short
    # peak limiter avoid seconds-long adaptive attenuation of quiet sentences.
    voice_filter = (f"volume={global_gain}dB:precision=double,alimiter=limit={limiter_ceiling}:attack=5:release=50:"
                    "level=false:latency=true,pan=stereo|c0=c0|c1=c0")
    stem = output_dir / "narration-stem.wav"
    run_ff(["-i", timed, "-af", voice_filter, "-ar", 48000, "-c:a", "pcm_s24le", stem], output_dir / "voice-stem.log")
    rate, stereo_count = 48000, frames * 800
    game, game_reports = np.zeros((stereo_count, 2), np.float32), []
    if settings.get("preserveGameAudio", True):
        for cut in plan.get("cuts", []):
            if cut.get("kind") != "independent-gameplay" or cut.get("sourceAudioEnabled") is not True:
                continue
            source = repo_path(cut["sourceFile"])
            if sha(source) != cut["sourceSha256"].lower():
                raise ValueError(f"Gameplay audio source missing/changed: {cut['id']}")
            source_start, cut_duration = float(cut["sourceStart"]), int(cut["frames"]) / fps
            extracted = output_dir / "game-cuts" / (cut["id"] + ".wav")
            extracted.parent.mkdir(exist_ok=True)
            require_new(extracted)
            run_ff(["-ss", source_start, "-i", source, "-t", cut_duration, "-vn", "-ar", rate,
                    "-ac", 2, "-c:a", "pcm_f32le", extracted], extracted.with_suffix(".log"))
            audio, decoded_rate = sf.read(extracted, dtype="float32", always_2d=True)
            expected_count = int(cut["frames"]) * 800
            if decoded_rate != rate or len(audio) < expected_count - 1:
                raise ValueError("Gameplay audio is shorter than its verified cut")
            audio = audio[:expected_count]
            level = rms(audio)
            gain = min(1.0, 10 ** (float(settings.get("gameRmsDbfs", -33)) / 20) / max(level, 1e-12))
            audio *= gain
            fade = min(960, len(audio) // 2)
            audio[:fade] *= np.linspace(0, 1, fade)[:, None]
            audio[-fade:] *= np.linspace(1, 0, fade)[:, None]
            start = int(cut["startFrame"]) * 800
            if start < 0 or start + len(audio) > stereo_count:
                raise ValueError("Gameplay audio placement exceeds final timeline")
            game[start:start + len(audio)] += audio
            game_reports.append({"cut": cut["id"], "source": artifact(source), "sourceRmsDbfs": db(level),
                                 "constantGainDb": db(gain), "cutEdgeFadeMs": 20, "retainedOriginalAudio": True})
    game_path = output_dir / "game-stem.wav"
    sf.write(game_path, game, rate, subtype="PCM_24")
    music_path, music_report = output_dir / "music-stem.wav", {"configured": False, "fallbackUsed": False}
    if settings.get("music"):
        music = settings["music"]
        decoded = output_dir / "music-source-decoded.wav"
        run_ff(["-i", repo_path(music["path"]), "-vn", "-ar", rate, "-ac", 2, "-c:a", "pcm_f32le", decoded], output_dir / "music-decode.log")
        source_audio, music_rate = sf.read(decoded, dtype="float32", always_2d=True)
        if music_rate != rate or not np.isfinite(source_audio).all():
            raise ValueError("Invalid decoded music")
        looped, joins = loop_music(source_audio, stereo_count, rate)
        continuous = output_dir / "music-continuous.wav"
        sf.write(continuous, looped, rate, subtype="FLOAT")
        music_level = float(settings.get("musicLufs", -31))
        if not -40 <= music_level <= -28:
            raise ValueError("Review the intended quiet background level")
        run_ff(["-i", continuous, "-af", f"loudnorm=I={music_level}:TP=-4:LRA=7,afade=t=in:st=0:d=1,afade=t=out:st={max(0, duration - 2)}:d=2",
                "-ar", rate, "-ac", 2, "-c:a", "pcm_s24le", music_path], output_dir / "music-level.log")
        music_report = {"configured": True, "source": artifact(repo_path(music["path"])), "title": music.get("title"),
                        "artist": music.get("artist"), "licenseRecord": artifact(repo_path(music["licenseRecord"])),
                        "initialLufs": music_level, "loopCrossfadeSeconds": 1, "loopJoins": joins, "fallbackUsed": False}
    else:
        sf.write(music_path, np.zeros((stereo_count, 2), np.float32), rate, subtype="PCM_24")
    final_wav, final_aac = output_dir / "final-mix.wav", output_dir / "final-mix.m4a"
    graph = ("[0:a]asplit=3[voice][side1][side2];[1:a][side1]sidechaincompress=threshold=0.025:ratio=3:attack=35:release=400[bg];"
             "[2:a][side2]sidechaincompress=threshold=0.035:ratio=2:attack=15:release=250[game];"
             "[voice][bg][game]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.794:level=false:latency=true[out]")
    run_ff(["-i", stem, "-i", music_path, "-i", game_path, "-filter_complex", graph, "-map", "[out]", "-t", duration,
            "-ar", rate, "-c:a", "pcm_s24le", final_wav], output_dir / "mix.log")
    run_ff(["-i", final_wav, "-c:a", "aac", "-b:a", "192k", final_aac], output_dir / "aac.log")
    final_stats = loudness(final_aac, output_dir / "final-aac-measure.log", target, -1.5)
    final_lufs, final_peak = finite_db(final_stats["input_i"], "final loudness"), finite_db(final_stats["input_tp"], "final peak")
    stem_audio, stem_rate = sf.read(stem, dtype="float32", always_2d=True)
    mixed_audio, mixed_rate = sf.read(final_wav, dtype="float32", always_2d=True)
    if stem_rate != rate or mixed_rate != rate or len(stem_audio) != stereo_count or len(mixed_audio) != stereo_count:
        raise ValueError("New narration/mix stem sample counts differ from the exact measured timeline")
    continuity_flags = []
    for report in reports:
        for window in report["windows"]:
            start, end = round(window["timelineStart"] * rate), min(stereo_count, round((window["timelineStart"] + 1) * rate))
            window["narrationStemRmsDbfs"] = db(rms(stem_audio[start:end]))
            window["predictedAfterConstantGainDbfs"] = window["afterFixedGainDbfs"] + global_gain
            # This broad whole-window estimate is diagnostic, not speech-active
            # proof or a substitute for final encoded matched-window review.
            window["roughStemDeltaDb"] = window["narrationStemRmsDbfs"] - window["predictedAfterConstantGainDbfs"]
            if window["roughStemDeltaDb"] < -4:
                continuity_flags.append({"scene": report["scene"], **window, "status": "needs aligned speech-active/contextual review"})
    outputs = [artifact(output_dir / name) for name in names]
    save(receipt_path, {"inputSignature": signature, "createdAt": now(), "inputs": signature_inputs, "outputs": outputs,
                       "frames": frames, "fps": fps, "duration": duration, "scenes": reports, "gameAudio": game_reports,
                       "music": music_report, "normalizationMeasurementOnly": measured,
                       "voiceGainMode": "constant-global-gain-with-short-peak-limiter",
                       "sceneMatchingEnabled": bool(settings.get("matchSceneRms", False)), "globalGainDb": global_gain,
                       "peakLimiter": {"ceilingDbfs": peak, "attackMs": 5, "releaseMs": 50, "autoMakeup": False},
                       "voiceDucked": False, "amixNormalize": False, "sourcePcmPreserved": True,
                       "finalAacMeasurement": final_stats, "levelTargetsMet": abs(final_lufs - target) <= 1 and final_peak <= -1.5,
                       "diagnosticContinuityFlags": continuity_flags,
                       "sourceToStemToEncodedContinuity": "pending aligned speech-active measurement and contextual review",
                       "fullFinalEncodedMixAsr": "pending", "humanWholeListening": "pending", "pronunciation": "pending"})
    print(f"Mixed {duration:.3f}s; measured {final_lufs:.2f}LUFS/{final_peak:.2f}dBTP; final ASR/continuity/listening remain pending")


def recognize_final(encoded_path, output_dir):
    if not (output_dir / "audio-build.json").is_file():
        raise ValueError("Complete the current measured mix before its encoded-audio ASR")
    audio_path, decode_receipt = output_dir / "encoded-audio-for-asr.wav", output_dir / "encoded-asr-input.json"
    inputs = {"encodedFile": artifact(encoded_path), "decode": "mono16000pcm_s16le", "audioBuild": artifact(output_dir / "audio-build.json")}
    signature = canonical_signature(inputs)
    if not output_cache(decode_receipt, signature):
        require_new(audio_path)
        run_ff(["-i", encoded_path, "-vn", "-ac", 1, "-ar", 16000, "-c:a", "pcm_s16le", audio_path], output_dir / "encoded-asr-decode.log")
        save(decode_receipt, {"inputSignature": signature, "inputs": inputs, "outputs": [artifact(audio_path)], "createdAt": now()})
    cache = output_dir / "final-mix-asr.json"
    full_asr(audio_path, cache, final=True)
    compare(cache, output_dir / "final-mix-text-comparison.json")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("stage", choices=("assemble", "recognize", "compare", "split", "caption-input", "mix", "recognize-final"))
    parser.add_argument("--raw-inputs", type=repo_path, default=LOCAL / "voice" / "raw-inputs.json")
    parser.add_argument("--review", type=repo_path)
    parser.add_argument("--boundary-overrides", type=repo_path)
    parser.add_argument("--plan", type=repo_path, default=Path(__file__).parent / "edit-plan.json")
    parser.add_argument("--output-dir", type=repo_path, default=LOCAL / "edit")
    parser.add_argument("--encoded-file", type=repo_path)
    args = parser.parse_args()
    args.output_dir.resolve().relative_to(LOCAL.resolve())
    if args.stage == "split" and not args.review:
        parser.error("split requires --review with the complete current ASR comparison record")
    if args.stage == "recognize-final" and not args.encoded_file:
        parser.error("recognize-final requires the actual current --encoded-file")
    with stage_lock(NARRATION, args.stage):
        if args.stage == "assemble":
            assemble(args.raw_inputs)
        elif args.stage == "recognize":
            assembly = read(NARRATION / "source-assembly.json")
            raw = NARRATION / "narration-source.wav"
            if sha(raw) != assembly["sha256"]:
                raise ValueError("Assembled audio changed since its receipt")
            full_asr(raw, NARRATION / "whole-source-asr.json")
            compare(NARRATION / "whole-source-asr.json", NARRATION / "whole-source-comparison.json")
        elif args.stage == "compare":
            compare(NARRATION / "whole-source-asr.json", NARRATION / "whole-source-comparison.json")
        elif args.stage == "split":
            split(args.review, args.boundary_overrides)
        elif args.stage == "caption-input":
            caption_input(args.plan, args.output_dir)
        elif args.stage == "mix":
            mix(args.plan, args.output_dir)
        elif args.stage == "recognize-final":
            recognize_final(args.encoded_file, args.output_dir)


if __name__ == "__main__":
    main()
