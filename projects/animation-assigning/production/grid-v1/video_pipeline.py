"""A01 animation native-speed FHD cut rendering, paired masters and structural verification.

No media job runs on import. CLI::

    python video_pipeline.py cuts --plan .../edit-plan.json
    python video_pipeline.py pair --plan .../edit-plan.json --mix final-mix.wav
    python video_pipeline.py verify --plan .../edit-plan.json

Paths in the plan are repository-relative (absolute paths are also accepted).
``startFrame``/``endFrame`` are GLOBAL, half-open timeline positions. The body
starts at frame120 and ends600 frames before ``totalFrames``. Every cut carries
``id, scene, startFrame, endFrame, frames, kind``. Gameplay adds ``sourceFile``
and ``sourceStart`` (seconds); explanations add ``renderedSource`` and optional
``renderedStartFrame``. An explanation uses either the existing ``nativeCapture``
receipt or ``explanationRender`` with kind ``annotated-still`` and a hash-pinned
completed receipt. A source freeze counts as explanation, never gameplay.
No gameplay looping, holding or speed changes are done.

Gameplay is contained, preserving display aspect ratio, in ``viewport``
``[x,y,width,height]`` (default full1920x1080). ``sourceAttribution`` (or legacy
``credit``) is provenance for the bottom of the description, never drawn into
video. ``copyrightCredit`` is also metadata-only. Preserve original source
watermarks with protectedRects; never erase them. A source requiring a new
on-screen credit is rejected unless the original recording already displays it.

Editorial marks use OUTPUT pixels and CUT-RELATIVE seconds::

    {"id":"target","shape":"rect","t0":0.2,"t1":3.4,
     "color":"red","thickness":8,"label":"사용할 대상",
     "labelPosition":[80,110],
     "keyframes":[{"t":0.2,"x":300,"y":200,"w":130,"h":220},
                  {"t":3.4,"x":450,"y":200,"w":130,"h":220}],
     "hiddenIntervals":[[1.4,1.8]],"revealSeconds":0.25}

Shapes: rect/circle with x,y,w,h keyframes, path/arrow with ``points`` per
keyframe (same point count in each keyframe). A static geometry may be supplied
directly on the mark. Keyframes must span the visible interval; no tracking
extrapolation is permitted. ``hiddenIntervals`` covers explicit occlusions;
``visibleIntervals`` can restrict availability further. Cut boundaries always
clear every mark. Colors are red/blue/green/yellow or exact RGB hex. All marks
are editorial guidance; this module never computes detector/game measurements.
Mark and label bounds must avoid ``captionProtectedRect`` (default the complete
two-line fixed-caption area including outline/shadow), credits and optional
``protectedRects``. Internal source cuts must be split into separate edit cuts.

Optional ``editorialGuideAss`` is a hash-pinned, cut-relative ASS receipt from
build-editorial-guides.py. These explicitly authored design-summary labels are
baked into the shared cut before pairing, so clean/captioned masters contain
the same guide. Its source/cut binding, times and protected bounds are checked
before rendering; it is never a game HUD, detector output or measured statistic.

Optional plan keys: brandingFile, membershipFile, mixFile, captionsAss, outputDir,
outputStem, expectedGameplayShare, ratioToleranceFrames (at most1).
``expectedGameplayShare`` records the exact measured cut share. The default
contract remains60:40; a hash-pinned ``ratioChoice: {path, sha256}`` may select
concept-sized footage only for this A01/grid-v1 revision, with the explicit
recommended-production-choice-v1 scope and reasons in that choice file.
The first two default to the byte-preserved approved reward-project clips.
``pair`` encodes ONE continuous AAC stream and copies it into both masters.
``verify`` is structural evidence only; visual/listening QA remains separate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
from fractions import Fraction
from pathlib import Path
from storage_paths import repo_path as routed_repo_path, write_path as routed_write_path, relative as routed_relative

from audio_pipeline import require_authorized, current_local_output, current_plan, tool

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
DEFAULT_OUTPUT = PROJECT / "production/local" / HERE.name / "edit"
FPS, WIDTH, HEIGHT = 60, 1920, 1080
ENCODER = ["-c:v", "libx264", "-threads", "4", "-preset", "veryfast",
           "-crf", "17", "-pix_fmt", "yuv420p", "-color_primaries", "bt709",
           "-color_trc", "bt709", "-colorspace", "bt709",
           "-video_track_timescale", "60000"]
COLORS = {"red": "EF8585", "blue": "73C7C2", "green": "A4C6A0",
          "yellow": "E8CF83", "orange": "F39A4B"}
CAPTION_RECT = [150, 892, 1784, 1060]  # x0,y0,x1,y1; two lines+outline+shadow
EXPLANATION_CHIP_RECT = [1540, 30, 1900, 116]


def path(value: str | Path) -> Path:
    return routed_repo_path(value)


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8-sig"))


def save(p: Path, value):
    p = routed_write_path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha(p: Path) -> str:
    digest = hashlib.sha256()
    with p.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def binary(name: str) -> str:
    override = os.environ.get(name.upper())
    return override or tool(name)


def run(arguments: list[str], log: Path):
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("w", encoding="utf-8") as stream:
        result = subprocess.run([binary("ffmpeg"), "-y", "-hide_banner", "-v", "warning",
                                 "-filter_threads", "1", "-filter_complex_threads", "1",
                                 *map(str, arguments)], cwd=ROOT, stdout=stream,
                                stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f"FFmpeg failed: {log}\n" + log.read_text(
            encoding="utf-8", errors="replace")[-4000:])


def probe(p: Path, count: bool = False) -> dict:
    args = [binary("ffprobe"), "-v", "error"]
    if count:
        args += ["-count_frames"]
    args += ["-show_streams", "-show_format", "-of", "json", str(p)]
    return json.loads(subprocess.check_output(args, cwd=ROOT))


def video_stream(p: Path, count: bool = False) -> dict:
    streams = [s for s in probe(p, count)["streams"] if s["codec_type"] == "video"]
    if len(streams) != 1:
        raise ValueError(f"Expected one video stream: {p}")
    return streams[0]


def assert_video(p: Path, frames: int, count: bool = False) -> dict:
    s = video_stream(p, count)
    actual = s.get("nb_read_frames") if count else s.get("nb_frames")
    if actual in (None, "N/A"):
        s = video_stream(p, True)
        actual = s.get("nb_read_frames")
    if (s["width"], s["height"]) != (WIDTH, HEIGHT):
        raise ValueError(f"Not1920x1080: {p}: {s}")
    if Fraction(s["avg_frame_rate"]) != FPS or int(actual) != frames:
        raise ValueError(f"Frame count/rate mismatch: {p}: expected{frames}@60: {s}")
    if s.get("sample_aspect_ratio", "1:1") not in ("1:1", "0:1"):
        raise ValueError(f"Non-square output pixels: {p}")
    return s


def fixed_caption_rect(plan: dict) -> list:
    if plan.get("captionProtectedRect", CAPTION_RECT) != CAPTION_RECT:
        raise ValueError("The fixed two-line caption geometry cannot be moved or reduced")
    return list(CAPTION_RECT)


def ratio_choice(plan: dict) -> dict | None:
    """Read a recorded local editorial choice, never a generic ratio bypass."""
    item = plan.get("ratioChoice")
    if item is None:
        return None
    if (not isinstance(item, dict) or not isinstance(item.get("sha256"), str)
            or not re.fullmatch(r"[0-9a-f]{64}", item["sha256"])):
        raise ValueError("ratioChoice requires a local choice file and its actual SHA256")
    choice_path = path(item["path"])
    if not choice_path.resolve().is_relative_to(HERE.resolve()) or choice_path.suffix.lower() != ".json":
        raise ValueError("ratioChoice must be recorded inside this revision, not a global override")
    if sha(choice_path) != item["sha256"]:
        raise ValueError("Recorded ratio choice changed; bind the current choice explicitly")
    choice = load(choice_path)
    expected = ("A01", "animation-assigning", "grid-v1")
    if (PROJECT.name, HERE.name) != expected[1:]:
        raise ValueError("Episode-specific ratio choice cannot be reused by another pipeline")
    for value in (plan, choice):
        if tuple(value.get(k) for k in ("episode", "slug", "revision")) != expected:
            raise ValueError("ratioChoice is restricted to episode A01, animation-assigning, grid-v1")
    if (choice.get("basis") != "recommended-production-choice-v1"
            or choice.get("defaultContractAcknowledged") != "actual60:explanation40"
            or not isinstance(choice.get("scope"), str) or not choice["scope"].strip()
            or not isinstance(choice.get("decision"), str) or not choice["decision"].strip()
            or not isinstance(choice.get("reasons"), list) or not choice["reasons"]
            or any(not isinstance(reason, str) or not reason.strip() for reason in choice["reasons"])):
        raise ValueError("ratioChoice needs the delegated basis, local scope, decision and evidence-based reasons")
    return {"path": routed_relative(choice_path), "sha256": item["sha256"],
            "basis": choice["basis"], "episode": "A01", "revision": "grid-v1",
            "scope": choice["scope"], "defaultContractAcknowledged": "actual60:explanation40"}


def validate_plan(plan: dict):
    fixed_caption_rect(plan)
    if (plan.get("fps"), plan.get("width"), plan.get("height")) != (FPS, WIDTH, HEIGHT):
        raise ValueError("Plan must explicitly specify fps60,width1920,height1080")
    if plan["totalFrames"] != plan["bodyFrames"] + 720:
        raise ValueError("totalFrames must equal bodyFrames+120branding+600membership")
    cursor, gameplay, ids = 120, 0, set()
    for cut in plan["cuts"]:
        cid = cut["id"]
        if not re.fullmatch(r"[A-Za-z0-9_-]+", cid) or cid in ids:
            raise ValueError(f"Unsafe/duplicate cut ID: {cid}")
        ids.add(cid)
        if cut["startFrame"] != cursor or cut["endFrame"] - cursor != cut["frames"] or cut["frames"] < 1:
            raise ValueError(f"Noncontiguous/invalid global cut: {cid}")
        cursor = cut["endFrame"]
        if cut["kind"] not in ("independent-gameplay", "explanation"):
            raise ValueError(f"Unsupported source classification: {cid}")
        if cut.get("loop") or cut.get("playbackSpeed", 1) != 1 or cut.get("holdAfterFrames"):
            raise ValueError(f"Only native-speed unlooped cuts are supported: {cid}")
        if cut["kind"] == "independent-gameplay":
            if cut.get("explanationRender") is not None or cut.get("nativeCapture") is not None:
                raise ValueError("Source freezes and native demonstrations must be classified as explanation")
            gameplay += cut["frames"]
            if not cut.get("sourceFile") or cut.get("sourceStart", 0) < 0:
                raise ValueError(f"Missing gameplay source: {cid}")
            if not (cut.get("sourceAttribution") or cut.get("credit")):
                raise ValueError(f"Independent gameplay needs description/source provenance: {cid}")
            if cut.get("onScreenAttributionRequired") is True and cut.get("sourceAlreadyDisplaysRequiredAttribution") is not True:
                raise ValueError("Use a source with description-compatible rights or an already visible required source notice")
        elif not cut.get("renderedSource"):
            raise ValueError(f"Explanation requires actually renderedSource: {cid}")
    if cursor != plan["totalFrames"] - 600:
        raise ValueError("Body must end immediately before exact600-frame membership")
    if plan["bodyFrames"] <= 0:
        raise ValueError("A body must contain a positive number of frames")
    measured_share = gameplay / plan["bodyFrames"]
    expected_share = plan.get("expectedGameplayShare")
    if (not isinstance(expected_share, (int, float)) or isinstance(expected_share, bool)
            or not math.isfinite(expected_share) or not 0 <= expected_share <= 1
            or not math.isclose(expected_share, measured_share, rel_tol=0, abs_tol=1e-12)):
        raise ValueError("expectedGameplayShare must equal the actual gameplayFrames/bodyFrames, not a quota")
    tolerance = plan.get("ratioToleranceFrames", 1)
    if not isinstance(tolerance, (int, float)) or not math.isfinite(tolerance) or not 0 <= tolerance <= 1:
        raise ValueError("Ratio tolerance cannot exceed one frame")
    choice = ratio_choice(plan)
    if choice is None and abs(gameplay - .6 * plan["bodyFrames"]) > tolerance:
        raise ValueError(f"Default60:40 contract outside one-frame tolerance: {gameplay}/{plan['bodyFrames']}")
    return {"gameplayFrames": gameplay, "explanationFrames": plan["bodyFrames"] - gameplay,
            "bodyFrames": plan["bodyFrames"], "gameplayShare": measured_share,
            "ratioChoice": choice}


def stamp(seconds: float) -> str:
    n = round(seconds * 100)
    return f"{n // 360000}:{n // 6000 % 60:02}:{n // 100 % 60:02}.{n % 100:02}"


def ass_header() -> str:
    return """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Mark,Malgun Gothic,42,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,4,0,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def ass_text(value: str) -> str:
    if any(c in value for c in ("{", "}", "\\")):
        raise ValueError("ASS text must not contain override syntax")
    return value.replace("\n", r"\N")


def event(start: float, end: float, text: str, layer: int = 1) -> str:
    return f"Dialogue: {layer},{stamp(start)},{stamp(end)},Mark,,0,0,0,,{text}\n"


def polygon(points: list) -> str:
    return "m " + " l ".join(f"{round(x)} {round(y)}" for x, y in points) + " c"


def outline(shape: str, geometry: dict, thickness: float) -> str:
    x, y, w, h = (geometry[k] for k in ("x", "y", "w", "h"))
    if w <= thickness * 2 or h <= thickness * 2:
        raise ValueError("Hollow mark must be larger than twice its stroke")
    if shape == "circle":
        def points(rx, ry):
            return [(x + w / 2 + rx * math.cos(i * math.pi / 32),
                     y + h / 2 + ry * math.sin(i * math.pi / 32)) for i in range(64)]
        return polygon(points(w / 2, h / 2)) + " " + polygon(list(reversed(
            points(w / 2 - thickness, h / 2 - thickness))))
    return polygon([(x, y), (x + w, y), (x + w, y + h), (x, y + h)]) + " " + polygon([
        (x + thickness, y + thickness), (x + thickness, y + h - thickness),
        (x + w - thickness, y + h - thickness), (x + w - thickness, y + thickness)])


def traced_path(points: list, thickness: float, progress: float, arrow: bool) -> str:
    lengths = [math.dist(a, b) for a, b in zip(points, points[1:])]
    remain, shapes, last = sum(lengths) * progress, [], None
    for a, b, length in zip(points, points[1:], lengths):
        if length <= 0 or remain <= 0:
            continue
        part = min(1, remain / length)
        end = (a[0] + (b[0] - a[0]) * part, a[1] + (b[1] - a[1]) * part)
        dx, dy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
        nx, ny = -dy * thickness / 2, dx * thickness / 2
        shapes.append(polygon([(a[0] + nx, a[1] + ny), (end[0] + nx, end[1] + ny),
                               (end[0] - nx, end[1] - ny), (a[0] - nx, a[1] - ny)]))
        last = end, dx, dy
        remain -= length
    if arrow and last:
        (x, y), dx, dy = last
        length, wing = max(24, thickness * 3), max(15, thickness * 1.8)
        shapes.append(polygon([(x, y), (x - dx * length - dy * wing, y - dy * length + dx * wing),
                               (x - dx * length + dy * wing, y - dy * length - dx * wing)]))
    return " ".join(shapes)


def interpolate(keys: list[dict], t: float, shape: str) -> dict:
    if t < keys[0]["t"] - 1e-7 or t > keys[-1]["t"] + 1e-7:
        raise ValueError("Tracking keyframes must span every visible frame")
    if len(keys) == 1:
        return keys[0]
    a, b = keys[-2:]
    for left, right in zip(keys, keys[1:]):
        if left["t"] <= t <= right["t"]:
            a, b = left, right
            break
    q = (t - a["t"]) / (b["t"] - a["t"])
    if shape in ("rect", "circle"):
        return {k: a[k] + (b[k] - a[k]) * q for k in ("x", "y", "w", "h")}
    if len(a["points"]) != len(b["points"]) or len(a["points"]) < 2:
        raise ValueError("Tracked paths require the same>=2 points at every keyframe")
    return {"points": [[x + (u - x) * q, y + (v - y) * q]
                       for (x, y), (u, v) in zip(a["points"], b["points"])]}


def intersects(a: list, b: list) -> bool:
    return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]


def check_bounds(bounds: list, protected: list, label: str):
    if bounds[0] < 0 or bounds[1] < 0 or bounds[2] > WIDTH or bounds[3] > HEIGHT:
        raise ValueError(f"{label} leaves frame; split/hide mark at out-of-frame interval")
    if any(intersects(bounds, box) for box in protected):
        raise ValueError(f"{label} overlaps caption/credit/protected UI; recompose or retime")


def annotations(cut: dict, plan: dict) -> tuple[str, dict]:
    from PIL import ImageFont
    duration, result, geometry_log = cut["frames"] / FPS, ass_header(), []
    protected = [fixed_caption_rect(plan), *cut.get("protectedRects", [])]
    if cut["kind"] == "explanation":
        protected.append(EXPLANATION_CHIP_RECT)
    font_value = plan.get("annotationFontFile", "C:/Windows/Fonts/malgun.ttf")
    font_file = (Path(font_value).resolve() if str(font_value).replace("\\", "/").lower()
                 == "c:/windows/fonts/malgun.ttf" else path(font_value))
    # Source attributions remain plan/description metadata. Original source
    # watermarks stay in the video; editorial credit strips are never drawn.
    for index, mark in enumerate(cut.get("marks", [])):
        shape = mark["shape"]
        if shape == "rectangle":
            shape = "rect"
        if shape not in ("rect", "circle", "path", "arrow"):
            raise ValueError(f"Unsupported editorial shape: {shape}")
        start, end = float(mark["t0"]), float(mark["t1"])
        if not 0 <= start < end <= duration + 1e-8:
            raise ValueError("Mark interval must be inside its own cut")
        if not mark.get("label"):
            raise ValueError("Every mark requires a short explanatory label")
        if re.search(r"https?://|www\.", mark["label"], re.I):
            raise ValueError("Editor-added source URLs belong only in the bottom description")
        keys = mark.get("keyframes")
        if not keys:
            geometry = {k: mark[k] for k in (("x", "y", "w", "h") if shape in ("rect", "circle") else ("points",))}
            keys = [{"t": start, **geometry}, {"t": end, **geometry}]
        if any(a["t"] >= b["t"] for a, b in zip(keys, keys[1:])):
            raise ValueError("Tracking keyframes must be strictly increasing")
        rgb = COLORS.get(mark["color"], mark["color"].lstrip("#")).upper()
        if not re.fullmatch(r"[0-9A-F]{6}", rgb):
            raise ValueError("Mark color must be semantic name or six-digit RGB")
        color = rgb[4:6] + rgb[2:4] + rgb[:2]
        thickness = float(mark.get("thickness", 8))
        if not 6 <= thickness <= 24:
            raise ValueError("Editorial stroke must be readable6–24 output pixels")
        lx, ly = mark["labelPosition"]
        size = int(mark.get("fontSize", 42))
        font = ImageFont.truetype(str(font_file), size)
        label_bounds = [lx - 6, ly - 6, lx + math.ceil(font.getlength(mark["label"])) + 6,
                        ly + size * 1.5 + 6]
        check_bounds(label_bounds, protected, "Mark label")
        visible, first_frame, last_frame = [], math.ceil(start * FPS), math.ceil(end * FPS)
        for frame in range(first_frame, last_frame):
            t, following = frame / FPS, min((frame + 1) / FPS, end)
            if any(a <= t < b for a, b in mark.get("hiddenIntervals", [])):
                continue
            if mark.get("visibleIntervals") and not any(a <= t < b for a, b in mark["visibleIntervals"]):
                continue
            geom = interpolate(keys, t, shape)
            if shape in ("rect", "circle"):
                bounds = [geom["x"], geom["y"], geom["x"] + geom["w"], geom["y"] + geom["h"]]
                drawing = outline(shape, geom, thickness)
            else:
                points = geom["points"]
                margin = max(24, thickness * 3) if shape == "arrow" else thickness / 2
                bounds = [min(p[0] for p in points) - margin, min(p[1] for p in points) - margin,
                          max(p[0] for p in points) + margin, max(p[1] for p in points) + margin]
                progress = min(1, (t - start + 1 / FPS) / max(mark.get("revealSeconds", .45), 1 / FPS))
                drawing = traced_path(points, thickness, progress, shape == "arrow")
            check_bounds(bounds, protected, f"Mark{mark.get('id', index)}@{t:.3f}s")
            # Per-frame events follow verified motion; never persist across cuts.
            result += event(t, following, f"{{\\an7\\pos(0,0)\\p1\\bord0\\shad0\\1c&H{color}&}}" + drawing, 2)
            result += event(t, following, f"{{\\an7\\pos({lx},{ly})\\fs{size}\\1c&H{color}&\\bord4}}" + ass_text(mark["label"]), 3)
            visible.append(frame)
        geometry_log.append({"id": mark.get("id", index), "shape": shape, "label": mark["label"],
                             "firstVisibleFrame": min(visible) if visible else None,
                             "lastVisibleFrame": max(visible) if visible else None,
                             "visibleFrameCount": len(visible), "detectorOutput": False,
                             "motionPixelsReviewed": "pending"})
    return result, {"captionProtectedRect": protected[0], "marks": geometry_log,
                    "editorAddedSourceCreditsRendered": False, "sourceAttributionPlacement": "description-bottom",
                    "coordinates": "output1920x1080 pixels; cut-relative times"}


def filter_path(p: Path) -> str:
    # Quotes protect spaces and punctuation in FFmpeg's filter grammar.
    return "'" + p.as_posix().replace("\\", "\\\\").replace(":", r"\:").replace("'", r"\'") + "'"


def editorial_guide_binding(cut: dict, plan: dict) -> str:
    """Bind authored guides to the actual cut, not a circular plan-file hash."""
    payload = {
        "cut": {k: v for k, v in cut.items() if k != "editorialGuideAss"},
        "fps": plan["fps"], "width": plan["width"], "height": plan["height"],
        "captionProtectedRect": plan.get("captionProtectedRect", CAPTION_RECT),
        "annotationFontFile": plan.get("annotationFontFile", "C:/Windows/Fonts/malgun.ttf"),
    }
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def editorial_guide_ass(cut: dict, plan: dict) -> tuple[Path | None, dict | None]:
    """Validate a prepared guide receipt without producing media or moving text."""
    item = cut.get("editorialGuideAss")
    if item is None:
        return None, None
    if not isinstance(item, dict) or cut["kind"] != "independent-gameplay":
        raise ValueError("Editorial guide requires an independent-gameplay cut receipt")
    expected = item.get("sha256", "")
    if not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise ValueError("Editorial guide requires its actual ASS SHA256")
    p = path(item["path"])
    p.relative_to((DEFAULT_OUTPUT / "editorial-guides").resolve())
    content = p.read_bytes()
    if p.suffix.lower() != ".ass" or hashlib.sha256(content).hexdigest() != expected:
        raise ValueError("Editorial guide ASS changed; prepare its current receipt again")
    if item.get("cutBindingSha256") != editorial_guide_binding(cut, plan):
        raise ValueError("Editorial guide cut/source/layout binding changed; prepare again")
    references = [item.get("guideSpec"), *item.get("mappingInputs", [])]
    if len(references) < 4 or any(not isinstance(row, dict) for row in references):
        raise ValueError("Editorial guide requires its current spec/ASR/caption/source-selection receipts")
    for row in references:
        if sha(path(row["path"])) != row["sha256"]:
            raise ValueError("Editorial guide speech/caption/source evidence changed; prepare again")
    if (item.get("clock"), item.get("coordinateSystem"), item.get("detectorOutput"),
            item.get("measuredGameData"), item.get("appliesTo")) != (
            "cut-relative-seconds", "output1920x1080", False, False,
            ["clean", "captioned"]):
        raise ValueError("Editorial guide must be explicit authored guidance in both masters")
    script = content.decode("utf-8-sig")
    if re.search(r"https?://|www\.", script, re.I):
        raise ValueError("Editor-added source URLs are not allowed in a video guide")
    if not (re.search(r"(?m)^PlayResX:\s*1920\s*$", script)
            and re.search(r"(?m)^PlayResY:\s*1080\s*$", script)):
        raise ValueError("Editorial guide ASS must retain native output coordinates")
    from PIL import ImageFont
    protected = [plan.get("captionProtectedRect", CAPTION_RECT), *cut.get("protectedRects", [])]
    font_value = plan.get("annotationFontFile", "C:/Windows/Fonts/malgun.ttf")
    font_file = Path(font_value) if Path(font_value).is_absolute() else path(font_value)
    events = item.get("events", [])
    if not events:
        raise ValueError("Editorial guide requires recorded actual cue/cut intersections")
    for row in events:
        begin, end = float(row["start"]), float(row["end"])
        if not all(math.isfinite(v) for v in (begin, end)) or not 0 <= begin < end <= cut["frames"] / FPS + 1e-7:
            raise ValueError("Editorial guide times must remain inside their own cut")
        if (abs(row["globalStart"] - (cut["startFrame"] / FPS + begin)) > 1e-7
                or abs(row["globalEnd"] - (cut["startFrame"] / FPS + end)) > 1e-7):
            raise ValueError("Editorial guide global/cut-relative mapping changed")
        bounds = row["bounds"]
        if len(bounds) != 4 or not all(math.isfinite(v) for v in bounds):
            raise ValueError("Editorial guide requires finite output bounds")
        check_bounds(bounds, protected, "Editorial design guide")
    return p, {"path": routed_relative(p), "sha256": expected,
               "cutBindingSha256": item["cutBindingSha256"], "events": events,
               "mappingInputs": references,
               "meaning": "authored design summary; never game HUD/detector/measurement",
               "finalMovingAnd375pxPixels": "pending"}


def explanation_kind_label(cut: dict, plan: dict):
    """Apply the same editorial marks plus an explicit, protected source-kind chip."""
    still = cut.get("explanationRender", {}).get("kind") == "annotated-still"
    label = "장면 해설" if still else "해설용 시연"
    script, geometry = annotations(cut, plan)
    text = r"{\an5\pos(1740,73)\fs36\b0\bord0\shad0\1c&HB8B8B8&}" + label
    geometry.update({
        "sourceKind": "inspected source-frame explanation" if still else "self-authored Unity explanation",
        "fixedLabel": {"text": label, "center": [1740, 73], "fontSize": 36,
                       "protectedRect": EXPLANATION_CHIP_RECT,
                       "reason": "Explicit editorial picture kind; not an animation-editor recording or measured game data"}})
    return script + event(0, cut["frames"] / FPS, text, 4), geometry


def gameplay_labels(cut: dict, plan: dict):
    """Game identity and honest footage kind, separate from description credits."""
    from PIL import ImageFont
    title = cut.get("gameLabel")
    picture = cut.get("pictureLabel", "실제 게임 영상")
    if not title:
        raise ValueError("Selected actual gameplay requires a concise game-name label")
    font = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 36)
    left_width = math.ceil(font.getlength(title)) + 40
    right_width = math.ceil(font.getlength(picture)) + 40
    if left_width > 900 or right_width > 600:
        raise ValueError("Game identity label is too wide")
    boxes = [[24, 18, 24 + left_width, 78], [1896-right_width, 18, 1896, 78]]
    marked = {**cut, "protectedRects": [*cut.get("protectedRects", []), *boxes]}
    script, geometry = annotations(marked, plan)
    duration = cut["frames"] / FPS
    for label, box in zip((title, picture), boxes):
        x0,y0,x1,y1 = box
        fill = r"{\an7\pos(0,0)\p1\bord0\shad0\1c&H15150B&\1a&H20&}" + polygon([[x0,y0],[x1,y0],[x1,y1],[x0,y1]])
        text = f"{{\\an7\\pos({x0+20},{y0+5})\\fs36\\b0\\bord0\\shad0\\1c&HF0F0F0&}}" + ass_text(label)
        script += event(0,duration,fill,4) + event(0,duration,text,5)
    geometry["identityLabels"] = [{"text":label,"bounds":box,"fontSize":36} for label,box in zip((title,picture),boxes)]
    return script, geometry


def pinned_file(item: dict, label: str) -> Path:
    if (not isinstance(item, dict) or not item.get("path")
            or not isinstance(item.get("sha256"), str)
            or not re.fullmatch(r"[0-9a-f]{64}", item["sha256"])):
        raise ValueError(f"{label} requires its source path and actual SHA256")
    p = path(item["path"])
    if sha(p) != item["sha256"]:
        raise ValueError(f"{label} bytes changed after the receipt was created")
    return p


def validate_explanation_source(cut: dict, source: Path, source_hash: str) -> dict:
    """Validate complete native capture or complete source-frame explanation, separately."""
    if source_hash != cut.get("renderedSourceSha256"):
        raise ValueError(f"Explanation source differs from the hash-pinned edit: {cut['id']}")
    if cut.get("renderedStartFrame", 0) != 0:
        raise ValueError("An explanation receipt must cover this complete cut, starting at frame0")
    item = cut.get("explanationRender")
    if item is None:
        # Preserve every native fingerprint/request/success check. A still receipt
        # is never accepted as a substitute for a missing native capture.
        native = cut.get("nativeCapture", {})
        if native.get("movieSha256") != source_hash:
            raise ValueError(f"Native source bytes differ from the frozen completed capture: {cut['id']}")
        receipt_path, request_path = path(native["successReceipt"]), path(native["request"])
        receipt, request = load(receipt_path), load(request_path)
        if (sha(receipt_path) != native["successSha256"] or sha(request_path) != native["requestSha256"]
                or receipt.get("status") != "complete" or receipt.get("completed") != cut["frames"]
                or receipt.get("compiledSourceFingerprint") != native["compiledFingerprint"]
                or request.get("expectedFingerprint") != native["compiledFingerprint"]
                or request.get("command") != "render"):
            raise ValueError(f"Native receipt is not the locked completed full capture: {cut['id']}")
        assert_video(source, cut["frames"])
        return {"kind": "native-unity", "successReceipt": native["successReceipt"],
                "successSha256": native["successSha256"], "movieSha256": source_hash}
    if (not isinstance(item, dict) or item.get("kind") != "annotated-still"
            or cut.get("nativeCapture") is not None):
        raise ValueError("Use exactly one nativeCapture or annotated-still explanationRender")
    receipt_path = pinned_file({"path": item.get("receipt"), "sha256": item.get("receiptSha256")},
                               "Annotated-still receipt")
    receipt = load(receipt_path)
    if (tuple(receipt.get(k) for k in ("episode", "slug", "revision"))
            != ("A01", "animation-assigning", "grid-v1")
            or receipt.get("status") != "complete" or receipt.get("kind") != "annotated-still"
            or receipt.get("frames") != cut["frames"] or receipt.get("completed") != cut["frames"]
            or (receipt.get("fps"), receipt.get("width"), receipt.get("height")) != (FPS, WIDTH, HEIGHT)):
        raise ValueError("Annotated-still receipt must record a complete A01/grid-v1 FHD60 cut")
    if receipt.get("detectorOutput", False) is not False or receipt.get("measuredGameData", False) is not False:
        raise ValueError("Source-frame annotations are editorial guides, never detector output or measured game data")
    movie = pinned_file(receipt.get("movie"), "Annotated-still movie")
    if movie.resolve() != source.resolve() or receipt["movie"]["sha256"] != source_hash:
        raise ValueError("Annotated-still receipt refers to a different generated movie")
    assert_video(source, cut["frames"])
    from PIL import Image
    source_image = pinned_file(receipt.get("sourceImage"), "Original extracted source image")
    with Image.open(source_image) as image:
        image_width, image_height = image.size
        image.verify()
    if min(image_width, image_height) < 1080 or max(image_width, image_height) < 1920:
        raise ValueError("Extract the genuine FHD source frame before composing/cropping it")
    if receipt.get("imageOutput") is not None:
        composed_image = pinned_file(receipt["imageOutput"], "Composed still image")
        with Image.open(composed_image) as image:
            if image.size != (WIDTH, HEIGHT):
                raise ValueError("Composed still image must be1920x1080")
            image.verify()
    video_item = receipt.get("sourceVideo")
    original = pinned_file(video_item, "Original gameplay video for the extracted frame")
    frame_time = video_item.get("frameTimeSeconds")
    if (not isinstance(frame_time, (int, float)) or isinstance(frame_time, bool)
            or not math.isfinite(frame_time) or frame_time < 0):
        raise ValueError("An extracted frame requires its finite nonnegative original-video timestamp")
    original_info = probe(original)
    original_duration = float(original_info["format"]["duration"])
    if not math.isfinite(original_duration) or frame_time >= original_duration:
        raise ValueError("Extracted source-frame timestamp is outside the original video")
    decoded = json.loads(subprocess.check_output([
        binary("ffprobe"), "-v", "error", "-select_streams", "v:0",
        "-read_intervals", f"{frame_time:.9f}%+3", "-show_frames", "-show_entries",
        "frame=width,height", "-of", "json", str(original)], cwd=ROOT)).get("frames", [])
    if not decoded:
        raise ValueError("No decodable original frame near the recorded still timestamp")
    dimensions = (decoded[0]["width"], decoded[0]["height"])
    if (min(dimensions) < 1080 or max(dimensions) < 1920
            or dimensions != (video_item.get("decodedWidth"), video_item.get("decodedHeight"))
            or dimensions != (image_width, image_height)):
        raise ValueError("Original-video decoded FHD dimensions must match the receipt and uncropped source image")
    layout = receipt.get("layout", {})
    if layout.get("captionProtectedRect") != CAPTION_RECT or layout.get("background") != "animation-grid":
        raise ValueError("Annotated-still layout must retain the animation grid and fixed caption geometry")
    viewport = layout.get("viewport")
    if (not isinstance(viewport, list) or len(viewport) != 4
            or any(type(v) is not int or v % 2 for v in viewport)
            or min(viewport[:2]) < 0 or min(viewport[2:]) <= 0
            or viewport[0] + viewport[2] > WIDTH or viewport[1] + viewport[3] > HEIGHT):
        raise ValueError("Annotated-still receipt requires a finite, in-frame evenpixel viewport")
    crop = layout.get("crop")
    if crop is not None and (not isinstance(crop, list) or len(crop) != 4
            or any(type(v) is not int for v in crop) or min(crop[:2]) < 0 or min(crop[2:]) <= 0
            or crop[0] + crop[2] > image_width or crop[1] + crop[3] > image_height):
        raise ValueError("Annotated-still crop must refer to the inspected original source image")
    return {"kind": "annotated-still", "receipt": item["receipt"],
            "receiptSha256": item["receiptSha256"], "movieSha256": source_hash,
            "sourceImage": receipt["sourceImage"], "sourceVideo": video_item,
            "layout": layout, "detectorOutput": False, "measuredGameData": False,
            "pixelToTimestampIdentity": "extraction provenance bound by receipt; not independently image-matched"}


def render_cuts(plan: dict, output: Path, only_ids=None):
    ratio = validate_plan(plan)
    selected = set(only_ids or [])
    if selected and not selected.issubset({c['id'] for c in plan['cuts']}):
        raise ValueError('Representative selection includes an unknown cut')
    output.mkdir(parents=True, exist_ok=True)
    source_hashes, code_hash = {}, sha(Path(__file__))
    for cut in plan["cuts"]:
        if selected and cut['id'] not in selected:
            continue
        gameplay = cut["kind"] == "independent-gameplay"
        guide_file, guide_geometry = editorial_guide_ass(cut, plan)
        source = path(cut["sourceFile"] if gameplay else cut["renderedSource"])
        source_info = video_stream(source)
        start = float(cut.get("sourceStart", 0)) if gameplay else cut.get("renderedStartFrame", 0) / FPS
        # Verify DECODED dimensions too, not only container metadata.
        # A stream-copied research excerpt can begin between keyframes. One
        # packet is insufficient to decode H.264 with B-frame reordering; probe
        # the actual selected interval for long enough to emit real frames.
        decode_probe = subprocess.check_output([binary("ffprobe"), "-v", "error", "-select_streams", "v:0",
            "-read_intervals", f"{start:.6f}%+3", "-show_frames", "-show_entries", "frame=width,height",
            "-of", "json", str(source)], cwd=ROOT)
        decoded_frames = json.loads(decode_probe).get("frames", [])
        if not decoded_frames:
            raise ValueError(f"No decodable frame near selected source start: {source} at {start}s")
        decoded = decoded_frames[0]
        if gameplay and (min(decoded["width"], decoded["height"]) < 1080 or
                         max(decoded["width"], decoded["height"]) < 1920):
            raise ValueError(f"Source is not genuine FHD-or-higher decoded media: {source}: {decoded}")
        if not gameplay:
            if ((source_info["width"], source_info["height"]) != (WIDTH, HEIGHT)
                    or (decoded["width"], decoded["height"]) != (WIDTH, HEIGHT)
                    or Fraction(source_info["avg_frame_rate"]) != FPS):
                raise ValueError(f"Explanation render must be1920x1080/60: {source}")
        source_duration = float(source_info.get("duration", probe(source)["format"]["duration"]))
        if start + cut["frames"] / FPS > source_duration + 1 / FPS:
            raise ValueError(f"Source too short; no hold/loop permitted: {cut['id']}")
        if str(source) not in source_hashes:
            source_hashes[str(source)] = sha(source)
        if gameplay and source_hashes[str(source)] != cut.get("sourceSha256"):
            raise ValueError(f"Actual source bytes differ from the hash-pinned edit: {cut['id']}")
        explanation_evidence = (None if gameplay else validate_explanation_source(
            cut, source, source_hashes[str(source)]))
        annotation_cut = cut
        if guide_geometry:
            annotation_cut = {**cut, "protectedRects": [*cut.get("protectedRects", []),
                              *[row["bounds"] for row in guide_geometry["events"]]]}
        ass, geometry = gameplay_labels(annotation_cut, plan) if gameplay else explanation_kind_label(annotation_cut, plan)
        mark_file, destination = output / (cut["id"] + "-marks.ass"), output / (cut["id"] + ".mp4")
        signature = {"cut": cut, "sourceSha256": source_hashes[str(source)], "sourceDecoded": decoded,
                     "codeSha256": code_hash, "encoder": ENCODER, "markGeometry": geometry,
                     "assSha256": hashlib.sha256(ass.encode()).hexdigest() if ass else None,
                     "editorialGuideAss": guide_geometry, "explanationRenderEvidence": explanation_evidence}
        receipt = output / (cut["id"] + "-render.json")
        if destination.exists() and receipt.exists():
            old = load(receipt)
            if old.get("signature") == signature and old.get("outputSha256") == sha(destination):
                assert_video(destination, cut["frames"])
                print(cut["id"], "cached", flush=True)
                continue
        if ass:
            mark_file.write_text(ass, encoding="utf-8")
        x, y, w, h = cut.get("viewport", [0, 0, WIDTH, HEIGHT])
        if any(v % 2 for v in (x, y, w, h)) or x < 0 or y < 0 or x + w > WIDTH or y + h > HEIGHT:
            raise ValueError("Viewport must be in-frame and have evenpixel geometry")
        # Fit using source display aspect ratio, then square pixels; no stretch.
        raw_sar = source_info.get("sample_aspect_ratio", "1:1")
        sar = Fraction(raw_sar.replace(":", "/")) if raw_sar not in ("N/A", "0:1", "0/1") else Fraction(1)
        if sar <= 0:
            sar = Fraction(1)
        crop = cut.get("sourceCrop")
        crop_filter = ""
        if crop:
            cx, cy, cw, ch = crop
            if any(int(v) != v or v % 2 for v in crop) or min(cx, cy) < 0 or min(cw, ch) <= 0 or cx + cw > source_info["width"] or cy + ch > source_info["height"]:
                raise ValueError(f"Invalid inspected source crop: {cut['id']}")
            aspect = cw * float(sar) / ch
            crop_filter = f"crop={cw}:{ch}:{cx}:{cy},"
        else:
            aspect = source_info["width"] * float(sar) / source_info["height"]
        fit_w, fit_h = w, 2 * math.floor((w / aspect) / 2)
        if fit_h > h:
            fit_h, fit_w = h, 2 * math.floor((h * aspect) / 2)
        left, top = x + (w - fit_w) // 2, y + (h - fit_h) // 2
        left, top = left // 2 * 2, top // 2 * 2
        vf = crop_filter + f"fps=60,scale={fit_w}:{fit_h}:flags=lanczos,setsar=1,pad=1920:1080:{left}:{top}:black,setpts=PTS-STARTPTS"
        if ass:
            vf += ",ass=" + filter_path(mark_file)
        if guide_file:
            if sha(guide_file) != cut["editorialGuideAss"]["sha256"]:
                raise ValueError("Editorial guide changed before cut encode")
            vf += ",ass=" + filter_path(guide_file)
        temp = destination.with_suffix(".partial.mp4")
        run(["-ss", f"{start:.9f}", "-threads", "4", "-i", str(source), "-an", "-vf", vf,
             "-frames:v", str(cut["frames"]), *ENCODER, "-movflags", "+faststart", str(temp)],
            output / (cut["id"] + "-render.log"))
        assert_video(temp, cut["frames"])
        temp.replace(destination)
        save(receipt, {"signature": signature, "outputSha256": sha(destination),
                       "visualMotionReview": "pending", "decodedDimensionsVerified": True})
        print(cut["id"], cut["frames"], "frames", flush=True)
    if selected:
        save(output / 'representative-cuts-build.json', {
            'scope': 'selected cuts only; complete cut assembly remains pending',
            'selectedCutIds': sorted(selected), 'ratioContract': ratio,
            'outputHashes': {key: sha(output / (key + '.mp4')) for key in sorted(selected)},
            'finalMovingCaptionPixels': 'pending'})
        return
    preserved = []
    for name, count, key in (("branding", 120, "brandingFile"), ("membership", 600, "membershipFile")):
        default = f"projects/game-reward-planning/production/final-v1/white-segments/{name}.mp4"
        original, destination = path(plan.get(key, default)), output / (name + ".mp4")
        assert_video(original, count, count=True)
        digest = sha(original)
        if not destination.exists() or sha(destination) != digest:
            shutil.copy2(original, destination)
        if sha(destination) != digest:
            raise ValueError(f"Original {name} bytes were not preserved")
        preserved.append({"kind": name, "frames": count, "source": routed_relative(original),
                          "sourceSha256": digest, "outputSha256": digest, "bytePreserved": True})
    files = [output / "branding.mp4", *[output / (c["id"] + ".mp4") for c in plan["cuts"]], output / "membership.mp4"]
    (output / "concat.txt").write_text("\n".join("file '" + p.as_posix().replace("'", "'\\''") + "'" for p in files) + "\n", encoding="utf-8")
    save(output / "cuts-build.json", {"ratio": ratio, "brandingMembership": preserved,
                                      "nativeSpeed": True, "playbackReview": "pending"})


def stream_hash(p: Path, selector: str) -> str:
    return subprocess.check_output([binary("ffmpeg"), "-v", "error", "-i", str(p),
        "-map", selector, "-c", "copy", "-f", "hash", "-hash", "sha256", "-"], text=True, cwd=ROOT).strip()


def output_files(plan: dict, output: Path) -> dict:
    stem = plan.get("outputStem", "similar-game-design-v2")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", stem):
        raise ValueError("Unsafe outputStem")
    return {suffix: output / f"{stem}-{suffix}.mp4" for suffix in ("clean", "captioned")}


def render_pair(plan: dict, output: Path, mix_override=None, ass_override=None, *, prepare_only=False):
    validate_plan(plan)
    cut_proofs = []
    for cut in plan["cuts"]:
        cut_file = output / (cut["id"] + ".mp4")
        metadata = assert_video(cut_file, cut["frames"])
        if Fraction(metadata["time_base"]) != Fraction(1, 60000):
            raise ValueError(f"Join cut has an incompatible track timescale: {cut['id']}")
        render_receipt = output / (cut["id"] + "-render.json")
        recorded = load(render_receipt)
        current_hash = sha(cut_file)
        if recorded.get("outputSha256") != current_hash:
            raise ValueError(f"Completed cut bytes differ from their render receipt: {cut['id']}")
        if recorded.get("signature", {}).get("cut") != cut:
            raise ValueError(f"Completed cut geometry/source differs from this pair plan: {cut['id']}")
        cut_proofs.append({"id": cut["id"], "frames": cut["frames"], "sha256": current_hash,
            "timeBase": metadata["time_base"], "renderReceiptSha256": sha(render_receipt),
            "originalRenderCodeSha256": recorded["signature"].get("codeSha256"),
            "reuseBasis": "Exact cut definition and output SHA256 match the completed receipt; only the downstream pair join changed. No render_cuts call."})
    assert_video(output / "branding.mp4", 120)
    assert_video(output / "membership.mp4", 600)
    # The approved originals use1/90000; our cut encodes use1/60000. Concat
    # demuxing requires matching stream time bases. Keep originals byte-for-byte
    # and create video-only, stream-copy join containers with the common scale.
    join_dir = output / "pair-join"
    join_dir.mkdir(parents=True, exist_ok=True)
    join_receipt = output / "pair-join-inputs.json"
    old_join = load(join_receipt) if join_receipt.exists() else {}
    join_proofs = []

    def decoded_pixels(file):
        decoded = subprocess.check_output([binary("ffmpeg"), "-v", "error", "-threads", "2",
            "-i", str(file), "-map", "0:v:0", "-an", "-sn", "-dn", "-c:v", "rawvideo",
            "-pix_fmt", "yuv420p", "-threads", "2", "-fps_mode", "passthrough",
            "-f", "hash", "-hash", "sha256", "-"], text=True, cwd=ROOT).strip()
        return decoded

    for name, count, key in (("branding", 120, "brandingFile"), ("membership", 600, "membershipFile")):
        default = f"projects/game-reward-planning/production/final-v1/white-segments/{name}.mp4"
        canonical = path(plan.get(key, default))
        original, joined = output / (name + ".mp4"), join_dir / (name + "-timescale60000.mp4")
        original_hash = sha(original)
        if sha(canonical) != original_hash:
            raise ValueError(f"Original {name} differs from the canonical approved bytes")
        previous = next((p for p in old_join.get("segments", []) if p["kind"] == name), None)
        cached = bool(previous and joined.exists() and previous.get("originalSha256") == original_hash
                      and previous.get("joinedSha256") == sha(joined)
                      and previous.get("decodedPixelIdentity") is True)
        if not cached:
            if joined.exists():
                raise ValueError(f"Preserve unverified existing join-only file: {joined}")
            run(["-i", str(original), "-map", "0:v:0", "-an", "-sn", "-dn", "-c:v", "copy",
                 "-video_track_timescale", "60000", "-movflags", "+faststart", str(joined)],
                join_dir / (name + "-remux.log"))
        source_metadata = assert_video(original, count, count=True)
        joined_metadata = assert_video(joined, count, count=True)
        if Fraction(joined_metadata["time_base"]) != Fraction(1, 60000):
            raise ValueError("Join-only remux did not establish1/60000 time base")
        if len(probe(joined)["streams"]) != 1:
            raise ValueError("Join-only branding/member file must be video-only")
        if cached:
            compressed_original = previous["compressedVideoSha256"]
            pixels_original = previous["decodedPixelsSha256"]
        else:
            compressed_original, compressed_joined = stream_hash(original, "0:v:0"), stream_hash(joined, "0:v:0")
            pixels_original, pixels_joined = decoded_pixels(original), decoded_pixels(joined)
            if compressed_original != compressed_joined or pixels_original != pixels_joined:
                raise ValueError("Stream-copy join remux changed compressed video or decoded pixels")
        if sha(original) != original_hash or sha(canonical) != original_hash:
            raise ValueError("Canonical/original bytes changed during join preparation")
        join_proofs.append({"kind": name, "frames": count, "original": routed_relative(original),
            "canonical": routed_relative(canonical), "originalSha256": original_hash,
            "canonicalAndOriginalBytesPreserved": True, "joined": routed_relative(joined),
            "joinedSha256": sha(joined), "originalTimeBase": source_metadata["time_base"],
            "joinedTimeBase": joined_metadata["time_base"], "fps": joined_metadata["avg_frame_rate"],
            "decodedFrameCount": int(joined_metadata["nb_read_frames"]),
            "compressedVideoSha256": compressed_original, "decodedPixelsSha256": pixels_original,
            "decodedPixelIdentity": True, "pixelProofReusedForSameHashes": cached,
            "codec": "video-only stream copy; no encoder or frame-rate filter"})
    pair_concat = output / "pair-concat.txt"
    join_files = [path(join_proofs[0]["joined"]),
                  *[output / (c["id"] + ".mp4") for c in plan["cuts"]], path(join_proofs[1]["joined"])]
    pair_concat.write_text("\n".join("file '" + p.as_posix().replace("'", "'\\''") + "'" for p in join_files) + "\n", encoding="utf-8")
    preparation = {"status": "join-inputs-verified-full-pair-not-claimed", "segments": join_proofs,
        "cuts": cut_proofs, "pairConcat": routed_relative(pair_concat), "pairConcatSha256": sha(pair_concat),
        "expectedFrames": 120 + sum(c["frames"] for c in plan["cuts"]) + 600,
        "allJoinStreamsTimeBase": "1/60000", "allJoinStreamsFps": "60/1",
        "canonicalSegmentsModified": False, "originalConcatModified": False,
        "sourceCutsRerendered": False, "mcPcmAssModified": False}
    if preparation["expectedFrames"] != plan["totalFrames"]:
        raise ValueError("Join frame sum differs from unchanged production clock")
    save(join_receipt, preparation)
    if prepare_only:
        return preparation
    mix = path(mix_override or plan.get("mixFile", str(output / "final-mix.wav")))
    ass = path(ass_override or plan.get("captionsAss", str(output / "captions.ko.ass")))
    if not ass.exists():
        raise FileNotFoundError(ass)
    duration = plan["totalFrames"] / FPS
    mix_info = probe(mix)
    if abs(float(mix_info["format"]["duration"]) - duration) > 1 / FPS:
        raise ValueError("Final mix must match timeline; no implicit padding/truncation")
    # Keep the mixer's hashed AAC intact. Both masters copy this exact stream.
    mixed_aac = output / "final-mix.m4a"
    mixed_receipt = output / "audio-build.json"
    retained = False
    if mixed_aac.exists() and mixed_receipt.exists():
        build = load(mixed_receipt)
        verified = {str(path(x["path"])): x["sha256"] for x in build["outputs"]}
        if verified.get(str(mix)) != sha(mix) or verified.get(str(mixed_aac)) != sha(mixed_aac):
            raise ValueError("The mix WAV/AAC differs from its completed audio-build receipt")
        if abs(float(build["duration"]) - duration) > 1 / FPS:
            raise ValueError("Retained continuous AAC belongs to a different measured timeline")
        retained = True
    # A small explicitly approved delivery headroom correction is encoded once
    # from PCM, never by recompressing the retained AAC. Both videos copy it.
    delivery_gain = float(plan.get("deliveryAudioGainDb", 0))
    if not -.2 <= delivery_gain <= 0:
        raise ValueError("Delivery-only gain must stay within the reviewed headroom correction")
    if delivery_gain:
        retained = False
    aac = mixed_aac if retained else output / "pair-audio.m4a"
    aac_receipt = output / "aac-source.json"
    audio_signature = {"sourceSha256": sha(mix), "duration": duration, "codec": "aac",
                       "bitrate": 192000, "sampleRate": 48000, "channels": 2, "deliveryGainDb": delivery_gain}
    if not retained and not (aac.exists() and aac_receipt.exists() and
            load(aac_receipt).get("signature") == audio_signature and
            load(aac_receipt).get("outputSha256") == sha(aac)):
        run(["-i", str(mix), "-vn", "-af", f"volume={delivery_gain}dB", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
             "-movflags", "+faststart", str(aac)], output / "audio-encode.log")
        save(aac_receipt, {"signature": audio_signature, "outputSha256": sha(aac)})
    files = output_files(plan, output)
    signature = {"planSha256": hashlib.sha256(json.dumps(plan, sort_keys=True).encode()).hexdigest(),
                 "cutSha256": [sha(output / (name + ".mp4")) for name in
                                ["branding", *[c["id"] for c in plan["cuts"]], "membership"]],
                 "aacSha256": sha(aac), "captionsAssSha256": sha(ass), "encoder": ENCODER,
                 "codeSha256": sha(Path(__file__)), "joinPreparationSha256": sha(join_receipt),
                 "pairConcatSha256": sha(pair_concat), "frameClock": "setpts=N/(60*TB) before any format normalization; no fps resampling"}
    receipt = output / "pair-build.json"
    if all(p.exists() for p in files.values()) and receipt.exists():
        old = load(receipt)
        if old.get("signature") == signature and all(old.get("outputs", {}).get(k, {}).get("sha256") == sha(p) for k, p in files.items()):
            print("Identical pair already exists; encoding reused", flush=True)
            return
    # Normalize visual metadata once before split; ASS sees one continuous clock.
    # Unknown SAR/range/colour properties on the byte-preserved bookends differ
    # from the rendered body. Reinitializing at that boundary resets setpts' N.
    # Every input is already the checked1920x1080/yuv420p/60 grid, so keep one
    # filter instance and normalize metadata explicitly without changing pixels.
    clock_prefix = "[0:v]setpts=N/(60*TB),settb=1/60000,setsar=1,format=yuv420p,setparams=range=tv:color_primaries=bt709:color_trc=bt709:colorspace=bt709"
    graph = clock_prefix + ",split=2[clean][capin];[capin]ass=" + filter_path(ass) + "[captioned]"
    args = ["-f", "concat", "-safe", "0", "-reinit_filter", "0", "-i", str(pair_concat), "-i", str(aac), "-filter_complex", graph]
    temporary = {key: p.with_suffix(".partial.mp4") for key, p in files.items()}
    for suffix in ("clean", "captioned"):
        args += ["-map", f"[{suffix}]", "-map", "1:a:0", "-frames:v", str(plan["totalFrames"]),
                 "-t", f"{duration:.9f}", *ENCODER, "-fps_mode", "passthrough", "-c:a", "copy", "-movflags", "+faststart", str(temporary[suffix])]
    run(args, output / "pair-encode.log")
    audio_hash = stream_hash(aac, "0:a:0")
    proofs = {}
    for suffix, p in temporary.items():
        assert_video(p, plan["totalFrames"])
        if stream_hash(p, "0:a:0") != audio_hash:
            raise ValueError("Pair did not preserve identical continuous AAC packets")
        p.replace(files[suffix])
        proofs[suffix] = {"path": routed_relative(files[suffix]), "sha256": sha(files[suffix]), "audioPacketsSha256": audio_hash}
    save(receipt, {"signature": signature, "outputs": proofs,
                   "continuousAac": True, "humanListeningAndMovingPixels": "pending"})


def pts_review(p: Path, expected: int) -> dict:
    args = [binary("ffprobe"), "-v", "error", "-threads", "4", "-err_detect", "explode", "-select_streams", "v:0", "-show_frames",
            "-show_entries", "frame=best_effort_timestamp_time", "-of", "csv=p=0", str(p)]
    process = subprocess.Popen(args, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, encoding="utf-8", errors="replace")
    count, last, max_error = 0, None, 0.0
    for line in process.stdout:
        fields = line.strip().split(",")
        if not fields or not fields[0]:
            continue
        try:
            value = float(fields[0])
        except ValueError:
            continue
        error = abs(value - count / FPS)
        if last is not None and value <= last:
            process.kill()
            raise ValueError(f"Nonmonotonic presentation timestamp: {p} frame{count}")
        if error > 2e-5:
            process.kill()
            raise ValueError(f"PTS grid discontinuity: {p} frame{count}: {value}")
        max_error, last, count = max(max_error, error), value, count + 1
    stderr = process.stderr.read()
    if process.wait() or stderr.strip():
        raise ValueError(f"Full frame/PTS scan failed: {p}: {stderr[-3000:]}")
    if count != expected:
        raise ValueError(f"Decoded PTS count mismatch: {count}!={expected}")
    return {"frames": count, "firstPts": 0, "lastPts": last, "maxGridErrorSeconds": max_error,
            "strictlyIncreasing": True, "allDecodedFramesScanned": True}


def verify(plan: dict, output: Path):
    ratio, records = validate_plan(plan), {}
    for suffix, p in output_files(plan, output).items():
        meta = assert_video(p, plan["totalFrames"])
        log = output / (suffix + "-full-decode.log")
        run(["-xerror", "-err_detect", "explode", "-threads", "4", "-i", str(p),
             "-map", "0:a:0", "-vn", "-f", "null", "-"], log)
        info = probe(p)
        audio = [s for s in info["streams"] if s["codec_type"] == "audio"]
        if len(audio) != 1 or audio[0]["codec_name"] != "aac" or audio[0]["sample_rate"] != "48000":
            raise ValueError(f"Unexpected final audio structure: {p}")
        actual_duration = float(info["format"]["duration"])
        if abs(actual_duration - plan["totalFrames"] / FPS) > 1 / FPS:
            raise ValueError(f"Final A/V duration mismatch: {p}")
        records[suffix] = {"path": routed_relative(p), "sha256": sha(p), "video": meta,
                           "pts": pts_review(p, plan["totalFrames"]),
                           "audioPacketsSha256": stream_hash(p, "0:a:0"),
                           "fullAudioVideoDecode": "pass: one complete video frame/PTS decode and one complete audio decode", "durationSeconds": actual_duration}
    if records["clean"]["audioPacketsSha256"] != records["captioned"]["audioPacketsSha256"]:
        raise ValueError("Clean and captioned masters have different audio packets")
    save(output / "structural-verification.json", {"status": "pass", "ratio": ratio,
         "outputs": records, "identicalContinuousAudio": True,
         "visualConceptMotionCaptionPixels": "pending separate review",
         "narrationLevelContinuityAsrAndHumanListening": "pending separate review"})
    print("Both complete masters decoded; all videoPTS/frame counts and sameAAC passed", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("stage", choices=["cuts", "pair", "verify"])
    parser.add_argument("--plan", default=str(HERE / "edit-plan.json"))
    parser.add_argument("--output-dir")
    parser.add_argument("--mix")
    parser.add_argument("--ass")
    parser.add_argument("--only-cut", action="append", help="Render/reuse representative cuts against the complete plan; no complete assembly claim")
    args = parser.parse_args()
    require_authorized("video-" + args.stage)
    plan = load(current_plan(args.plan))
    if plan.get("slug", PROJECT.name) != PROJECT.name:
        raise ValueError("Edit plan belongs to another video")
    output = current_local_output(args.output_dir or plan.get("outputDir", str(DEFAULT_OUTPUT)))
    if args.stage == "cuts":
        render_cuts(plan, output, args.only_cut)
    elif args.stage == "pair":
        render_pair(plan, output, args.mix, args.ass)
    else:
        verify(plan, output)


if __name__ == "__main__":
    main()
