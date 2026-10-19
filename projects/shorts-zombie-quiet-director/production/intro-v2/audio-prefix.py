"""Prepend only the new spoken intro; preserve the complete old mixed PCM.

Commands: mix (also reports) | report. No work runs on import. Existing successful
outputs are hash-reused and never overwritten. No voice fade, speed change,
whole-program normalization, music restart, or AAC packet splice is performed.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import math
import os
import time

import numpy as np
import soundfile as sf

R = Path(__file__).resolve().parents[4]
P = Path(__file__).resolve().parents[2]
L = P / "production/local/intro-v2"
OLD = P / "production/local"
TIMING = P / "production/intro-v2/timing.json"
VOICE = R / "shared/output/narration" / P.name / "zombie-quiet-intro-v2/intro-v2.wav"
REVISION = "zombie-quiet-intro-v2"
RATE = 48000
SETTINGS = {
    "compressor": "acompressor=threshold=0.12:ratio=3:attack=5:release=140:makeup=1",
    "referenceRangeSeconds": [0.20, 2.54], "introSamplePeakCeilingDbfs": -3.0,
    "encodedTruePeakMaximumDbtp": -1.5, "speechSpeed": 1,
    "voiceFades": False, "introMusic": False, "globalGainDb": 0,
    "activeWindowSeconds": 0.05, "activeGateBelow80thPercentileDb": 18,
    "activeGateMinimumDbfs": -50, "minimumTailSeconds": 0.30,
}


def read(path):
    return json.loads(Path(path).read_text(encoding="utf8"))


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rel(path):
    return Path(path).resolve().relative_to(R.resolve()).as_posix()


def save_new(path, value):
    with Path(path).open("x", encoding="utf8", newline="\n") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def guard():
    selected = read(R / "shared/publishing/video-production-control.json")["shortsRecurringAuthorization"]
    if (selected.get("selectedShort") != P.name
            or selected.get("latestSelection", {}).get("selectedRevision") != REVISION):
        raise RuntimeError("The exact intro revision is no longer selected.")


def helper():
    # The retained helper defines functions only; its main is guarded.
    spec = importlib.util.spec_from_file_location("zombie_audio_retained", P / "production/finish-audio.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_exact_pcm(path):
    samples, rate = sf.read(path, dtype="float32", always_2d=True)
    if rate != RATE or samples.shape[1] != 2 or not np.isfinite(samples).all():
        raise RuntimeError("Retained stem must be finite48k stereo PCM: " + str(path))
    return samples


def rms_db(samples):
    return 20 * math.log10(max(float(np.sqrt(np.mean(samples.astype(np.float64) ** 2))), 1e-12))


def active_stats(samples):
    hop = round(SETTINGS["activeWindowSeconds"] * RATE)
    windows = [samples[first:first + hop] for first in range(0, len(samples), hop)
               if len(samples[first:first + hop]) >= hop // 2]
    if not windows:
        raise RuntimeError("No complete context for speech-active measurement.")
    levels = np.array([rms_db(window) for window in windows])
    gate = max(SETTINGS["activeGateMinimumDbfs"],
               float(np.percentile(levels, 80)) - SETTINGS["activeGateBelow80thPercentileDb"])
    selected = [window for window, level in zip(windows, levels) if level > gate]
    if not selected:
        raise RuntimeError("No audible speech in level-matching context.")
    return {
        "rmsDbfs": rms_db(np.concatenate(selected)), "activeSeconds": sum(map(len, selected)) / RATE,
        "gateDbfs": gate, "activeWindowMedianDbfs": float(np.median(levels[levels > gate])),
        "windowSeconds": SETTINGS["activeWindowSeconds"],
    }


def recipe():
    guard()
    timing = read(TIMING)
    for key in ["introSeconds", "introFrames", "totalSeconds", "totalFrames", "voiceOffsetSeconds", "introVoiceSeconds"]:
        if key not in timing or not math.isfinite(float(timing[key])):
            raise RuntimeError("Missing or nonfinite timing." + key)
    if (int(timing["introFrames"]) != timing["introFrames"]
            or int(timing["totalFrames"]) != timing["totalFrames"]
            or abs(timing["introSeconds"] - timing["introFrames"] / 60) > 1e-8
            or abs(timing["totalSeconds"] - timing["totalFrames"] / 60) > 1e-8
            or abs(timing["voiceOffsetSeconds"] - 0.15) > 1e-8
            or timing["introSeconds"] + 1e-8 < timing["voiceOffsetSeconds"] + timing["introVoiceSeconds"] + 0.30):
        raise RuntimeError("Intro must contain untrimmed voice,0.15s lead and at least0.30s tail on60fps boundaries.")
    paths = {"introVoice": VOICE, "oldMix": OLD / "final-mix.wav",
             "oldNarration": OLD / "narration-stem.wav", "oldBackground": OLD / "background-stem.wav"}
    data = {"revision": REVISION, "scriptSha256": sha(__file__), "timing": timing,
            "timingSha256": sha(TIMING), "settings": SETTINGS,
            "inputs": {name: {"path": rel(path), "sha256": sha(path)} for name, path in paths.items()}}
    fingerprint = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
    return timing, data, fingerprint


def mix():
    timing, data, fingerprint = recipe()
    receipt = L / "audio-prefix-build.json"
    if receipt.exists():
        built = read(receipt)
        if (built.get("fingerprint") != fingerprint
                or any(sha(R / item["path"]) != item["sha256"] for item in built["artifacts"].values())):
            raise RuntimeError("Existing intro mix differs; preserve it and inspect rather than overwrite.")
        return report()
    outputs = ["intro-source-timeline.wav", "intro-prepared.wav", "intro-narration.wav",
               "narration-stem.wav", "background-stem.wav", "final-mix.wav", "final-mix.m4a"]
    if any((L / name).exists() for name in outputs):
        raise RuntimeError("Unreceipted prefix outputs exist; inspect them first.")
    old_mix = read_exact_pcm(OLD / "final-mix.wav")
    old_narration = read_exact_pcm(OLD / "narration-stem.wav")
    old_background = read_exact_pcm(OLD / "background-stem.wav")
    if len({len(old_mix), len(old_narration), len(old_background)}) != 1:
        raise RuntimeError("Retained body stems have different lengths.")
    prefix_count = int(timing["introFrames"]) * 800
    total_count = int(timing["totalFrames"]) * 800
    if total_count != prefix_count + len(old_mix):
        raise RuntimeError("Total duration must equal the exact complete body plus intro.")
    h = helper()
    raw = h.pcm(VOICE)
    if abs(len(raw) / RATE - timing["introVoiceSeconds"]) > 2 / RATE:
        raise RuntimeError("Measured intro voice duration differs from timing input.")
    lead = round(timing["voiceOffsetSeconds"] * RATE)
    if lead + len(raw) > prefix_count - round(0.30 * RATE):
        raise RuntimeError("Never trim voice or remove the planned speech-safe tail.")
    L.mkdir(parents=True, exist_ok=True)
    work = L / ("audio-work-" + fingerprint[:12] + "-" + str(os.getpid()) + "-" + str(time.time_ns()))
    work.mkdir(exist_ok=False)
    source = np.zeros((prefix_count, 2), dtype=np.float32)
    source[lead:lead + len(raw)] = raw
    sf.write(work / "intro-source-timeline.wav", source, RATE, subtype="FLOAT")
    h.run([h.FF, "-v", "warning", "-n", "-i", str(work / "intro-source-timeline.wav"),
           "-af", SETTINGS["compressor"], "-c:a", "pcm_f32le", str(work / "intro-prepared.wav")])
    prepared = read_exact_pcm(work / "intro-prepared.wav")
    if len(prepared) != prefix_count:
        raise RuntimeError("Intro compressor changed PCM sample count.")
    first, last = [round(seconds * RATE) for seconds in SETTINGS["referenceRangeSeconds"]]
    reference = active_stats(old_narration[first:last])
    measured = active_stats(prepared[lead:lead + len(raw)])
    desired_gain = 10 ** ((reference["rmsDbfs"] - measured["rmsDbfs"]) / 20)
    peak = float(np.max(np.abs(prepared)))
    peak_gain = 10 ** (SETTINGS["introSamplePeakCeilingDbfs"] / 20) / max(peak, 1e-12)
    gain = min(desired_gain, peak_gain)
    intro = (prepared * gain).astype(np.float32)
    matching = {"reference": reference, "prepared": measured,
                "source": active_stats(raw), "matched": active_stats(intro[lead:lead + len(raw)]),
                "constantGainDb": 20 * math.log10(gain), "samplePeakLimited": peak_gain < desired_gain}
    matching["introMinusOldOpeningSpeechActiveDb"] = matching["matched"]["rmsDbfs"] - reference["rmsDbfs"]
    zeros = np.zeros_like(intro)
    joined = np.concatenate([intro, old_mix])
    narration = np.concatenate([intro, old_narration])
    background = np.concatenate([zeros, old_background])
    for name, samples in [("intro-narration.wav", intro), ("narration-stem.wav", narration),
                          ("background-stem.wav", background), ("final-mix.wav", joined)]:
        sf.write(work / name, samples, RATE, subtype="FLOAT")
    for name, retained in [("final-mix.wav", old_mix), ("narration-stem.wav", old_narration),
                           ("background-stem.wav", old_background)]:
        if not np.array_equal(read_exact_pcm(work / name)[prefix_count:], retained):
            raise RuntimeError("Retained body PCM is not sample-exact in " + name)
    h.run([h.FF, "-v", "warning", "-n", "-i", str(work / "final-mix.wav"),
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
           "-movflags", "+faststart", str(work / "final-mix.m4a")])
    guard()
    if recipe()[-1] != fingerprint:
        raise RuntimeError("Inputs changed during mixing; preserve staged outputs.")
    for name in outputs:
        if (L / name).exists():
            raise RuntimeError("Concurrent prefix output exists; preserve both staging sets.")
    for name in outputs:
        (work / name).rename(L / name)
    save_new(receipt, {
        "fingerprint": fingerprint, "recipe": data, "matching": matching,
        "artifacts": {name: {"path": rel(L / name), "sha256": sha(L / name)} for name in outputs},
        "bodyPcmSampleExact": True, "bodyNarrationPcmUnchanged": True,
        "bodyBackgroundPcmUnchanged": True, "bodyStartsAtSample": prefix_count,
        "bodySamples": len(old_mix), "totalSamples": total_count,
        "introBackground": "No music or game sound; original body music onset retained without restart/remix.",
        "aacPacketSplice": False, "globalNormalization": False, "voiceFade": False,
        "speechSpeed": 1, "humanListening": "pending", "finalMixAsr": "pending separate one-time full mix check",
    })
    report()


def report():
    timing, data, fingerprint = recipe()
    built = read(L / "audio-prefix-build.json")
    if built["fingerprint"] != fingerprint:
        raise RuntimeError("Audio-prefix report inputs differ.")
    for artifact in built["artifacts"].values():
        if sha(R / artifact["path"]) != artifact["sha256"]:
            raise RuntimeError("A successful prefix artifact changed; preserve and inspect.")
    path = L / "audio-prefix-review.json"
    if path.exists():
        previous = read(path)
        if previous.get("fingerprint") != fingerprint:
            raise RuntimeError("Preserve earlier audio review; inputs changed.")
        if not previous.get("truePeakPass"):
            raise RuntimeError("The preserved review still fails true peak; no automatic remix.")
        print("Reused prefix audio review: " + rel(path))
        return
    h = helper()
    stem = read_exact_pcm(L / "narration-stem.wav")
    background = read_exact_pcm(L / "background-stem.wav")
    mixed = read_exact_pcm(L / "final-mix.wav")
    decoded = h.pcm(L / "final-mix.m4a")
    prefix_count = int(timing["introFrames"]) * 800
    old_mix = read_exact_pcm(OLD / "final-mix.wav")
    body_exact = np.array_equal(mixed[prefix_count:], old_mix)
    if not body_exact or len(decoded) < len(stem) or len(decoded) - len(stem) > 1024:
        raise RuntimeError("Body PCM preservation or decoded AAC length check failed.")
    estimate = decoded[:len(stem)] - background
    rows = []
    for first in range(0, len(stem) - 19200 + 1, 4800):
        last = first + 19200
        original_level = rms_db(stem[first:last])
        if original_level < -42:
            continue
        encoded_level = rms_db(estimate[first:last])
        rows.append({"start": first / RATE, "end": last / RATE,
                     "stemRmsDbfs": original_level, "decodedSpeechEstimateDbfs": encoded_level,
                     "encodedMinusStemDb": encoded_level - original_level,
                     "encodedAttenuationCandidate": encoded_level < original_level - 1.5})
    candidates = h.grouped(rows, "encodedAttenuationCandidate")
    join_rows = [row for row in rows if timing["introSeconds"] - 3 <= row["start"] <= timing["introSeconds"] + 3]
    matching = built["matching"]
    intro_source = read_exact_pcm(L / "intro-source-timeline.wav")
    intro_prepared = read_exact_pcm(L / "intro-prepared.wav")
    source_windows = []
    for first in range(0, prefix_count - 19200 + 1, 4800):
        last = first + 19200
        source_level = rms_db(intro_source[first:last])
        if source_level < -50:
            continue
        prepared_level = rms_db(intro_prepared[first:last])
        processed_level = rms_db(stem[first:last])
        source_windows.append({"start": first / RATE, "end": last / RATE,
                               "sourceRmsDbfs": source_level, "preparedRmsDbfs": prepared_level,
                               "processedRmsDbfs": processed_level,
                               "sourceToPreparedDb": prepared_level - source_level,
                               "preparedToProcessedDb": processed_level - prepared_level})
    flags = []
    if abs(matching["introMinusOldOpeningSpeechActiveDb"]) > 2:
        flags.append("Intro speech-active RMS differs from retained old opening by more than2dB.")
    if candidates:
        flags.append("Encoded speech attenuation candidates require contextual listening.")
    measured = h.loud(L / "final-mix.m4a")
    true_peak = float(measured["input_tp"])
    peak_pass = math.isfinite(true_peak) and true_peak <= SETTINGS["encodedTruePeakMaximumDbtp"]
    if not peak_pass:
        flags.append("Encoded true peak exceeds-1.5dBTP; no global normalization applied.")
    save_new(path, {
        "fingerprint": fingerprint, "bodyPcmSampleExact": body_exact,
        "introLevelMatching": matching, "encodedMeasured": measured,
        "truePeakPass": peak_pass, "aacDecodedSamples": len(decoded), "expectedSamples": len(stem),
        "aacTailPaddingSamples": len(decoded) - len(stem),
        "speechActiveWindows": rows, "introBodyJoinWindows": join_rows,
        "introSourcePreparedProcessedWindows": source_windows,
        "encodedAttenuationCandidates": candidates, "reviewFlags": flags,
        "technicalResult": "review-required" if flags else "pass",
        "humanListening": "pending; check intro clarity and intro-to-old-hook join in context",
        "limitations": "Decoded speech estimate subtracts the known synchronized background; it is not source separation. Whole-file loudness alone is not a continuity pass.",
    })
    if not peak_pass:
        raise RuntimeError("True-peak check failed; staging/review retained, no automatic remix.")
    print(json.dumps({"review": rel(path), "bodyPcmSampleExact": body_exact,
                      "reviewFlags": flags, "humanListening": "pending"}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["mix", "report"])
    arguments = parser.parse_args()
    {"mix": mix, "report": report}[arguments.command]()
