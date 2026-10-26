"""Word-anchored complete paired captions and measured fixed48px layout for D22.

CLI: python caption_pipeline.py --input caption-input.json [--output-dir ...]

Input schema (all relative paths resolve from the repository root)::

    {"fps":60,"paragraphs":[
      {"id":"p01","scene":"01","line":0,"start":2.0,"duration":12.4,
       "ko":"Approved Korean display paragraph.",
       "en":"Complete paired English paragraph.",
       "asrFile":".../p01.json","audioFile":".../p01.wav",
       "aliases":{"Unity":"유니티"},
       "captionUnits":[{"ko":"직접 나눈 한 절입니다.","en":"One authored clause.",
         "emphasis":{"ko":{"start":0,"end":2,"role":"term"},
                     "en":{"start":4,"end":12,"role":"term"}}}]}
    ]}

``start`` is the paragraph PCM origin on the complete GLOBAL video timeline,
including branding. ``duration`` is measured PCM duration. ASR words carry text
and ``timestamp:[localStart,localEnd]`` (or word/start/end). ASR audio_sha256 is
checked against audioFile when supplied; no ASR is run. Inline ``words`` may
replace asrFile. Optional root ``scriptKo``/``scriptEn`` can replace inline text
using matching ``scenes[].id`` and zero-based ``line`` in ``scenes[].lines``.
Aliases change alignment normalization ONLY, never captions/display text.

No guessed paragraph-duration timing, dropped words, compressed font or ellipses.
Uncertain ASR matching (<93%; minCoverage may tighten this threshold),
missing timestamps, text mismatch, overlapping/zero-time cues, or oversized
layout stops the build. Authored paired clause units are required; a word-count
partition is not a semantic review. Prefer one measured48px line; a second line
needs twoLineReason to preserve a single clause. Every word is retained and EN
shares Korean speech boundaries, rather than being separately measured speech.
Each cue optionally emphasizes one matched KO/EN span with term/result/problem
colors (>=4.5:1 against white) and weight700. Other text uses weight500.

Outputs: plain captions.ko/en.srt, styled captions.ko/en.ass, captions.json,
caption-layout.json and caption-alignment.json. Geometry is measured; encoded pixel and human listening
review remains pending. This module does not mutate source PCM, ASR or scripts.
"""
from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import math
import re
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path
from storage_paths import repo_path as routed_repo_path, relative as routed_relative, write_path as routed_write_path

from PIL import ImageFont

from audio_pipeline import require_authorized, current_local_output

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE.parents[1] / "production/local" / HERE.name / "edit"
FONT_SIZE, MAX_WIDTH, LINE_HEIGHT = 48, 1570, 62
EMPHASIS_COLORS = {"term": "0b6b66", "result": "1a7f37", "problem": "b42318"}
CAPTION_POLICY = "caption-clause-keyword-v1"


def contrast_on_white(rgb: str) -> float:
    values = [int(rgb[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in values]
    luminance = sum(v * k for v, k in zip(linear, (.2126, .7152, .0722)))
    return 1.05 / (luminance + .05)


def font_input(value: str) -> Path:
    candidate = Path(value).resolve()
    system_fonts = Path("C:/Windows/Fonts").resolve()
    if candidate.is_relative_to(system_fonts):
        return candidate  # Approved installed fonts are read-only inputs.
    return path(value)


def measured_font(filename: Path, weight: int):
    font = ImageFont.truetype(str(filename), FONT_SIZE)
    try:
        axes = font.get_variation_axes()
    except (AttributeError, OSError):
        return font
    if axes:
        values = []
        for axis in axes:
            name = axis.get("name", b"")
            name = name.decode("utf-8", "replace") if isinstance(name, bytes) else str(name)
            values.append(weight if "weight" in name.lower() else axis["default"])
        font.set_variation_by_axes(values)
    return font


def emphasis_span(spec, text: str) -> dict | None:
    if not spec:
        return None
    if isinstance(spec, list):
        if len(spec) != 1:
            raise ValueError("At most one contiguous emphasized span is allowed per cue/language")
        spec = spec[0]
    if not isinstance(spec, dict) or spec.get("role") not in EMPHASIS_COLORS:
        raise ValueError("Emphasis role must be term, result, or problem")
    begin, end = spec.get("start"), spec.get("end")
    if type(begin) is not int or type(end) is not int or not 0 <= begin < end <= len(text):
        raise ValueError("Emphasis indices use the whitespace-collapsed displayed cue text")
    if not text[begin:end].strip():
        raise ValueError("Cannot emphasize only whitespace")
    rgb = EMPHASIS_COLORS[spec["role"]]
    if contrast_on_white(rgb) < 4.5:
        raise ValueError("Caption emphasis must reach 4.5:1 against its white box")
    return {"start": begin, "end": end, "role": spec["role"],
            "text": text[begin:end], "color": "#" + rgb, "weight": 700,
            "contrastOnWhite": contrast_on_white(rgb)}


def path(value) -> Path:
    return routed_repo_path(value)


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8-sig"))


def sha(p: Path) -> str:
    digest = hashlib.sha256()
    with p.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_write(p: Path, obj):
    p = routed_write_path(p)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def retain_normalized(text: str) -> str:
    """For preservation checks remove whitespace only, retaining punctuation."""
    return re.sub(r"\s+", "", text)


def normalized(text: str, aliases: dict | None = None) -> str:
    text = text.lower()
    for display, spoken in sorted((aliases or {}).items(), key=lambda x: -len(x[0])):
        text = text.replace(display.lower(), spoken.lower())
    return re.sub(r"[^가-힣a-z0-9]", "", text)


def linear(values: list[float], positions: list[int], length: int) -> list[float]:
    result = []
    for i in range(length):
        right = bisect.bisect_right(positions, i)
        if right == 0:
            value = values[0]
        elif right == len(positions):
            value = values[-1]
        else:
            a, b = positions[right - 1], positions[right]
            q = (i - a) / (b - a)
            value = values[right - 1] + (values[right] - values[right - 1]) * q
        result.append(value)
    return result


def align_characters(text: str, words: list[dict], duration: float,
                     aliases: dict, minimum: float) -> tuple[list, list, dict]:
    expected, actual, starts, ends = normalized(text, aliases), "", [], []
    previous = 0.0
    if not expected:
        raise ValueError("Paragraph has no alignable characters")
    for item in words:
        token = normalized(item.get("text", item.get("word", "")), aliases)
        if not token:
            continue
        interval = item.get("timestamp", [item.get("start"), item.get("end")])
        if len(interval) != 2 or any(v is None for v in interval):
            raise ValueError("Every nonempty ASR word requires actual start/end timestamps")
        begin, end = map(float, interval)
        if begin < previous - .002 or begin < 0 or end <= begin or end > duration + .03:
            raise ValueError(f"Invalid local ASR interval {interval}; PCM duration{duration}")
        # A <=2ms timestamp quantization overlap is clamped, never extrapolated.
        begin, end = max(previous, begin), min(duration, end)
        if end <= begin:
            raise ValueError("ASR word collapses after quantization clamp")
        actual += token
        starts.extend(begin + (end - begin) * k / len(token) for k in range(len(token)))
        ends.extend(begin + (end - begin) * (k + 1) / len(token) for k in range(len(token)))
        previous = end
    positions, matched_starts, matched_ends = [], [], []
    matcher = SequenceMatcher(None, expected, actual, autojunk=False)
    for block in matcher.get_matching_blocks():
        for offset in range(block.size):
            positions.append(block.a + offset)
            matched_starts.append(starts[block.b + offset])
            matched_ends.append(ends[block.b + offset])
    coverage = len(positions) / len(expected)
    if coverage < minimum:
        raise ValueError(f"Script/ASR coverage{coverage:.2%} below{minimum:.2%}; inspect recognition/aliases")
    if not positions:
        raise ValueError("No matched spoken characters")
    char_starts, char_ends = linear(matched_starts, positions, len(expected)), linear(matched_ends, positions, len(expected))
    last = 0.0
    for i in range(len(expected)):
        char_starts[i] = max(last, char_starts[i])
        char_ends[i] = max(char_starts[i], char_ends[i])
        last = char_ends[i]
    position_set = set(positions)
    return char_starts, char_ends, {"matchingCharacterCoverage": coverage,
        "matchedCharacters": len(positions), "displayNormalizedCharacters": len(expected),
        "asrNormalizedCharacters": len(actual), "minimumCoverage": minimum,
        "boundaryMethod": "actualASRword endpoints; linear within-word characters and matched-character interpolation",
        "unmatchedDisplayCharacterIndices": [i for i in range(len(expected)) if i not in position_set]}


def wrap(text: str, font, max_width: int = MAX_WIDTH) -> list[str] | None:
    """Two measured lines, semantic word boundaries; never drop/truncate text."""
    text = " ".join(text.split())
    if not text:
        return None
    if font.getlength(text) <= max_width:
        return [text]
    words, best = text.split(), None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        wa, wb = font.getlength(a), font.getlength(b)
        if max(wa, wb) <= max_width:
            cost = abs(wa - wb)
            if best is None or cost < best[0]:
                best = cost, [a, b]
    return best[1] if best else None


def fixed_partition(text: str, count: int, font) -> list[str] | None:
    words = text.split()
    if count > len(words):
        return None
    ideal = font.getlength(" ".join(words)) / count

    @lru_cache(None)
    def segment(a, b):
        value = " ".join(words[a:b])
        return value, wrap(value, font)

    @lru_cache(None)
    def solve(start, remaining):
        if remaining == 0:
            return (0, ()) if start == len(words) else (math.inf, ())
        best = math.inf, ()
        for end in range(start + 1, len(words) - remaining + 2):
            value, lines = segment(start, end)
            if lines is None:
                # A segment that already exceeds2lines cannot shrink by adding.
                break
            future, rest = solve(end, remaining - 1)
            if not math.isfinite(future):
                continue
            cost = (font.getlength(value) - ideal) ** 2 + future
            if value.endswith((".", "?", "!", ";", "。")):
                cost -= ideal ** 2 * .23
            elif value.endswith((",", ":")):
                cost -= ideal ** 2 * .09
            if cost < best[0]:
                best = cost, (value, *rest)
        return best

    score, parts = solve(0, count)
    return list(parts) if math.isfinite(score) else None


def partition_pair(ko: str, en: str, font, explicit=None) -> list[dict]:
    """Use authored bilingual clauses; never guess clause/translation boundaries."""
    if not explicit:
        raise ValueError("Current clause captions require authored paired captionUnits; word-count partitioning is not semantic review")
    if not all(isinstance(u.get(k), str) and u[k].strip() for u in explicit for k in ("ko", "en")):
        raise ValueError("Every explicit captionUnit requires full nonempty KO/EN")
    for language, original in (("ko", ko), ("en", en)):
        if retain_normalized("".join(unit[language] for unit in explicit)) != retain_normalized(original):
            raise ValueError(f"{language} caption units changed or dropped display content")
    result = []
    for unit in explicit:
        canonical = {language: " ".join(unit[language].split()) for language in ("ko", "en")}
        lines = {language: wrap(canonical[language], font) for language in ("ko", "en")}
        if any(value is None for value in lines.values()):
            raise ValueError("Explicit paired clause exceeds measured1570px/max2lines")
        two_lines = any(len(value) == 2 for value in lines.values())
        if two_lines and not str(unit.get("twoLineReason", "")).strip():
            raise ValueError("Prefer one line; a two-line clause needs its specific semantic-preservation reason")
        specification = unit.get("emphasis", {})
        if not isinstance(specification, dict):
            raise ValueError("emphasis is a KO/EN mapping of at most one span per language")
        emphasis = {language: emphasis_span(specification.get(language), canonical[language]) for language in ("ko", "en")}
        if bool(emphasis["ko"]) != bool(emphasis["en"]):
            raise ValueError("An emphasized idea needs its paired KO/EN span, not an unpaired translated guess")
        if emphasis["ko"] and emphasis["ko"]["role"] != emphasis["en"]["role"]:
            raise ValueError("Paired KO/EN emphasis must carry the same semantic role")
        row = {language: "\n".join(lines[language]) for language in ("ko", "en")}
        # Wrapping replaces a single inter-word space by a newline, preserving
        # codepoint offsets for the authored span. No display character drops.
        if any(len(row[language]) != len(canonical[language]) for language in ("ko", "en")):
            raise ValueError("Wrapping changed emphasis character offsets")
        row.update(emphasis=emphasis, twoLineReason=unit.get("twoLineReason"),
                   clauseAuthorship="explicit bilingual units; semantic review belongs to the existing complete-text review")
        result.append(row)
    return result


def srt_stamp(seconds: float) -> str:
    n = round(seconds * 1000)
    return f"{n // 3600000:02}:{n // 60000 % 60:02}:{n // 1000 % 60:02},{n % 1000:03}"


def ass_stamp(seconds: float) -> str:
    n = round(seconds * 100)
    return f"{n // 360000}:{n // 6000 % 60:02}:{n // 100 % 60:02}.{n % 100:02}"


def ass_header(font_name: str) -> str:
    return f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},48,&H00090B08,&H00090B08,&H00181B16,&H00323C07,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def geometry(text: str, font, bold_font=None, emphasis=None) -> dict:
    lines, widths, offset = text.split("\n"), [], 0
    for line in lines:
        if emphasis and bold_font:
            begin, end = max(0, emphasis["start"] - offset), min(len(line), emphasis["end"] - offset)
            if begin < end:
                width = font.getlength(line[:begin]) + bold_font.getlength(line[begin:end]) + font.getlength(line[end:])
            else:
                width = font.getlength(line)
        else:
            width = font.getlength(line)
        widths.append(float(width)); offset += len(line) + 1
    if len(lines) > 2 or max(widths) > MAX_WIDTH:
        raise ValueError("Caption exceeds two lines/1570px at actual48px font and weight")
    width, height = math.ceil(max(widths)) + 44, len(lines) * LINE_HEIGHT + 22
    x, y = round(960 - width / 2), round(970 - height / 2)
    if x - 3 < 0 or x + width + 17 > 1920 or y - 3 < 0 or y + height + 17 > 1080:
        raise ValueError("Fixed caption box/outline/shadow leaves frame")
    return {"lines": lines, "lineWidths": widths, "width": width, "height": height,
            "x": x, "y": y, "center": [960, 970], "shadowOffset": [14, 14],
            "completeBounds": [x - 3, y - 3, x + width + 17, y + height + 17]}


def ass_events(row: dict, g: dict, language="ko") -> str:
    def event(layer, text):
        return f"Dialogue: {layer},{ass_stamp(row['start'])},{ass_stamp(row['end'])},Default,,0,0,0,,{text}\n"

    def box(x, y, color, border):
        return f"{{\\an7\\pos({x},{y})\\p1\\bord{border}\\shad0\\1c&H{color}&\\3c&H181B16&}}m 0 0 l {g['width']} 0 {g['width']} {g['height']} 0 {g['height']}"

    result = event(0, box(g["x"] + 14, g["y"] + 14, "323C07", 0))
    result += event(1, box(g["x"], g["y"], "FFFFFF", 3))
    span, offset = row.get("emphasis", {}).get(language), 0
    for i, text in enumerate(g["lines"]):
        if any(c in text for c in ("{", "}", "\\")):
            raise ValueError("Display captions cannot contain ASS override syntax")
        rendered = text
        if span:
            begin, end = max(0, span["start"] - offset), min(len(text), span["end"] - offset)
            if begin < end:
                rgb = EMPHASIS_COLORS[span["role"]]
                bgr = rgb[4:6] + rgb[2:4] + rgb[:2]
                rendered = (text[:begin] + f"{{\\1c&H{bgr}&\\b700}}" + text[begin:end]
                            + "{\\1c&H090B08&\\b500}" + text[end:])
        result += event(2, f"{{\\an5\\pos(960,{g['y'] + 42 + i * 62})\\bord0\\shad0\\b500}}" + rendered)
        offset += len(text) + 1
    return result


def script_lookup(script_file):
    if not script_file:
        return {}
    return {str(s["id"]): s["lines"] for s in load(path(script_file))["scenes"]}


def build(data: dict, output: Path) -> dict:
    if data.get("fps", 60) != 60:
        raise ValueError("Production caption clock must be60fps")
    if not data.get("paragraphs"):
        raise ValueError("A caption build requires actual aligned paragraphs")
    noto = Path("C:/Windows/Fonts/NotoSansKR-VF.ttf")
    font_file = font_input(data.get("fontFile", str(noto) if noto.is_file() else "C:/Windows/Fonts/malgun.ttf"))
    bold_default = font_file if "notosanskr" in font_file.name.lower() else Path("C:/Windows/Fonts/malgunbd.ttf")
    bold_file = font_input(data.get("fontBoldFile", str(bold_default)))
    font, bold_font = measured_font(font_file, 500), measured_font(bold_file, 700)
    font_name = data.get("fontName", "Noto Sans KR" if "notosanskr" in font_file.name.lower() else "Malgun Gothic")
    ko_script, en_script = script_lookup(data.get("scriptKo")), script_lookup(data.get("scriptEn"))
    rows, evidence, layout, ids = [], [], [], set()
    previous = 0.0
    for index, paragraph in enumerate(data["paragraphs"]):
        pid = paragraph.get("id", f"paragraph-{index + 1}")
        if pid in ids:
            raise ValueError(f"Duplicate paragraph ID: {pid}")
        ids.add(pid)
        scene, line = str(paragraph.get("scene", pid)), int(paragraph.get("line", 0))
        ko = paragraph.get("ko") or ko_script[scene][line]
        en = paragraph.get("en") or en_script[scene][line]
        origin, duration = float(paragraph["start"]), float(paragraph["duration"])
        if origin < 2 or duration <= 0:
            raise ValueError("Global paragraph origin must follow2sbranding; duration must be measuredpositive")
        asr_file = path(paragraph["asrFile"]) if paragraph.get("asrFile") else None
        asr = load(asr_file) if asr_file else {"words": paragraph["words"]}
        audio_file = path(paragraph["audioFile"]) if paragraph.get("audioFile") else None
        audio_hash = sha(audio_file) if audio_file else None
        if audio_file:
            import soundfile as sf
            info = sf.info(str(audio_file))
            if abs(info.duration - duration) > 1 / info.samplerate:
                raise ValueError(f"Paragraph duration differs from actualPCM: {pid}")
            if asr.get("audio_sha256") and asr["audio_sha256"].lower() != audio_hash:
                raise ValueError(f"Stale ASR/PCM hash mismatch: {pid}")
        aliases = {**data.get("aliases", {}), **paragraph.get("aliases", {})}
        minimum = float(paragraph.get("minCoverage", data.get("minCoverage", .93)))
        if not .93 <= minimum <= 1:
            raise ValueError("minCoverage may tighten but cannot bypass93%alignment minimum")
        starts, ends, alignment = align_characters(ko, asr["words"], duration, aliases, minimum)
        units = partition_pair(ko, en, font, paragraph.get("captionUnits"))
        cursor, cue_ids = 0, []
        for unit in units:
            size = len(normalized(unit["ko"], aliases))
            if not size:
                raise ValueError("Empty normalized caption unit")
            begin, end = origin + starts[cursor], origin + ends[cursor + size - 1]
            # Quantize once to ASS's actualcentisecond clock. SRT uses the SAME
            # endpoints to avoid claiming different timing than encoded pixels.
            begin, end = round(begin * 100) / 100, round(end * 100) / 100
            if begin < previous - .0001 or end <= begin:
                raise ValueError(f"Overlapping/collapsed currentASR caption: {pid} {begin}--{end}")
            if data.get("bodyEndFrame") is not None and end > data["bodyEndFrame"] / 60 + .001:
                raise ValueError("Speech captions enter membershipoutro")
            row = {"cue": len(rows) + 1, "paragraph": pid, "scene": scene, "line": line,
                   "start": begin, "end": end, "ko": unit["ko"], "en": unit["en"],
                   "emphasis": unit["emphasis"], "twoLineReason": unit["twoLineReason"]}
            rows.append(row)
            ko_geometry = geometry(unit["ko"], font, bold_font, unit["emphasis"]["ko"])
            en_geometry = geometry(unit["en"], font, bold_font, unit["emphasis"]["en"])
            layout.append({**row, **ko_geometry, "enGeometry": en_geometry,
                           "startFrame": math.ceil(begin * 60 - 1e-7),
                           "endFrameExclusive": math.ceil(end * 60 - 1e-7)})
            cue_ids.append(row["cue"])
            previous, cursor = end, cursor + size
        if cursor != len(normalized(ko, aliases)):
            raise ValueError("Caption chunks changed normalizedKorean source")
        evidence.append({"paragraph": pid, "scene": scene, "line": line,
            "originSeconds": origin, "measuredPcmDuration": duration,
            "audioFile": routed_relative(audio_file) if audio_file else None, "audioSha256": audio_hash,
            "asrFile": routed_relative(asr_file) if asr_file else None,
            "asrSha256": sha(asr_file) if asr_file else hashlib.sha256(json.dumps(asr, sort_keys=True).encode()).hexdigest(),
            "audioHashVerification": "pass" if audio_hash and asr.get("audio_sha256") else "not supplied",
            "aliases": aliases, "cues": cue_ids, **alignment,
            "koFullContentRetained": True, "enFullContentRetained": True,
            "clauseUnits": "authored paired clauses; meaning verified in the existing whole-script review",
            "englishTiming": "samepairedKoreanspeech boundaries; not separatelyspokenEnglish"})
    output.mkdir(parents=True, exist_ok=True)
    for language in ("ko", "en"):
        srt = "\n\n".join(f"{row['cue']}\n{srt_stamp(row['start'])} --> {srt_stamp(row['end'])}\n{row[language]}" for row in rows) + "\n"
        (output / f"captions.{language}.srt").write_text(srt, encoding="utf-8")
    for language in ("ko", "en"):
        ass = ass_header(font_name) + "".join(ass_events(row, item if language == "ko" else item["enGeometry"], language)
                                             for row, item in zip(rows, layout))
        (output / f"captions.{language}.ass").write_text(ass, encoding="utf-8")
    json_write(output / "captions.json", {"style": "boxed-white-forest-v1", "cuePolicy": CAPTION_POLICY,
        "emphasisRoles": {k: {"rgb": "#" + v, "contrastOnWhite": contrast_on_white(v)} for k, v in EMPHASIS_COLORS.items()},
        "cues": rows})
    result = {"style": "boxed-white-forest-v1", "fontFile": str(font_file),
        "fontSha256": sha(font_file), "fontName": font_name, "fontSize": FONT_SIZE,
        "bodyWeight": 500, "emphasisWeight": 700, "boldFontFile": str(bold_file), "boldFontSha256": sha(bold_file),
        "cuePolicy": CAPTION_POLICY,
        "maxLineWidth": MAX_WIDTH, "maxLines": 2, "fixedCenter": [960, 970],
        "clock": "centisecond endpoints shared by SRT and ASS; actual60fps visibleframe bounds recorded",
        "geometryPassed": True, "actualEncodedPixels": "pending", "rows": layout}
    json_write(output / "caption-layout.json", result)
    json_write(output / "caption-alignment.json", {"status": "word-anchored-captions-built",
        "codeSha256": sha(Path(__file__)), "paragraphs": evidence,
        "bilingualCueCount": len(rows), "semanticTranslationPairing": "explicit authored clauses; complete text retained; final contexts still require review",
        "humanListeningAndPronunciation": "pending", "sourceAudioAndScriptsModified": False})
    print(f"{len(rows)} completepairedcues; measured48px fixedcenter960,970", flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir")
    args = parser.parse_args()
    require_authorized("captions")
    data = load(path(args.input))
    build(data, current_local_output(args.output_dir or data.get("outputDir", str(DEFAULT_OUTPUT))))


if __name__ == "__main__":
    main()
