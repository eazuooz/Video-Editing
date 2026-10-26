"""Align approved spoken clauses to current complete voice ASR word timestamps.

No ASR, TTS, rendering or work runs on import. Content must match exactly after
normalization and any explicitly reviewed, voice-hash-bound aliases. No missing
words or sentence endings are filled with guessed timestamps.
"""
from pathlib import Path
import argparse
import bisect
import copy
import difflib
import hashlib
import json
import math
import re
import struct
import unicodedata

P = Path(__file__).resolve().parents[1]
R = P.parents[1]
from audio_revision import L, VOICE, REVISION, normalize_speech, guard as revision_guard
FPS = 60
VOICE_OFFSET = 0.20
TAIL_SECONDS = 0.40
DEFAULT_VOICE = (
    "projects/shorts-splatoon-ink-readability/production/local/audio-v2/voice/"
    "narration.wav"
)
ASS_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Text,Malgun Gothic,60,&H00090B08,&H00090B08,&H00181B16,&H00000000,1,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: Box,Malgun Gothic,60,&H00FFFFFF,&H00FFFFFF,&H00181B16,&H00000000,0,0,0,0,100,100,0,0,1,3,0,7,0,0,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def read(path):
    return json.loads(Path(path).read_text(encoding="utf8"))


def sha(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def encoded(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def relative(path):
    try:
        return Path(path).resolve().relative_to(R.resolve()).as_posix()
    except ValueError:
        return str(Path(path).resolve())


def normalized(text):
    return normalize_speech(text, read(P / "production/clauses.json").get("pronunciationAliases", {}))


def select_asr(requested, voice_sha, duration, reason=None):
    """Select one complete raw report explicitly; never splice successful words."""
    original = L / f"asr-voice-{voice_sha[:12]}.json"
    selected = Path(requested) if requested else original
    if not selected.is_absolute():
        selected = L / selected if selected.parent == Path('.') else R / selected
    if not selected.resolve().is_relative_to(L.resolve()) or selected.suffix.lower() != '.json':
        raise RuntimeError('Selected raw ASR must stay inside the current audio-v2 directory.')
    if requested and (not reason or not reason.strip()):
        raise RuntimeError('Explicit ASR selection requires a concrete --asr-reason.')
    if reason and not requested:
        raise RuntimeError('--asr-reason requires an explicit --asr-path.')
    primary, chosen = read(original), read(selected)
    for label, report in [('original full', primary), ('selected', chosen)]:
        if (report.get('revision') != REVISION or report.get('sha256') != voice_sha
                or report.get('role') != 'voice' or report.get('fullInput') is not True
                or report.get('rawRecognitionUnmodified') is not True
                or report.get('expectedTextPromptUsed') is not False
                or report.get('completePcmSha256', voice_sha) != voice_sha
                or not report.get('text') or not report.get('chunks')):
            raise RuntimeError(label + ' ASR is not complete raw recognition of this exact current PCM.')
        actual_duration = report.get('inputDurationSeconds')
        if (not isinstance(actual_duration, (int, float)) or not math.isfinite(actual_duration)
                or abs(actual_duration - duration) > .001):
            raise RuntimeError(label + ' ASR duration differs from the complete current PCM.')
    evidence = {
        'selected': relative(selected), 'selectedSha256': sha(selected),
        'originalFull': relative(original), 'originalFullSha256': sha(original),
        'voiceSha256': voice_sha, 'selectedByExplicitArgument': bool(requested),
        'reason': reason or 'Default complete-voice raw ASR.',
        'selectedMethod': chosen.get('independentMethod', 'complete-input recognition'),
        'bothRawReportsPreserved': True, 'noExpectedTextPrompt': True,
        'originalReportedNormalizedMatch': primary.get('normalizedMatch'),
        'actualHumanListening': 'pending; recognition selection does not establish pronunciation',
    }
    return selected, chosen, evidence


def validate_paragraph_asr(report, voice, voice_sha, duration, lines):
    """Verify all original paragraphs and measured token offsets against assembly."""
    paragraphs = report.get('paragraphs')
    if paragraphs is None:
        if 'paragraph' in report.get('independentMethod', '').lower() or report.get('timingSha256'):
            raise RuntimeError('Paragraph recognition is missing its original paragraph evidence.')
        return None
    timing_path = voice.with_suffix('.timing.json')
    timing = read(timing_path)
    if (report.get('completePcmSha256') != voice_sha
            or report.get('originalFullAsrPreserved') is not True
            or report.get('timingSha256') != sha(timing_path)
            or timing.get('voiceSha256') != voice_sha):
        raise RuntimeError('Paragraph ASR must bind the preserved full report and exact PCM assembly timing.')
    entries, rate = timing.get('entries', []), timing.get('sample_rate')
    if (type(rate) is not int or rate <= 0 or len(entries) != len(lines)
            or not isinstance(paragraphs, list) or len(paragraphs) != len(entries)):
        raise RuntimeError('Paragraph ASR must cover every current narration paragraph once.')
    padding = report.get('asrOnlyPaddingSeconds')
    if padding is None and '300ms ASR-only leading/trailing silence' in report.get('independentMethod', ''):
        padding = .3
    if not isinstance(padding, (int, float)) or not math.isfinite(padding) or padding < 0:
        raise RuntimeError('Paragraph ASR must declare its ASR-only padding for timestamp verification.')
    combined, raw_texts, previous_end = [], [], 0
    for index, (row, entry, line) in enumerate(zip(paragraphs, entries, lines), 1):
        if (row.get('index') != index or entry.get('index') != index
                or entry.get('lineIndex') != index - 1
                or normalized(entry.get('text', '')) != normalized(line)):
            raise RuntimeError('Paragraph ASR/assembly order or source text differs from current narration.')
        first, last = row.get('startSample'), row.get('endSample')
        if (type(first) is not int or type(last) is not int or not previous_end <= first < last
                or last > round(duration * rate)
                or first != round(float(entry['start']) * rate)
                or last != round(float(entry['end']) * rate)):
            raise RuntimeError('Paragraph ASR sample boundaries differ from the exact PCM assembly.')
        raw = row.get('raw', {})
        source_chunks, adjusted = raw.get('chunks', []), row.get('adjusted', [])
        if not source_chunks or len(source_chunks) != len(adjusted):
            raise RuntimeError('Paragraph ASR must retain each original token and its adjusted timestamp.')
        require_match(normalized(raw.get('text', '')),
                      ''.join(normalized(chunk['text']) for chunk in source_chunks),
                      'Raw paragraph text and raw tokens differ')
        for source, target in zip(source_chunks, adjusted):
            times, mapped = source.get('timestamp'), target.get('timestamp')
            if (source.get('text') != target.get('text') or not times or not mapped
                    or len(times) != 2 or len(mapped) != 2
                    or any(not isinstance(value, (int, float)) or not math.isfinite(value)
                           for value in times + mapped)):
                raise RuntimeError('Paragraph ASR changed a word or omitted its measured timestamp.')
            expected_times = [min(last / rate, max(first / rate, first / rate + value - padding))
                              for value in times]
            if any(abs(a - b) > 1e-6 for a, b in zip(expected_times, mapped)):
                raise RuntimeError('Paragraph ASR adjusted timestamps do not map to original measured tokens.')
        combined.extend(adjusted)
        raw_texts.append(raw['text'])
        previous_end = last
    if report['chunks'] != combined:
        raise RuntimeError('Selected paragraph ASR is not the complete ordered token sequence.')
    require_match(normalized(report['text']), normalized(' '.join(raw_texts)),
                  'Selected paragraph text is not the complete raw recognition')
    return {'paragraphs': len(paragraphs), 'timing': relative(timing_path),
            'timingSha256': sha(timing_path), 'originalTokenOffsetsVerified': True,
            'asrOnlyPaddingSeconds': padding, 'noWordsSelectedAcrossReports': True}


def require_match(expected, actual, label):
    if expected == actual:
        return
    differences = [
        {"kind": tag, "expectedRange": [a, b], "actualRange": [c, d],
         "expected": expected[max(0, a - 12):b + 12],
         "actual": actual[max(0, c - 12):d + 12]}
        for tag, a, b, c, d in difflib.SequenceMatcher(
            None, expected, actual, autojunk=False,
        ).get_opcodes() if tag != "equal"
    ]
    raise RuntimeError(label + "; review required, no outputs written: "
                       + json.dumps(differences, ensure_ascii=False))


def title_spelling_alias(raw, expected, clauses):
    """Canonical title numeral only, scoped to the complete existing p1-3 cue."""
    source = '그런데스플래툰2개발중에는'
    target = '그런데스플래툰투개발중에는'
    cue = next((item for item in clauses if item['id'] == 'p1-3'), None)
    if source not in raw:
        return {}, []
    if (not cue or normalized(cue['ko']) != source or normalized(cue['spoken']) != target
            or raw.count(source) != 1 or expected.count(target) != 1):
        raise RuntimeError('Canonical title numeral must match the exact unique display/spoken p1-3 phrase.')
    return {source: target}, [{
        'cue': 'p1-3', 'from': source, 'to': target,
        'category': 'Context-specific canonical game-title numeral spelling',
        'authority': 'Parent explicit instruction after both current raw ASRs recognized the title numeral2',
        'rawRecognitionUnmodified': True, 'wordTimestampsUnmodified': True,
        'characterCountUnchanged': True, 'realWordSubstitution': False,
        'scopeLimit': 'No standalone2, 두, 저기, 변의, other words or decimal conversion.',
        'actualPhoneticListening': 'pending',
    }]


def wav_duration(path):
    """Read RIFF metadata without modifying PCM; float WAV is supported."""
    with Path(path).open("rb") as stream:
        header = stream.read(12)
        if header[:4] != b"RIFF" or header[8:] != b"WAVE":
            raise RuntimeError("Expected a RIFF WAVE narration source.")
        rate = align = size = None
        while True:
            chunk = stream.read(8)
            if len(chunk) != 8:
                break
            kind, length = struct.unpack("<4sI", chunk)
            if kind == b"fmt ":
                data = stream.read(length)
                if len(data) < 16:
                    raise RuntimeError("Invalid WAV format chunk.")
                fields = struct.unpack("<HHIIHH", data[:16])
                rate, align = fields[2], fields[4]
            else:
                if kind == b"data":
                    size = length
                stream.seek(length, 1)
            if length % 2:
                stream.seek(1, 1)
        if not rate or not align or size is None or size % align:
            raise RuntimeError("Missing or unaligned WAV duration metadata.")
        return size / align / rate


def apply_aliases(raw, aliases):
    """Return canonical characters with exact provenance in normalized ASR text.

    Changed-length aliases keep a proportional source-character range. Timing
    interpolation is explicitly recorded, never presented as per-character ASR.
    Aliases are matched once against raw text, avoiding chained substitutions.
    """
    if not aliases:
        return raw, [(i, i + 1) for i in range(len(raw))], []
    pattern = re.compile("|".join(re.escape(key) for key in sorted(aliases, key=lambda x: (-len(x), x))))
    output, bounds, evidence = [], [], []
    previous = 0
    for match in pattern.finditer(raw):
        start, end = match.span()
        output.append(raw[previous:start])
        bounds.extend((i, i + 1) for i in range(previous, start))
        replacement = aliases[match.group()]
        output.append(replacement)
        step = (end - start) / len(replacement)
        bounds.extend((start + i * step, start + (i + 1) * step)
                      for i in range(len(replacement)))
        evidence.append({"from": match.group(), "to": replacement,
                         "rawCharRange": [start, end],
                         "changedCharacterCount": len(replacement) != end - start})
        previous = end
    output.append(raw[previous:])
    bounds.extend((i, i + 1) for i in range(previous, len(raw)))
    return "".join(output), bounds, evidence


def half_up(value):
    return math.floor(value + 0.5)


def stamp(seconds, ass=False):
    base = 100 if ass else 1000
    whole = half_up(seconds * base)
    seconds, fraction = divmod(whole, base)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return (f"{hours}:{minutes:02}:{seconds:02}.{fraction:02}" if ass else
            f"{hours:02}:{minutes:02}:{seconds:02},{fraction:03}")


def wrap(text, font):
    lines = []
    for paragraph in text.strip().splitlines():
        line = ""
        for word in paragraph.split():
            if font.getlength(word) > 796:
                raise RuntimeError("Caption token exceeds796px; split the clause: " + word)
            candidate = (line + " " + word).strip()
            if line and font.getlength(candidate) > 796:
                lines.append(line)
                line = word
            else:
                line = candidate
        if line:
            lines.append(line)
    if not 1 <= len(lines) <= 2:
        raise RuntimeError("Caption requires more than2lines; shorten/split the clause: " + text)
    return lines


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--asr-path', help='Explicit current audio-v2 raw complete/paragraph ASR JSON for this PCM hash.')
    parser.add_argument('--asr-reason', help='Concrete reason for selecting this independent raw recognition.')
    args = parser.parse_args(argv)
    revision_guard()
    project_path = P / "project.json"
    project = read(project_path)
    voice = VOICE
    voice = voice if voice.is_absolute() else R / voice
    voice_sha = sha(voice)
    duration = wav_duration(voice)
    if not math.isfinite(duration) or duration <= 0:
        raise RuntimeError("Narration duration must be finite and positive.")
    minimum_frames = math.ceil((VOICE_OFFSET + duration + TAIL_SECONDS) * FPS - 1e-8)
    # A target length is not permission to append an unrelated silent tail.
    frames = minimum_frames
    timeline_seconds = frames / FPS
    asr_path, asr, asr_selection = select_asr(args.asr_path, voice_sha, duration, args.asr_reason)
    narration_path = Path(read(P / "production/tts-manifest.json")["paths"]["script"])
    narration_path = narration_path if narration_path.is_absolute() else R / narration_path
    narration = read(narration_path)
    lines = [line for scene in narration["scenes"] for line in scene["lines"]]
    if not lines or any(not isinstance(line, str) or not normalized(line) for line in lines):
        raise RuntimeError("Narration needs nonempty scene lines.")
    asr_selection['paragraphCoverage'] = validate_paragraph_asr(asr, voice, voice_sha, duration, lines)
    expected = "".join(normalized(line) for line in lines)
    text_path = P / "production/narration.ko.txt"
    if text_path.exists():
        require_match(expected, normalized(text_path.read_text(encoding="utf8")),
                      "Narration JSON and raw expected text differ")

    clauses_path = P / "production/clauses.json"
    clauses = read(clauses_path)["clauses"]
    if not clauses or len({item["id"] for item in clauses}) != len(clauses):
        raise RuntimeError("Caption clauses must have unique IDs and be nonempty.")
    for item in clauses:
        if (not isinstance(item["id"], str) or not item["id"]
                or type(item["lineIndex"]) is not int
                or not 0 <= item["lineIndex"] < len(lines)
                or any(not isinstance(item[key], str) or not item[key].strip()
                       for key in ["spoken", "ko", "en"])):
            raise RuntimeError("Invalid caption clause: " + str(item.get("id")))
    if [item["lineIndex"] for item in clauses] != sorted(item["lineIndex"] for item in clauses):
        raise RuntimeError("Caption clauses are out of narration line order.")
    require_match(expected, "".join(normalized(item["spoken"]) for item in clauses),
                  "Spoken caption clauses differ from raw expected narration")
    for index, line in enumerate(lines):
        require_match(normalized(line), "".join(normalized(item["spoken"]) for item in clauses
                      if item["lineIndex"] == index), f"Clause ownership differs on line{index}")

    reconciliation_path = L / "asr-reconciliation.json"
    aliases, reconciliation = {}, None
    if reconciliation_path.exists():
        reconciliation = read(reconciliation_path)
        if reconciliation.get("voiceSha256") != voice_sha:
            raise RuntimeError("Reviewed aliases refer to another voice PCM hash.")
        if reconciliation.get("asrSha256") != sha(asr_path):
            raise RuntimeError("Reviewed aliases refer to another raw ASR report.")
        if not isinstance(reconciliation.get("aliases"), dict):
            raise RuntimeError("Reconciliation must supply an aliases object.")
        for source, target in reconciliation["aliases"].items():
            if not isinstance(source, str) or not isinstance(target, str):
                raise RuntimeError("Reviewed aliases must map text strings to text strings.")
            allowed = read(P / 'production/clauses.json')['orthographicNormalization']['mapping']
            if allowed.get(source) != target:
                raise RuntimeError('Only the recorded shading loanword spelling is permitted; real words and numerals cannot be repaired by aliases.')
            source, target = normalized(source), normalized(target)
            if not source or not target or (source in aliases and aliases[source] != target):
                raise RuntimeError("Empty or conflicting normalized alias.")
            aliases[source] = target

    words, raw_parts, cursor = [], [], 0
    chunks = asr.get("chunks", [])
    if not chunks:
        raise RuntimeError("Current whole-voice ASR has no word timestamps.")
    for index, chunk in enumerate(chunks):
        text = normalized(chunk["text"])
        if not text:
            continue
        times = chunk.get("timestamp")
        if not times or len(times) != 2 or any(value is None for value in times):
            raise RuntimeError(f"Missing measured word timestamp at chunk{index}.")
        start, end = map(float, times)
        if not (math.isfinite(start) and math.isfinite(end) and 0 <= start <= end):
            raise RuntimeError(f"Invalid measured word timestamp at chunk{index}.")
        if words and start < words[-1]["start"] - 1e-6:
            raise RuntimeError("Word timestamps are not in temporal order.")
        words.append({"index": index, "text": chunk["text"], "start": start,
                      "end": end, "charStart": cursor, "charEnd": cursor + len(text)})
        raw_parts.append(text)
        cursor += len(text)
    raw = "".join(raw_parts)
    require_match(normalized(asr["text"]), raw, "Raw ASR full text and word chunks differ")
    title_aliases, title_evidence = title_spelling_alias(raw, expected, clauses)
    aliases.update(title_aliases)
    actual, char_bounds, alias_events = apply_aliases(raw, aliases)
    require_match(expected, actual, "Current voice ASR differs from expected narration")
    canonical_full, _, _ = apply_aliases(normalized(asr["text"]), aliases)
    require_match(expected, canonical_full, "Canonical full ASR text differs")

    starts = [word["charStart"] for word in words]
    ends = [word["charEnd"] for word in words]

    def boundary(position, edge):
        # Avoid a floating alias ratio placing an exact word edge1e-15 inside
        # the preceding word, which could otherwise swallow a real pause.
        nearest = round(position)
        if abs(position - nearest) < 1e-8:
            position = nearest
        index = (bisect.bisect_right(starts, position) - 1 if edge == "start"
                 else bisect.bisect_left(ends, position))
        if not 0 <= index < len(words):
            raise RuntimeError("No measured word covers character boundary.")
        word = words[index]
        fraction = (position - word["charStart"]) / (word["charEnd"] - word["charStart"])
        if not 0 <= fraction <= 1:
            raise RuntimeError("Character boundary is outside measured word.")
        value = word["start"] + fraction * (word["end"] - word["start"])
        return value, {"wordIndex": word["index"], "rawCharOffset": position,
                       "fraction": fraction, "interpolatedWithinWord": 0 < fraction < 1}

    timed, evidence, position, previous_end = [], [], 0, 0
    for clause in clauses:
        length = len(normalized(clause["spoken"]))
        if not length:
            raise RuntimeError("An empty normalized clause cannot be timed.")
        raw_start, first = boundary(char_bounds[position][0], "start")
        raw_end, last = boundary(char_bounds[position + length - 1][1], "end")
        if raw_start >= duration or raw_end <= raw_start:
            raise RuntimeError("Clause has empty/out-of-PCM timestamps: " + clause["id"])
        clip_start, clip_end = max(0.0, raw_start), min(duration, raw_end)
        desired_start = half_up((VOICE_OFFSET + clip_start) * FPS)
        desired_end = half_up((VOICE_OFFSET + clip_end) * FPS)
        start_frame = max(previous_end, math.ceil(VOICE_OFFSET * FPS), desired_start)
        end_frame = min(frames, desired_end)
        if not 0 <= start_frame < end_frame <= frames:
            raise RuntimeError("Empty/overlapping caption requires timestamp review: " + clause["id"])
        item = copy.deepcopy(clause)
        item.update(start=start_frame / FPS, end=end_frame / FPS,
                    startFrame=start_frame, endFrame=end_frame)
        timed.append(item)
        evidence.append({
            "id": item["id"], "lineIndex": item["lineIndex"],
            "normalizedCharRange": [position, position + length],
            "rawWordTimes": [raw_start, raw_end], "firstBoundary": first,
            "lastBoundary": last, "clippedToPcm": raw_end != clip_end or raw_start != clip_start,
            "frameRange": [start_frame, end_frame],
            "nonOverlapAdjustmentFrames": start_frame - desired_start,
        })
        position += length
        previous_end = end_frame
    if position != len(expected):
        raise RuntimeError("Caption timing failed complete character coverage.")

    from PIL import ImageFont

    font = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 60)
    rows, events, subtitles = [], [], {"ko": [], "en": []}
    for index, cue in enumerate(timed, 1):
        display = {language: wrap(cue[language], font) for language in ["ko", "en"]}
        if any(token in cue["ko"] for token in ["{", "}", "\\"]):
            raise RuntimeError("ASS control characters require explicit display handling.")
        width = max(font.getlength(line) for line in display["ko"]) + 44
        height = len(display["ko"]) * 78 + 26
        x, y = 510 - width / 2, 1380 - height / 2
        if x < 80 or x + width > 930:
            raise RuntimeError("Caption box enters reserved side clearance: " + cue["id"])
        when = f"{stamp(cue['start'], True)},{stamp(cue['end'], True)}"
        for layer, dx, dy, color in [(10, 12, 12, "&H323C07&"), (11, 0, 0, "&HFFFFFF&")]:
            a, b = x + dx, y + dy
            polygon = f"m {a:.1f} {b:.1f} l {a + width:.1f} {b:.1f} {a + width:.1f} {b + height:.1f} {a:.1f} {b + height:.1f}"
            events.append(f"Dialogue: {layer},{when},Box,,0,0,0,,{{\\an7\\pos(0,0)\\1c{color}\\p1}}" + polygon)
        for line_index, line in enumerate(display["ko"]):
            baseline = 1380 + (line_index - (len(display["ko"]) - 1) / 2) * 78
            emphasis=cue.get("emphasis")
            styled=line
            if emphasis and emphasis["text"] in line:
                palette={"term": "&H595000&", "result": "&H215200&", "problem": "&H3131A5&"}
                token=emphasis["text"]
                if cue["ko"].count(token)!=1: raise RuntimeError("Emphasis must be one unique span")
                styled=line.replace(token,"{\\1c"+palette[emphasis["role"]]+"}"+token+"{\\1c&H090B08&}",1)
            events.append(f"Dialogue: 12,{when},Text,,0,0,0,,{{\\an5\\pos(510,{baseline:.1f})}}" + styled)
        for language in ["ko", "en"]:
            subtitles[language].append(
                f"{index}\n{stamp(cue['start'])} --> {stamp(cue['end'])}\n" + "\n".join(display[language])
            )
        rows.append({"id": cue["id"], "cue": index, "start": cue["start"], "end": cue["end"],
                     "lines": display["ko"], "englishLines": display["en"], "box": [x, y, width, height], "emphasis": cue.get("emphasis")})

    fingerprints = {
        "voiceSha256": voice_sha, "asrSha256": sha(asr_path),
        "originalFullAsrSha256": asr_selection['originalFullSha256'],
        "contextualTitleSpelling": title_evidence,
        "pronunciationAliases": read(P / "production/clauses.json").get("pronunciationAliases", {}),
        "narrationSha256": sha(narration_path), "clausesSha256": sha(clauses_path),
        "reconciliationSha256": sha(reconciliation_path) if reconciliation else None,
    }
    output = {
        "schemaVersion": 1, "revision": REVISION, "status": ("canonical-content-word-timed; raw-variants-and-playback-review-pending"
            if aliases else "exact-transcript-word-timed; playback-review-pending"),
        "lineIndexBase": 0, "fps": FPS, "frames": frames,
        "durationSeconds": timeline_seconds, "voiceDurationSeconds": duration,
        "voiceOffsetSeconds": VOICE_OFFSET, "tailSecondsMinimum": TAIL_SECONDS,
        "speechSpeed": 1, "target60Applied": frames == 60 * FPS,
        "timingInputs": fingerprints, "asrSelection": asr_selection, "cues": timed,
    }
    alignment = {
        "status": ("canonical-character-coverage-after-scoped-variants; pronunciation-and-playback-review-pending"
            if aliases else "exact-normalized-character-coverage; playback-review-pending"),
        "voice": relative(voice), "fullVoiceAsr": relative(asr_path),
        "asrSelection": asr_selection,
        "normalizedNarrationCharacters": len(expected), "normalizedCoverageExact": True,
        "fingerprints": fingerprints, "reviewedAliases": aliases, "aliasApplications": alias_events,
        "reconciliation": relative(reconciliation_path) if reconciliation else None,
        "timestampPolicy": "Measured word edges; explicit interpolation only inside timestamped words;60fps nearest-frame quantization",
        "durationPolicy": "ceil((voice+0.20start+0.40tail)*60); natural speech speed, no padding to target60",
        "words": words, "cues": evidence,
        "reviewFlags": [item for item in evidence if item["firstBoundary"]["interpolatedWithinWord"]
                        or item["lastBoundary"]["interpolatedWithinWord"]
                        or item["nonOverlapAdjustmentFrames"] or item["clippedToPcm"]],
        "humanListening": "pending",
    }
    targets = {
        P / "script/captions.json": encoded(output),
        L / "caption-alignment.json": encoded(alignment),
        L / "caption-layout.json": encoded({"rows": rows, "center": [510, 1380], "font": 60,
                                            "maxLines": 2, "textWidthMaximum": 796}),
        L / "captions.ko.ass": ASS_HEADER + "\n".join(events) + "\n",
        L / "captions.ko.srt": "\n\n".join(subtitles["ko"]) + "\n",
        L / "captions.en.srt": "\n\n".join(subtitles["en"]) + "\n",
    }
    for path, text in targets.items():
        if path.exists() and path.read_text(encoding="utf8") != text:
            raise RuntimeError("Preserve/reconcile previous timing output before changing it: " + relative(path))
    for path, text in targets.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(text, encoding="utf8")
    print(encoded({"captions": relative(P / "script/captions.json"), "cueCount": len(timed),
                   "durationSeconds": timeline_seconds, "frames": frames,
                   "reviewFlags": len(alignment["reviewFlags"]), "mediaJobsStarted": 0}))


if __name__ == "__main__":
    main()
