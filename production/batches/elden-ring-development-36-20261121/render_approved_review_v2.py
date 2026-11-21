"""Retime the existing visual edit against the approved voice, in a separate PC review version."""
import argparse
import math
from pathlib import Path
import time

import build_pc_review as edit
from make_approved_voice_v2 import DEFAULT_OUTPUT, pcm, pinned_plan, read, save, sha

ORIGINAL = DEFAULT_OUTPUT.with_name("pc-review-v1")
VOICENAME = "기존 쇼츠 승인 목소리 · Qwen3-TTS 1.7B"
LEAD_SECONDS = 0.13
CUE_END_CLEARANCE_SECONDS = 0.20


def route_clip(route, source_records, original_record, seconds):
    clip = edit.Clip(*route)
    source = source_records[clip.source]
    if source["sha256"] != original_record["sha256"] or clip.start != original_record["start"]:
        raise ValueError("The previously reviewed native footage input or start changed")
    if clip.start + seconds > source["seconds"]:
        raise ValueError(f"Native cut needs more footage than this source contains: {source['url']}")
    return clip, source


def collect_takes(episode, output):
    takes = []
    for index in range(4):
        key = f"{episode['id']}-{index}"
        source = output / "approved-voice" / f"{key}.wav"
        proof = output / "voice-qa-source" / f"{key}.json"
        if not source.is_file() or not proof.is_file():
            return None
        review = read(proof)
        receipt = pcm(source)
        if review["sha256"] != receipt["sha256"]:
            return None
        if not review["timestamped"] or review["similarity"] < .88:
            raise ValueError(f"Scene {key} needs audio review: similarity {review['similarity']:.3f}")
        takes.append({"path": source, "proof": proof, "review": review, **receipt})
    return takes


def scene_lengths(takes, earlier):
    frames = []
    for start in (0, 2):
        required = max(item["samples"] / item["sampleRate"] for item in takes[start:start + 2])
        required += LEAD_SECONDS + CUE_END_CLEARANCE_SECONDS
        # Each pair uses the same number of frames. A six-frame step gives the concat
        # demuxer an exact decimal duration at 60 fps.
        pair = max(earlier["cuts"][start]["frames"], math.ceil(required * 10) * 6)
        frames.extend((pair, pair))
    return frames


def picture(episode, index, frames, original, clips, destination, label):
    old_picture = original / f"{index}-{label}.mp4"
    prior_frames = read(original / "verification.json")["cuts"][index]["frames"]
    if frames == prior_frames and old_picture.is_file():
        # Reuse encoded video packets. The prior review and the new mix stay versioned independently.
        return old_picture, "prior-video-packets"
    target = destination / f"{index}-{label}.mp4"
    plate = destination / f"{index}-{label}.png"
    clip, source = clips[index // 2] if index % 2 == 0 else (None, None)
    model = None
    if index % 2 and episode["id"] in edit.MATCHED_DEMOS:
        model = edit.PAIR_REVIEW / edit.MATCHED_DEMOS[episode["id"]][index // 2]
        if not model.is_file():
            raise FileNotFoundError(model)
    edit.card(episode, index, clip, model, label == "captioned", plate)
    edit.overlay_clip(plate, source["path"] if source else None, clip, model, frames, target)
    return target, "same-native-source-retimed"


def narration_audio(takes, lengths, destination):
    pads = []
    for index, (take, frames) in enumerate(zip(takes, lengths, strict=True)):
        target = destination / f"scene-{index}-mix.wav"
        shift = -22 - take["review"]["levels"]["activeMedianDbfs"]
        if abs(shift) > 12:
            raise ValueError(f"Active narration level needs review: {take['file']}")
        edit.ffmpeg("-i", take["path"], "-af", f"volume={shift:.2f}dB,adelay=130:all=1,apad",
                    "-t", frames / edit.FPS, "-ar", 48000, "-ac", 1, target)
        pads.append(target)
    voice = destination / "narration-timed.wav"
    edit.ffmpeg("-f", "concat", "-safe", 0, "-i", edit.concat_list(pads, destination / "narration.txt"),
                "-c:a", "pcm_s16le", voice)
    return voice


def mix(episode, voice, seconds, destination):
    target = destination / "mix.m4a"
    voice_gain = -16.75 - edit.rms_measure(voice)["integratedLUFS"]
    filters = (
        f"[0:a]volume={voice_gain:.3f}dB,aformat=sample_rates=48000:channel_layouts=stereo,asplit[voice][key];"
        f"[1:a]volume=-13dB,afade=d=0.4,afade=t=out:st={seconds - 1}:d=1,"
        "aformat=sample_rates=48000:channel_layouts=stereo[bed];"
        "[bed][key]sidechaincompress=threshold=0.035:ratio=3:attack=25:release=240[ducked];"
        "[voice][ducked]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.79:level=false:latency=true[a]"
    )
    edit.ffmpeg("-i", voice, "-ss", 14 + int(episode["id"]) % 12 * 7, "-i", edit.MUSIC,
                "-filter_complex", filters, "-map", "[a]", "-t", seconds, "-c:a", "aac", "-b:a", "192k", target)
    return target


def srt(episode, takes, lengths, destination):
    offsets = []
    position = 0
    for take, frames in zip(takes, lengths, strict=True):
        intervals = take["review"]["timestamped"]
        positive = [(max(0, start["start"]), min(take["samples"] / take["sampleRate"], start["end"]))
                    for start in intervals]
        valid = [(a, b) for a, b in positive if b > a]
        if not valid:
            raise ValueError(f"No positive speech timestamps in {take['file']}")
        lo = max(0, math.floor((valid[0][0] + LEAD_SECONDS) * edit.FPS) - 2)
        hi = min(frames, math.ceil((valid[-1][1] + LEAD_SECONDS) * edit.FPS) + 8)
        if lo >= hi:
            raise ValueError(f"Bad subtitle anchors: {take['file']}")
        offsets.append((position + lo, position + hi))
        position += frames
    for suffix, script in (("ko", episode["narrationKo"]), ("en", episode["captionsEn"])):
        cues = [f"{n}\n{edit.code_time(lo)} --> {edit.code_time(hi)}\n{sentence}\n"
                for n, ((lo, hi), sentence) in enumerate(zip(offsets, script, strict=True), 1)]
        edit.exact_write(destination / f"{suffix}.srt", "\n".join(cues))
    return offsets


def movie(episode, takes, output, sources, route):
    number = episode["id"]
    original = ORIGINAL / number
    prior = read(original / "verification.json")
    dest = output / number
    dest.mkdir(exist_ok=True)
    lengths = scene_lengths(takes, prior)
    clips = [route_clip(route[n], sources, prior["cuts"][n * 2], lengths[n * 2] / edit.FPS) for n in range(2)]
    offsets = srt(episode, takes, lengths, dest)
    sound = mix(episode, narration_audio(takes, lengths, dest), sum(lengths) / edit.FPS, dest)
    outputs = {}
    picture_modes = {}
    for label in ("captioned", "clean"):
        shots = []
        for index, frames in enumerate(lengths):
            path, mode = picture(episode, index, frames, original, clips, dest, label)
            shots.append(path)
            picture_modes.setdefault(index, mode)
        listing = dest / f"{label}.txt"
        listing.write_text("".join(f"file '{item.as_posix()}'\n" for item in shots), encoding="utf-8")
        target = dest / f"{label}.mp4"
        edit.ffmpeg("-f", "concat", "-safe", 0, "-i", listing, "-i", sound,
                    "-map", "0:v", "-map", "1:a", "-c", "copy", "-movflags", "+faststart", target)
        outputs[label] = edit.validate(target, sum(lengths))
    cuts = []
    for index, frames in enumerate(lengths):
        row = {**prior["cuts"][index], "frames": frames, "picture": picture_modes[index],
               "voiceSha256": takes[index]["sha256"], "sourceVoiceProofSha256": sha(takes[index]["proof"]),
               "subtitleFrames": list(offsets[index])}
        if index % 2 == 0:
            row["end"] = row["start"] + frames / edit.FPS
        cuts.append(row)
    gameplay = sum(lengths[::2])
    assert gameplay == sum(lengths[1::2])
    report = {**outputs, "seconds": sum(lengths) / edit.FPS, "gameplaySeconds": gameplay / edit.FPS,
              "explanationSeconds": gameplay / edit.FPS, "missing": [], "cuts": cuts,
              "narration": VOICENAME, "music": edit.ATTRIBUTION, "priorPictureManifestSha256": sha(original / "verification.json"),
              "audio": edit.rms_measure(dest / "captioned.mp4"), "humanReview": "pending",
              "subtitles": {lang: sha(dest / f"{lang}.srt") for lang in ("ko", "en")}}
    save(dest / "verification.json", report)
    print(f"{number}: {report['seconds']:.1f}s, game and explanation {report['gameplaySeconds']:.1f}s each", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--watch", action="store_true")
    parser.add_argument("--only", nargs="*", default=[])
    args = parser.parse_args()
    sources, route = edit.open_inputs(ORIGINAL)
    remaining = [ep for ep in pinned_plan() if not args.only or ep["id"] in args.only]
    deadline = time.monotonic() + 7200
    blocked = {}
    while remaining:
        for episode in remaining[:]:
            number = episode["id"]
            try:
                takes = collect_takes(episode, args.output)
                if takes is None:
                    continue
                proof = args.output / number / "verification.json"
                cached = read(proof) if proof.is_file() else None
                if not cached or [cut["voiceSha256"] for cut in cached["cuts"]] != [item["sha256"] for item in takes]:
                    movie(episode, takes, args.output, sources, route[number])
                remaining.remove(episode)
                blocked.pop(number, None)
            except (OSError, RuntimeError, ValueError, AssertionError) as error:
                message = str(error)
                if blocked.get(number) != message:
                    print(f"{number} on hold: {message}", flush=True)
                blocked[number] = message
        if not remaining or not args.watch or time.monotonic() >= deadline:
            break
        time.sleep(10)
    print(f"Unfinished episodes: {[ep['id'] for ep in remaining]}", flush=True)


if __name__ == "__main__":
    main()
