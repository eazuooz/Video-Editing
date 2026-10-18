"""D20 native-speed FHD cut rendering, paired masters and structural verification.

No media job runs on import. CLI::

    python video_pipeline.py cuts --plan .../edit-plan.json
    python video_pipeline.py pair --plan .../edit-plan.json --mix final-mix.wav
    python video_pipeline.py verify --plan .../edit-plan.json

Paths in the plan are repository-relative (absolute paths are also accepted).
``startFrame``/``endFrame`` are GLOBAL, half-open timeline positions. The body
starts at frame120 and ends600 frames before ``totalFrames``. Every cut carries
``id, scene, startFrame, endFrame, frames, kind``. Gameplay adds ``sourceFile``
and ``sourceStart`` (seconds); explanations add ``renderedSource`` and optional
``renderedStartFrame``. No looping, holding, speed changes or cropping is done.

Gameplay is contained, preserving display aspect ratio, in ``viewport``
``[x,y,width,height]`` (default full1920x1080). Credits default to [30,34].
``credit`` may be a string or {text,position:[x,y],fontSize:26}.

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

Optional plan keys: brandingFile, membershipFile, mixFile, captionsAss, outputDir,
outputStem, expectedGameplayShare (default0.6), ratioToleranceFrames (default1).
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

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
DEFAULT_OUTPUT = PROJECT / "production/local/reference-preserving-v2/edit"
FPS, WIDTH, HEIGHT = 60, 1920, 1080
ENCODER = ["-c:v", "libx264", "-threads", "4", "-preset", "veryfast",
           "-crf", "17", "-pix_fmt", "yuv420p", "-color_primaries", "bt709",
           "-color_trc", "bt709", "-colorspace", "bt709",
           "-video_track_timescale", "60000"]
COLORS = {"red": "EF5350", "blue": "42A5F5", "green": "66BB6A",
          "yellow": "FFD54F"}
CAPTION_RECT = [150, 892, 1784, 1060]  # x0,y0,x1,y1; two lines+outline+shadow


def path(value: str | Path) -> Path:
    p = Path(value)
    return p.resolve() if p.is_absolute() else (ROOT / p).resolve()


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8-sig"))


def save(p: Path, value):
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
    return override or shutil.which(name) or name


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


def validate_plan(plan: dict):
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
            gameplay += cut["frames"]
            if not cut.get("sourceFile") or cut.get("sourceStart", 0) < 0:
                raise ValueError(f"Missing gameplay source: {cid}")
            if not cut.get("credit"):
                raise ValueError(f"Independent gameplay requires its source credit: {cid}")
        elif not cut.get("renderedSource"):
            raise ValueError(f"Explanation requires actually renderedSource: {cid}")
    if cursor != plan["totalFrames"] - 600:
        raise ValueError("Body must end immediately before exact600-frame membership")
    target = plan.get("expectedGameplayShare", .6) * plan["bodyFrames"]
    if abs(gameplay - target) > plan.get("ratioToleranceFrames", 1):
        raise ValueError(f"Gameplay ratio outside one-frame tolerance: {gameplay}/{plan['bodyFrames']}")
    return {"gameplayFrames": gameplay, "explanationFrames": plan["bodyFrames"] - gameplay,
            "bodyFrames": plan["bodyFrames"], "gameplayShare": gameplay / plan["bodyFrames"]}


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
    protected = [plan.get("captionProtectedRect", CAPTION_RECT), *cut.get("protectedRects", [])]
    font_file = path(plan.get("annotationFontFile", "C:/Windows/Fonts/malgun.ttf"))
    credit = cut.get("credit")
    if credit:
        credit = {"text": credit} if isinstance(credit, str) else credit
        text, size = credit["text"], credit.get("fontSize", 26)
        x, y = credit.get("position", [30, 34])
        font = ImageFont.truetype(str(font_file), size)
        bounds = [x - 4, y - 4, x + math.ceil(font.getlength(text)) + 4, y + size * 1.5 + 4]
        check_bounds(bounds, protected, "Credit")
        protected.append(bounds)
        result += event(0, duration, f"{{\\an7\\pos({x},{y})\\fs{size}\\bord3}}" + ass_text(text), 0)
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
                    "coordinates": "output1920x1080 pixels; cut-relative times"}


def filter_path(p: Path) -> str:
    # Quotes protect spaces and punctuation in FFmpeg's filter grammar.
    return "'" + p.as_posix().replace("\\", "\\\\").replace(":", r"\:").replace("'", r"\'") + "'"


def render_cuts(plan: dict, output: Path):
    ratio = validate_plan(plan)
    output.mkdir(parents=True, exist_ok=True)
    source_hashes, code_hash = {}, sha(Path(__file__))
    for cut in plan["cuts"]:
        gameplay = cut["kind"] == "independent-gameplay"
        source = path(cut["sourceFile"] if gameplay else cut["renderedSource"])
        source_info = video_stream(source)
        # Verify DECODED dimensions too, not only container metadata.
        decode_probe = subprocess.check_output([binary("ffprobe"), "-v", "error", "-select_streams", "v:0",
            "-read_intervals", "%+#1", "-show_frames", "-show_entries", "frame=width,height",
            "-of", "json", str(source)], cwd=ROOT)
        decoded = json.loads(decode_probe)["frames"][0]
        if gameplay and (min(decoded["width"], decoded["height"]) < 1080 or
                         max(decoded["width"], decoded["height"]) < 1920):
            raise ValueError(f"Source is not genuine FHD-or-higher decoded media: {source}: {decoded}")
        if not gameplay:
            if (source_info["width"], source_info["height"]) != (WIDTH, HEIGHT) or Fraction(source_info["avg_frame_rate"]) != FPS:
                raise ValueError(f"Explanation render must be1920x1080/60: {source}")
        start = float(cut.get("sourceStart", 0)) if gameplay else cut.get("renderedStartFrame", 0) / FPS
        source_duration = float(source_info.get("duration", probe(source)["format"]["duration"]))
        if start + cut["frames"] / FPS > source_duration + 1 / FPS:
            raise ValueError(f"Source too short; no hold/loop permitted: {cut['id']}")
        if str(source) not in source_hashes:
            source_hashes[str(source)] = sha(source)
        ass, geometry = annotations(cut, plan) if gameplay else (None, None)
        mark_file, destination = output / (cut["id"] + "-marks.ass"), output / (cut["id"] + ".mp4")
        signature = {"cut": cut, "sourceSha256": source_hashes[str(source)], "sourceDecoded": decoded,
                     "codeSha256": code_hash, "encoder": ENCODER, "markGeometry": geometry,
                     "assSha256": hashlib.sha256(ass.encode()).hexdigest() if ass else None}
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
        temp = destination.with_suffix(".partial.mp4")
        run(["-ss", f"{start:.9f}", "-threads", "4", "-i", str(source), "-an", "-vf", vf,
             "-frames:v", str(cut["frames"]), *ENCODER, "-movflags", "+faststart", str(temp)],
            output / (cut["id"] + "-render.log"))
        assert_video(temp, cut["frames"])
        temp.replace(destination)
        save(receipt, {"signature": signature, "outputSha256": sha(destination),
                       "visualMotionReview": "pending", "decodedDimensionsVerified": True})
        print(cut["id"], cut["frames"], "frames", flush=True)
    preserved = []
    for name, count, key in (("branding", 120, "brandingFile"), ("membership", 600, "membershipFile")):
        default = f"projects/game-reward-planning/production/local/reference-preserving-v2/edit/{name}.mp4"
        original, destination = path(plan.get(key, default)), output / (name + ".mp4")
        assert_video(original, count, count=True)
        digest = sha(original)
        if not destination.exists() or sha(destination) != digest:
            shutil.copy2(original, destination)
        if sha(destination) != digest:
            raise ValueError(f"Original {name} bytes were not preserved")
        preserved.append({"kind": name, "frames": count, "source": str(original),
                          "sourceSha256": digest, "outputSha256": digest, "bytePreserved": True})
    files = [output / "branding.mp4", *[output / (c["id"] + ".mp4") for c in plan["cuts"]], output / "membership.mp4"]
    (output / "concat.txt").write_text("\n".join("file '" + p.as_posix().replace("'", "'\\''") + "'" for p in files) + "\n", encoding="utf-8")
    save(output / "cuts-build.json", {"ratio": ratio, "brandingMembership": preserved,
                                      "nativeSpeed": True, "playbackReview": "pending"})


def stream_hash(p: Path, selector: str) -> str:
    return subprocess.check_output([binary("ffmpeg"), "-v", "error", "-i", str(p),
        "-map", selector, "-c", "copy", "-f", "hash", "-hash", "sha256", "-"], text=True, cwd=ROOT).strip()


def output_files(plan: dict, output: Path) -> dict:
    stem = plan.get("outputStem", "familiar-game-rules-v2")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", stem):
        raise ValueError("Unsafe outputStem")
    return {suffix: output / f"{stem}-{suffix}.mp4" for suffix in ("clean", "captioned")}


def render_pair(plan: dict, output: Path, mix_override=None, ass_override=None):
    validate_plan(plan)
    for cut in plan["cuts"]:
        assert_video(output / (cut["id"] + ".mp4"), cut["frames"])
    assert_video(output / "branding.mp4", 120)
    assert_video(output / "membership.mp4", 600)
    mix = path(mix_override or plan.get("mixFile", str(output / "final-mix.wav")))
    ass = path(ass_override or plan.get("captionsAss", str(output / "captions.ko.ass")))
    if not ass.exists():
        raise FileNotFoundError(ass)
    duration = plan["totalFrames"] / FPS
    mix_info = probe(mix)
    if abs(float(mix_info["format"]["duration"]) - duration) > 1 / FPS:
        raise ValueError("Final mix must match timeline; no implicit padding/truncation")
    aac, aac_receipt = output / "final-mix.m4a", output / "aac-source.json"
    audio_signature = {"sourceSha256": sha(mix), "duration": duration, "codec": "aac",
                       "bitrate": 192000, "sampleRate": 48000, "channels": 2}
    if not (aac.exists() and aac_receipt.exists() and
            load(aac_receipt).get("signature") == audio_signature and
            load(aac_receipt).get("outputSha256") == sha(aac)):
        run(["-i", str(mix), "-vn", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
             "-movflags", "+faststart", str(aac)], output / "audio-encode.log")
        save(aac_receipt, {"signature": audio_signature, "outputSha256": sha(aac)})
    files = output_files(plan, output)
    signature = {"planSha256": hashlib.sha256(json.dumps(plan, sort_keys=True).encode()).hexdigest(),
                 "cutSha256": [sha(output / (name + ".mp4")) for name in
                                ["branding", *[c["id"] for c in plan["cuts"]], "membership"]],
                 "aacSha256": sha(aac), "captionsAssSha256": sha(ass), "encoder": ENCODER,
                 "codeSha256": sha(Path(__file__))}
    receipt = output / "pair-build.json"
    if all(p.exists() for p in files.values()) and receipt.exists():
        old = load(receipt)
        if old.get("signature") == signature and all(old.get("outputs", {}).get(k, {}).get("sha256") == sha(p) for k, p in files.items()):
            print("Identical pair already exists; encoding reused", flush=True)
            return
    # Normalize visual metadata once before split; ASS sees one continuous clock.
    graph = "[0:v]fps=60,setsar=1,settb=1/60000,setpts=N/(60*TB),format=yuv420p,split=2[clean][capin];[capin]ass=" + filter_path(ass) + "[captioned]"
    args = ["-f", "concat", "-safe", "0", "-i", str(output / "concat.txt"), "-i", str(aac), "-filter_complex", graph]
    temporary = {key: p.with_suffix(".partial.mp4") for key, p in files.items()}
    for suffix in ("clean", "captioned"):
        args += ["-map", f"[{suffix}]", "-map", "1:a:0", "-frames:v", str(plan["totalFrames"]),
                 "-t", f"{duration:.9f}", *ENCODER, "-c:a", "copy", "-movflags", "+faststart", str(temporary[suffix])]
    run(args, output / "pair-encode.log")
    audio_hash = stream_hash(aac, "0:a:0")
    proofs = {}
    for suffix, p in temporary.items():
        assert_video(p, plan["totalFrames"])
        if stream_hash(p, "0:a:0") != audio_hash:
            raise ValueError("Pair did not preserve identical continuous AAC packets")
        p.replace(files[suffix])
        proofs[suffix] = {"path": str(files[suffix]), "sha256": sha(files[suffix]), "audioPacketsSha256": audio_hash}
    save(receipt, {"signature": signature, "outputs": proofs,
                   "continuousAac": True, "humanListeningAndMovingPixels": "pending"})


def pts_review(p: Path, expected: int) -> dict:
    args = [binary("ffprobe"), "-v", "error", "-select_streams", "v:0", "-show_frames",
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
        meta = assert_video(p, plan["totalFrames"], count=True)
        log = output / (suffix + "-full-decode.log")
        run(["-xerror", "-err_detect", "explode", "-threads", "4", "-i", str(p),
             "-map", "0:v:0", "-map", "0:a:0", "-f", "null", "-"], log)
        info = probe(p)
        audio = [s for s in info["streams"] if s["codec_type"] == "audio"]
        if len(audio) != 1 or audio[0]["codec_name"] != "aac" or audio[0]["sample_rate"] != "48000":
            raise ValueError(f"Unexpected final audio structure: {p}")
        actual_duration = float(info["format"]["duration"])
        if abs(actual_duration - plan["totalFrames"] / FPS) > 1 / FPS:
            raise ValueError(f"Final A/V duration mismatch: {p}")
        records[suffix] = {"path": str(p), "sha256": sha(p), "video": meta,
                           "pts": pts_review(p, plan["totalFrames"]),
                           "audioPacketsSha256": stream_hash(p, "0:a:0"),
                           "fullAudioVideoDecode": "pass", "durationSeconds": actual_duration}
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
    args = parser.parse_args()
    plan = load(path(args.plan))
    output = path(args.output_dir or plan.get("outputDir", str(DEFAULT_OUTPUT)))
    if args.stage == "cuts":
        render_cuts(plan, output)
    elif args.stage == "pair":
        render_pair(plan, output, args.mix, args.ass)
    else:
        verify(plan, output)


if __name__ == "__main__":
    main()
