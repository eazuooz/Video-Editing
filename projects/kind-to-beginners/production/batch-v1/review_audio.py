"""Matched speech-active audio continuity review for the selected D22 revision.

    python review_audio.py --plan .../edit-plan.json --encoded ...captioned.mp4

Optional --edit-dir, --source-dir, --output-dir, --previous-report and
--export-contexts. Defaults follow sibling audio_pipeline.py. No ASR, model,
network, GPU, process/lease management, PCM repair or manifest mutation occurs.
Importing the module does no work. FFmpeg decoding/measurement uses CPU4.

The existing audio-build.json and every source PCM/ASR hash are authenticated.
Source -> timed narration is checked sample-for-sample with the declared fixed
scene gain. Source -> processed stem is compared with the declared global gain;
stem -> final WAV -> actual encoded audio uses speech-waveform projection,
including correlation, residual and uncertainty diagnostics. Mixed total RMS is
reported but cannot by itself pass or fail narration transfer.

Main windows:1s/250ms hop. Fine cadence windows:400ms/100ms. Paragraph/scene,
original-source joins, and game/explanation audio transitions also receive
60/100/150ms checks. All masks use existing ASR word timestamps, not a loudness
gate that could discard quiet syllables. A tiny constant resampling/AAC delay
is measured independently at several speech anchors and recorded; changing local
delays are flagged rather than time-warped away. No utterance is stretched.

Output qa/audio-continuity.json contains current input hashes/settings, exact
ranges and raw/processed/encoded levels, grouped flags with before/after values,
source cadence candidates, joins and optional previous-report comparisons.
--export-contexts additionally writes equal-playback-gain source-reference,
processed and encoded WAV contexts for bounded listening. Whole LUFS is auxiliary:
reuse the existing final AAC measurement only when actual audio packets match.

Flags require contextual review. Even a measurement pass leaves actual human
whole listening, pronunciation, source ASR meaning and final pixel QA pending.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
from storage_paths import repo_path as routed_repo_path, relative as routed_relative, write_path as routed_write_path
import shutil
import subprocess
import uuid

# Bound numerical libraries before importing them; never change another job.
os.environ["OMP_NUM_THREADS"] = "4"
os.environ["OPENBLAS_NUM_THREADS"] = "4"
os.environ["MKL_NUM_THREADS"] = "4"
import numpy as np
import soundfile as sf

from audio_pipeline import require_authorized, current_local_output, current_plan, audio_plan_contract

ROOT = Path(__file__).resolve().parents[4]
PROJECT = Path(__file__).resolve().parents[2]
REVISION = Path(__file__).resolve().parent.name
LOCAL = PROJECT / "production/local" / REVISION
NARRATION = LOCAL / "voice"
RATE = 48000
SETTINGS = {
    "sampleRate": RATE, "mainWindowSeconds": 1.0, "mainHopSeconds": .25,
    "fineWindowSeconds": .4, "fineHopSeconds": .1,
    "minimumMainSpeechSeconds": .25, "minimumFineSpeechSeconds": .10,
    "joinWindowsMs": [60, 100, 150], "sourceCadenceDropDb": 6.0,
    "sourceCadenceMinimumSeconds": .5, "sceneMedianDifferenceDb": 3.0,
    "sourceStemAttenuationDb": -3.0, "mixVoiceTransferDb": -2.5,
    "encodingTransferDb": -1.0, "joinIntroducedDropDb": 3.0,
    "alignmentSearchMs": 10, "alignmentAcceptedMs": 2.0,
    "alignmentDriftMs": 1.0, "minimumProjectionCorrelation": .6,
    "fullScaleClipThreshold": .9999,
    "diagnosticStereoDownmix": "Arithmetic channel average: normalize FFmpeg default equal-power stereo sum by1/sqrt(2); never change source PCM",
    "meaning": "Diagnostic starting criteria, not automatic perceptual approval or automatic repair",
}


def now():
    return datetime.now(timezone.utc).isoformat()


def path(value):
    return routed_repo_path(value)


def relative(p):
    return routed_relative(p)


def read(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))


def save(p, value):
    p = routed_write_path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    temporary = p.with_name(p.name + "." + uuid.uuid4().hex + ".writing")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, p)


def sha(p):
    digest = hashlib.sha256()
    with Path(p).open("rb") as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def artifact(p):
    p = Path(p)
    return {"path": relative(p), "sha256": sha(p), "bytes": p.stat().st_size}


def signature(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def tool(name):
    configured = os.environ.get("VIDEO_" + name.upper()) or os.environ.get(name.upper() + "_BINARY")
    candidates = [Path(configured)] if configured else []
    installed = shutil.which(name)
    if installed:
        candidates.append(Path(installed))
    winget = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/WinGet/Packages"
    if winget.is_dir():
        candidates += sorted(winget.glob("Gyan.FFmpeg*/ffmpeg*/bin/" + name + ".exe"))
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    raise FileNotFoundError(f"Set VIDEO_{name.upper()} to the installed executable")


def run_ff(arguments, log):
    process = subprocess.run([tool("ffmpeg"), "-hide_banner", "-nostdin", "-v", "info",
        "-threads", "4", "-filter_threads", "1", "-filter_complex_threads", "1", "-n",
        *map(str, arguments)], cwd=ROOT, capture_output=True,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    Path(log).parent.mkdir(parents=True, exist_ok=True)
    Path(log).write_bytes(process.stderr)
    if process.returncode:
        raise RuntimeError(process.stderr.decode("utf-8", errors="replace")[-4000:])
    return process.stderr.decode("utf-8", errors="replace")


def mono(p):
    values, rate = sf.read(p, dtype="float32", always_2d=True)
    if not len(values) or not np.isfinite(values).all():
        raise ValueError(f"Invalid finite PCM: {p}")
    return np.mean(values, axis=1, dtype=np.float32), rate


def cached_decode(p, cache, name):
    """One authenticated decode per changed file/settings, never a recognition."""
    source = artifact(p)
    target, receipt = cache / (name + ".wav"), cache / (name + ".json")
    inputs = {"source": source, "sampleRate": RATE, "channels": 1,
              "format": "pcm_f32le", "ffmpeg": tool("ffmpeg")}
    key = signature(inputs)
    # A validation-only tool repair changes the full review signature, not the
    # decoding input/settings. Reuse a separately authenticated prior decode
    # rather than repeat it under the new review-key directory.
    for prior_receipt in sorted(cache.parent.glob("*/" + name + ".json")):
        prior = read(prior_receipt)
        if prior.get("inputSignature") != key:
            continue
        prior_target = path(prior["output"]["path"])
        prior_target.relative_to(cache.parent.resolve())
        if prior_target.is_file() and sha(prior_target) == prior["output"]["sha256"]:
            return (*mono(prior_target), {**prior, "reusedExistingReceipt": relative(prior_receipt)})
    if receipt.exists():
        previous = read(receipt)
        if previous.get("inputSignature") == key and target.exists() and sha(target) == previous["output"]["sha256"]:
            return (*mono(target), previous)
        # Preserve existing diagnostics rather than replace a different output.
        target = cache / (name + "-" + key[:12] + ".wav")
        receipt = target.with_suffix(".json")
        if receipt.exists():
            previous = read(receipt)
            if previous.get("inputSignature") == key and target.exists() and sha(target) == previous["output"]["sha256"]:
                return (*mono(target), previous)
    if target.exists():
        raise FileExistsError(f"Preserve an unregistered diagnostic decode: {target}")
    cache.mkdir(parents=True, exist_ok=True)
    run_ff(["-i", p, "-map", "0:a:0", "-vn", "-ac", 1, "-ar", RATE,
            "-c:a", "pcm_f32le", target], target.with_suffix(".log"))
    result = {"inputSignature": key, "createdAt": now(), "inputs": inputs, "output": artifact(target),
              "scope": "PCM decoding for level comparison only; no ASR executed"}
    save(receipt, result)
    return (*mono(target), result)


def db(value):
    return float(20 * np.log10(max(float(value), 1e-12)))


def stereo_analysis_average(values, source, receipt):
    """Compare per-channel voice level, not the +3dB default stereo sum.

    All three diagnostic inputs are required to be true stereo. Their existing
    FFmpeg -ac1 decode uses equal-power coefficients sqrt(.5) per channel.
    Dividing that cached float waveform by sqrt(2) yields (L+R)/2 without a
    second full decode. A bounded explicit-pan calibration is kept in local QA.
    """
    info = json.loads(subprocess.check_output([tool("ffprobe"), "-v", "error",
        "-select_streams", "a:0", "-show_entries", "stream=channels,channel_layout",
        "-of", "json", str(source)], cwd=ROOT, text=True,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)))
    streams = info.get("streams", [])
    if len(streams) != 1 or streams[0].get("channels") != 2 or streams[0].get("channel_layout") != "stereo":
        raise ValueError("Inspect diagnostic downmix coefficients for a non-stereo source")
    factor = 1 / math.sqrt(2)
    return values * np.float32(factor), {**receipt, "analysisNormalization": {
        "sourceChannels": streams[0], "factor": factor, "gainDb": db(factor),
        "result": "Arithmetic average (L+R)/2; compare to original mono voice at declared gain",
        "cachedPcmOverwritten": False, "additionalFullDecode": False}}


def rms(values):
    if not len(values):
        return 0.0
    return float(np.sqrt(np.mean(np.asarray(values, dtype=np.float64) ** 2)))


def dot(a, b):
    """One-dimensional float64 inner product without optional native BLAS.

    The installed Windows BLAS delay-load fails on np.dot for these vectors.
    Elementwise multiplication/reduction is the same bounded calculation and
    avoids changing global DLL/runtime settings or another running job.
    """
    return float(np.sum(np.asarray(a, dtype=np.float64) * np.asarray(b, dtype=np.float64), dtype=np.float64))


def projection(reference, observed):
    """Estimate voice transfer; report uncertainty instead of calling it isolation.

    Ordinary projection is complemented by robust projection and 20ms block
    estimates. Background transients cannot be hidden by reporting total RMS.
    The uncertainty interval is diagnostic, not a statistical confidence claim
    about independent audio samples or a speech source-separation result.
    """
    x, y = np.asarray(reference, dtype=np.float64), np.asarray(observed, dtype=np.float64)
    energy = dot(x, x)
    if len(x) < 8 or energy < 1e-15:
        return {"gain": None, "gainDb": None, "ordinaryGainDb": None,
                "correlation": None, "residualDbfs": None, "uncertaintyDb": None,
                "usable": False, "reason": "Insufficient reference speech energy; no inferred gain"}
    ordinary = dot(x, y) / energy
    gain = ordinary
    for _ in range(3):
        residual = y - gain * x
        scale = float(np.median(np.abs(residual - np.median(residual))) * 1.4826)
        if scale < 1e-9:
            break
        weights = np.minimum(1.0, (2.5 * scale) / np.maximum(np.abs(residual), 1e-12))
        gain = dot(weights * x, y) / max(dot(weights * x, x), 1e-15)
    correlation = dot(x, y) / max(math.sqrt(dot(x, x) * dot(y, y)), 1e-15)
    block = round(.020 * RATE)
    gains = []
    for start in range(0, len(x) - block + 1, block):
        a, b = x[start:start + block], y[start:start + block]
        e = dot(a, a)
        if e > 1e-12:
            gains.append(dot(a, b) / e)
    uncertainty = None
    if len(gains) >= 3:
        scatter = 1.4826 * float(np.median(np.abs(np.asarray(gains) - np.median(gains))))
        # Serially correlated samples do not count as independent observations.
        uncertainty = float(20 / math.log(10) * 2 * scatter / max(abs(gain), 1e-6) / math.sqrt(len(gains)))
    usable = gain > 0 and correlation >= SETTINGS["minimumProjectionCorrelation"]
    return {"gain": gain, "gainDb": db(gain) if gain > 0 else None,
            "ordinaryGainDb": db(ordinary) if ordinary > 0 else None,
            "correlation": correlation, "residualDbfs": db(rms(y - gain * x)),
            "uncertaintyDb": uncertainty, "blockCount": len(gains), "usable": usable,
            "reason": "Estimated transfer of the known speech waveform; background remains additive"}


def intervals(words, duration):
    rows = []
    for word in words:
        a, b = word.get("timestamp", [word.get("start"), word.get("end")])
        if a is None or b is None:
            raise ValueError("Existing source ASR requires complete word timestamps")
        a, b = float(a), float(b)
        # Whisper can emit a token without measurable duration. Preserve its
        # original record, but do not invent a non-zero speech-active span.
        if 0 <= a == b <= duration:
            continue
        if not 0 <= a < b <= duration + .031:
            raise ValueError(f"ASR word outside its measured PCM: {a}--{b}/{duration}")
        rows.append((a, min(duration, b)))
    return rows


def speech_mask(count, spans):
    result = np.zeros(count, dtype=bool)
    for a, b in spans:
        result[max(0, round(a * RATE)):min(count, round(b * RATE))] = True
    return result


def aligned_piece(values, start, count, lag=0):
    # Positive lag means observed audio occurs later than the reference.
    left, right = start + lag, start + lag + count
    if left < 0 or right > len(values):
        raise ValueError("Aligned diagnostic interval leaves actual decoded PCM")
    return values[left:right]


def correlation_lag(reference, observed, center, mask):
    start = max(0, center - RATE // 4)
    count = min(RATE // 2, len(reference) - start)
    active = mask[start:start + count]
    if active.sum() < RATE * .15:
        return None
    x = reference[start:start + count][active].astype(np.float64)
    if rms(x) < 1e-6:
        return None
    search = round(SETTINGS["alignmentSearchMs"] / 1000 * RATE)
    # Coarse then exact sample refinement bounds work and records actual lag.
    candidates = range(-search, search + 1, 4)
    scored = []
    for lag in candidates:
        if start + lag < 0 or start + count + lag > len(observed):
            continue
        y = observed[start + lag:start + lag + count][active].astype(np.float64)
        score = dot(x, y) / max(math.sqrt(dot(x, x) * dot(y, y)), 1e-15)
        scored.append((score, lag))
    if not scored:
        return None
    _score, best = max(scored)
    refined = []
    for lag in range(max(-search, best - 4), min(search, best + 4) + 1):
        if start + lag < 0 or start + count + lag > len(observed):
            continue
        y = observed[start + lag:start + lag + count][active].astype(np.float64)
        score = dot(x, y) / max(math.sqrt(dot(x, x) * dot(y, y)), 1e-15)
        refined.append((score, lag))
    score, lag = max(refined)
    return {"time": center / RATE, "lagSamples": lag, "lagMs": lag / RATE * 1000,
            "correlation": score, "speechSamples": int(active.sum())}


def alignment(reference, observed, mask):
    # Choose one strong speech window in each timeline third, not one arbitrary
    # first syllable. Local drift cannot be repaired by fitting separate lags.
    anchors = []
    for third in range(3):
        a, b = len(reference) * third // 3, len(reference) * (third + 1) // 3
        candidates = []
        for center in range(max(a, RATE // 2), min(b, len(reference) - RATE // 2), RATE):
            active = mask[center - RATE // 4:center + RATE // 4]
            if active.sum() < RATE * .15:
                continue
            level = rms(reference[center - RATE // 4:center + RATE // 4][active])
            candidates.append((level, center))
        if candidates:
            anchor = correlation_lag(reference, observed, max(candidates)[1], mask)
            if anchor:
                anchors.append(anchor)
    if not anchors:
        raise ValueError("No existing ASR speech anchors available for aligned audio review")
    lag = round(float(np.median([x["lagSamples"] for x in anchors])))
    spread = max(x["lagSamples"] for x in anchors) - min(x["lagSamples"] for x in anchors)
    accepted = abs(lag) <= SETTINGS["alignmentAcceptedMs"] / 1000 * RATE and spread <= SETTINGS["alignmentDriftMs"] / 1000 * RATE
    return {"lagSamples": lag, "lagMs": lag / RATE * 1000, "anchors": anchors,
            "spreadMs": spread / RATE * 1000, "accepted": accepted,
            "timeWarped": False, "method": "One constant bounded resampling/AAC delay; three independent speech anchors"}


def measure_window(scene, local_start, seconds, source, timed, stem, mixed, encoded,
                   mask, origin, stem_lag, mix_lag, encoded_lag, expected_gain):
    a, count = round(local_start * RATE), round(seconds * RATE)
    count = min(count, len(source) - a)
    if a < 0 or count <= 0:
        return None
    active = mask[a:a + count]
    active_seconds = float(active.sum() / RATE)
    minimum = .025 if seconds <= .15 else SETTINGS["minimumFineSpeechSeconds"] if seconds < .5 else SETTINGS["minimumMainSpeechSeconds"]
    if active_seconds < minimum:
        return None
    start = origin + a
    x = source[a:a + count][active]
    t = aligned_piece(timed, start, count)[active]
    s = aligned_piece(stem, start, count, stem_lag)[active]
    m = aligned_piece(mixed, start, count, mix_lag)[active]
    z = aligned_piece(encoded, start, count, encoded_lag)[active]
    source_stem, stem_mix, stem_encoded, mix_encoded = projection(x, s), projection(s, m), projection(s, z), projection(m, z)
    transfer_delta = None
    if stem_encoded["gainDb"] is not None and stem_mix["gainDb"] is not None:
        transfer_delta = stem_encoded["gainDb"] - stem_mix["gainDb"]
    row = {"scene": scene, "localStart": local_start, "time": start / RATE,
           "end": (start + count) / RATE, "windowSeconds": count / RATE,
           "speechActiveSeconds": active_seconds, "speechActiveFraction": active_seconds / (count / RATE),
           "sourceDbfs": db(rms(x)), "timedDbfs": db(rms(t)), "stemDbfs": db(rms(s)),
           "finalWavTotalDbfs": db(rms(m)), "encodedTotalDbfs": db(rms(z)),
           "expectedConstantGainDb": expected_gain, "predictedStemDbfs": db(rms(x)) + expected_gain,
           "sourceToStem": source_stem, "stemToFinalWav": stem_mix,
           "stemToEncoded": stem_encoded, "finalWavToEncoded": mix_encoded,
           "sourceStemMinusExpectedDb": source_stem["gainDb"] - expected_gain if source_stem["gainDb"] is not None else None,
           "encodedMinusPreEncodeVoiceTransferDb": transfer_delta,
           "sourcePeakDbfs": db(np.max(np.abs(x))), "stemPeakDbfs": db(np.max(np.abs(s))),
           "encodedPeakDbfs": db(np.max(np.abs(z))),
           "encodedFullScaleClipSamples": int(np.count_nonzero(np.abs(z) >= SETTINGS["fullScaleClipThreshold"])),
           "mixedTotalRmsUsedAsVoiceVerdict": False}
    return row


def flag_rows(windows, *, short=False):
    results = []
    for row in windows:
        delta = row["sourceStemMinusExpectedDb"]
        reasons = []
        if delta is not None and delta < SETTINGS["sourceStemAttenuationDb"]:
            reasons.append("source-to-stem lower than declared constant gain; inspect limiter/fades")
        estimate = row["stemToEncoded"]
        if estimate["gainDb"] is not None and estimate["gainDb"] < SETTINGS["mixVoiceTransferDb"]:
            reasons.append("estimated encoded speech transfer decreased")
        change = row["encodedMinusPreEncodeVoiceTransferDb"]
        if change is not None and change < SETTINGS["encodingTransferDb"]:
            reasons.append("encoded speech transfer lower than pre-encode mix")
        if row["encodedFullScaleClipSamples"]:
            reasons.append("decoded full-scale speech samples; inspect clipping")
        if not estimate["usable"] and row["stemDbfs"] > -55:
            reasons.append("background/noise or attenuation prevents a reliable voice projection")
        if reasons:
            results.append({"scene": row["scene"], "start": row["time"], "end": row["end"],
                "localStart": row["localStart"], "reasons": reasons, "measurements": row,
                "status": "pending-contextual-review", "rangeType": "60–150ms join" if short else "speech-active window"})
    return results


def group_flags(flags):
    groups = []
    for item in sorted(flags, key=lambda x: (x["start"], x["end"])):
        if groups and item["start"] <= groups[-1]["end"] + .025:
            group = groups[-1]
            group["end"] = max(group["end"], item["end"])
            group["scenes"] = sorted(set(group["scenes"] + [item["scene"]]))
            group["reasons"] = sorted(set(group["reasons"] + item["reasons"]))
            group["windows"].append(item)
        else:
            groups.append({"id": f"audio-flag-{len(groups) + 1:03}", "start": item["start"], "end": item["end"],
                "scenes": [item["scene"]], "reasons": item["reasons"], "windows": [item],
                "status": "pending-contextual-review", "before": "Current source PCM and declared constant gain",
                "after": "Current processed stem, final WAV and actual encoded audio",
                "correctedAfter": "No correction performed by this read-only reviewer"})
    return groups


def source_cadence(windows):
    candidates = []
    for scene in sorted(set(x["scene"] for x in windows)):
        local = [x for x in windows if x["scene"] == scene]
        flagged = []
        for row in local:
            neighbours = [x["sourceDbfs"] for x in local if .5 <= abs(x["time"] - row["time"]) <= 3]
            if len(neighbours) < 4:
                continue
            baseline = float(np.median(neighbours))
            if baseline - row["sourceDbfs"] >= SETTINGS["sourceCadenceDropDb"]:
                flagged.append({"time": row["time"], "end": row["end"], "sourceDbfs": row["sourceDbfs"],
                                "localBaselineDbfs": baseline, "dropDb": baseline - row["sourceDbfs"]})
        runs = []
        for row in flagged:
            if runs and row["time"] - runs[-1][-1]["time"] <= .151:
                runs[-1].append(row)
            else:
                runs.append([row])
        for run in runs:
            # Consecutive window STARTS, not one isolated400ms window's extent,
            # must span>=.5sec so natural short word tails are not overcounted.
            if run[-1]["time"] - run[0]["time"] + SETTINGS["fineHopSeconds"] >= SETTINGS["sourceCadenceMinimumSeconds"]:
                candidates.append({"scene": scene, "start": run[0]["time"], "end": run[-1]["end"],
                    "windows": run, "origin": "Already present in current source PCM; not attributed to mixing",
                    "status": "pending contextual listening; could be natural prosody or a source voice issue"})
    return candidates


def source_edges(sources):
    """Retain quiet tails; diagnose an actual hard PCM edge near speech."""
    rows, candidates = [], []
    for sid, values in sources.items():
        pcm, mask, origin = values["pcm"], values["mask"], values["origin"]
        for side in ("start", "end"):
            edge = float(abs(pcm[0] if side == "start" else pcm[-1]))
            measured = []
            for ms in SETTINGS["joinWindowsMs"]:
                count = min(len(pcm), round(ms / 1000 * RATE))
                segment = pcm[:count] if side == "start" else pcm[-count:]
                active = mask[:count] if side == "start" else mask[-count:]
                measured.append({"windowMs": ms, "sourceTotalDbfs": db(rms(segment)),
                    "sourceSpeechDbfs": db(rms(segment[active])) if active.any() else None,
                    "speechActiveMs": float(active.sum() / RATE * 1000)})
            t = origin / RATE if side == "start" else (origin + len(pcm)) / RATE
            candidate = edge > .02 and measured[-1]["speechActiveMs"] >= 25
            row = {"scene": sid, "edge": side, "time": t, "sourceEndpointAbsoluteAmplitude": edge,
                   "nearby60to150ms": measured, "candidate": candidate,
                   "meaning": "A hard PCM boundary near source speech may need click/clipped-syllable listening; sample preservation prevents blaming a later fade"}
            rows.append(row)
            if candidate:
                candidates.append({"scene": sid, "start": max(origin / RATE, t - .15),
                    "end": min((origin + len(pcm)) / RATE, t + .15),
                    "localStart": max(0, t - .15 - origin / RATE),
                    "reasons": ["Current source speech approaches a hard PCM edge; inspect a click or clipped syllable"],
                    "measurements": row, "status": "pending-contextual-review", "rangeType": "source PCM edge"})
    return rows, candidates


def audio_packet_hash(p):
    return subprocess.check_output([tool("ffmpeg"), "-v", "error", "-threads", "4", "-i", str(p),
        "-map", "0:a:0", "-c", "copy", "-f", "hash", "-hash", "sha256", "-"], cwd=ROOT, text=True).strip()


def whole_loudness(encoded, edit, build, cache):
    actual_packets = audio_packet_hash(encoded)
    reference = edit / "final-mix.m4a"
    if reference.exists() and build.get("finalAacMeasurement") and audio_packet_hash(reference) == actual_packets:
        return {"status": "reused identical encoded AAC packets", "audioPacketsSha256": actual_packets,
                "measurement": build["finalAacMeasurement"], "source": relative(edit / "audio-build.json"),
                "role": "Auxiliary whole-file loudness, not local speech continuity proof"}
    receipt = cache / "encoded-loudness.json"
    key = {"encodedSha256": sha(encoded), "audioPacketsSha256": actual_packets, "filter": "loudnorm measurement only"}
    if receipt.exists() and read(receipt).get("inputs") == key:
        return read(receipt)
    text = run_ff(["-i", encoded, "-map", "0:a:0", "-vn", "-af", "loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json",
                   "-f", "null", "-"], cache / "encoded-loudness.log")
    stats = json.loads(text[text.rfind("{"):text.rfind("}") + 1])
    result = {"inputs": key, "measurement": stats, "status": "measured actual encoded audio once",
              "role": "Auxiliary whole-file loudness, not local speech continuity proof"}
    save(receipt, result)
    return result


def previous_comparison(previous, current, current_sources):
    if not previous:
        return {"status": "No earlier correction report supplied; this is the first current measurement"}
    old = read(previous)
    lookup = {(x["scene"], round(x["localStart"], 3)): x for x in old.get("windows", [])}
    old_hashes = {x["scene"]: x["pcm"]["sha256"] for x in old.get("inputs", {}).get("sourceScenes", [])}
    new_hashes = {x["scene"]: x["pcm"]["sha256"] for x in current_sources}
    comparisons, incompatible = [], []
    for row in current:
        match = lookup.get((row["scene"], round(row["localStart"], 3)))
        if not match:
            continue
        if old_hashes.get(row["scene"]) != new_hashes.get(row["scene"]):
            incompatible.append({"scene": row["scene"], "localStart": row["localStart"],
                                 "reason": "Source PCM changed; do not compare as an unchanged utterance"})
            continue
        comparisons.append({"scene": row["scene"], "localStart": row["localStart"],
            "before": {"timelineStart": match["time"], "sourceStemMinusExpectedDb": match.get("sourceStemMinusExpectedDb"),
                       "estimatedVoiceTransferDb": match.get("stemToEncoded", {}).get("gainDb")},
            "after": {"timelineStart": row["time"], "sourceStemMinusExpectedDb": row["sourceStemMinusExpectedDb"],
                      "estimatedVoiceTransferDb": row["stemToEncoded"]["gainDb"]}})
    return {"status": "Before/after matched by unchanged source hash, scene and source-local interval",
            "previousReport": artifact(previous), "windows": comparisons, "incompatibleSourceWindows": incompatible}


def export_contexts(groups, cadence, cache, reference, stem, encoded, stem_lag, encoded_lag):
    requested = [{"id": g["id"], "start": g["start"], "end": g["end"], "type": "transfer"} for g in groups]
    requested += [{"id": f"source-cadence-{i + 1:03}", "start": g["start"], "end": g["end"], "type": "source cadence"}
                  for i, g in enumerate(cadence)]
    outputs = []
    for item in requested:
        lower = max(0, -stem_lag, -encoded_lag) / RATE
        upper = min(len(reference), len(stem) - stem_lag, len(encoded) - encoded_lag) / RATE
        start, end = max(lower, item["start"] - 2.5), min(upper, item["end"] + 2.5)
        a, b = round(start * RATE), round(end * RATE)
        folder = cache / "contexts" / item["id"]
        folder.mkdir(parents=True, exist_ok=True)
        files = []
        for name, values, lag in (("source-at-declared-gain", reference, 0), ("processed-stem", stem, stem_lag),
                                  ("actual-encoded", encoded, encoded_lag)):
            data = aligned_piece(values, a, b - a, lag)
            target = folder / (name + ".wav")
            if not target.exists():
                sf.write(target, data, RATE, subtype="FLOAT")
            files.append({**artifact(target), "peakDbfs": db(np.max(np.abs(data))),
                          "normalization": "None; same playback volume required"})
        outputs.append({**item, "contextStart": start, "contextEnd": end, "files": files,
                        "listenedByHuman": False})
    return outputs


def review(args):
    require_authorized("review-audio")
    plan_file, encoded = current_plan(args.plan), path(args.encoded)
    plan = read(plan_file)
    if plan.get("fps") != 60:
        raise ValueError("Expected the actual measured60fps edit plan")
    edit = current_local_output(args.edit_dir or plan.get("outputDir", str(LOCAL / "edit")))
    output = current_local_output(args.output_dir or str(edit / "qa"))
    source_dir = path(args.source_dir or str(NARRATION))
    source_dir.relative_to(NARRATION.resolve())
    build_file = edit / "audio-build.json"
    build = read(build_file)
    if build.get("inputs", {}).get("plan", {}).get("sha256") != sha(plan_file):
        if build.get("inputs", {}).get("audioPlanContract") != audio_plan_contract(plan):
            raise ValueError("Current audio-build audio dependencies differ from the measured edit plan")
    if build.get("voiceGainMode") != "constant-global-gain-with-short-peak-limiter" or build.get("voiceDucked") is not False or build.get("amixNormalize") is not False:
        raise ValueError("Inspect current voice processing; expected constant gain, voice not ducked, amix normalize0")
    for item in build["outputs"]:
        if sha(path(item["path"])) != item["sha256"]:
            raise ValueError(f"Current recorded audio stem changed: {item['path']}")
    source_records = []
    for scene in plan["scenes"]:
        sid = str(scene["id"])
        pcm, asr = source_dir / "chunks" / (sid + "-scene.wav"), source_dir / "asr" / (sid + ".json")
        recognition = read(asr)
        if recognition.get("audio_sha256") != sha(pcm):
            raise ValueError(f"Stale existing PCM/ASR cache: {sid}")
        source_records.append({"scene": sid, "pcm": artifact(pcm), "asr": artifact(asr)})
    timing_file = source_dir / "source-scene-timings.json"
    if not timing_file.exists():
        raise FileNotFoundError("Existing paragraph timing is required; this reviewer never generates ASR")
    previous = path(args.previous_report) if args.previous_report else None
    assembly_file = source_dir / "source-assembly.json"
    inputs = {"plan": artifact(plan_file), "audioBuild": artifact(build_file), "encoded": artifact(encoded),
              "sourceScenes": source_records, "sourceTimings": artifact(timing_file),
              "rawSourceAssembly": artifact(assembly_file) if assembly_file.exists() else None,
              "codeSha256": sha(Path(__file__)), "settings": SETTINGS,
              "previousReport": artifact(previous) if previous else None,
              "exportContexts": bool(args.export_contexts)}
    key, destination = signature(inputs), output / "audio-continuity.json"
    if destination.exists() and read(destination).get("inputSignature") == key:
        print("Reusing identical current source/stem/encoded continuity evidence; no decode, ASR or measurement repeated")
        return read(destination)
    if destination.exists():
        prior = read(destination)
        archive = output / ("audio-continuity-previous-" + prior.get("inputSignature", sha(destination))[:12] + ".json")
        if not archive.exists():
            shutil.copy2(destination, archive)
    cache = output / "audio-review-cache" / key[:12]
    cache.mkdir(parents=True, exist_ok=True)
    timed, rate = mono(edit / "narration-timed.wav")
    if rate != RATE:
        raise ValueError("Timed narration must preserve the original mono48k scene clock")
    stem, stem_rate, stem_decode = cached_decode(edit / "narration-stem.wav", cache, "narration-stem48k")
    mixed, mixed_rate, mixed_decode = cached_decode(edit / "final-mix.wav", cache, "pre-encode-mix48k")
    final, final_rate, encoded_decode = cached_decode(encoded, cache, "actual-encoded48k")
    stem, stem_decode = stereo_analysis_average(stem, edit / "narration-stem.wav", stem_decode)
    mixed, mixed_decode = stereo_analysis_average(mixed, edit / "final-mix.wav", mixed_decode)
    final, encoded_decode = stereo_analysis_average(final, encoded, encoded_decode)
    expected_count = round(plan["totalFrames"] / 60 * RATE)
    if any(r != RATE for r in (stem_rate, mixed_rate, final_rate)) or len(timed) != expected_count or len(stem) != expected_count or len(mixed) != expected_count:
        raise ValueError("Processed stems do not match the actual measured timeline")
    # Pipeline AAC is48kHz/1024samples per packet. Bound at most one codec
    # packet at the current diagnostic rate, plus one quantization sample.
    if abs(len(final) - expected_count) > math.ceil(1024 * RATE / 48000) + 1:
        raise ValueError("Actual encoded audio duration differs beyond one AAC frame")
    timeline_mask, expected_reference = np.zeros(expected_count, bool), np.zeros(expected_count, np.float32)
    sources, sample_proofs, zero_duration_tokens = {}, [], []
    build_scenes = {str(s["scene"]): s for s in build["scenes"]}
    for scene, identity in zip(plan["scenes"], source_records):
        sid = str(scene["id"])
        values, rate = mono(path(identity["pcm"]["path"]))
        if rate != RATE:
            raise ValueError("Expected unchanged source48k PCM")
        recognition = read(path(identity["asr"]["path"]))
        spans = intervals(recognition["words"], len(values) / RATE)
        for index, word in enumerate(recognition["words"]):
            a, b = word.get("timestamp", [word.get("start"), word.get("end")])
            if a is not None and b is not None and 0 <= float(a) == float(b) <= len(values) / RATE:
                zero_duration_tokens.append({"scene": sid, "wordIndex": index,
                    "originalWord": word, "asrSha256": identity["asr"]["sha256"],
                    "pcmSha256": identity["pcm"]["sha256"], "speechMaskAddedSamples": 0,
                    "reason": "Zero-duration ASR token inside valid PCM contributes zero measured area; original token and PCM unchanged"})
        active = speech_mask(len(values), spans)
        origin_seconds = float(scene["voiceStartFrame"]) / 60 if "voiceStartFrame" in scene else float(scene["voiceStart"])
        origin = round(origin_seconds * RATE)
        if origin < 0 or origin + len(values) > expected_count:
            raise ValueError("Current source placement leaves exact timeline")
        report = build_scenes[sid]
        if report.get("sourceSha256") != identity["pcm"]["sha256"] or report["voiceStartSample"] != origin:
            raise ValueError("Source gain/placement report differs from current source/plan")
        scene_gain, global_gain = float(report["fixedGainDb"]), float(build["globalGainDb"])
        applied = values * np.float32(10 ** (scene_gain / 20))
        existing = timed[origin:origin + len(values)]
        maximum_error = float(np.max(np.abs(applied - existing)))
        exact = bool(np.array_equal(applied, existing))
        if not exact:
            raise ValueError(f"Timed narration changed approved PCM beyond declared constant gain: {sid}, maxerror{maximum_error}")
        expected_reference[origin:origin + len(values)] = applied * np.float32(10 ** (global_gain / 20))
        timeline_mask[origin:origin + len(values)] |= active
        sample_proofs.append({"scene": sid, "sourceSha256": identity["pcm"]["sha256"],
            "voiceStart": origin_seconds, "samples": len(values), "fixedSceneGainDb": scene_gain,
            "exactSourceSamplesAfterDeclaredGain": exact, "maximumAbsoluteError": maximum_error,
            "speechFadeAddedBeforeProcessing": False, "timeStretch": False})
        sources[sid] = {"pcm": values, "mask": active, "spans": spans, "origin": origin,
                        "expectedGainDb": scene_gain + global_gain}
    alignments = {"sourceToStem": alignment(expected_reference, stem, timeline_mask),
                  "stemToPreEncodeMix": alignment(stem, mixed, timeline_mask),
                  "stemToEncoded": alignment(stem, final, timeline_mask)}
    stem_lag = alignments["sourceToStem"]["lagSamples"]
    # The stem itself is the reference for mix/encoded lag, therefore add its
    # bounded source alignment when addressing global source-clock windows.
    mix_lag = stem_lag + alignments["stemToPreEncodeMix"]["lagSamples"]
    final_lag = stem_lag + alignments["stemToEncoded"]["lagSamples"]
    windows, fine, summaries = [], [], []
    for scene in plan["scenes"]:
        sid, values = str(scene["id"]), sources[str(scene["id"])]
        common = (sid, values["pcm"], values["mask"], values["origin"], values["expectedGainDb"])
        def window(t, width):
            return measure_window(common[0], t, width, common[1], timed, stem, mixed, final,
                                  common[2], common[3], stem_lag, mix_lag, final_lag, common[4])
        duration = len(values["pcm"]) / RATE
        local = []
        for step in range(math.ceil(duration / SETTINGS["mainHopSeconds"])):
            row = window(step * SETTINGS["mainHopSeconds"], SETTINGS["mainWindowSeconds"])
            if row:
                windows.append(row)
                local.append(row)
        # Fine cadence scanning needs source/stem levels, not a second expensive
        # projection scan. Main and boundary windows already compare the mix.
        for step in range(math.ceil(duration / SETTINGS["fineHopSeconds"])):
            local_start = step * SETTINGS["fineHopSeconds"]
            a = round(local_start * RATE)
            count = min(round(SETTINGS["fineWindowSeconds"] * RATE), len(values["pcm"]) - a)
            active = values["mask"][a:a + count]
            if active.sum() < SETTINGS["minimumFineSpeechSeconds"] * RATE:
                continue
            start = values["origin"] + a
            fine.append({"scene": sid, "localStart": local_start, "time": start / RATE,
                         "end": (start + count) / RATE, "speechActiveSeconds": float(active.sum() / RATE),
                         "sourceDbfs": db(rms(values["pcm"][a:a + count][active])),
                         "stemDbfs": db(rms(aligned_piece(stem, start, count, stem_lag)[active]))})
        if not local:
            raise ValueError(f"No meaningful speech-active measurement windows: {sid}")
        summaries.append({"scene": sid, "speechWindows": len(local),
            "sourceMedianDbfs": float(np.median([x["sourceDbfs"] for x in local])),
            "stemMedianDbfs": float(np.median([x["stemDbfs"] for x in local])),
            "expectedConstantGainDb": values["expectedGainDb"],
            "minimumSourceStemMinusExpectedDb": min(x["sourceStemMinusExpectedDb"] for x in local if x["sourceStemMinusExpectedDb"] is not None),
            "minimumEstimatedVoiceTransferDb": min(x["stemToEncoded"]["gainDb"] for x in local if x["stemToEncoded"]["gainDb"] is not None)})
    timings = {str(s["id"]): s for s in read(timing_file)["scenes"]}
    boundaries = []
    for scene in plan["scenes"]:
        sid, values = str(scene["id"]), sources[str(scene["id"])]
        begin, finish = values["origin"] / RATE, (values["origin"] + len(values["pcm"])) / RATE
        boundaries += [{"kind": "scene voice start", "time": begin, "scene": sid},
                       {"kind": "scene voice end", "time": finish, "scene": sid}]
        for paragraph in timings[sid].get("paragraphs", []):
            for edge in ("start", "end"):
                boundaries.append({"kind": "paragraph " + edge, "time": begin + float(paragraph[edge]),
                                   "scene": sid, "paragraph": paragraph.get("paragraph")})
        for cut in plan.get("cuts", []):
            t = cut["startFrame"] / 60
            if begin < t < finish:
                boundaries.append({"kind": "game/explanation source cut", "time": t, "scene": sid, "cut": cut["id"]})
    # Explicitly map original input-file joins through split source samples;
    # a raw input join need not coincide with a paragraph or scene boundary.
    raw_assembly = artifact(assembly_file) if assembly_file.exists() else None
    if assembly_file.exists():
        placements = read(assembly_file).get("placements", [])
        for previous_placement, next_placement in zip(placements, placements[1:]):
            for sample, edge in ((previous_placement["endSample"], "previous file end"),
                                 (next_placement["startSample"], "next file start")):
                for sid, timing in timings.items():
                    if timing["startSample"] <= sample <= timing["endSample"]:
                        boundaries.append({"kind": "raw source join: " + edge, "scene": sid,
                            "time": (sources[sid]["origin"] + sample - timing["startSample"]) / RATE,
                            "sourceAssemblySample": sample})
    joins, short_flags = [], []
    seen = set()
    for boundary in boundaries:
        identity = (boundary["kind"], boundary["scene"], round(boundary["time"], 5))
        if identity in seen:
            continue
        seen.add(identity)
        values = sources[boundary["scene"]]
        local_time = boundary["time"] - values["origin"] / RATE
        checks = []
        for ms in SETTINGS["joinWindowsMs"]:
            width = ms / 1000
            pair = {}
            for side, at in (("before", local_time - width), ("after", local_time)):
                if at < 0 or at + width > len(values["pcm"]) / RATE + 1e-8:
                    pair[side] = None
                    continue
                pair[side] = measure_window(boundary["scene"], at, width, values["pcm"], timed, stem,
                    mixed, final, values["mask"], values["origin"], stem_lag, mix_lag, final_lag, values["expectedGainDb"])
            introduced_delta = None
            if pair["before"] and pair["after"]:
                a, b = pair["before"]["sourceStemMinusExpectedDb"], pair["after"]["sourceStemMinusExpectedDb"]
                if a is not None and b is not None:
                    introduced_delta = b - a
            if introduced_delta is not None and introduced_delta < -SETTINGS["joinIntroducedDropDb"]:
                item = pair["after"]
                short_flags.append({"scene": boundary["scene"], "start": item["time"], "end": item["end"],
                    "localStart": item["localStart"], "reasons": ["introduced60–150ms attenuation at a speech-active boundary"],
                    "measurements": item, "status": "pending-contextual-review", "rangeType": "join"})
            for row in pair.values():
                if row:
                    short_flags.extend(flag_rows([row], short=True))
            checks.append({"windowMs": ms, **pair, "introducedSourceToStemGainChangeDb": introduced_delta})
        join_sample = round(boundary["time"] * RATE)
        jumps = {}
        for name, signal, lag in (("timed", timed, 0), ("stem", stem, stem_lag), ("encoded", final, final_lag)):
            i = join_sample + lag
            jumps[name] = float(abs(signal[i] - signal[i - 1])) if 0 < i < len(signal) else None
        joins.append({**boundary, "checks": checks, "waveformOneSampleJump": jumps,
                      "sourceSpeechPreservedBeforeProcessing": True,
                      "shortWindowValuesRequireContext": True})
    scene_joins = []
    for a, b in zip(summaries, summaries[1:]):
        change = b["stemMedianDbfs"] - a["stemMedianDbfs"]
        scene_joins.append({"from": a["scene"], "to": b["scene"], "speechMedianDifferenceDb": change,
                            "sourceMedianDifferenceDb": b["sourceMedianDbfs"] - a["sourceMedianDbfs"],
                            "status": "pending contextual review" if abs(change) >= SETTINGS["sceneMedianDifferenceDb"] else "within diagnostic3dB criterion"})
    edge_review, edge_candidates = source_edges(sources)
    flags = group_flags(flag_rows(windows) + short_flags + edge_candidates)
    cadence = source_cadence(fine)
    contexts = export_contexts(flags, cadence, cache, expected_reference, stem, final, stem_lag, final_lag) if args.export_contexts else []
    result = {"schemaVersion": 1, "inputSignature": key, "createdAt": now(), "inputs": inputs,
        "status": "needs-contextual-review" if flags or cadence or any(not a["accepted"] for a in alignments.values()) or any(abs(j["speechMedianDifferenceDb"]) >= 3 for j in scene_joins) else "pass-measured-continuity",
        "settings": SETTINGS, "scope": "Complete current source, processed narration, pre-encode mix and actual encoded speech-active timeline",
        "speechMask": "Existing authenticated ASR word timestamps; quiet syllables are not excluded by an amplitude gate",
        "zeroDurationSpeechMaskTokens": zero_duration_tokens,
        "newAsrRuns": 0, "gpuWork": False, "foreignProcessesChanged": [], "sourcePcmModified": False,
        "samplePreservation": sample_proofs, "alignment": alignments, "rawSourceAssembly": raw_assembly,
        "decodedInputs": {"stem": stem_decode, "preEncodeMix": mixed_decode, "actualEncoded": encoded_decode},
        "scenes": summaries, "windows": windows, "fineCadenceWindows": fine,
        "flaggedVoiceTransferWindows": flags, "sustainedLocalDropCandidates": cadence,
        "sceneJoins": scene_joins, "boundaryChecks": joins,
        "sourcePcmEdges": edge_review,
        "wholeLoudness": whole_loudness(encoded, edit, build, cache),
        "beforeAfterCorrection": previous_comparison(previous, windows, source_records), "listeningContexts": contexts,
        "projectionLimitations": "The known narration waveform is projected into the mix. Correlated game voices, masking, compression and low SNR can make transfer uncertain; flags must be heard in context. This is not detector output or perfect vocal source separation.",
        "humanListening": "pending; no actual listening claimed from measurement or ASR",
        "humanWholeListening": "pending", "pronunciation": "pending",
        "sourceAndFinalAsrMeaningReview": "Use root’s existing complete ASR review; this module neither reruns nor approves it"}
    save(destination, result)
    print(f"Measured {len(windows)} speech windows and {len(joins)} boundaries; {len(flags)} grouped transfer flags and {len(cadence)} source cadence candidates. Human listening remains pending.", flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--encoded", required=True)
    parser.add_argument("--edit-dir")
    parser.add_argument("--source-dir")
    parser.add_argument("--output-dir")
    parser.add_argument("--previous-report")
    parser.add_argument("--export-contexts", action="store_true")
    review(parser.parse_args())


if __name__ == "__main__":
    main()
