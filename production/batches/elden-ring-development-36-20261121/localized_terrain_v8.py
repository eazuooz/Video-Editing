"""Integrate the reviewed 07-1 voice, leaving the other three dry scenes byte-exact."""
from copy import deepcopy
from pathlib import Path
import wave

import build_pc_review as edit
import render_clarity_music_v5 as music
import render_established_format_v6 as layout
from make_approved_voice_v2 import DEFAULT_OUTPUT, pcm, read, sha
from render_approved_review_v2 import LEAD_SECONDS


EPISODE = "07"
SCENE = 1
OUTPUT = DEFAULT_OUTPUT.parent / "pc-review-v8" / "terrain-voice-clean"
ORIGINAL = DEFAULT_OUTPUT.parent / "pc-review-v6" / EPISODE
ORIGINAL_SAMPLES_PER_FRAME = 800


def replacement_source():
    raw = OUTPUT / "07-1.wav"
    proof = OUTPUT / "07-1-source-review.json"
    review = read(proof)
    raw_info = pcm(raw)
    if not review["approvedForEdit"] or not review["ending"]["passes"]:
        raise ValueError("07-1 source narration still needs a clean-ended exact read-back")
    if (review["sha256"], review["samples"], review["sampleRate"]) != (
        raw_info["sha256"], raw_info["samples"], raw_info["sampleRate"],
    ):
        raise ValueError("07-1 raw audio differs from its independently reviewed WAV")
    return raw, proof, review, raw_info


def dry_narration(record, frames, raw, review, raw_info, work):
    prior = music.exact_voice(EPISODE, frames)
    if sha(prior) != record["music"]["mixEvidence"]["dryNarrationSha256"]:
        raise ValueError("Original dry dialogue no longer matches its PC review")
    new_scene = work / "07-1-timed.wav"
    shift = -22 - review["levels"]["activeMedianDbfs"]
    if abs(shift) > 12:
        raise ValueError("07-1 active narration needs a level review")
    duration = raw_info["samples"] / raw_info["sampleRate"]
    if duration + LEAD_SECONDS + .20 > frames[SCENE] / edit.FPS:
        raise ValueError("07-1 speech exceeds the original shot duration")
    fade_start = duration - .006
    filters = (f"volume={shift:.2f}dB,afade=d=0.006,afade=t=out:st={fade_start:.5f}:d=0.006,"
               f"adelay={round(LEAD_SECONDS * 1000)}:all=1,apad")
    edit.ffmpeg("-i", raw, "-af", filters, "-t", frames[SCENE] / edit.FPS,
                "-ar", 48000, "-ac", 1, new_scene)
    edited = work / "narration-timed.wav"
    with wave.open(str(prior), "rb") as old, wave.open(str(new_scene), "rb") as changed:
        if (old.getframerate(), old.getsampwidth(), old.getnchannels()) != (
            changed.getframerate(), changed.getsampwidth(), changed.getnchannels(),
        ):
            raise ValueError("Replacement scene format differs from the exact prior audio")
        with wave.open(str(edited), "wb") as output:
            output.setparams(old.getparams())
            for index, frame_count in enumerate(frames):
                sample_count = frame_count * ORIGINAL_SAMPLES_PER_FRAME
                untouched = old.readframes(sample_count)
                replacement = changed.readframes(sample_count) if index == SCENE else untouched
                if len(replacement) != sample_count * old.getsampwidth():
                    raise ValueError("Dry audio scene duration changed")
                output.writeframesraw(replacement)
    with wave.open(str(prior), "rb") as old, wave.open(str(edited), "rb") as new:
        for index, frame_count in enumerate(frames):
            before = old.readframes(frame_count * ORIGINAL_SAMPLES_PER_FRAME)
            after = new.readframes(frame_count * ORIGINAL_SAMPLES_PER_FRAME)
            if (before == after) == (index == SCENE):
                raise ValueError(f"Unexpected dry narration change at 07-{index}")
    return edited


def visual_lines(text, font):
    if font.getlength(text) <= 800:
        return [text]
    words = text.split()
    options = []
    for cut in range(1, len(words)):
        parts = [" ".join(words[:cut]), " ".join(words[cut:])]
        widths = [font.getlength(part) for part in parts]
        if max(widths) <= 800:
            options.append((abs(widths[0] - widths[1]), parts))
    if not options:
        raise ValueError("07-1 sentence cannot fit two caption lines at the approved font size")
    return min(options)[1]


def replacement_paragraph(paragraph, review, proof, raw, cut):
    revised = deepcopy(paragraph)
    font = layout.compositor(read(layout.FORMAT), EPISODE).caption
    offset = paragraph["sceneStartFrame"] / edit.FPS + LEAD_SECONDS
    cues = []
    next_word = 0
    words = review["timestamped"]
    for sentence in review["sentenceIntervals"]:
        limit = next(i for i in range(next_word, len(words)) if words[i]["end"] == sentence["end"])
        if words[next_word]["start"] != sentence["start"]:
            raise ValueError("07-1 subtitle does not start at a verified complete word")
        start = offset + sentence["start"]
        end = offset + sentence["end"]
        lines = visual_lines(sentence["ko"], font)
        cues.append({
            "text": sentence["ko"], "lines": lines, "startSeconds": round(start, 4),
            "endSeconds": round(end, 4), "startFrame": round(start * edit.FPS),
            "endFrame": round(end * edit.FPS), "sourceStartSeconds": sentence["start"],
            "sourceEndSeconds": sentence["end"], "sourceWordIndices": [next_word, limit + 1],
            "sourceFirstWord": words[next_word]["text"].strip(),
            "sourceLastWord": words[limit]["text"].strip(),
            "maxLineWidth": max(font.getlength(line) for line in lines),
        })
        next_word = limit + 1
    if len(cues) != 2 or next_word != len(words) or not (
        paragraph["sceneStartFrame"] <= cues[0]["startFrame"] < cues[0]["endFrame"]
        <= cues[1]["startFrame"] < cues[1]["endFrame"] <= paragraph["sceneStartFrame"] + cut["frames"]
    ):
        raise ValueError("07-1 replacement cue bounds changed")
    revised.update(
        sourceProof=str(proof), sourceProofSha256=sha(proof), sourceVoiceSha256=sha(raw),
        originalKo=review["expected"], originalEn=review["identity"]["narrationEn"],
        englishOriginalFrameRange=[cues[0]["startFrame"], cues[-1]["endFrame"]],
        cues=cues, alignmentNotes={
            "timestampSource": review["timestampType"], "lexicalDifferences": review["differences"],
            "treatment": "Exact source narration and complete ASR word onset and offset for both sentences.",
            "english": "Each translated clause uses the whole spoken sentence range.",
        },
    )
    return revised


def english_subtitles(record, review, paragraph):
    old = ORIGINAL / "en.srt"
    if sha(old) != record["subtitles"]["en"]:
        raise ValueError("Original English subtitle source changed")
    blocks = old.read_text(encoding="utf-8").strip().split("\n\n")
    if len(blocks) != len(record["cuts"]):
        raise ValueError("Expected one original English cue per 07 scene")
    old_cues = [block.split("\n", 1)[1] for block in blocks]
    new_cues = [
        f'{edit.code_time(cue["startFrame"])} --> {edit.code_time(cue["endFrame"])}\n{sentence["en"]}'
        for cue, sentence in zip(paragraph["cues"], review["sentenceIntervals"], strict=True)
    ]
    old_cues[SCENE:SCENE + 1] = new_cues
    return "\n\n".join(f"{i}\n{cue}" for i, cue in enumerate(old_cues, 1)) + "\n"


def localized_terrain_v8(record, paragraphs, work):
    raw, proof, review, raw_info = replacement_source()
    frames = [cut["frames"] for cut in record["cuts"]]
    if frames != [660, 660, 720, 720]:
        raise ValueError("Episode 07 must keep its reviewed 23-second/23-second edit")
    cut = record["cuts"][SCENE]
    if cut["voiceSha256"] != review["identity"]["originalTakeSha256"]:
        raise ValueError("07-1 source narration no longer matches the reviewed cut")
    lesson = next(item for item in paragraphs if item["id"] == "07-1")
    revised = replacement_paragraph(lesson, review, proof, raw, cut)
    english = english_subtitles(record, review, revised)
    work = Path(work) / "terrain-07-localized-audio"
    work.mkdir(parents=True, exist_ok=True)
    voice = dry_narration(record, frames, raw, review, raw_info, work)
    mix_path, mix_evidence = music.mixed_sound(EPISODE, record["music"], frames, work, voice=voice)
    cut.update(voiceSha256=raw_info["sha256"], sourceVoiceProofSha256=sha(proof),
               subtitleFrames=revised["englishOriginalFrameRange"])
    record["music"]["mixEvidence"] = mix_evidence
    record["audio"] = {key: mix_evidence[key] for key in ("integratedLUFS", "truePeakDbTP")}
    record["existingNarrationPreserved"] = False
    record["previousAudioTrackPreserved"] = False
    record["localizedNarration"] = {
        "scene": "07-1", "source": str(raw), "sourceReview": str(proof),
        "wholeWordSentenceIntervals": review["sentenceIntervals"], "voice": str(voice),
        "otherDryScenesByteExact": True, "mixedFinalReadback": "pending",
    }
    return [revised if item is lesson else item for item in paragraphs], mix_path, english
