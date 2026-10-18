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
from difflib import SequenceMatcher
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import runpy
import subprocess
import sys

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
MAX_OBSERVATION_PAUSE_SECONDS = 6
QUIET_WINDOW_SECONDS = 0.080
MIN_ACTUAL_CUT_FRAMES = 120

# Only these additional, within-paragraph sentences invite a concrete
# observation. Abstract formula/implementation handoffs are not pause inventory.
# Existing paragraph boundaries still need the same sentence/ASR/PCM checks.
INTERNAL_OBSERVATION_PURPOSES = {
    "02": {1: "몸통과 날개옷에 시선을 둔 뒤 실제 기울기 변화를 관찰",
           3: "날개옷 옆 윤곽이 몸의 방향과 함께 달라지는 모습을 비교",
           4: "이미 본 방향·기울기·비틀림을 같은 비행에서 나눠 관찰",
           5: "몸과 함께 움직이는 카메라·배경의 영향을 구분"},
    "05": {1: "보이는 몸통 윤곽과 관찰 표시가 함께 움직이는지 확인",
           2: "날개옷 기울기와 몸의 긴 방향이 달라지는 모습을 나눠 관찰",
           3: "몸의 아래쪽과 화면 아래쪽이 달라지는 모습을 비교",
           4: "따라오는 카메라가 보이는 기울기를 바꾸는 상황을 관찰",
           6: "서로 다른 발췌 구간에서 표시가 지워지고 새 관찰을 시작하는지 확인"},
    "08": {1: "구조물 사이에서 몸통의 화면상 긴 방향이 달라지는 모습을 따라감",
           2: "몸통에 이어 날개옷의 기울기를 따로 관찰"},
    "11": {1: "급히 기울고 세로로 보이는 몸의 자세를 관찰",
           2: "카메라·주변 구조물과 몸의 보이는 기울기를 구분",
           3: "몸통과 날개옷이 함께 바뀌는 동안 중간 자세가 이어지는지 관찰"},
    "14": {1: "장애물 가까이에서 방향을 바꾸는 몸과 날개옷을 관찰",
           2: "시작·끝 화면뿐 아니라 그 사이의 회전 경로를 관찰"},
    "17": {1: "구조물 곁을 지나며 몸통·날개옷 모습이 계속 바뀌는지 관찰",
           2: "끝의 두 자세와 그 사이의 중간 자세를 나눠 관찰",
           3: "끝 자세를 저장하는 일과 달리 경로에서 필요한 중간 자세를 관찰",
           4: "발췌 구간 사이에서 관찰 표시가 초기화되는지 확인"},
    "20": {1: "중심 부근 점의 화면상 위치 변화를 따라감",
           2: "위치가 움직이는 동안 몸통·날개옷의 기울기 변화도 따로 관찰",
           3: "보이는 이동 경로를 회전축 화살표로 오해하지 않도록 몸의 자세와 구분",
           5: "움직이는 카메라와 화면상 기울기의 관계를 관찰",
           6: "발췌 구간이 바뀔 때 화면상 경로·관찰 표시가 초기화되는지 확인"},
    "23": {1: "몸통 표시와 날개옷 기울기를 차례로 따라감",
           2: "움직이는 위치와 순간 자세의 변화를 따로 관찰"},
}

PARAGRAPH_OBSERVATION_PURPOSES = {
    "02": ["몸의 보이는 기울기 변화", "옆 방향 변화와 위아래 방향 변화의 구분",
           "몸의 방향과 날개옷 비틀림의 변화", "방향·기울기·비틀림의 관찰 순서",
           "화면 방향과 몸의 방향을 섞지 않기", "정확한 각도 눈금이 아닌 관찰 안내의 역할"],
    "05": ["몸이 방향을 바꿀 때 보이는 윤곽", "몸통과 날개옷을 나눠 보는 효과",
           "몸 기준과 주변 기준의 방향 차이", "카메라가 보이는 기울기에 주는 영향",
           "보이지 않는 축을 측정했다고 오해하지 않기", "서로 다른 비행 구간 안에서만 변화 관찰"],
    "08": ["돌아 들어간 뒤 달라진 몸통 방향", "방향이 달라진 뒤의 날개옷 기울기",
           "고정축과 몸의 축을 구분해야 하는 관찰 상황", "한 구간 안의 몸통·날개옷 변화"],
    "11": ["화면에서 세로로 보이는 몸의 자세", "카메라 영향과 내부 회전 표현 추측의 구분",
           "중간 자세가 자연스럽게 이어져야 하는 상황", "실제 비행 관찰과 계산 모형의 역할 구분"],
    "14": ["장애물 가까이에서 몸·날개옷이 바뀌는 모습", "끝 자세 사이의 중간 경로",
           "자연스러운 가까운 경로가 필요한 관찰 상황", "실제 보이는 경로와 특정 함수 사용 주장의 구분"],
    "17": ["움직이는 동안 계속 바뀌는 몸통·날개옷", "끝 자세만으로 알 수 없는 중간 모습",
           "자연스러운 회전에 필요한 중간 자세", "서로 다른 비행을 한 경로로 잇지 않기"],
    "20": ["중심 부근 점의 화면상 위치 변화", "점의 이동과 몸의 자세 변화",
           "위치 경로와 회전량 정보의 구분", "비슷한 화살표 모양이어도 담는 정보가 다름",
           "화면 관찰과 따로 정의한 계산 모형의 구분", "각 발췌 구간 안의 이동·자세 변화"],
    "23": ["몸통과 날개옷을 차례로 관찰", "움직이는 위치와 몸의 회전 구분",
           "복잡한 겉모습에서 내부 각도 합산을 단정하지 않기", "보이는 움직임과 계산 규칙의 구분"],
}
_MATH_NORMALIZER = None


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


def math_normalizer():
    """Install the same established timing-only normalization as align-voice-v2.

    Import the existing helper under a non-main name. This neither runs its
    legacy batch nor edits shared code, PCM, expected text or raw ASR.
    """
    global _MATH_NORMALIZER
    if _MATH_NORMALIZER is None:
        helper = ROOT / "production/batches/game-math-part2-full-series/align.py"
        previous = sys.argv[:]
        sys.path.insert(0, str(ROOT / "qwen3-tts"))
        try:
            sys.argv = [str(helper), PROJECT.name]
            namespace = runpy.run_path(str(helper), run_name="m04_sentence_seam_normalization")
            _MATH_NORMALIZER = namespace["normalized"]
        finally:
            sys.argv = previous
    return _MATH_NORMALIZER


def sentence_observation_seams(audio, sr, lines, asr, sid):
    """Verify approved sentence ends against raw ASR words and actual80ms PCM.

    Every insertion point lies strictly between ASR word intervals; the complete
    low-energy window also fits inside that recognized gap. Some Korean ASR
    words omit punctuation: accept only the exact approved finite ending at a
    matched word end, with12 preceding and8 following normalized characters.
    The original punctuation/timestamps are preserved and recorded verbatim.
    """
    normalized = math_normalizer()
    words, actual = [], ""
    for index, word in enumerate(asr["words"]):
        token = normalized(word["text"])
        if token:
            words.append({**word, "index": index, "a": len(actual), "b": len(actual) + len(token)})
            actual += token
    sentences, expected = [], ""
    for line_index, line in enumerate(lines):
        parts = re.split(r"(?<=[.!?])\s+", line.strip())
        for sentence_index, text in enumerate(parts):
            token = normalized(text)
            sentences.append({"text": text, "line": line_index + 1, "sentenceInLine": sentence_index + 1,
                              "a": len(expected), "b": len(expected) + len(token),
                              "paragraphEnd": sentence_index == len(parts) - 1})
            expected += token
    if expected != normalized(" ".join(lines)):
        raise ValueError(f"{sid}: sentence splitting changed context-dependent normalized tokens")
    blocks = SequenceMatcher(None, expected, actual, autojunk=False).get_matching_blocks()
    mapping = {block.a + n: block.b + n for block in blocks for n in range(block.size)}
    coverage = len(mapping) / max(1, len(expected))
    if coverage < .93:
        raise ValueError(f"{sid}: scene ASR coverage{coverage:.1%} is below the established93% gate")
    scene_rms = float(np.sqrt(np.mean(audio ** 2)))
    threshold = min(.004, scene_rms * .14)
    half = round(QUIET_WINDOW_SECONDS * sr) // 2
    accepted, rejected = [], []
    for sentence_index, sentence in enumerate(sentences[:-1]):
        line = sentence["line"]
        if sentence["paragraphEnd"]:
            purpose = PARAGRAPH_OBSERVATION_PURPOSES[sid][line - 1]
            category = "paragraph"
        else:
            purpose = INTERNAL_OBSERVATION_PURPOSES[sid].get(line) if sentence["sentenceInLine"] == 1 else None
            category = "within-paragraph"
        if not purpose:
            continue
        row = {"afterLine": line, "afterSentence": sentence_index + 1,
               "sentenceInLine": sentence["sentenceInLine"], "boundaryKind": category,
               "approvedSentence": sentence["text"], "observationPurpose": purpose}

        def reject(reason):
            rejected.append({**row, "reason": reason})

        if not re.search(r"[.!?]$", sentence["text"]):
            reject("approved text is not a complete sentence ending")
            continue
        count = min(12, sentence["b"] - sentence["a"])
        suffix = [mapping.get(v) for v in range(sentence["b"] - count, sentence["b"])]
        if any(v is None for v in suffix) or suffix != list(range(suffix[0], suffix[0] + count)):
            reject("approved sentence-ending normalized suffix does not exactly match current ASR")
            continue
        index = next((i for i, word in enumerate(words) if word["b"] == suffix[-1] + 1), None)
        if index is None or index + 1 == len(words):
            reject("approved sentence end is not an ASR word boundary")
            continue
        word, following = words[index:index + 2]
        ending = normalized(sentence["text"].split()[-1])
        if not normalized(word["text"]).endswith(ending):
            reject("approved finite ending and current ASR ending differ")
            continue
        next_sentence = sentences[sentence_index + 1]
        next_count = min(8, next_sentence["b"] - next_sentence["a"])
        prefix = [mapping.get(v) for v in range(next_sentence["a"], next_sentence["a"] + next_count)]
        if prefix != list(range(following["a"], following["a"] + next_count)):
            reject("next approved sentence does not directly match the next ASR word")
            continue
        a, b = word["timestamp"]
        c, d = following["timestamp"]
        if None in (a, b, c, d) or b <= a or d <= c:
            reject("zero/null recognized word interval is not safe boundary evidence")
            continue
        row.update(asrEndingWord={"index": word["index"], "text": word["text"], "timestamp": word["timestamp"]},
                   nextAsrWord={"index": following["index"], "text": following["text"], "timestamp": following["timestamp"]},
                   normalizedEndingSuffix=expected[sentence["b"] - count:sentence["b"]],
                   asrPunctuationPresent=bool(re.search(r"[.!?][\"”’\)\]]*$", word["text"].strip())),
                   terminatorEvidence="exact approved finite ending at current ASR word end; next approved sentence also matched",
                   asrGapSeconds=c - b)
        left = max(half, math.ceil(b * sr) + half)
        right = min(len(audio) - half, math.floor(c * sr) - half)
        if left > right:
            reject("recognized inter-word gap cannot contain a complete80ms quiet window")
            continue
        intended, options = (b + c) / 2, []
        for sample in range(left, right + 1, max(1, round(.005 * sr))):
            energy = float(np.sqrt(np.mean(audio[sample - half:sample + half] ** 2)))
            if energy <= threshold:
                options.append((energy + abs(sample / sr - intended) * scene_rms * .015, sample))
        if not options:
            reject("no actual80ms low-energy window inside the recognized word gap")
            continue
        _, sample = min(options)
        radius = round(.004 * sr)
        lo, hi = max(left, sample - radius), min(right + 1, sample + radius + 1)
        sample = lo + int(np.argmin(np.abs(audio[lo:hi])))
        energy = float(np.sqrt(np.mean(audio[sample - half:sample + half] ** 2)))
        if energy > threshold:
            reject("near-zero sample adjustment no longer passes80ms low-energy threshold")
            continue
        at = sample / sr
        if not b <= at <= c or any(w["timestamp"][0] is not None and w["timestamp"][1] is not None and
                                   w["timestamp"][0] + .025 < at < w["timestamp"][1] - .025 for w in words):
            reject("seam intersects a current recognized word")
            continue
        if accepted and sample <= accepted[-1]["rawSample"]:
            raise ValueError(f"{sid}: sentence seams must be unique and monotonic")
        row.update(rawSample=sample, rawAt=at, seamRms=energy, seamThreshold=threshold,
                   quietWindowMilliseconds=80, quietWindowSamples=[sample - half, sample + half],
                   maxPauseSeconds=MAX_OBSERVATION_PAUSE_SECONDS)
        accepted.append(row)
    evidence = {"status": "approved-sentence-current-ASR-and-PCM-verified", "scene": sid,
                "normalizer": "Existing math align.py spoken-number/axis normalization; timing only, no shared edits",
                "normalizedSceneCoverage": coverage, "sceneRms": scene_rms, "seamThreshold": threshold,
                "acceptedParagraphSeams": sum(p["boundaryKind"] == "paragraph" for p in accepted),
                "acceptedWithinParagraphSeams": sum(p["boundaryKind"] == "within-paragraph" for p in accepted),
                "acceptedSeams": accepted, "rejectedSeams": rejected,
                "maximumIndividualPauseSeconds": MAX_OBSERVATION_PAUSE_SECONDS,
                "finalSceneTailIsNotASeam": True, "humanContextualListening": "pending realized joins"}
    return accepted, evidence


def place_verified_observation_pauses(audio, sr, seams, slot_seconds, seam_review):
    duration = len(audio) / sr
    extra = max(0., slot_seconds - duration - TAIL_SECONDS)
    if extra < .35:
        return audio, [], {"status": "not-needed", "rawSamplesPreserved": True, "sentenceSeamReview": seam_review}
    silence_samples = round(extra * sr)
    if not seams or silence_samples > len(seams) * round(MAX_OBSERVATION_PAUSE_SECONDS * sr):
        raise ValueError("Insufficient verified sentence-end observation capacity; never split words or extend pauses beyond6s")
    # Use every meaningful safe seam, keeping pauses as short and even as the
    # measured slot permits rather than filling the old paragraph ends to6s.
    per_seam, remainder = divmod(silence_samples, len(seams))
    pauses, pieces, kept, last = [], [], [], 0
    for index, candidate in enumerate(seams):
        count = per_seam + (index < remainder)
        if not count:
            continue
        pause = {**candidate, "silenceSamples": count, "seconds": count / sr}
        if pause["seconds"] > MAX_OBSERVATION_PAUSE_SECONDS:
            raise AssertionError("Individual observation pause exceeds6s")
        sample = pause["rawSample"]
        segment = audio[last:sample]
        pieces.extend([segment, np.zeros(count, dtype=audio.dtype)])
        kept.append(segment)
        pauses.append(pause)
        last = sample
    pieces.append(audio[last:])
    kept.append(audio[last:])
    placed, restored = np.concatenate(pieces), np.concatenate(kept)
    if not np.array_equal(restored, audio) or len(placed) != len(audio) + silence_samples:
        raise AssertionError("Original PCM samples must remain bit-identical and ordered")
    evidence = {"status": "distributed-at-approved-sentence-ASR-PCM-verified-seams", "quietWindowMilliseconds": 80,
                "rawSamplesPreserved": True, "rawSampleSha256": hashlib.sha256(audio.tobytes()).hexdigest(),
                "restoredSampleSha256": hashlib.sha256(restored.tobytes()).hexdigest(),
                "observationSeconds": silence_samples / sr, "seamsUsed": len(pauses),
                "maximumPauseSeconds": max(p["seconds"] for p in pauses),
                "minimumPauseSeconds": min(p["seconds"] for p in pauses),
                "trailingSeconds": slot_seconds - len(placed) / sr,
                "sourceSpeed": 1, "gameplayFreezeOrLoop": False, "sentenceSeamReview": seam_review}
    return placed, pauses, evidence


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


def split_observation_caption_cues(caption_rows, scene_rows, lesson):
    """Separate two bilingual cues that currently preview speech after a pause.

    Split display text only. Exact ends/starts come from the already verified
    Korean sentence-ending word and next word, using the unchanged pause map.
    The English parts are exact approved translations of the same two clauses.
    """
    scene_lookup = {s["id"]: s for s in scene_rows}
    lesson_lookup = {s["id"]: s for s in lesson["scenes"]}
    specifications = {93: ("08", 1), 167: ("14", 0)}
    evidence = []
    original_counts = {lang: len(caption_rows[lang]) for lang in ("ko", "en")}
    replacements = {"ko": {}, "en": {}}
    for source_cue, (sid, line_index) in specifications.items():
        scene, design = scene_lookup[sid], lesson_lookup[sid]
        pair, parts = {}, {}
        for lang in ("ko", "en"):
            matches = [r for r in caption_rows[lang] if r["sourceCue"] == source_cue]
            if len(matches) != 1 or matches[0]["scene"] != sid:
                raise ValueError(f"Expected one unchanged {lang} sourceCue{source_cue} in scene{sid}")
            row = matches[0]
            text = " ".join(row["text"].split())
            approved = " ".join(design[lang][line_index].split())
            first, separator, rest = text.partition(". ")
            first += "."
            if not separator or not rest or not approved.startswith(text) or not approved.startswith(first + " "):
                raise ValueError(f"{lang} sourceCue{source_cue}: current cue is not the approved two-clause prefix")
            pair[lang], parts[lang] = row, (first, rest)
        pauses = [p for p in scene["observationPauses"] if p["approvedSentence"] == parts["ko"][0]]
        if len(pauses) != 1:
            raise ValueError(f"sourceCue{source_cue}: require its verified approved-sentence observation seam")
        pause = pauses[0]
        raw_end = float(pause["asrEndingWord"]["timestamp"][1])
        raw_start = float(pause["nextAsrWord"]["timestamp"][0])
        if not raw_end <= pause["rawAt"] <= raw_start:
            raise ValueError("Caption split word boundary differs from its verified observation gap")

        def final_time(raw_time):
            return scene["start"] + raw_time + sum(p["seconds"] for p in scene["observationPauses"] if p["rawAt"] <= raw_time)

        end_before, start_after = final_time(raw_end), final_time(raw_start)
        item = {"sourceCue": source_cue, "scene": sid, "approvedLineIndex": line_index,
                "asrEndingWord": pause["asrEndingWord"], "nextAsrWord": pause["nextAsrWord"],
                "rawSceneSpeechEnd": raw_end, "rawSceneNextSpeechStart": raw_start,
                "insertedObservationSeconds": pause["seconds"],
                "blankCaptionInterval": [end_before, start_after],
                "meaning": "first sentence ends before observation; following approved clause begins only with its actual speech after observation",
                "languages": {}}
        for lang in ("ko", "en"):
            row, (first, rest) = pair[lang], parts[lang]
            if not row["start"] < end_before < start_after < row["end"]:
                raise ValueError(f"{lang} sourceCue{source_cue}: ASR split must stay inside the original mapped cue")
            children = [
                {**row, "text": first, "end": end_before, "sourceCuePart": 1},
                {**row, "text": rest, "start": start_after, "sourceCuePart": 2},
            ]
            for child in children:
                child.update(sourceCuePartCount=2, originalSourceCueText=row["text"],
                             originalMappedCueStart=row["start"], originalMappedCueEnd=row["end"],
                             partSourceStart=scene["rawOrigin"] + (raw_start if child["sourceCuePart"] == 2 else row["sourceStart"] - scene["rawOrigin"]),
                             partSourceEnd=scene["rawOrigin"] + (raw_end if child["sourceCuePart"] == 1 else row["sourceEnd"] - scene["rawOrigin"]))
            replacements[lang][source_cue] = children
            item["languages"][lang] = {"originalText": row["text"], "originalStart": row["start"], "originalEnd": row["end"],
                                       "approvedLine": design[lang][line_index],
                                       "parts": [{"text": c["text"], "start": c["start"], "end": c["end"], "sourceCuePart": c["sourceCuePart"]} for c in children]}
        evidence.append(item)
    for lang in ("ko", "en"):
        original = caption_rows[lang]
        updated = [child for row in original for child in replacements[lang].get(row["sourceCue"], [row])]
        if len(updated) != original_counts[lang] + len(specifications):
            raise AssertionError("Each selected source cue must produce exactly two final cues")
        for index, row in enumerate(updated, 1):
            row["finalCue"] = index
            if row["end"] <= row["start"]:
                raise ValueError("Split caption must have positive actual speech duration")
        for left, right in zip(updated, updated[1:]):
            if left["end"] > right["start"] + .002:
                raise ValueError("Split caption overlaps its neighboring cue")
        caption_rows[lang] = updated
        for item in evidence:
            item["languages"][lang]["finalCueNumbers"] = [r["finalCue"] for r in updated if r["sourceCue"] == item["sourceCue"]]
    if [(r["start"], r["end"]) for r in caption_rows["ko"]] != [(r["start"], r["end"]) for r in caption_rows["en"]]:
        raise AssertionError("KO/EN split caption times differ")
    return {"status": "two-approved-bilingual-cues-split-at-current-ASR-sentence-gap", "sourceCueCount": original_counts,
            "finalCueCount": {lang: len(caption_rows[lang]) for lang in ("ko", "en")}, "splits": evidence,
            "sourceBodySrtUnmodified": True, "audioAndSceneTimingUnchanged": True,
            "unselectedCueTextAndTimesUnchanged": True}


def canonical_caption_display(caption_rows, speech_contract):
    """Change display spelling only; retain every measured cue and spoken text.

    This lesson-specific list deliberately does not replace Korean 이/비/피/알
    globally. In particular, ordinary '알 수', numeric '이 파이', and particles
    remain untouched. No whole-formula or spoken-number conversion is performed.
    """
    axis_scenes = {"03", "04", "06", "07", "10", "12", "18", "22", "24", "25"}
    pi_scenes = {"13", "15", "19", "22", "25"}
    # Longer names/products precede their individual pronunciation aliases.
    ko_rules = [
        ("wrapPi", {"13", "25"}, r"랩\s*파이", "wrapPi"),
        ("std::remainder", {"15"}, r"표준\s+라이브러리의\s+리메인더", "std::remainder"),
        ("R", {"03"}, r"회전\s+행렬\s+알", "회전 행렬 R"),
        ("n-unit-vector", {"18"}, r"단위벡터\s+엔", "단위벡터 n"),
        ("n-unit-axis", {"19"}, r"단위축\s+엔", "단위축 n"),
        ("theta-n-product", {"19"}, r"세타\s+엔", "θn"),
        # '즉' starts the following measured cue here. The approved scene19
        # definition plus the exact '벡터 이,' phrase supplies the context.
        ("e-rotation-vector", {"19"}, r"벡터\s+이(?=,)", "벡터 e"),
        ("theta", {"18", "19"}, r"세타", "θ"),
        ("t-interpolation", {"13"}, r"비율\s+티", "비율 t"),
        ("delta", {"13", "15", "25"}, r"델타", "Δ"),
        ("omega", {"24"}, r"오메가", "ω"),
        ("axis-X", axis_scenes, r"엑스", "X"),
        ("axis-Y", axis_scenes, r"와이", "Y"),
        ("axis-Z", axis_scenes, r"제트", "Z"),
        ("pi", pi_scenes, r"파이", "π"),
    ]
    en_rules = [
        ("std::remainder", {"15"}, r"The standard remainder function", "std::remainder"),
        ("theta", {"18", "19"}, r"\btheta\b", "θ"),
        ("pi", pi_scenes, r"\bpi\b", "π"),
        ("axis-X", axis_scenes, r"\bx\b", "X"),
        ("axis-Y", axis_scenes, r"\by\b", "Y"),
        ("axis-Z", axis_scenes, r"\bz\b", "Z"),
        ("axis-angle-name", {"18", "26"}, r"\baxis-angle\b", "axis–angle"),
        ("Axis-angle-name", {"26"}, r"\bAxis-angle\b", "Axis–angle"),
    ]
    audit, adjacent_pairs, matched_aliases = {}, {}, {}
    for lang, rules in (("ko", ko_rules), ("en", en_rules)):
        rows = caption_rows[lang]
        unchanged_times = [(row["start"], row["end"]) for row in rows]
        # Inspect concatenated neighboring cues before per-cue substitution.
        # Never silently produce 'wrap'/'Pi' or a leftover half alias. Current
        # measured cues keep every function/product alias atomic; a future split
        # must receive an explicit, reviewed display map instead of retiming.
        adjacent_pairs[lang], matched_aliases[lang] = 0, 0
        for sid in dict.fromkeys(row["scene"] for row in rows):
            group = [row for row in rows if row["scene"] == sid]
            text, bounds = "", []
            for row in group:
                part = " ".join(row["text"].split())
                if text:
                    text += " "
                bounds.append((len(text), len(text) + len(part), row["sourceCue"]))
                text += part
            adjacent_pairs[lang] += max(0, len(group) - 1)
            for rule, scenes, pattern, replacement in rules:
                if sid not in scenes:
                    continue
                for match in re.finditer(pattern, text):
                    cues = [cue for a, b, cue in bounds if a < match.end() and b > match.start()]
                    matched_aliases[lang] += 1
                    if len(cues) != 1:
                        raise ValueError(f"{lang} scene{sid} canonical alias {rule} crosses measured cues{cues}; require an atomic display map, never split a function or change cue times")
        audit[lang] = []
        for row in rows:
            original = row["text"]
            text, changes = " ".join(original.split()), []
            for rule, scenes, pattern, replacement in rules:
                if row["scene"] not in scenes:
                    continue
                before = text
                text, count = re.subn(pattern, replacement, text)
                if count:
                    changes.append({"rule": rule, "count": count, "before": before, "after": text})
            # The first formal Korean/English term is already independently
            # written in the approved lesson; only aliases above are changed.
            row.update(spokenText=original, text=text if changes else original)
            audit[lang].append({"sourceCue": row["sourceCue"], "finalCue": row.get("finalCue", row["sourceCue"]),
                                "sourceCuePart": row.get("sourceCuePart", 1), "scene": row["scene"],
                                "sourceStart": row["sourceStart"], "sourceEnd": row["sourceEnd"],
                                "start": row["start"], "end": row["end"], "spokenText": original,
                                "displayText": row["text"], "changes": changes})
            if not row["text"].strip():
                raise ValueError("Canonical display conversion must not create an empty cue")
        if [(row["start"], row["end"]) for row in rows] != unchanged_times:
            raise AssertionError("Display conversion changed measured caption times")
    names = [
        ("오일러 각", "Euler angles", "오일러 각 (Euler angles)"),
        ("짐벌락", "gimbal lock", "짐벌락 (Gimbal lock)"),
        ("월드 좌표계", "world frame", "월드 좌표계 (World frame)"),
        ("몸체 좌표계", "body frame", "몸체 좌표계 (Body frame)"),
        ("내재적 회전", "intrinsic rotation", "내재적 회전 (Intrinsic rotation)"),
        ("외재적 회전", "extrinsic rotation", "외재적 회전 (Extrinsic rotation)"),
        ("축·각 표현", "axis–angle representation", "축·각 표현 (Axis–angle)"),
        ("회전벡터", "rotation vector", "회전벡터 (Rotation vector)"),
        ("지수 사상", "exponential map", "지수 사상 (Exponential map)"),
        ("정규화", "normalization", "정규화 (Normalization)"),
    ]
    terminology = []
    for ko_name, en_name, ui in names:
        first = {}
        for lang, name in (("ko", ko_name), ("en", en_name)):
            row = next((r for r in caption_rows[lang] if name.casefold() in " ".join(r["text"].split()).casefold()), None)
            if row is None:
                raise ValueError(f"Missing approved canonical first term: {lang} {name}")
            first[lang] = {"term": name, "sourceCue": row["sourceCue"], "finalCue": row.get("finalCue", row["sourceCue"]),
                           "scene": row["scene"], "displayText": row["text"]}
        terminology.append({"canonicalUiLabel": ui, "firstAppearance": first})
    return {"policy": "M04-speech-aliases-separated-from-canonical-caption-display-v1",
            "speechContract": speech_contract, "cueMap": audit, "canonicalFirstTerms": terminology,
            "changedCues": {lang: sum(bool(c["changes"]) for c in rows) for lang, rows in audit.items()},
            "crossCueAliasReview": {"adjacentPairsChecked": adjacent_pairs, "aliasMatchesChecked": matched_aliases,
                                    "splitAliasCount": 0, "functionNamesAtomic": True},
            "measuredCueTimesAndCountsUnchanged": True, "sourceBodySrtUnmodified": True,
            "ordinaryKoreanLettersNotGloballyReplaced": ["이", "비", "피", "알"],
            "canonicalAxisDisplay": "X/Y/Z per approved speechContract; formula subscripts and matrices keep their separately authored UI spelling",
            "wholeFormulaOrNumberConversion": False,
            "widthValidation": "Existing prepare-captions.py real48px/1570px/two-line gate remains required"}


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
        # Balance observation time per verified meaningful seam across scenes.
        # A longer spoken scene must not automatically receive longer pauses
        # when another scene offers more short, safe observation opportunities.
        selected = min(eligible, key=lambda s: (
            (s["frames"] - s["minimumFrames"]) / max(1, s.get("verifiedObservationSeams", 1)),
            s["frames"] / s["minimumFrames"], s["id"]))
        selected["frames"] += 1
        required -= 1
    return actual_target, explanation_target


def allocate_actual_source_ranges(sid, frames, primary, secondary):
    """Fill a fixed actual scene using unique inspected shots of at least2s.

    Only the shared secondary queue is consumed. Tiny primary fragments made by
    reserving an annotation, and tiny secondary tails, are deliberately unused.
    No voice/timing/frame-budget or source-speed adjustment is allowed here.
    """
    available = [dict(v) for v in primary]
    selected, skipped, adjusted = [], [], []
    remaining = frames
    while remaining:
        if remaining < MIN_ACTUAL_CUT_FRAMES:
            raise ValueError(f"{sid}: allocator left an invalid final{remaining}frame cut")
        if available:
            segment, pool = available.pop(0), "primary"
        elif secondary:
            segment, pool = secondary.pop(0), "secondary"
        else:
            raise ValueError(f"{sid}: inspected footage exhausted after excluding short source fragments")
        span = segment["b"] - segment["a"]
        locked = "annotationWindowIndex" in segment
        minimum = max(MIN_ACTUAL_CUT_FRAMES, segment.get("lockedWindowEnd", segment["a"]) - segment["a"])
        summary = {"sourceId": segment["sourceId"], "sourceInFrame": segment["a"],
                   "sourceOutFrame": segment["b"], "frames": span, "pool": pool}
        if span < MIN_ACTUAL_CUT_FRAMES:
            if locked:
                raise ValueError(f"{sid}: locked annotation source is shorter than the minimum actual cut")
            skipped.append({**summary, "reason": "source fragment shorter than120frames"})
            continue
        used = min(remaining, span)
        after = remaining - used
        if 0 < after < MIN_ACTUAL_CUT_FRAMES:
            # Reserve a whole final2s shot now, rather than creating a flash
            # and discovering it after audio/captions have already been built.
            shortened = used - (MIN_ACTUAL_CUT_FRAMES - after)
            if shortened < minimum:
                if locked:
                    raise ValueError(f"{sid}: fixed scene cannot preserve its annotation and a final2s shot")
                skipped.append({**summary, "reason": "shot cannot leave a final120frame clip without itself becoming too short"})
                continue
            adjusted.append({**summary, "originalUseFrames": used, "selectedFrames": shortened,
                             "reason": "reserve at least120frames for final shot"})
            used = shortened
        if used < minimum:
            raise ValueError(f"{sid}: selected cut would truncate an annotation or fall below120frames")
        selected.append({**segment, "b": segment["a"] + used})
        remaining -= used
        tail = span - used
        if pool == "secondary" and tail:
            remainder = {**segment, "a": segment["a"] + used}
            if tail >= MIN_ACTUAL_CUT_FRAMES:
                secondary.insert(0, remainder)
            else:
                skipped.append({"sourceId": segment["sourceId"], "sourceInFrame": remainder["a"],
                                "sourceOutFrame": segment["b"], "frames": tail, "pool": "secondary-tail",
                                "reason": "do not reinsert a secondary tail shorter than120frames"})
    if sum(v["b"] - v["a"] for v in selected) != frames or any(v["b"] - v["a"] < MIN_ACTUAL_CUT_FRAMES for v in selected):
        raise AssertionError(f"{sid}: fixed frame budget / minimum actual-cut invariant failed")
    if any("annotationWindowIndex" in v for v in primary):
        if not selected or "annotationWindowIndex" not in selected[0]:
            raise AssertionError(f"{sid}: annotation must remain the first actual shot")
    review = {"status": "fixed-scene-source-only-allocation-validated", "minimumCutFrames": MIN_ACTUAL_CUT_FRAMES,
              "minimumCutSeconds": MIN_ACTUAL_CUT_FRAMES / FPS, "sceneFrames": frames,
              "selectedFrames": sum(v["b"] - v["a"] for v in selected),
              "minimumSelectedCutFrames": min(v["b"] - v["a"] for v in selected),
              "skippedFragments": skipped, "shortFinalCutPrevention": adjusted,
              "voiceAndCaptionTimingChanged": False, "sourceSpeed": 1, "freezeOrLoop": False}
    return selected, review


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
        seams, seam_review = [], {}
        if row["kind"] == "actual":
            seams, seam_review = sentence_observation_seams(pcm, rate, spoken["lines"], asr, sid)
            capacity = len(pcm) / rate + TAIL_SECONDS + len(seams) * MAX_OBSERVATION_PAUSE_SECONDS
            row["quietCapacityFrames"] = max(minimum, math.floor(capacity * FPS + 1e-7))
            row["verifiedObservationSeams"] = len(seams)
        rows.append(row)
        raw[sid] = (pcm, cues, asr, seams, seam_review)
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
        pcm, cues, asr, seams, seam_review = raw[sid]
        if row["kind"] == "actual":
            audio, pauses, evidence = place_verified_observation_pauses(pcm, SR, seams, count / FPS, seam_review)
            # A low-energy stop consonant is not permission to split a word.
            for pause in pauses:
                at = pause["rawAt"]
                for word in asr["words"]:
                    a, b = word["timestamp"]
                    if a is not None and b is not None and a + 0.025 < at < b - 0.025:
                        raise ValueError(f"Scene{sid}: quiet seam intersects recognized word {word['text']!r}; inspect a bounded seam")
            selected_ranges, row["sourceAllocationReview"] = allocate_actual_source_ranges(sid, count, primary[sid], secondary)
            local_start = 0
            for segment in selected_ranges:
                used = segment["b"] - segment["a"]
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
                local_start += used
            if local_start != count:
                raise AssertionError("Actual source allocation changed a fixed scene frame budget")
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
    if not cuts or any(c["frames"] < MIN_ACTUAL_CUT_FRAMES for c in cuts):
        raise ValueError("Actual source cuts must each be at least120frames /2seconds")
    caption_rows = {}
    for lang in ("ko", "en"):
        converted = []
        for source_cue, cue in enumerate(read_srt(ROOT / manifest["paths"]["captions" + lang.title()]), 1):
            scene = next((s for s in reversed(rows) if cue["start"] >= s["rawOrigin"] - 0.004), None)
            if scene is None:
                raise ValueError("Caption before first raw scene")
            local_a, local_b = cue["start"] - scene["rawOrigin"], cue["end"] - scene["rawOrigin"]
            if local_b > scene["voiceSeconds"] + 0.05:
                raise ValueError("Raw caption crosses scene voice boundary")
            converted.append({**cue, "scene": scene["id"], "sourceCue": source_cue,
                              "sourceStart": cue["start"], "sourceEnd": cue["end"],
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
    if ko["speechContract"] != lesson["canonicalTerminology"]:
        raise ValueError("Spoken/display alias contract differs between current script and lesson")
    caption_split_review = split_observation_caption_cues(caption_rows, rows, lesson)
    caption_display = canonical_caption_display(caption_rows, ko["speechContract"])
    caption_display.update(observationPauseCueSplits=caption_split_review,
                           canonicalDisplayConversionPreservesInputCueTimesAndCounts=True,
                           measuredCueTimesAndCountsUnchanged=False,
                           onlyTwoApprovedObservationCueSplits=True,
                           allOtherSourceCueTextAndTimesUnchanged=True)
    result = {"schemaVersion": 2, "slug": PROJECT.name, "revision": "teaching-rules-v2",
              "timing": "measured-and-asr-aligned", "fps": FPS, "frames": cursor + 600, "totalFrames": cursor + 600,
              "seconds": (cursor + 600) / FPS, "bodyFrames": actual_frames + explanation_frames,
              "actualFrames": actual_frames, "explanationFrames": explanation_frames,
              "actualShare": 0.4, "explanationShare": 0.6, "ratioErrorFrames": 0,
              "introSeconds": 2, "outroSeconds": 10, "scenes": rows, "cuts": cuts,
              "sources": catalog, "captions": {lang: relative(out / f"captions.{lang}.srt") for lang in ("ko", "en")},
              "captionCount": len(caption_rows["ko"]), "koCaptions": caption_rows["ko"], "enCaptions": caption_rows["en"],
              "captionDisplayReview": caption_display,
              "inputHashes": {relative(f): sha(f) for f in (manifest_file, lesson_file, timing_file, media_file, annotation_file,
                  Path(__file__).resolve(), ROOT / "production/batches/game-math-part2-full-series/align.py",
                  ROOT / "qwen3-tts/align_project_subtitles.py", ROOT / manifest["paths"]["script"],
                  ROOT / manifest["paths"]["scriptEn"], ROOT / manifest["paths"]["captionsKo"],
                  ROOT / manifest["paths"]["captionsEn"])},
              "sourceIntervalsUnique": True, "sourceSpeed": 1, "sourceFreezeOrLoop": False,
              "actualCutValidation": {"status": "passed", "minimumRequiredFrames": MIN_ACTUAL_CUT_FRAMES,
                  "minimumSelectedFrames": min(c["frames"] for c in cuts), "selectedCutCount": len(cuts),
                  "subminimumCuts": 0, "sceneFrameBudgetsUnchangedBySourceAllocation": True},
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
