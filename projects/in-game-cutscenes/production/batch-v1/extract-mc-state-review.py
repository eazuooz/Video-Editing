"""Extract every used MC reveal from the final encoded master, after rendering.

This complements the shared caption/mark/boundary extractor. It does not render
media, infer approval, or replace direct inspection of the resulting pixels.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for part in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(part)
    return value.hexdigest()


def balanced_sum(terms: list[str]) -> str:
    if len(terms) == 1:
        return terms[0]
    middle = len(terms) // 2
    return "(" + balanced_sum(terms[:middle]) + "+" + balanced_sum(terms[middle:]) + ")"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("slug", choices=["in-game-cutscenes", "start-with-climax"])
    parser.add_argument("--version", default="final-v1")
    args = parser.parse_args()
    if not args.version.replace("-", "").isalnum():
        raise ValueError("Use a simple, explicit QA version")
    root = Path(__file__).resolve().parents[4]
    project = root / "projects" / args.slug
    production = project / "production" / "batch-v1"
    sys.path.insert(0, str(production))
    from audio_pipeline import require_authorized
    from storage_paths import repo_path, relative

    require_authorized("encoded MC reveal-state review extraction")
    plan_file = production / "edit-plan.json"
    audit_file = production / "mc-cue-deadline-review.json"
    plan = json.loads(plan_file.read_text(encoding="utf-8-sig"))
    audit = json.loads(audit_file.read_text(encoding="utf-8-sig"))
    if audit["planSha256"] != digest(plan_file):
        raise ValueError("MC schedule audit is stale for the edit plan")
    scene = root / "motion-canvas" / "src" / "projects" / args.slug / "batch-v1" / "visuals.tsx"
    data = scene.with_name("motion-data.json")
    if audit["sourceSha256"] != digest(scene) or audit["dataSha256"] != digest(data):
        raise ValueError("MC schedule audit is stale for the authored scene/data")
    edit = repo_path(plan["outputDir"])
    master = edit / (plan["outputStem"] + "-captioned.mp4")
    inputs = {
        "captionedSha256": digest(master), "planSha256": digest(plan_file),
        "scheduleAuditSha256": digest(audit_file), "sceneSha256": digest(scene),
        "motionDataSha256": digest(data),
    }
    folder = edit / "qa" / args.version / "mc-states"
    receipt = folder / "frame-index.json"
    if receipt.exists():
        previous = json.loads(receipt.read_text(encoding="utf-8-sig"))
        if previous["inputs"] != inputs:
            raise ValueError("Keep prior evidence; choose a new --version for changed inputs")
        print("Unchanged MC-state evidence reused")
        return
    folder.mkdir(parents=True, exist_ok=True)
    cuts = {cut["id"]: cut for cut in plan["cuts"]}
    records = []
    points = set()
    for review in audit["reviews"]:
        cut = cuts[review["cut"]]
        if not review["allUsedCueRevealsCompleteBeforeCutEnd"]:
            raise ValueError("Unresolved cue schedule")
        for event in review["events"]:
            # Capture after the final animated value is visible, with at least
            # one encoded frame before the source cut's end.
            local_time = min(float(event["fullyVisible"]) + .10,
                             cut["frames"] / 60 - 1 / 60)
            frame = max(cut["startFrame"], min(cut["endFrame"] - 1,
                        cut["startFrame"] + round(local_time * 60)))
            record = {"cut": cut["id"], "kind": review["kind"],
                      "paragraphIds": review["paragraphIds"], "event": event["name"],
                      "fullyVisibleLocalSeconds": event["fullyVisible"],
                      "frame": frame, "time": frame / 60}
            records.append(record)
            points.add(frame)
    ordered = sorted(points)
    if not ordered:
        raise ValueError("No reveal states selected")
    frames = folder / "frames"
    frames.mkdir(exist_ok=True)
    expression = balanced_sum([f"eq(n,{frame})" for frame in ordered])
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-threads", "2",
                    "-i", str(master), "-vf", "select='" + expression + "'",
                    "-fps_mode", "vfr", "-frames:v", str(len(ordered)),
                    "-compression_level", "1", "-threads", "2", "-n",
                    str(frames / "%04d.png")], check=True)
    if len(list(frames.glob("*.png"))) != len(ordered):
        raise ValueError("Incomplete decoded state extraction")
    mapping = {frame: frames / f"{index + 1:04d}.png" for index, frame in enumerate(ordered)}
    for index, row in enumerate(records):
        row["state"] = index + 1
        row["file"] = relative(mapping[row["frame"]])
    for width in [640, 375]:
        height = round(width * 9 / 16)
        for page in range((len(records) + 7) // 8):
            batch = records[page * 8:(page + 1) * 8]
            board = Image.new("RGB", (width * 2, (height + 38) * 4), "#151515")
            draw = ImageDraw.Draw(board)
            for index, row in enumerate(batch):
                x, y = (index % 2) * width, (index // 2) * (height + 38)
                with Image.open(mapping[row["frame"]]) as native:
                    image = native.convert("RGB").resize((width, height), Image.Resampling.LANCZOS)
                board.paste(image, (x, y))
                label = f"S{row['state']:03d} {row['cut']} {row['time']:.3f}s"
                draw.text((x + 5, y + height + 4), label, fill="white")
                draw.text((x + 5, y + height + 20), row["event"][:75], fill="white")
            board.save(folder / f"states-{width}-{page + 1:02d}.jpg", quality=93)
    result = {"inputs": inputs, "status": "extracted-awaiting-direct-pixel-review",
              "master": relative(master), "nativeWidth": 1920, "nativeHeight": 1080,
              "states": records, "frames": [{"frame": frame, "time": frame / 60,
                  "file": relative(mapping[frame]), "sha256": digest(mapping[frame])}
                  for frame in ordered], "wholeListening": False,
              "scope": "One final encoded still after every used authored reveal; motion/playback is separate."}
    receipt.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"states": len(records), "uniqueFrames": len(ordered),
                      "directory": relative(folder)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
