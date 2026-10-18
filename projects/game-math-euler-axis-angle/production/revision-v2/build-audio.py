"""Selected M04 CPU mixer: constant voice gain; only music is ducked.

Run after build-timeline.py and source narration review. This script never
loads a GPU model or overwrites raw narration, ASR, timing, or the baseline.
  python build-audio.py --check-inputs
  python build-audio.py

Default outputs: production/local/revision-v2/{narration-stem.wav,
music-stem.wav,final-mix.wav,final-mix.m4a,audio-build.json}.
Source gameplay is video-only; no game soundtrack/speech is mixed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / "projects/game-math-euler-axis-angle"
DEFAULT_OUT = PROJECT / "production/local/revision-v2"
VOICE_RATE = 24000
MIX_RATE = 48000
MUSIC = ROOT / "shared/assets/music/youtube-audio-library/Nimbus-Eveningland.mp3"
MUSIC_SHA256 = "06ddb8d0f2aa82e499ab2cb398b8a241c626d9d3da82bbaf274d1178435f8c08"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def relative(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def db(value):
    return 20 * math.log10(max(float(value), 1e-10))


def rms(array):
    return float(np.sqrt(np.mean(np.square(array, dtype=np.float64)))) if len(array) else 0.0


def speech_mask(samples, rate, words):
    mask = np.zeros(samples, dtype=bool)
    for word in words:
        a, b = word["timestamp"]
        if a is not None and b is not None:
            mask[max(0, round(a * rate)):min(samples, round(b * rate))] = True
    return mask


def require_selected():
    control = read(ROOT / "shared/publishing/video-production-control.json")
    if control.get("selectedVideo") != PROJECT.name:
        raise RuntimeError("M04 is no longer selected; do not mix an unselected video")


def run(arguments, name, output):
    completed = subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-y", *map(str, arguments)],
                               cwd=ROOT, capture_output=True)
    log = output / (name + ".log")
    log.write_bytes(completed.stderr)
    if completed.returncode:
        raise RuntimeError(completed.stderr.decode(errors="replace")[-4000:])
    return completed.stderr.decode(errors="replace")


def loudness_stats(log):
    start, end = log.rfind("{"), log.rfind("}")
    if start < 0 or end < start:
        raise ValueError("FFmpeg loudness measurement did not return JSON")
    result = json.loads(log[start:end + 1])
    if not math.isfinite(float(result["input_i"])):
        raise ValueError("Narration loudness is not finite")
    return result


def preserved_placement(pcm, placed, pauses, rate):
    """Prove silence insertion has preserved every original decoded sample."""
    raw_at, placed_at, restored = 0, 0, []
    for pause in pauses:
        boundary, count = int(pause["rawSample"]), int(pause["silenceSamples"])
        chunk_count = boundary - raw_at
        restored.append(placed[placed_at:placed_at + chunk_count])
        placed_at += chunk_count
        silence = placed[placed_at:placed_at + count]
        if len(silence) != count or np.any(silence != 0):
            raise ValueError("A placed observation pause is not zero-valued silence")
        placed_at += count
        raw_at = boundary
    restored.append(placed[placed_at:])
    recovered = np.concatenate(restored)
    if recovered.shape != pcm.shape or not np.array_equal(recovered, pcm):
        raise ValueError("Placed voice does not preserve every source PCM sample")
    return {"originalDecodedSampleSha256": hashlib.sha256(pcm.tobytes()).hexdigest(),
            "recoveredDecodedSampleSha256": hashlib.sha256(recovered.tobytes()).hexdigest(),
            "equal": True, "insertedSilenceSamples": sum(int(p["silenceSamples"]) for p in pauses)}


def build(args):
    require_selected()
    output = Path(args.output_dir).resolve()
    output.relative_to(DEFAULT_OUT.resolve())
    plan_file = Path(args.timeline).resolve()
    plan = read(plan_file)
    if plan.get("timing") != "measured-and-asr-aligned" or plan.get("fps") != 60:
        raise ValueError("Current measured60fps timeline required")
    if plan.get("actualFrames", 0) * 3 != plan.get("explanationFrames", 0) * 2:
        raise ValueError("Current40:60frame ratio required")
    if sha(MUSIC) != MUSIC_SHA256:
        raise ValueError("Nimbus source is absent/changed; do not substitute an unverified track")
    duration = plan["totalFrames"] / 60
    scenes = []
    for scene in plan["scenes"]:
        raw_path, placed_path = ROOT / scene["voice"], ROOT / scene["placedVoice"]
        if sha(raw_path) != scene["voiceSha256"] or sha(placed_path) != scene["placedVoiceSha256"]:
            raise ValueError(f"Changed source/placed narration scene{scene['id']}")
        asr_path = ROOT / scene["asr"]
        asr = read(asr_path)
        if sha(asr_path) != scene["asrSha256"] or asr["audio_sha256"] != scene["voiceSha256"]:
            raise ValueError("Changed ASR alignment; rebuild timing before mixing")
        pcm, rate = sf.read(raw_path, dtype="float32")
        placed, placed_rate = sf.read(placed_path, dtype="float32")
        if rate != VOICE_RATE or placed_rate != VOICE_RATE or pcm.ndim != 1 or placed.ndim != 1:
            raise ValueError("Approved24kHzmono source expected")
        sample_proof = preserved_placement(pcm, placed, scene["observationPauses"], rate)
        mask = speech_mask(len(pcm), rate, asr["words"])
        if int(mask.sum()) < rate / 2:
            raise ValueError("Insufficient recognized speech for a stable scene gain")
        speech_level = db(rms(pcm[mask]))
        gain_db = -20.0 - speech_level
        # Gain is constant over the entire scene. No adaptive voice ducking,
        # seconds-long automatic gain curve, or per-window normalization.
        if abs(gain_db) > 24:
            raise ValueError(f"Unusual scene gain{gain_db:.2f}dB: inspect source before mixing")
        windows = []
        for start in range(0, max(0, len(pcm) - rate + 1), rate // 2):
            submask = mask[start:start + rate]
            values = pcm[start:start + rate][submask]
            if len(values) >= rate * 0.25:
                windows.append({"rawTime": start / rate, "sourceSpeechDbfs": db(rms(values)),
                                "afterConstantGainDbfs": db(rms(values)) + gain_db})
        scenes.append((scene, placed, gain_db, {"scene": scene["id"],
                       "sourceSha256": scene["voiceSha256"], "placedSha256": scene["placedVoiceSha256"],
                       "sourceSpeechRmsDbfs": speech_level, "fixedGainDb": gain_db,
                       "pcmPreservation": sample_proof, "speechWindows": windows}))
    if args.check_inputs:
        print(json.dumps({"inputValidationPassed": True, "outputsWritten": False, "scenes": len(scenes),
                          "seconds": duration, "musicSha256": MUSIC_SHA256, "sourceAudioUsed": False}))
        return
    output.mkdir(parents=True, exist_ok=True)
    total_samples = round(duration * VOICE_RATE)
    voice = np.zeros(total_samples, dtype=np.float32)
    reports, cursor = [], 0
    for scene, placed, gain_db, report in scenes:
        start = round(scene["startFrame"] * VOICE_RATE / 60)
        end = start + len(placed)
        if start < cursor or end > total_samples:
            raise ValueError("Overlapping/out-of-range voice placement")
        # Source files are untouched. Tiny6ms fades only affect utterance file
        # edges; actual source→stem→encoded level-continuity QA remains required.
        current = placed * (10 ** (gain_db / 20))
        edge = min(round(0.006 * VOICE_RATE), len(current) // 2)
        if edge:
            current[:edge] *= np.linspace(0, 1, edge)
            current[-edge:] *= np.linspace(1, 0, edge)
        voice[start:end] = current
        cursor = end
        report.update(outputStartSeconds=start / VOICE_RATE, outputEndSeconds=end / VOICE_RATE,
                      edgeFadeMs=6, noSourcePcmOverwrite=True)
        reports.append(report)
    fixed_voice = output / "voice-fixed-gain.wav"
    sf.write(fixed_voice, voice, VOICE_RATE, subtype="FLOAT")
    # Measure the same duplicated stereo layout that will enter the mix.
    # Measuring mono and then copying it into two channels raises integrated
    # loudness by about3LU, so that would apply the wrong constant gain.
    stats = loudness_stats(run(["-i", fixed_voice, "-af", "pan=stereo|c0=c0|c1=c0,loudnorm=I=-16:TP=-2:LRA=9:print_format=json",
                               "-f", "null", "-"], "voice-measure", output))
    gain_db = -16.0 - float(stats["input_i"])
    narration_filter = (f"volume={gain_db}dB:precision=double,"
                        "alimiter=limit=0.7499:attack=5:release=50:level=false:latency=true,"
                        "pan=stereo|c0=c0|c1=c0")
    narration = output / "narration-stem.wav"
    run(["-i", fixed_voice, "-af", narration_filter, "-ar", MIX_RATE, "-c:a", "pcm_s24le", narration],
        "narration-fixed-gain", output)
    music_duration = float(json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(MUSIC)
    ], text=True, encoding="utf-8"))["format"]["duration"])
    repeat = max(1, math.ceil((duration - 1) / (music_duration - 1)))
    inputs = [argument for _ in range(repeat) for argument in ("-i", MUSIC)]
    filters, last = [], "0:a"
    for index in range(1, repeat):
        filters.append(f"[{last}][{index}:a]acrossfade=d=1:c1=tri:c2=tri[m{index}]")
        last = f"m{index}"
    filters.append(f"[{last}]atrim=duration={duration},loudnorm=I=-31:TP=-4:LRA=7,"
                   f"afade=t=in:st=0:d=0.45,afade=t=out:st={duration - 0.45}:d=0.45[music]")
    music_stem = output / "music-stem.wav"
    run([*inputs, "-filter_complex", ";".join(filters), "-map", "[music]", "-t", duration,
         "-ar", MIX_RATE, "-ac", 2, "-c:a", "pcm_s24le", music_stem], "music-loop-level", output)
    # The voice drives the music sidechain. The voice branch never receives
    # sidechain compression, so background changes cannot attenuate speech.
    graph = ("[0:a]asplit=2[voice][side];[1:a][side]"
             "sidechaincompress=threshold=0.025:ratio=3:attack=35:release=400[bg];"
             "[voice][bg]amix=inputs=2:normalize=0:duration=first,"
             "alimiter=limit=0.794:level=false:latency=true[out]")
    mix = output / "final-mix.wav"
    run(["-i", narration, "-i", music_stem, "-filter_complex", graph, "-map", "[out]", "-t", duration,
         "-ar", MIX_RATE, "-ac", 2, "-c:a", "pcm_s24le", mix], "final-mix", output)
    aac = output / "final-mix.m4a"
    run(["-i", mix, "-ar", MIX_RATE, "-ac", 2, "-c:a", "aac", "-b:a", "192k", aac], "final-aac", output)
    # The final-pair compositor uses this same receipt to avoid encoding an
    # already current AAC stem for a second time.
    save(output / "aac-source.json", {"sha256": sha(mix), "rate": MIX_RATE, "bitrate": "192k"})
    loudness = loudness_stats(run(["-i", aac, "-af", "loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json",
                                  "-f", "null", "-"], "encoded-measure", output))
    report = {"schemaVersion": 2, "slug": PROJECT.name, "revision": "teaching-rules-v2", "seconds": duration,
              "timeline": relative(plan_file), "timelineSha256": sha(plan_file), "scenes": reports,
              "voiceGainMode": "one-constant-gain-per-scene-plus-one-global-gain-and-short-peak-limiter",
              "globalGainDb": gain_db, "normalizationMeasurementOnly": stats,
              "peakLimiter": {"narrationCeilingDbfs": 20 * math.log10(0.7499), "attackMs": 5,
                              "releaseMs": 50, "autoMakeup": False, "finalCeilingDbfs": 20 * math.log10(0.794)},
              "music": {"title": "Nimbus — Eveningland", "file": relative(MUSIC), "sha256": MUSIC_SHA256,
                        "initialLufs": -31, "loopCrossfadeSeconds": 1, "voiceDrivenDuck": True,
                        "rightsEvidenceReuse": "Identical selected/verified Nimbus asset used in previous completed AI showcase; no new track substitution"},
              "voiceDucked": False, "sourceAudioUsed": False, "gameAudio": [], "amixNormalize": False,
              "outputSampleRate": MIX_RATE, "outputChannels": 2, "aacBitrate": "192k",
              "encodedLoudnessMeasurement": loudness,
              "outputs": [{"file": relative(file), "sha256": sha(file), "bytes": file.stat().st_size}
                          for file in (fixed_voice, narration, music_stem, mix, aac)],
              "sourceToStemToEncodedSpeechContinuity": "pending-current-encoded-review",
              "currentFinalMixFullAsr": "pending-one-pass", "humanWholeListening": "pending"}
    save(output / "audio-build.json", report)
    print(json.dumps({"seconds": duration, "scenes": len(scenes), "audio": relative(aac),
                      "voiceDucked": False, "initialMusicLufs": -31, "humanWholeListening": "pending"}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeline", default=str(Path(__file__).resolve().parent / "timeline.json"))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUT))
    parser.add_argument("--check-inputs", action="store_true", help="Validate all hashes/PCM without mixing or writing outputs")
    build(parser.parse_args())
