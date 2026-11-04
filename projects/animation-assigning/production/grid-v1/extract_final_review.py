"""Extract hash-bound final encoded pixels for targeted A01 visual review.

CPU only. Reads the final captioned master; never rebuilds or changes it.
Samples every caption midpoint, each cut's first/middle/last frame, and three
frames in every visible editorial-mark interval. A sample is evidence of that
frame, not a claim that the full moving video has been watched.

    python extract_final_review.py --dry-run
    python extract_final_review.py
    python extract_final_review.py --resume

Do not run extraction until the final captioned master is complete. --dry-run
only prints the schedule summary and does not require or create media.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess

from storage_paths import HERE, LOCAL, local_output, relative, repo_path


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def artifact(path):
    return {"path": relative(path), "sha256": sha(path), "bytes": Path(path).stat().st_size}


def save(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def executable(name, supplied=None):
    result = supplied or os.environ.get(name.upper()) or shutil.which(name)
    if not result:
        raise FileNotFoundError(f"{name} not found; pass --{name}")
    return result


def frames_inside(start, end, fps):
    """Frames whose presentation times fall in [start,end)."""
    first = math.ceil(start * fps - 1e-8)
    last = math.ceil(end * fps - 1e-8) - 1
    if last < first:
        raise ValueError(f"No visible frame in interval {start}–{end}")
    return first, last


def subtract(intervals, holes):
    result = list(intervals)
    for a, b in holes:
        replacement = []
        for x, y in result:
            if b <= x or a >= y:
                replacement.append((x, y))
            else:
                if x < a:
                    replacement.append((x, min(a, y)))
                if b < y:
                    replacement.append((max(b, x), y))
        result = replacement
    return result


def visible_intervals(mark, duration):
    start, end = float(mark["t0"]), float(mark["t1"])
    if not 0 <= start < end <= duration + 1e-8:
        raise ValueError("Annotation outside its cut")
    intervals = [(start, end)]
    if mark.get("visibleIntervals"):
        intervals = [(max(start, a), min(end, b)) for a, b in mark["visibleIntervals"]
                     if max(start, a) < min(end, b)]
    return subtract(intervals, mark.get("hiddenIntervals", []))


def schedule(plan, captions):
    fps = int(plan["fps"])
    if fps != 60:
        raise ValueError("This revision expects a 60fps final master")
    total = int(plan["totalFrames"])
    requests = []

    def add(frame, group, label, **details):
        frame = int(frame)
        if not 0 <= frame < total:
            raise ValueError(f"Review frame outside master: {label}/{frame}")
        requests.append({"frame": frame, "globalTime": frame / fps,
                         "group": group, "label": label, **details})

    for cue in captions["cues"]:
        first, last = frames_inside(cue["start"], cue["end"], fps)
        add((first + last) // 2, "captions", f"Caption {cue['cue']:03}",
            cue=cue["cue"], paragraph=cue["paragraph"],
            cueStart=cue["start"], cueEnd=cue["end"], ko=cue["ko"], en=cue["en"])
    for cut in plan["cuts"]:
        first, end = int(cut["startFrame"]), int(cut["endFrame"])
        if end - first != int(cut["frames"]):
            raise ValueError(f"Cut frame count mismatch: {cut['id']}")
        last = end - 1
        for label, frame in (("first", first), ("middle", (first + last) // 2), ("last", last)):
            add(frame, "cuts", f"{cut['id']} {label}", cut=cut["id"],
                sample=label, kind=cut["kind"], cutLocalTime=(frame-first)/fps)
        for index, mark in enumerate(cut.get("marks", [])):
            mark_id = mark.get("id", f"{cut['id']}-mark-{index}")
            for interval_index, (a, b) in enumerate(visible_intervals(mark, cut["frames"] / fps)):
                f, l = frames_inside(a, b, fps)
                for label, local in (("first", f), ("middle", (f + l) // 2), ("last", l)):
                    add(first + local, "annotations", f"{mark_id} {label}",
                        cut=cut["id"], mark=mark_id, markLabel=mark["label"],
                        intervalIndex=interval_index, visibleInterval=[a, b],
                        sample=label, cutLocalTime=local/fps)
    # These six additional pixels check the unchanged branding/membership ends.
    for name, first, end in (("branding", 0, int(plan["introFrames"])),
                             ("membership", total-int(plan["outroFrames"]), total)):
        for label, frame in (("first", first), ("middle", (first+end-1)//2), ("last", end-1)):
            add(frame, "ends", f"{name} {label}", sample=label)
    return requests


def source_probe(ffprobe, master, plan):
    command = [ffprobe, "-v", "error", "-select_streams", "v:0", "-show_streams",
               "-show_format", "-of", "json", str(master)]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=True)
    data = json.loads(result.stdout)
    stream = data["streams"][0]
    if (stream["width"], stream["height"]) != (1920, 1080):
        raise ValueError("Review the actual FHD master, not a proxy or scaled preview")
    if Fraction(stream["avg_frame_rate"]) != 60:
        raise ValueError("Final master is not 60fps")
    if stream.get("nb_frames", "N/A") != "N/A" and int(stream["nb_frames"]) != plan["totalFrames"]:
        raise ValueError("Final master frame count differs from the frozen plan")
    return data


def extract(ffmpeg, master, frames, output):
    # One CPU decode pass; ffmpeg numbers the selected PNGs consecutively. The
    # showinfo PTS check below independently binds each selected image to time.
    # A flat 378-term addition creates a left-deep expression tree that exceeds
    # libavutil's expression recursion limit. Explicit balanced parentheses keep
    # exactly the same membership test with logarithmic expression depth.
    def balanced(terms):
        if len(terms) == 1:
            return terms[0]
        middle = len(terms) // 2
        return "(" + balanced(terms[:middle]) + "+" + balanced(terms[middle:]) + ")"

    expression = balanced([f"eq(n\\,{frame})" for frame in frames])
    raw = output / "decoded"
    raw.mkdir(exist_ok=True)
    log = output / "decode.log"
    command = [ffmpeg, "-hide_banner", "-nostdin", "-v", "info", "-y",
               "-threads", "2", "-filter_threads", "1", "-i", str(master),
               "-map", "0:v:0", "-vf", f"select={expression},showinfo", "-an",
               "-fps_mode", "passthrough", "-c:v", "png", "-threads", "1",
               "-compression_level", "3", str(raw / "sample-%05d.png")]
    with log.open("w", encoding="utf-8") as stream:
        result = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f"CPU extraction failed; inspect {log}")
    text = log.read_text(encoding="utf-8", errors="replace")
    pts = [float(value) for value in re.findall(r"\bn:\s*\d+\s+pts:\s*-?\d+\s+pts_time:([-+0-9.eE]+)", text)]
    images = sorted(raw.glob("sample-*.png"))
    if len(images) != len(frames) or len(pts) != len(frames):
        raise ValueError(f"Expected {len(frames)} samples, got {len(images)} PNG/{len(pts)} PTS")
    rows = []
    for frame, png, actual_time in zip(frames, images, pts):
        if abs(actual_time-frame/60) > .001:
            raise ValueError(f"Decoded frame/time mismatch at {frame}: {actual_time}")
        rows.append({"frame": frame, "globalTime": frame/60,
                     "decodedPtsTime": actual_time, "full": artifact(png)})
    return rows


def make_visual_index(output, requests, rows):
    from PIL import Image, ImageDraw, ImageFont
    font_path = Path("C:/Windows/Fonts/malgun.ttf")
    label_font = ImageFont.truetype(str(font_path), 19)
    small_font = ImageFont.truetype(str(font_path), 15)
    mobile = output / "mobile-375"
    mobile.mkdir(exist_ok=True)
    for row in rows:
        image = Image.open(repo_path(row["full"]["path"])).convert("RGB")
        if image.size != (1920, 1080):
            raise ValueError("Decoded PNG dimensions changed")
        target = mobile / f"frame-{row['frame']:06}.png"
        image.resize((375, 211), Image.Resampling.LANCZOS).save(target)
        row["mobile375"] = artifact(target)
    by_frame = {row["frame"]: row for row in rows}
    grouped = defaultdict(list)
    for request in requests:
        grouped[request["group"]].append(request)
    sheets = []
    for group, group_requests in grouped.items():
        for variant, width, height, key in (("full", 640, 360, "full"),
                                           ("mobile375", 375, 211, "mobile375")):
            font = label_font if variant == "full" else small_font
            cell_height, page_size = height + 58, 12
            for page in range(math.ceil(len(group_requests)/page_size)):
                batch = group_requests[page*page_size:(page+1)*page_size]
                sheet = Image.new("RGB", (width*3, cell_height*math.ceil(len(batch)/3)), "#111111")
                draw = ImageDraw.Draw(sheet)
                for i, request in enumerate(batch):
                    x, y = (i%3)*width, (i//3)*cell_height
                    source = repo_path(by_frame[request["frame"]][key]["path"])
                    im = Image.open(source).convert("RGB")
                    if im.size != (width, height):
                        im = im.resize((width, height), Image.Resampling.LANCZOS)
                    sheet.paste(im, (x, y))
                    draw.text((x+5, y+height+3), request["label"], font=font, fill="white")
                    draw.text((x+5, y+height+29),
                              f"f{request['frame']}  {request['globalTime']:.3f}s", font=font, fill="#D0D0D0")
                destination = output / f"{group}-{variant}-{page+1:02}.jpg"
                sheet.save(destination, quality=92)
                sheets.append({"group": group, "variant": variant,
                               "requests": batch, "image": artifact(destination)})
    import html
    page = ["<!doctype html><meta charset='utf-8'><title>A01 final pixels review</title>",
            "<style>body{background:#111;color:#eee;font:16px sans-serif;margin:24px}img{max-width:100%;height:auto}section{margin:30px 0}a{color:#9bd}</style>",
            "<h1>A01 — final encoded pixel samples</h1>",
            "<p>Targeted still-frame evidence only. Moving footage, speech and full listening are separate checks. Mobile frames are actual master pixels resized to375px, not recomposed slides.</p>"]
    for sheet in sheets:
        name = Path(sheet["image"]["path"]).name
        page.append(f"<section><h2>{html.escape(sheet['group'])} / {sheet['variant']}</h2><a href='{name}'><img loading='lazy' src='{name}'></a></section>")
    (output / "index.html").write_text("\n".join(page), encoding="utf-8")
    return sheets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", default=str(HERE / "edit-plan.json"))
    parser.add_argument("--captions")
    parser.add_argument("--master")
    parser.add_argument("--output-dir", default=str(LOCAL / "qa/final-pixels-v1"))
    parser.add_argument("--ffmpeg")
    parser.add_argument("--ffprobe")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    plan_path = repo_path(args.plan)
    plan = read(plan_path)
    edit = repo_path(plan["outputDir"])
    stem = plan["outputStem"]
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", stem):
        raise ValueError("Unsafe outputStem")
    captions_path = repo_path(args.captions) if args.captions else edit / "captions.json"
    master = repo_path(args.master) if args.master else edit / f"{stem}-captioned.mp4"
    output = local_output(args.output_dir)
    requests = schedule(plan, read(captions_path))
    frames = sorted({item["frame"] for item in requests})
    counts = {group: sum(item["group"] == group for item in requests)
              for group in sorted({item["group"] for item in requests})}
    if args.dry_run:
        print(json.dumps({"status": "schedule-only-no-media-read-or-write", "master": str(master),
                          "counts": counts, "uniqueFrames": len(frames),
                          "firstFrame": frames[0], "lastFrame": frames[-1]}, ensure_ascii=False))
        return
    if not master.is_file():
        raise FileNotFoundError(f"Final captioned master is not ready: {master}")
    inputs = {"plan": artifact(plan_path), "captions": artifact(captions_path),
              "master": artifact(master), "extractor": artifact(Path(__file__))}
    output.mkdir(parents=True, exist_ok=True)
    receipt = output / "review-manifest.json"
    job_path = output / "review-job.json"
    if receipt.exists() and not args.resume:
        raise FileExistsError("Review evidence exists; use --resume only for identical inputs")
    job = {"inputs": inputs, "requests": requests, "uniqueFrames": frames, "counts": counts}
    if job_path.exists():
        old_job = read(job_path)
        if not args.resume:
            raise ValueError("Existing extraction job requires --resume")
        if old_job["inputs"] != inputs:
            # Only an extractor-code correction after a failed zero-frame
            # attempt may resume in this directory. Never reuse pixels from
            # another master, caption set, plan, or sampling schedule.
            same_sources = all(old_job["inputs"].get(key) == inputs[key]
                               for key in ("plan", "captions", "master"))
            same_schedule = all(old_job.get(key) == job[key]
                                for key in ("requests", "uniqueFrames", "counts"))
            zero_frames = not any((output/"decoded").glob("*.png"))
            failure_log = output/"decode.log"
            recorded_failure = failure_log.is_file() and "Error opening output" in failure_log.read_text(encoding="utf-8", errors="replace")
            if receipt.exists() or not (same_sources and same_schedule and zero_frames and recorded_failure):
                raise ValueError("Existing extraction inputs/schedule/pixels differ; choose a new local QA directory")
            attempts = output/"failed-attempts"
            attempts.mkdir(exist_ok=True)
            number = 1
            while (attempts/f"attempt-{number:02}").exists():
                number += 1
            preserved = attempts/f"attempt-{number:02}"
            preserved.mkdir()
            for path in (job_path, failure_log):
                shutil.copy2(path, preserved/path.name)
            job["resumedFromFailedAttempt"] = {
                "reason": "Extractor expression-depth correction; identical source hashes and exact sampling schedule, no prior PNGs.",
                "preservedJob": artifact(preserved/job_path.name),
                "preservedLog": artifact(preserved/failure_log.name),
            }
    save(job_path, job)
    if receipt.exists():
        record = read(receipt)
        for row in record["frames"]:
            for key in ("full", "mobile375"):
                if sha(repo_path(row[key]["path"])) != row[key]["sha256"]:
                    raise ValueError("Existing review pixels changed")
        print(json.dumps({"status": "verified-existing-identical-input-evidence", "manifest": str(receipt)}))
        return
    probe = source_probe(executable("ffprobe", args.ffprobe), master, plan)
    rows = extract(executable("ffmpeg", args.ffmpeg), master, frames, output)
    sheets = make_visual_index(output, requests, rows)
    record = {"schemaVersion": 1, "episode": "A01", "status": "extracted-not-yet-visually-reviewed",
              "inputs": inputs, "masterProbe": probe, "counts": counts,
              "uniqueFrameCount": len(rows), "requests": requests, "frames": rows,
              "contactSheets": sheets, "index": artifact(output / "index.html"),
              "sampling": "All caption midpoints, cut first/middle/last, three per visible annotation interval, branding/member ends.",
              "mobileTransform": "Complete actual1920x1080 encoded frame ->375x211 Lanczos; no crop or added production elements.",
              "fullMovingVideoViewed": False, "humanListening": False,
              "pixelsVisuallyReviewed": False,
              "limitations": "Sparse extracted frames cannot certify motion, all-frame occlusion/tracking, caption reading pace, or audio quality."}
    save(receipt, record)
    print(json.dumps({"status": record["status"], "uniqueFrames": len(rows),
                      "manifest": str(receipt), "manifestSha256": sha(receipt)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
