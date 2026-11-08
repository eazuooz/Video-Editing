"""Render explicitly requested, measured-timing relation diagrams serially on CPU."""
import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ROOT = HERE.parents[4]


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def write(p, data):
    Path(p).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    args = argparse.ArgumentParser()
    args.add_argument("--ids", nargs="+", required=True)
    args = args.parse_args()
    plan_path = BASE / "planning/relations-plan.json"
    timing_path = BASE / "local/timing.json"
    plan = read(plan_path)
    measured = read(timing_path)
    selected = []
    for key in args.ids:
        ep = next(e for e in measured["episodes"] if e["id"] == key)
        source = next(e for e in plan["episodes"] if e["id"] == key)
        by = {s["id"]: s for s in source["sentences"]}
        assert len(ep["sentences"]) == len(by), key
        for s in ep["sentences"]:
            assert s["id"] in by and s["beat"] == by[s["id"]]["beat"] and s["ko"] == by[s["id"]]["ko"], key
            assert 0 <= s["start"] < s["end"] <= ep["duration"], key
        assert digest(ep["audio"]) == ep["audioSha256"], key
        selected.append(ep)
    snap_path = BASE / "local/visual-previews" / ("timing-" + "-".join(args.ids) + ".json")
    write(snap_path, {"fps": 60, "sourceTimingSha256": digest(timing_path), "asrBoundaryRepairs": measured.get("asrBoundaryRepairs", []), "episodes": selected})
    qa_path = HERE / "main-render-qa.json"
    qa = read(qa_path) if qa_path.exists() else {"kind": "silent-relation-diagram-render-QA", "episodes": []}
    for ep in selected:
        control = read(ROOT / "shared/publishing/video-production-control.json")["animationRelationsRevision20261108"]
        assert control["renderAuthorized"] and ep["id"] in control["episodes"]
        project = ROOT / "projects" / ep["slug"]
        assert read(project / "project.json")["slug"] == ep["slug"]
        output = project / "production/local/relations-v4/relation.mp4"
        assert output.parent.exists()
        if output.exists():
            raise RuntimeError(f"Preserving completed output; inspect before rerender: {output}")
        print("Rendering", ep["id"], flush=True)
        subprocess.run(["node", str(HERE / "renderer.cjs"), "render", "--plan", str(plan_path), "--timing", str(snap_path), "--id", ep["id"], "--out", str(output)], check=True, cwd=ROOT)
        probe = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate,nb_frames,duration", "-of", "json", str(output)]))["streams"][0]
        assert probe["width"] == 1920 and probe["height"] == 1080 and probe["r_frame_rate"] == "60/1" and int(probe["nb_frames"]) == ep["frames"]
        subprocess.run(["ffmpeg", "-v", "error", "-i", str(output), "-f", "null", "-"], check=True)
        frames = [min(ep["frames"] - 1, round((s["start"] + .8) * 60)) for s in ep["sentences"]]
        expression = "+".join(f"eq(n,{n})" for n in frames)
        contact = BASE / "local/visual-previews" / (ep["id"] + "-relation-encoded.jpg")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(output), "-vf", f"select='{expression}',scale=640:360,tile=3x{math.ceil(len(frames)/3)}", "-frames:v", "1", "-q:v", "2", str(contact)], check=True)
        result = {"id": ep["id"], "path": str(output), "sha256": digest(output), "probe": probe, "timingSnapshot": str(snap_path), "sentenceBeatCheck": f"{len(ep['sentences'])}/{len(ep['sentences'])} exact plan match", "audioHashCheck": "passed", "fullDecode": "passed", "sampleFrames": frames, "frameContact": str(contact), "encodedVisualInspection": "pending"}
        qa["episodes"] = sorted([x for x in qa["episodes"] if x["id"] != ep["id"]] + [result], key=lambda x: x["id"])
        write(qa_path, qa)
        print("Encoded and decoded", ep["id"], probe["nb_frames"], "frames", flush=True)


if __name__ == "__main__":
    main()
