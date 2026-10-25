"""Transform reviewed source-coordinate bursts without rendering media.

Inputs remain byte-for-byte unchanged.  Output is a derived edit plan whose
gameplay is contained in the agreed viewport; explanations/audio/timing stay
untouched.  This script validates the real video_pipeline annotations schema
in memory.  It never invokes FFmpeg, a renderer, GPU, ASR, or publishing.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path

import video_pipeline as pipeline
from PIL import ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
VIEWPORT = [224, 52, 1472, 828]
HEADER_RECT = [0, 0, 1920, 48]
FONT_SIZE = 50
THICKNESS = 8
MIN_VISIBLE_SECONDS = .25
EPS = 1e-7
COLOR_ROLES = {"focus": "green", "reference": "blue", "goal": "yellow", "caution": "red"}

RELATIONS = {
    "mineral-before": (["광물"], "Object definition before the approach: the mineral is identified while this same paragraph returns to the game."),
    "opened-passage": (["주변 공간이 열", "피할 적과 얻을 광물"], "The visible opened passage carries the immediately preceding result into the next paragraph's same minerals, threats and space."),
    "escape-timer": (["탈출 안내", "제한 시간"], "The real countdown is visible while escape guidance/time limit is introduced."),
    "pod-entrance": (["탈출 지점", "목적이 선택"], "Delayed visual confirmation of the already defined escape destination within the same purpose/terrain paragraph; not a new mining target."),
    "world-endpoints": (["시작점", "성으로"], "Define the visible start/castle as the world-building screen is introduced, then inherit the land/path sentence."),
    "placed-road": (["길을 놓고", "이어질 구조"], "The placed road confirms the structure being described. Clear before erasure changes the road."),
    "world-branch": (["갈림길"], "The actual junction is named during the branching/course-placement explanation."),
    "shared-countdown": (["여러 캐릭터", "같은 출발"], "Define the real shared start signal during the same multiplayer-start explanation."),
    "relative-positions": (["여러 캐릭터", "같은 출발", "상대가 어디"], "Two visible character positions confirm the same shared-start/movement statement; no rank or winning intention is claimed."),
}


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(path):
    try:
        return str(Path(path).absolute().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def normalize(text):
    return "".join(c for c in text if c.isalnum()).lower()


def union(intervals):
    result = []
    for a, b in sorted(intervals):
        if b <= a:
            continue
        if result and a <= result[-1][1] + EPS:
            result[-1][1] = max(result[-1][1], b)
        else:
            result.append([a, b])
    return result


def reviewed_spans(track, burst):
    """Hide any pair that crosses an unverified/occluded native sample."""
    spans = []
    for a, b in zip(burst["keyframes"], burst["keyframes"][1:]):
        if all(k.get("visible", False) and k.get("targetVisible", False) for k in (a, b)):
            spans.append([max(a["sourceTime"], burst["sourceIn"]),
                          min(b["sourceTime"], burst["sourceOutExclusive"])])
    spans = union(spans)
    for hidden in track.get("hiddenIntervals", []):
        h0, h1 = hidden["in"], hidden["outExclusive"]
        remaining = []
        for a, b in spans:
            if b <= h0 or a >= h1:
                remaining.append([a, b])
            else:
                if a < h0:
                    remaining.append([a, h0])
                if b > h1:
                    remaining.append([h1, b])
        spans = remaining
    return spans


def contain(cut):
    sw, sh = cut["sourceNativeDimensions"]
    x, y, width, height = VIEWPORT
    scale = min(width / sw, height / sh)
    return [x + (width - sw * scale) / 2, y + (height - sh * scale) / 2,
            sw * scale, sh * scale]


def point(value, box):
    x, y, width, height = box
    return [x + value[0] * width, y + value[1] * height]


def interpolate_shape(keys, when, shape_id):
    """Only interpolate between actual reviewed source samples."""
    if when < keys[0]["sourceTime"] - EPS or when > keys[-1]["sourceTime"] + EPS:
        raise ValueError("Source annotation extrapolation is forbidden")
    left, right = keys[-2:]
    for a, b in zip(keys, keys[1:]):
        if a["sourceTime"] - EPS <= when <= b["sourceTime"] + EPS:
            left, right = a, b
            break
    a = next(x for x in left["shapes"] if x["id"] == shape_id)
    b = next(x for x in right["shapes"] if x["id"] == shape_id)
    if a["kind"] != b["kind"]:
        raise ValueError("A tracked primitive cannot change shape kind")
    q = (when - left["sourceTime"]) / (right["sourceTime"] - left["sourceTime"])
    q = min(1., max(0., q))
    out = copy.deepcopy(a)
    for name in ("center", "radii", "labelAnchor"):
        if a.get(name) is not None:
            out[name] = [v + (w - v) * q for v, w in zip(a[name], b[name])]
    if "points" in a:
        if len(a["points"]) != len(b["points"]):
            raise ValueError("Tracked paths need identical point counts")
        out["points"] = [[v + (w - v) * q for v, w in zip(p, r)]
                         for p, r in zip(a["points"], b["points"])]
    return out


def output_geometry(shape, box):
    if shape["kind"] == "ellipse":
        x, y = point(shape["center"], box)
        rx, ry = shape["radii"][0] * box[2], shape["radii"][1] * box[3]
        return "circle", {"x": x - rx, "y": y - ry, "w": 2 * rx, "h": 2 * ry}
    if shape["kind"] not in ("polyline", "arrow"):
        raise ValueError("Unsupported reviewed primitive: " + shape["kind"])
    pts = [point(p, box) for p in shape["points"]]
    if shape.get("closed"):
        pts.append(pts[0][:])
    return ("arrow" if shape["kind"] == "arrow" else "path"), {"points": pts}


def paragraph_scope(track, burst, cut):
    scope = list(track["paragraphIds"])
    carry = None
    # Explicit root authorization: keep this original1s result, without
    # inventing motion or extending its source-time availability.
    if (track["id"], burst["id"], cut.get("bankId")) == (
            "ore-opening", "opened-passage", "scout-ore-opening"):
        scope = ["05-p01", "05-p02"]
        carry = {
            "from": "05-p01", "to": "05-p02",
            "reason": "The next '여기서는' inherits the same mineral/avoidance/space result; root explicitly authorized this adjacent carry.",
            "sourceTimeExtension": False,
        }
    return [p for p in scope if p in cut["paragraphIds"]], carry


def speech_receipt(burst_id, a, b, scope, paragraphs):
    keywords, reason = RELATIONS[burst_id]
    targets, current = [], []
    for pid in scope:
        para = paragraphs[pid]
        for cue in para["captionCues"]:
            overlap = max(0., min(b, cue["end"]) - max(a, cue["start"]))
            item = {"paragraphId": pid, "text": cue["ko"], "start": cue["start"],
                    "end": cue["end"], "overlapSeconds": round(overlap, 8)}
            if overlap > EPS:
                current.append(item)
            if any(normalize(k) in normalize(cue["ko"]) for k in keywords):
                targets.append(item)
    if not targets:
        raise ValueError("No measured speech evidence for " + burst_id)
    gap = min(max(0., c["start"] - b, a - c["end"]) for c in targets)
    return {
        "status": "related-objects-and-continuous-event-reviewed-not-exact-noun-lock",
        "reason": reason, "targetKeywords": keywords, "targetCues": targets,
        "currentOverlappingCues": current, "nearestTargetCueGapSeconds": round(gap, 8),
        "exactTargetCueOverlap": any(c["overlapSeconds"] > EPS for c in targets),
        "timingSource": "Measured existing48k/ASR paragraph and caption cues; no estimated TTS time.",
        "finalMovingSpeechAndPictureReview": "pending",
    }


def geometry_bounds(mark, t):
    g = pipeline.interpolate(mark["keyframes"], t, mark["shape"])
    if mark["shape"] == "circle":
        return [g["x"], g["y"], g["x"] + g["w"], g["y"] + g["h"]]
    points = g["points"]
    margin = 24 if mark["shape"] == "arrow" else THICKNESS / 2
    return [min(p[0] for p in points) - margin, min(p[1] for p in points) - margin,
            max(p[0] for p in points) + margin, max(p[1] for p in points) + margin]


def active(mark, t):
    return mark["t0"] - EPS <= t < mark["t1"] - EPS


def label_layout(cut, plan, adjustments):
    """One static label per mark; do not let text cross a tracked target."""
    font = ImageFont.truetype(plan["annotationFontFile"], FONT_SIZE)
    protected = [plan["captionProtectedRect"], HEADER_RECT, *cut.get("protectedRects", [])]
    placed = []
    for mark in cut["marks"]:
        original = mark["labelPosition"][:]
        width = math.ceil(font.getlength(mark["label"]))
        candidates = [(0, 0), (0, -90), (-100, -90), (100, -90),
                      (0, -180), (-180, 0), (100, 80), (-100, 80)]
        chosen = None
        for dx, dy in candidates:
            # Keep text inside the gameplay pane, including its6px outline.
            x = min(max(original[0] + dx, VIEWPORT[0] + 8),
                    VIEWPORT[0] + VIEWPORT[2] - width - 8)
            y = min(max(original[1] + dy, HEADER_RECT[3] + 8),
                    plan["captionProtectedRect"][1] - FONT_SIZE * 1.5 - 8)
            bounds = [x - 6, y - 6, x + width + 6, y + FONT_SIZE * 1.5 + 6]
            try:
                pipeline.check_bounds(bounds, protected, "Annotation label")
            except ValueError:
                continue
            conflict = any(pipeline.intersects(bounds, r["bounds"])
                           and max(mark["t0"], r["t0"]) < min(mark["t1"], r["t1"]) - EPS
                           for r in placed)
            if conflict:
                continue
            first = math.ceil(mark["t0"] * plan["fps"])
            last = math.ceil(mark["t1"] * plan["fps"])
            for frame in range(first, last):
                t = frame / plan["fps"]
                if any(active(other, t) and pipeline.intersects(bounds, geometry_bounds(other, t))
                       for other in cut["marks"]):
                    conflict = True
                    break
            if not conflict:
                chosen = [round(x, 4), round(y, 4)]
                placed.append({"bounds": bounds, "t0": mark["t0"], "t1": mark["t1"]})
                break
        if chosen is None:
            raise ValueError("No collision-free label placement for " + mark["id"])
        mark["labelPosition"] = chosen
        if math.dist(chosen, original) > .001:
            adjustments.append({"cutId": cut["id"], "markId": mark["id"],
                                "from": original, "to": chosen,
                                "reason": "Keep50px text clear of target geometry, other labels, header and fixed captions."})


def transform(plan, tracks, plan_hash, tracks_hash):
    if (plan["fps"], plan["width"], plan["height"]) != (60, 1920, 1080):
        raise ValueError("Only the measured1920x1080/60fps plan is supported")
    out = copy.deepcopy(plan)
    out["annotationFontFile"] = "C:/Windows/Fonts/malgun.ttf"
    paragraphs = {p["id"]: p for p in plan["measuredParagraphs"]}
    receipt = {"status": "pending", "viewport": VIEWPORT, "headerProtectedRect": HEADER_RECT,
               "inputPlanSha256": plan_hash, "annotationTracksSha256": tracks_hash,
               "marks": [], "skipped": [], "labelAdjustments": [], "cutValidation": []}
    checked_evidence = set()
    for track in tracks["tracks"]:
        for burst in track["bursts"]:
            for key in burst["keyframes"]:
                evidence = key["evidence"]
                if evidence["sourceSha256"] != track["sourceSha256"]:
                    raise ValueError("Native evidence source binding changed")
                frame = ROOT / evidence["path"]
                if evidence["path"] not in checked_evidence:
                    if digest(frame) != evidence["nativeFrameSha256"]:
                        raise ValueError("Reviewed native PNG changed: " + str(frame))
                    checked_evidence.add(evidence["path"])
    for cut in out["cuts"]:
        if cut["kind"] != "independent-gameplay":
            continue
        if cut.get("editorialGuideAss"):
            raise ValueError("Create guide ASS receipts after annotation/viewport transformation")
        if cut.get("marks"):
            raise ValueError("Input must be the original measured plan, not an annotated derivative")
        if cut.get("playbackSpeed", 1) != 1 or cut.get("loop"):
            raise ValueError("Native timing cannot be changed")
        cut["viewport"] = VIEWPORT[:]
        # Reserve header for mark validation only.  A later guide ASS owns its
        # actual header bounds, so this is metadata rather than protectedRects.
        cut["annotationReservedHeader"] = HEADER_RECT[:]
        cut["annotationContainRect"] = contain(cut)
        cut["marks"] = []
        duration = cut["frames"] / plan["fps"]
        source_a, source_b = cut["sourceStart"], cut["sourceStart"] + duration
        global_a = cut["startFrame"] / plan["fps"]
        for track in tracks["tracks"]:
            if track["sourceId"] != cut["source"]:
                continue
            if track["sourceSha256"] != cut["sourceSha256"]:
                raise ValueError("Annotation source hash does not match current cut")
            for burst in track["bursts"]:
                scope, carry = paragraph_scope(track, burst, cut)
                if not scope:
                    continue
                scope_times = union([(paragraphs[p]["startFrame"] / plan["fps"],
                                      paragraphs[p]["endFrame"] / plan["fps"]) for p in scope])
                keys = burst["keyframes"]
                segments = []
                for scope_a, scope_b in scope_times:
                    for visible_a, visible_b in reviewed_spans(track, burst):
                        # Clipped boundaries must lie between verified keys.
                        a = max(source_a, visible_a, source_a + scope_a - global_a)
                        b = min(source_b, visible_b, source_a + scope_b - global_a)
                        if b > a + EPS:
                            segments.append([a, b])
                for a, b in union(segments):
                    if b <= a + EPS:
                        continue
                    if b - a < MIN_VISIBLE_SECONDS:
                        receipt["skipped"].append({"cutId": cut["id"], "burstId": burst["id"],
                                                   "sourceIntersection": [a, b],
                                                   "reason": "Too brief after the verified/scope intersection; no false extension."})
                        continue
                    speech = speech_receipt(burst["id"], global_a + a - source_a,
                                            global_a + b - source_a, scope, paragraphs)
                    shape_ids = [s["id"] for s in keys[0]["shapes"]]
                    for shape_id in shape_ids:
                        first = next(s for s in keys[0]["shapes"] if s["id"] == shape_id)
                        if not first.get("label"):
                            receipt["skipped"].append({"cutId": cut["id"], "burstId": burst["id"],
                                                       "shapeId": shape_id,
                                                       "reason": "Optional unlabeled helper omitted; pipeline requires one meaningful label per mark. The primary named contour/circle/path remains."})
                            continue
                        sample_times = sorted({a, b, *[k["sourceTime"] for k in keys if a < k["sourceTime"] < b]})
                        output_keys = []
                        for t in sample_times:
                            source_shape = interpolate_shape(keys, t, shape_id)
                            kind, geometry = output_geometry(source_shape, cut["annotationContainRect"])
                            output_keys.append({"t": t - source_a, **geometry})
                        mid_shape = interpolate_shape(keys, (a + b) / 2, shape_id)
                        mark_id = ".".join([cut["id"], track["id"], burst["id"], shape_id])
                        mark = {"id": mark_id, "shape": kind, "t0": a - source_a,
                                "t1": b - source_a, "color": COLOR_ROLES[first["colorRole"]],
                                "thickness": THICKNESS, "fontSize": FONT_SIZE,
                                "label": first["label"],
                                "labelPosition": point(mid_shape["labelAnchor"], cut["annotationContainRect"]),
                                "keyframes": output_keys, "hiddenIntervals": [],
                                "visibleIntervals": [[a - source_a, b - source_a]],
                                "revealSeconds": min(burst.get("revealSeconds", .1), (b - a) / 2),
                                "annotationSource": {"trackId": track["id"], "burstId": burst["id"],
                                                     "primitiveId": shape_id, "sourceSha256": track["sourceSha256"],
                                                     "sourceInterval": [a, b], "paragraphScope": scope,
                                                     "adjacentCarry": carry,
                                                     "geometryEvidence": [k["evidence"] for k in keys],
                                                     "speechRelation": speech,
                                                     "detectorOutput": False, "measuredGameData": False}}
                        cut["marks"].append(mark)
                        receipt["marks"].append({"id": mark_id, "cutId": cut["id"],
                                                 "sourceInterval": [a, b], "cutRelativeInterval": [mark["t0"], mark["t1"]],
                                                 "globalInterval": [global_a + mark["t0"], global_a + mark["t1"]],
                                                 "paragraphScope": scope, "adjacentCarry": carry,
                                                 "speechRelation": speech})
        label_layout(cut, out, receipt["labelAdjustments"])
        # Static ASS/geometry validation only; no media is rendered.
        validation_cut = copy.deepcopy(cut)
        validation_cut.setdefault("protectedRects", []).append(HEADER_RECT[:])
        _, log = pipeline.annotations(validation_cut, out)
        receipt["cutValidation"].append({"cutId": cut["id"], "viewport": cut["viewport"], **log})
        cut["annotationStatus"] = ("verified-source-burst-transform; final moving/375px review pending"
                                    if cut["marks"] else "no eligible reviewed burst in this source/time/paragraph intersection")
    receipt.update({"status": "pass-static-transform-validation", "actualCutCount": len(receipt["cutValidation"]),
                    "markCount": len(receipt["marks"]), "mediaRenderRun": False,
                    "reviewedNativePngHashesChecked": len(checked_evidence),
                    "checks": {"allActualCutsContainedWithoutCropOrDistortion": True,
                               "closedContoursRepeatFirstPoint": True,
                               "nativeCutParagraphAndVerifiedSpanIntersection": True,
                               "occludedOrUnverifiedSamplesHidden": True,
                               "noSourceTimeExtrapolation": True,
                               "labelsAvoidTrackedGeometryAndEachOther": True,
                               "captionAndTemporaryHeaderReservationPassEveryVisibleFrame": True,
                               "sourceUiProtectedRectsPreserved": True,
                               "headerReservationNotWrittenIntoProtectedRects": True},
                    "finalMovingAnd375pxReview": "pending", "originalPlanPreserved": True})
    out["annotationReview"] = "Verified short source bursts transformed; static per-frame schema/bounds pass. Final moving speech/picture and375px review pending."
    out["annotationTransform"] = {"sourcePlanSha256": plan_hash, "tracksSha256": tracks_hash,
                                  "viewport": VIEWPORT, "fontSize": FONT_SIZE,
                                  "geometryClock": "output pixels / cut-relative seconds",
                                  "sourceTimeExtrapolation": False, "detectorOutput": False,
                                  "measuredGameData": False, "audioNarrationExplanationChanged": False}
    return out, receipt


def verify_preservation(original, derived):
    """Only the explicitly authorized actual-cut display/mark fields change."""
    allow = {"viewport", "annotationReservedHeader", "annotationContainRect", "marks", "annotationStatus"}
    if len(original["cuts"]) != len(derived["cuts"]):
        raise ValueError("Cut count changed")
    for a, b in zip(original["cuts"], derived["cuts"]):
        if a["kind"] == "explanation":
            if a != b:
                raise ValueError("Explanation cut changed")
        elif {k: v for k, v in a.items() if k not in allow} != {k: v for k, v in b.items() if k not in allow}:
            raise ValueError("Gameplay timing/source/audio changed")
    for key in ("scenes", "measuredParagraphs", "audio", "mixFile", "captionsAss", "bodyFrames",
                "actualFrames", "explanationFrames", "mcFrames", "totalFrames"):
        if original.get(key) != derived.get(key):
            raise ValueError("Protected timing/audio/caption value changed: " + key)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=HERE / "edit-plan.json")
    parser.add_argument("--tracks", type=Path, default=ROOT / "projects/similar-game-design/planning/annotation-tracks-v2.json")
    parser.add_argument("--output", type=Path, default=HERE / "edit-plan-annotated.json")
    parser.add_argument("--validation", type=Path, default=HERE / "annotation-transform-validation.json")
    args = parser.parse_args()
    if args.output.resolve() in (args.plan.resolve(), args.tracks.resolve()):
        raise ValueError("The derived output cannot overwrite either input")
    before = {args.plan: digest(args.plan), args.tracks: digest(args.tracks)}
    original, tracks = read(args.plan), read(args.tracks)
    result, receipt = transform(original, tracks, before[args.plan], before[args.tracks])
    verify_preservation(original, result)
    receipt["inputs"] = [{"path": relative(p), "sha256": h} for p, h in before.items()]
    receipt["builder"] = {"path": relative(Path(__file__)), "sha256": digest(__file__)}
    write(args.output, result)
    receipt["output"] = {"path": relative(args.output), "sha256": digest(args.output)}
    for path, expected in before.items():
        if digest(path) != expected:
            raise ValueError("An immutable input changed during transform")
    write(args.validation, receipt)
    print(json.dumps({"output": relative(args.output), "validation": relative(args.validation),
                      "actualCuts": receipt["actualCutCount"], "marks": receipt["markCount"],
                      "viewport": VIEWPORT, "mediaRenderRun": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
