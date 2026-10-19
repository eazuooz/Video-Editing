"""Prepare authored design-summary ASS after root finishes the current cut plan.

    python build-editorial-guides.py --dry-run
    python build-editorial-guides.py --prepare

Reads actual whole-source ASR words and current paired caption paragraphs, adds
no narration or source media, and preserves source/cut timing. --prepare writes
hash-pinned per-cut ASS and only its editorialGuideAss cut attachments. It does
not decode, render, recognize speech, use a GPU/browser, or modify Git. --help
does not import the production pipeline or inspect media.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import re
import uuid

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LOCAL = HERE.parents[1] / "production/local/reference-preserving-v3"
OUTPUT = LOCAL / "edit/editorial-guides"
SPEC = HERE / "editorial-guides.json"


def read(p):
    return json.loads(p.read_text(encoding="utf-8-sig"))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def scoped(value):
    p = Path(value)
    p = (p if p.is_absolute() else ROOT / p).resolve()
    p.relative_to(ROOT.resolve())
    return p


def receipt(p):
    return {"path": p.resolve().relative_to(ROOT.resolve()).as_posix(),
            "sha256": sha(p), "bytes": p.stat().st_size}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def normalized(text):
    return re.sub(r"[^0-9a-z가-힣]", "", str(text).lower())


def paragraph_rows(rows, pid):
    result = [r for r in rows if r["paragraph"] == pid]
    require(result, f"Current caption paragraph missing: {pid}")
    return result


def phrase_anchor(words, phrase, window, offset):
    """Locate an actual contiguous ASR phrase within its caption paragraph."""
    needle, matches = normalized(phrase), []
    for i, word in enumerate(words):
        a, b = word["timestamp"]
        if a is None or b is None or not window[0] - .04 <= a + offset < window[1]:
            continue
        joined = ""
        for j in range(i, min(i + 15, len(words))):
            start, end = words[j]["timestamp"]
            if start is None or end is None or end + offset > window[1] + .04:
                break
            joined += normalized(words[j]["text"])
            if joined == needle:
                matches.append({"phrase": phrase, "wordIndices": [i, j],
                    "sourceStart": a, "sourceEnd": end,
                    "globalStart": a + offset, "globalEnd": end + offset,
                    "actualWords": copy.deepcopy(words[i:j + 1])})
                break
            if not needle.startswith(joined):
                break
    require(len(matches) == 1, f"ASR phrase must match once inside its actual paragraph: {phrase}")
    return matches[0]


def selected_cut(cut, guide, sources):
    return (cut["kind"] == "independent-gameplay"
            and str(cut["scene"]).zfill(2) == guide["scene"]
            and cut.get("semanticSlot") in guide["semanticSlots"]
            and sources[cut["source"]]["game"] in guide["games"])


def write_atomic(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    temporary = p.with_name("." + p.name + "-" + uuid.uuid4().hex + ".tmp")
    # Hash and write the identical UTF-8 bytes on Windows too. text-mode writes
    #would translate LF to CRLF after the ASS content hash was calculated.
    temporary.write_bytes(value.encode("utf-8"))
    temporary.replace(p)


def build(plan_path, spec_path):
    from PIL import ImageFont
    from video_pipeline import (FPS, CAPTION_RECT, COLORS, ass_header, ass_text,
                                event, check_bounds, editorial_guide_binding)
    spec, plan = read(spec_path), copy.deepcopy(read(plan_path))
    require((spec["slug"], spec["revision"]) == ("player-customization", HERE.name),
            "Wrong current editorial-guide specification")
    require((plan["fps"], plan["width"], plan["height"]) == (60, 1920, 1080),
            "Measured FHD60 plan required")
    immutable = [spec["sourceAsr"], spec["captionLayout"]]
    for item in immutable:
        require(sha(scoped(item["path"])) == item["sha256"],
                "Current voice/caption evidence changed; update the guide specification")
    asr = read(scoped(spec["sourceAsr"]["path"]))
    captions = read(scoped(spec["captionLayout"]["path"]))
    selection_path = scoped(spec["sourceSelectionPath"])
    selection = read(selection_path)
    sources = {s["key"]: s for s in selection["sources"]}
    require(selection["referenceOnlyMediaExcluded"] is True, "Reference media cannot enter guide cuts")
    expected_audio = [x for x in plan["inputs"]
                      if x["path"].endswith("/narration-source.wav")]
    require(len(expected_audio) == 1 and expected_audio[0]["sha256"] == asr["audio_sha256"],
            "ASR does not belong to the current preserved narration")
    font_path = Path(spec["style"]["fontFile"])
    require(sha(font_path) == spec["style"]["fontSha256"], "Guide font changed")
    size, header_size = spec["style"]["fontSize"], spec["style"]["headerFontSize"]
    require(40 <= size <= 42 and 40 <= header_size <= 42, "Use the planned readable40-42px guide")
    font, header_font = ImageFont.truetype(str(font_path), size), ImageFont.truetype(str(font_path), header_size)
    offset = plan["brandingFrames"] / FPS
    inputs = [receipt(plan_path), receipt(spec_path), receipt(selection_path),
              *immutable, receipt(Path(__file__)), receipt(HERE / "video_pipeline.py")]
    # Only this builder's previous attachments may be regenerated; no foreign
    #editorial data or any source/cut/marks/timing field is replaced.
    for cut in plan["cuts"]:
        previous = cut.get("editorialGuideAss")
        if previous:
            require(previous.get("producer") == "build-editorial-guides.py",
                    "Preserve an editorial attachment owned by another producer")
            cut.pop("editorialGuideAss")
    blocks, mappings = [], []
    for guide in spec["guides"]:
        rows = paragraph_rows(captions["rows"], guide["paragraph"])
        window = [min(r["start"] for r in rows), max(r["end"] for r in rows)]
        eligible = [c for c in plan["cuts"] if selected_cut(c, guide, sources)]
        require(eligible, "No current selected gameplay cut for " + guide["id"])
        if guide["kind"] == "four-step-summary":
            anchors = [phrase_anchor(asr["words"], step["asrStartsWith"], window, offset)
                       for step in guide["steps"]]
            require(all(a["globalStart"] < b["globalStart"] for a, b in zip(anchors, anchors[1:])),
                    "Actual recap speech order changed")
            phases = [[a["globalStart"], anchors[i + 1]["globalStart"]
                       if i + 1 < len(anchors) else window[1]] for i, a in enumerate(anchors)]
            prefix, separator = guide["prefix"], " → "
            width = header_font.getlength(prefix) + sum(font.getlength(s["label"]) for s in guide["steps"]) + 3 * font.getlength(separator)
            x, y = guide["centerX"] - width / 2, guide["topY"]
            for active, (begin, end) in enumerate(phases):
                parts = [rf"{{\fs{header_size}\1c&HFFFFFF&}}" + ass_text(prefix), rf"{{\fs{size}}}"]
                for index, step in enumerate(guide["steps"]):
                    if index:
                        parts.append(r"{\1c&HFFFFFF&}" + ass_text(separator))
                    rgb = COLORS["yellow"] if index == active else "FFFFFF"
                    bgr = rgb[4:6] + rgb[2:4] + rgb[:2]
                    parts.append(rf"{{\1c&H{bgr}&}}" + ass_text(step["label"]))
                blocks.append({"guide": guide, "start": begin, "end": end,
                               "text": "".join(parts), "bounds": [x - 6, y - 6, x + math.ceil(width) + 6, y + size * 1.5 + 6],
                               "position": [x, y], "activeStage": active,
                               "actualAnchor": anchors[active], "cueNumbers": [r["cue"] for r in rows]})
            mappings.append({"guideId": guide["id"], "captionParagraph": guide["paragraph"],
                             "captionWindowGlobal": window, "asrWordAnchors": anchors,
                             "highlightGlobalWindows": phases})
        elif guide["kind"] == "combination-notice":
            begin = max(window[0], min(c["startFrame"] / FPS for c in eligible))
            end = min(begin + guide["displaySeconds"], window[1])
            require(begin < end, "No actual source window for the combination notice")
            width, y = font.getlength(guide["text"]), guide["topY"]
            x = guide["centerX"] - width / 2
            rgb = COLORS["yellow"]
            bgr = rgb[4:6] + rgb[2:4] + rgb[:2]
            blocks.append({"guide": guide, "start": begin, "end": end,
                           "text": rf"{{\fs{size}\1c&H{bgr}&}}" + ass_text(guide["text"]),
                           "bounds": [x - 6, y - 6, x + math.ceil(width) + 6, y + size * 1.5 + 6],
                           "position": [x, y], "activeStage": None,
                           "actualAnchor": None, "cueNumbers": [r["cue"] for r in rows]})
            mappings.append({"guideId": guide["id"], "captionParagraph": guide["paragraph"],
                             "captionWindowGlobal": window, "noticeGlobalWindow": [begin, end]})
        else:
            raise ValueError("Unknown explicitly authored guide kind")
    prepared, attachments = [], []
    for cut in plan["cuts"]:
        script, events = ass_header(), []
        protected = [plan.get("captionProtectedRect", CAPTION_RECT), *cut.get("protectedRects", [])]
        for block in blocks:
            guide = block["guide"]
            if not selected_cut(cut, guide, sources):
                continue
            lo = max(block["start"], cut["startFrame"] / FPS)
            hi = min(block["end"], cut["endFrame"] / FPS)
            if hi <= lo:
                continue
            source = sources[cut["source"]]
            require(source["sourceRole"] == "independent-gameplay" and source["referenceLesson"] is False
                    and source["media"]["sha256"] == cut["sourceSha256"], "Guide source identity changed")
            check_bounds(block["bounds"], [*protected, *guide["additionalProtectedOutputRects"]], "Editorial guide")
            require(block["bounds"][2] - block["bounds"][0] <= guide["maxWidth"], "Guide became too wide")
            a, b = lo - cut["startFrame"] / FPS, hi - cut["startFrame"] / FPS
            x, y = block["position"]
            script += event(a, b, rf"{{\an7\pos({x:.3f},{y:.3f})\bord4\shad0}}" + block["text"], 4)
            events.append({"guideId": guide["id"], "start": a, "end": b,
                           "globalStart": lo, "globalEnd": hi, "bounds": block["bounds"],
                           "activeStage": block["activeStage"], "actualAnchor": block["actualAnchor"],
                           "captionCues": block["cueNumbers"], "meaning": guide["meaning"]})
        if not events:
            continue
        digest = hashlib.sha256(script.encode("utf-8")).hexdigest()
        destination = OUTPUT / f'{cut["id"]}-{digest[:16]}.ass'
        attachment = {"producer": "build-editorial-guides.py",
                      "path": destination.relative_to(ROOT).as_posix(), "sha256": digest,
                      "cutBindingSha256": editorial_guide_binding(cut, plan),
                      "clock": "cut-relative-seconds", "coordinateSystem": "output1920x1080",
                      "appliesTo": ["clean", "captioned"], "detectorOutput": False,
                      "measuredGameData": False, "events": events,
                      "guideSpec": receipt(spec_path),
                      "mappingInputs": [*immutable, receipt(selection_path)],
                      "finalPixels": "pending"}
        cut["editorialGuideAss"] = attachment
        prepared.append((destination, script))
        attachments.append({"cutId": cut["id"], **attachment})
    for guide in spec["guides"]:
        require(any(any(e["guideId"] == guide["id"] for e in a["events"]) for a in attachments),
                "An authored guide has no actual current cut intersection")
    result = {"slug": "player-customization", "revision": HERE.name,
              "inputs": inputs, "sourceAsrClockOffsetSeconds": offset,
              "meaning": "authored editorial summary/notice, not native game UI or detector/measurement",
              "globalSpeechMappings": mappings, "cutAttachments": attachments,
              "assClock": "cut-relative seconds; half-open actual global cut intersection",
              "framesOrNarrationModified": False, "sameCutLayerInBothMasters": True,
              "geometryMeaning": "planned static bounds only; renderer additionally checks credits/protected areas and source marks",
              "actualCaptioned1080p375pxMovingPixels": "pending", "continuousPlaybackOrListening": "not performed"}
    return plan, result, prepared


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Resolve current actual words/cues/cuts; no writes or media")
    mode.add_argument("--prepare", action="store_true", help="Write per-cut ASS/receipts and attach only editorialGuideAss fields")
    parser.add_argument("--plan", default=str(HERE / "edit-plan.json"))
    parser.add_argument("--spec", default=str(SPEC))
    args = parser.parse_args()
    try:
        plan_path, spec_path = scoped(args.plan), scoped(args.spec)
        plan, result, prepared = build(plan_path, spec_path)
        if args.prepare:
            from audio_pipeline import require_authorized
            from video_pipeline import editorial_guide_ass
            authorization = require_authorized("prepare-authored-editorial-guides")
            for item in result["inputs"]:
                require(sha(scoped(item["path"])) == item["sha256"], "Guide input changed before preparation")
            newline_repairs = []
            for p, script in prepared:
                if p.exists():
                    expected = script.encode("utf-8")
                    if p.read_bytes() != expected:
                        previous = p.read_bytes()
                        require(previous.replace(b"\r\n", b"\n") == expected,
                                "Preserve conflicting existing ASS")
                        # The previous failed prepare never attached these
                        #CRLF files. Preserve exact old bytes before repairing
                        #only this producer's newline-equivalent partial ASS.
                        backup = p.with_name(p.name + ".preserved-crlf-" + sha(p)[:12] + ".txt")
                        if backup.exists():
                            require(backup.read_bytes() == previous, "Preserve conflicting newline-repair evidence")
                        else:
                            backup.write_bytes(previous)
                        write_atomic(p, script)
                        newline_repairs.append({"currentAss": receipt(p), "preservedPreviousBytes": receipt(backup),
                                                "meaning": "LF/CRLF byte-write repair only; identical decoded ASS text"})
                else:
                    write_atomic(p, script)
            for cut in plan["cuts"]:
                editorial_guide_ass(cut, plan)
            write_atomic(plan_path, json.dumps(plan, ensure_ascii=False, indent=2) + "\n")
            result.update(authorization=authorization, planAfter=receipt(plan_path),
                          newlineEquivalentPartialFileRepairs=newline_repairs)
            write_atomic(OUTPUT / "manifest.json", json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps({"status": "prepared" if args.prepare else "dry-run; no writes",
                          "cutAssFiles": len(prepared), "actualWordAndCueMapping": result["globalSpeechMappings"],
                          "mediaJobs": 0, "finalMovingMobilePixels": "pending"}, ensure_ascii=False, indent=2))
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(2, f"Editorial guide preparation stopped: {exc}\n")


if __name__ == "__main__":
    main()
