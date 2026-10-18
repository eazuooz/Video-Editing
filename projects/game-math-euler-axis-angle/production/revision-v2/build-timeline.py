"""Measured M04 revision timeline. CPU only; no source/ASR/voice input mutation.

Run after the complete selected TTS batch and bilingual ASR alignment:
  python build-timeline.py --check-inputs
  python build-timeline.py

The canonical timeline is production/revision-v2/timeline.json; PCM/captions
live only in production/local/revision-v2. Every annotation source
window is reserved at the beginning of its matching actual scene. Remaining
source intervals are consumed once, at native speed, without loops or holds.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import subprocess

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / "projects/game-math-euler-axis-angle"
HERE = Path(__file__).resolve().parent
DEFAULT_OUT = PROJECT / "production/local/revision-v2"
DEFAULT_TIMELINE = HERE / "timeline.json"
FPS = 60
SR = 24000
TAIL_SECONDS = 0.6


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


def save(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def require_selected():
    control = read(ROOT / "shared/publishing/video-production-control.json")
    if control.get("selectedVideo") != PROJECT.name:
        raise RuntimeError("M04 is not the currently selected production; no output written")
    lease = ROOT / "shared/output/GPU_HANDOFF.json"
    if lease.exists():
        state = read(lease)
        if state.get("project") == PROJECT.name and state.get("state") == "tts_running":
            raise RuntimeError("Finish the current selected TTS batch before measuring its inputs")


def observations():
    file = ROOT / "production/batches/game-math-part2-full-series/observations.py"
    spec = importlib.util.spec_from_file_location("m04_observation_helpers", file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_seconds(value):
    h, m, sec = value.replace(",", ".").split(":")
    return int(h) * 3600 + int(m) * 60 + float(sec)


def read_srt(path):
    rows = []
    for block in re.split(r"\r?\n\s*\r?\n", Path(path).read_text(encoding="utf-8-sig").strip()):
        lines = block.splitlines()
        start, end = [parse_seconds(v.strip()) for v in lines[1].split("-->")]
        rows.append({"start": start, "end": end, "text": "\n".join(lines[2:])})
    return rows


def stamp(seconds):
    ms = round(seconds * 1000)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(path, rows):
    text = "\n\n".join(f"{i}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}" for i, c in enumerate(rows, 1))
    Path(path).write_text(text + "\n", encoding="utf-8")


def source_catalog(media):
    catalog = {}
    for key in ("primarySource", "additionalSource"):
        record = media.get(key)
        if not record:
            continue
        source = record["source"]
        file = ROOT / source["file"]
        if sha(file) != source["sha256"]:
            raise ValueError(f"Changed source bytes: {file}")
        probe = json.loads(subprocess.check_output([
            "ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate:format=duration",
            "-of", "json", str(file)
        ], text=True, encoding="utf-8"))
        stream = next(s for s in probe["streams"] if s["codec_type"] == "video")
        if stream["width"] < 1920 or stream["height"] < 1080:
            raise ValueError(f"Not genuine FHD source: {file}")
        catalog[source["id"]] = {
            "id": source["id"], "file": relative(file), "sha256": source["sha256"],
            "url": source["url"], "uploader": source["uploader"],
            "width": stream["width"], "height": stream["height"], "nativeFps": stream["r_frame_rate"],
            "durationSeconds": float(probe["format"]["duration"]), "sourceAudioUsed": False,
        }
    return catalog


def intervals(media, annotations, catalog):
    primary_record = media["primarySource"]
    primary_id = primary_record["source"]["id"]
    by_scene = {}
    for row in primary_record["sourceCapacity"]["cuts"]:
        by_scene[row["scene"]] = [
            {"sourceId": primary_id, "a": round(seg["in"] * FPS),
             "b": round((seg["in"] + seg["maxSeconds"]) * FPS), "purpose": "original inspected scene interval"}
            for seg in row["approvedSegments"]
        ]
    windows = {}
    for index, window in enumerate(annotations["windows"]):
        sid = str(window["scene"]).zfill(2)
        if sid in windows:
            raise ValueError("Multiple annotation windows require explicit scene-specific source ordering")
        wa, wb = round(window["sourceIn"] * FPS), round(window["sourceOutExclusive"] * FPS)
        matching = [v for v in by_scene[sid] if v["sourceId"] == window["sourceId"] and v["a"] <= wa < wb <= v["b"]]
        if len(matching) != 1:
            raise ValueError(f"Annotation window {sid} must be contained in one approved source interval")
        original = matching[0]
        # Put the target at the first spoken observation. Reserve its complete
        # remaining original shot; subtract that piece before using the rest.
        first = {**original, "a": wa, "annotationWindowIndex": index, "lockedWindowEnd": wb}
        remainder = []
        for value in by_scene[sid]:
            if value is original:
                if value["a"] < wa:
                    remainder.append({**value, "b": wa})
            else:
                remainder.append(value)
        by_scene[sid] = [first, *remainder]
        windows[sid] = {"index": index, "sourceId": window["sourceId"], "a": wa, "b": wb}
    extra = []
    additional = media.get("additionalSource")
    if additional:
        for value in additional["candidateSegments"]:
            extra.append({"sourceId": additional["source"]["id"], "a": round(value["in"] * FPS),
                          "b": round(value["out"] * FPS), "purpose": value.get("purpose"),
                          "movingReview": "selected moving composite pending", "proof": value.get("proof")})
    # Reject overlap in the complete approved inventory, before any allocation.
    all_intervals = [x for group in by_scene.values() for x in group] + extra
    for source_id in catalog:
        ordered = sorted([v for v in all_intervals if v["sourceId"] == source_id], key=lambda v: v["a"])
        for left, right in zip(ordered, ordered[1:]):
            if left["b"] > right["a"]:
                raise ValueError(f"Overlapping approved source inventory: {source_id} {left} {right}")
        for value in ordered:
            if value["a"] < 0 or value["b"] / FPS > catalog[source_id]["durationSeconds"] + 1 / FPS:
                raise ValueError("Approved interval exceeds decoded source duration")
    return by_scene, extra, windows


def allocate_frames(rows, primary, extra_capacity):
    explanatory = [s for s in rows if s["kind"] == "explanation"]
    actual = [s for s in rows if s["kind"] == "actual"]
    # Exact 2:3 frame counts: explanation is a multiple of3, actual a multiple2.
    # Runtime is driven by useful explanation, never by adding explanatory idle.
    explanation_target = math.ceil(sum(s["minimumFrames"] for s in explanatory) / 3) * 3
    actual_target = explanation_target // 3 * 2
    for scene in rows:
        scene["frames"] = scene["minimumFrames"]
    for scene in explanatory[:explanation_target - sum(s["frames"] for s in explanatory)]:
        scene["frames"] += 1
    for scene in actual:
        scene["primaryCapacityFrames"] = sum(v["b"] - v["a"] for v in primary[scene["id"]])
        if scene["frames"] > scene["quietCapacityFrames"]:
            raise ValueError("Measured actual narration exceeds its quiet-seam capacity")
    required = actual_target - sum(s["frames"] for s in actual)
    if required < 0:
        raise ValueError("Actual speech is already over40%; add useful explanation rather than silent explanatory padding")
    def used_extra():
        return sum(max(0, s["frames"] - s["primaryCapacityFrames"]) for s in actual)
    if used_extra() > extra_capacity:
        raise ValueError("Actual scene narration requires more inspected supplementary footage")
    while required:
        reserve = extra_capacity - used_extra()
        eligible = [s for s in actual if s["frames"] < s["quietCapacityFrames"] and
                    (s["frames"] < s["primaryCapacityFrames"] or reserve > 0)]
        if not eligible:
            need = required / FPS
            raise ValueError(f"Need {need:.3f}s more safe observed footage/sentence-seam capacity. Add narration or verified ranges; never loop/slow/freeze.")
        selected = min(eligible, key=lambda s: (s["frames"] / s["minimumFrames"], s["id"]))
        selected["frames"] += 1
        required -= 1
    return actual_target, explanation_target


def build(args):
    require_selected()
    out = Path(args.output_dir).resolve()
    out.relative_to(DEFAULT_OUT.resolve())
    timeline_output = Path(args.timeline).resolve()
    timeline_output.relative_to((PROJECT / "production/revision-v2").resolve())
    manifest_file = HERE / "tts-manifest.json"
    manifest = read(manifest_file)
    lesson_file = HERE / "lesson.json"
    lesson = read(lesson_file)
    narrator_dir = ROOT / manifest["tts"]["outputDir"]
    timing_file = narrator_dir / (manifest["tts"]["filenameStem"] + ".timing.json")
    timing = read(timing_file)
    if not timing.get("alignment"):
        raise ValueError("ASR-aligned paragraph/caption timing required")
    ko = read(ROOT / manifest["paths"]["script"])
    en = read(ROOT / manifest["paths"]["scriptEn"])
    media_file = PROJECT / "sources/media-revision-v2.json"
    annotation_file = PROJECT / "sources/annotation-plan-v2.json"
    media, annotations = read(media_file), read(annotation_file)
    catalog = source_catalog(media)
    primary, extra, windows = intervals(media, annotations, catalog)
    obs = observations()
    rows, raw = [], {}
    for design, spoken, translated in zip(lesson["scenes"], ko["scenes"], en["scenes"]):
        sid = design["id"]
        if spoken["id"] != sid or translated["id"] != sid or design["ko"] != spoken["lines"] or design["en"] != translated["lines"]:
            raise ValueError(f"Stale lesson/script scene {sid}")
        entries = [e for e in timing["entries"] if e["scene_id"] == sid]
        if len(entries) != len(spoken["lines"]) or [e["text"] for e in entries] != spoken["lines"]:
            raise ValueError(f"Stale measured paragraph entries: {sid}")
        file = narrator_dir / "chunks" / f"{sid}-scene.wav"
        pcm, rate = sf.read(file, dtype="float32")
        if rate != SR or pcm.ndim != 1:
            raise ValueError("Approved source voice must remain24kHz mono")
        asr_file = narrator_dir / "asr" / f"{sid}.json"
        asr = read(asr_file)
        digest = sha(file)
        if asr["audio_sha256"] != digest:
            raise ValueError(f"Stale scene ASR {sid}")
        origin = entries[0]["start"]
        cues = [{"start": e["voice_start"] - origin, "end": e["end"] - origin} for e in entries]
        minimum = math.ceil((len(pcm) / rate + TAIL_SECONDS) * FPS - 1e-8)
        row = {"id": sid, "title": design["title"], "kind": design["kind"], "classification": design["kind"],
               "minimumFrames": minimum, "rawOrigin": origin, "voice": relative(file), "voiceSha256": digest,
               "voiceSeconds": len(pcm) / rate, "asr": relative(asr_file), "asrSha256": sha(asr_file),
               "rawLineStarts": [e["voice_start"] - origin for e in entries], "paragraphs": entries}
        if row["kind"] == "actual":
            row["quietCapacityFrames"] = max(minimum, math.floor(obs.observation_capacity_seconds(pcm, rate, cues) * FPS + 1e-7))
        rows.append(row)
        raw[sid] = (pcm, cues, asr)
    if len(rows) != 26 or len(ko["scenes"]) != 26 or len(en["scenes"]) != 26:
        raise ValueError("Selected revision must retain26 scenes")
    actual_frames, explanation_frames = allocate_frames(rows, primary, sum(s["b"] - s["a"] for s in extra))
    cursor, cuts, source_usage = 120, [], []
    secondary = [dict(v) for v in extra]
    placed = {}
    for row in rows:
        sid, count = row["id"], row["frames"]
        row.update(startFrame=cursor, endFrame=cursor + count, start=cursor / FPS, seconds=count / FPS,
                   voiceStart=cursor / FPS, voiceStartFrame=cursor)
        pcm, cues, asr = raw[sid]
        if row["kind"] == "actual":
            audio, pauses, evidence = obs.place_observation_pauses(pcm, SR, cues, count / FPS)
            # A low-energy stop consonant is not permission to split a word.
            for pause in pauses:
                at = pause["rawAt"]
                for word in asr["words"]:
                    a, b = word["timestamp"]
                    if a is not None and b is not None and a + 0.025 < at < b - 0.025:
                        raise ValueError(f"Scene{sid}: quiet seam intersects recognized word {word['text']!r}; inspect a bounded seam")
            available = [dict(v) for v in primary[sid]]
            remaining, local_start = count, 0
            while remaining:
                if available:
                    segment = available.pop(0)
                elif secondary:
                    segment = secondary.pop(0)
                else:
                    raise ValueError("Inspected footage exhausted")
                used = min(remaining, segment["b"] - segment["a"])
                if "lockedWindowEnd" in segment and segment["a"] + used < segment["lockedWindowEnd"]:
                    raise ValueError("Scene too short to preserve its whole annotation window")
                source = catalog[segment["sourceId"]]
                cut = {"id": f"{sid}-cut-{len([c for c in cuts if c['scene'] == sid]) + 1:02d}", "scene": sid,
                       "sourceId": source["id"], "sourceFile": source["file"], "sourceSha256": source["sha256"],
                       "sourceStart": segment["a"] / FPS, "sourceEnd": (segment["a"] + used) / FPS,
                       "frames": used, "seconds": used / FPS, "startFrame": local_start,
                       "globalStartFrame": cursor + local_start, "sourceSpeed": 1,
                       "kind": "actual", "classification": "actual-existing-gameplay", "sourceAudioUsed": False,
                       "purpose": segment.get("purpose"), "credit": "Superflight / Morkala", "sourceUrl": source["url"],
                       "movingReview": "current moving composite and final captions pending"}
                if "annotationWindowIndex" in segment:
                    cut["annotationWindowIndex"] = segment["annotationWindowIndex"]
                cuts.append(cut)
                source_usage.append((source["id"], segment["a"], segment["a"] + used))
                remaining -= used
                local_start += used
                if used < segment["b"] - segment["a"] and not available:
                    # Unused secondary capacity remains available to later scenes.
                    if source["id"] != media["primarySource"]["source"]["id"]:
                        secondary.insert(0, {**segment, "a": segment["a"] + used})
            win = windows[sid]
            marked = [c for c in cuts if c["scene"] == sid and c.get("annotationWindowIndex") == win["index"]]
            if len(marked) != 1:
                raise ValueError("Missing or duplicated locked annotation window")
            row["annotationWindow"] = {"sourceId": win["sourceId"], "sourceIn": win["a"] / FPS,
                                       "sourceOutExclusive": win["b"] / FPS, "startFrame": 0,
                                       "endFrame": win["b"] - win["a"], "globalStartFrame": cursor,
                                       "speechRebind": "first revised observation paragraph; final moving review pending"}
            row["cuts"] = [c for c in cuts if c["scene"] == sid]
        else:
            audio, pauses, evidence = pcm, [], {"status": "unchanged-original-pcm", "rawSamplesPreserved": True}
        row["observationPauses"], row["observationReview"] = pauses, evidence
        row["lineStarts"] = [obs.mapped_time(v, pauses) for v in row["rawLineStarts"]]
        row["voicePlacedSamples"] = len(audio)
        row["voicePlacementSeconds"] = len(audio) / SR
        row["placedVoice"] = relative(out / "placed-voice" / (sid + ".wav")) if pauses else row["voice"]
        if len(audio) > round(count / FPS * SR):
            raise ValueError("Placed voice exceeds measured scene slot")
        placed[sid] = audio
        cursor += count
    for source_id in catalog:
        used = sorted([(a, b) for source, a, b in source_usage if source == source_id])
        if any(a[1] > b[0] for a, b in zip(used, used[1:])):
            raise ValueError("Selected source interval reused; no output written")
    caption_rows = {}
    for lang in ("ko", "en"):
        converted = []
        for cue in read_srt(ROOT / manifest["paths"]["captions" + lang.title()]):
            scene = next((s for s in reversed(rows) if cue["start"] >= s["rawOrigin"] - 0.004), None)
            if scene is None:
                raise ValueError("Caption before first raw scene")
            local_a, local_b = cue["start"] - scene["rawOrigin"], cue["end"] - scene["rawOrigin"]
            if local_b > scene["voiceSeconds"] + 0.05:
                raise ValueError("Raw caption crosses scene voice boundary")
            converted.append({**cue, "scene": scene["id"],
                              "start": scene["start"] + obs.mapped_time(local_a, scene["observationPauses"]),
                              "end": scene["start"] + obs.mapped_time(local_b, scene["observationPauses"])})
        for a, b in zip(converted, converted[1:]):
            if a["end"] > b["start"] + 0.002:
                raise ValueError("Overlapping final captions after pause insertion")
        caption_rows[lang] = converted
    if len(caption_rows["ko"]) != len(caption_rows["en"]):
        raise ValueError("Bilingual cue count mismatch")
    if any(abs(k[key] - e[key]) > 0.002 for k, e in zip(caption_rows["ko"], caption_rows["en"]) for key in ("start", "end")):
        raise ValueError("Bilingual cue timing mismatch")
    result = {"schemaVersion": 2, "slug": PROJECT.name, "revision": "teaching-rules-v2",
              "timing": "measured-and-asr-aligned", "fps": FPS, "frames": cursor + 600, "totalFrames": cursor + 600,
              "seconds": (cursor + 600) / FPS, "bodyFrames": actual_frames + explanation_frames,
              "actualFrames": actual_frames, "explanationFrames": explanation_frames,
              "actualShare": 0.4, "explanationShare": 0.6, "ratioErrorFrames": 0,
              "introSeconds": 2, "outroSeconds": 10, "scenes": rows, "cuts": cuts,
              "sources": catalog, "captions": {lang: relative(out / f"captions.{lang}.srt") for lang in ("ko", "en")},
              "captionCount": len(caption_rows["ko"]), "koCaptions": caption_rows["ko"], "enCaptions": caption_rows["en"],
              "inputHashes": {relative(f): sha(f) for f in (manifest_file, lesson_file, timing_file, media_file, annotation_file)},
              "sourceIntervalsUnique": True, "sourceSpeed": 1, "sourceFreezeOrLoop": False,
              "annotationWindowsLocked": True, "speechAndAnnotationsMovingReview": "pending",
              "humanWholeListening": "pending"}
    if actual_frames * 3 != explanation_frames * 2:
        raise AssertionError("40:60 invariant failed")
    if not args.check_inputs:
        out.mkdir(parents=True, exist_ok=True)
        for scene in rows:
            if scene["observationPauses"]:
                file = ROOT / scene["placedVoice"]
                file.parent.mkdir(parents=True, exist_ok=True)
                sf.write(file, placed[scene["id"]], SR, subtype="FLOAT")
            scene["placedVoiceSha256"] = sha(ROOT / scene["placedVoice"])
        for lang in ("ko", "en"):
            write_srt(out / f"captions.{lang}.srt", caption_rows[lang])
        save(timeline_output, result)
    print(json.dumps({"outputWritten": not args.check_inputs, "frames": result["frames"], "seconds": result["seconds"],
                      "actualSeconds": actual_frames / FPS, "explanationSeconds": explanation_frames / FPS,
                      "cuts": len(cuts), "captions": result["captionCount"], "annotationWindowsLocked": True}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUT))
    parser.add_argument("--timeline", default=str(DEFAULT_TIMELINE))
    parser.add_argument("--check-inputs", action="store_true", help="Run measured validation/allocation without writing outputs")
    build(parser.parse_args())
