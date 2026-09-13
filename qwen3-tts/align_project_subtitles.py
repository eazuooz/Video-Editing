"""Align approved script captions to local Whisper word timestamps.

Korean cue boundaries follow recognized words, not paragraph-length guesses.
English translation uses exactly the same cue times as the Korean subtitles.
The first timing entry retains the WAV scene origin for cut/mix synchronization.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path

import numpy as np
import soundfile as sf

from build_translated_srt import split_caption, timestamp, weight, wrapped_lines

ROOT = Path(__file__).resolve().parents[1]


def normalized(text: str) -> str:
    text = text.lower().replace("api", "에이피아이").replace("ai", "에이아이")
    return re.sub(r"[^가-힣a-z0-9]", "", text)


def partition_fixed(text: str, width: int, count: int) -> list[str]:
    """Balance a requested bilingual cue count without losing any words."""
    words = text.split()
    target = sum(weight(word) for word in words) / count

    @lru_cache(None)
    def solve(start: int, remaining: int):
        if not remaining:
            return (0.0, ()) if start == len(words) else (float('inf'), ())
        best = (float('inf'), ())
        for end in range(start + 1, len(words) - remaining + 2):
            segment = ' '.join(words[start:end])
            if len(wrapped_lines(segment, width)) > 2:
                break
            future, rest = solve(end, remaining - 1)
            cost = (weight(segment) - target)**2 + future
            if segment.endswith(('.', '?', '!', ',', ';')):
                cost -= target**2 * .35
            if cost < best[0]:
                best = (cost, (segment, *rest))
        return best

    score, result = solve(0, count)
    if not np.isfinite(score):
        raise ValueError(f'Cannot fit {count} bilingual captions into width {width}')
    return list(result)


def align_characters(text: str, words: list[dict], duration: float):
    expected = normalized(text)
    actual, starts, ends = "", [], []
    last = 0.0
    for word in words:
        token = normalized(word["text"])
        if not token:
            continue
        begin, end = word["timestamp"]
        begin = max(last, float(begin) if begin is not None else last)
        end = min(duration, max(begin, float(end) if end is not None else duration))
        begin = min(begin, end)
        actual += token
        starts.extend(np.linspace(begin, end, len(token), endpoint=False).tolist())
        ends.extend(np.linspace(begin, end, len(token) + 1)[1:].tolist())
        last = end
    matcher = SequenceMatcher(None, expected, actual, autojunk=False)
    positions, mapped_start, mapped_end = [], [], []
    for block in matcher.get_matching_blocks():
        for delta in range(block.size):
            positions.append(block.a + delta)
            mapped_start.append(starts[block.b + delta])
            mapped_end.append(ends[block.b + delta])
    coverage = len(positions) / max(1, len(expected))
    if coverage < .93:
        raise ValueError(f"Script/ASR match only {coverage:.1%}; inspect before captions")
    indices = np.arange(len(expected))
    char_start = np.maximum.accumulate(np.interp(indices, positions, mapped_start))
    char_end = np.maximum.accumulate(np.interp(indices, positions, mapped_end))
    return char_start, char_end, coverage


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    args = parser.parse_args()
    project = ROOT / "projects" / args.project
    manifest = json.loads((project / "project.json").read_text(encoding="utf-8"))
    output = (ROOT / manifest["tts"]["outputDir"]).resolve()
    output.relative_to(ROOT)
    stem = manifest["tts"]["filenameStem"]
    timing_path = output / f"{stem}.timing.json"
    timing = json.loads(timing_path.read_text(encoding="utf-8"))
    backup = output / f"{stem}.timing.unaligned.json"
    if not backup.exists():
        backup.write_text(json.dumps(timing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ko = json.loads((project / "script/narration.ko.json").read_text(encoding="utf-8"))
    en = json.loads((project / "script/narration.en.json").read_text(encoding="utf-8"))
    if len(ko["scenes"]) != len(en["scenes"]):
        raise ValueError("Translation scene mismatch")
    captions = {"ko": [], "en": []}
    evidence = []
    for scene, translation in zip(ko["scenes"], en["scenes"]):
        scene_id = scene["id"]
        if translation["id"] != scene_id or len(scene["lines"]) != len(translation["lines"]):
            raise ValueError(f"Translation mismatch scene {scene_id}")
        wav_path = output / "chunks" / f"{scene_id}-scene.wav"
        audio, sr = sf.read(wav_path)
        duration = len(audio) / sr
        asr = json.loads((output / "asr" / f"{scene_id}.json").read_text(encoding="utf-8"))
        if hashlib.sha256(wav_path.read_bytes()).hexdigest() != asr["audio_sha256"]:
            raise ValueError(f"Stale ASR cache scene {scene_id}; run review_project_narration.py again")
        starts, ends, coverage = align_characters(" ".join(scene["lines"]), asr["words"], duration)
        entries = [entry for entry in timing["entries"] if entry["scene_id"] == scene_id]
        if len(entries) != len(scene["lines"]):
            raise ValueError(f"Timing paragraph mismatch scene {scene_id}")
        origin = entries[0]["start"]
        cursor = 0
        for line_index, (line, english, entry) in enumerate(zip(scene["lines"], translation["lines"], entries)):
            length = len(normalized(line))
            begin = origin + float(starts[cursor])
            end = origin + float(ends[cursor + length - 1])
            entry["voice_start"] = begin
            entry["start"] = origin if line_index == 0 else begin
            entry["end"] = end
            entry["alignment"] = "whisper-word-timestamps-script-matched"
            cue_count = max(len(split_caption(line, 32)), len(split_caption(english, 46)))
            ko_chunks = partition_fixed(line, 32, cue_count)
            en_chunks = partition_fixed(english, 46, cue_count)
            offset = cursor
            for chunk, translated_chunk in zip(ko_chunks, en_chunks):
                count = len(normalized(chunk))
                a, b = origin + float(starts[offset]), origin + float(ends[offset + count - 1])
                captions["ko"].append((a, b, "\n".join(wrapped_lines(chunk, 32))))
                captions["en"].append((a, b, "\n".join(wrapped_lines(translated_chunk, 46))))
                offset += count
            if offset != cursor + length:
                raise ValueError("Korean caption text changed")
            cursor += length
        evidence.append({"scene":scene_id,"matchingCharacterCoverage":coverage,"wavSha256":asr["audio_sha256"],"narrationOrigin":origin,"lastRecognizedWordEnd":float(ends[-1]),"wavDuration":duration})
    for language, cues in captions.items():
        previous = 0.0
        blocks = []
        for index, (begin, end, text) in enumerate(cues, 1):
            if begin < previous - .002 or end <= begin:
                raise ValueError(f"Invalid {language} cue {index}: {begin}--{end}")
            previous = end
            blocks.append(f"{index}\n{timestamp(begin)} --> {timestamp(end)}\n{text}")
        destination = ROOT / manifest["paths"]["captionsKo" if language == "ko" else "captionsEn"]
        destination.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")
        print(f"{language}: {len(cues)} readable cues -> {destination}")
    timing["alignment"] = {"ko":"Whisper word timestamps matched to approved script; imperfect ASR matches interpolated", "en":"Same numbered cue boundaries as Korean; translation partitioned within corresponding paragraphs, not English speech", "paragraphCount":len(timing['entries']), "captionCount":len(captions['ko'])}
    timing_path.write_text(json.dumps(timing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / f"{stem}.alignment-review.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
