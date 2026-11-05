"""Render the actual annotated game inserts while the lecture narration is recording.

Each video-only intermediate preserves the compositor's pixels losslessly. An edit can
reuse it only if its exact frames, source, annotation and filter still match. Game audio
is mixed from the synchronized original source at the final speech-approved time.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from edition import BATCH, ROOT, read, save, sha


def render_episode(episode):
    row = next(r for r in read(BATCH / "batch.json")["items"][2:] if r["id"] == episode)
    project = ROOT / "projects" / row["slug"]
    folder = project / "production/local/part2-game-inserts"
    folder.mkdir(parents=True, exist_ok=True)
    bootstrap = folder / "project.json"
    save(bootstrap, {"project": project.name})
    import runpy
    sys.argv = ["compose-module", "--queue", str(bootstrap)]
    compose = runpy.run_path(str(BATCH / "compose-module.py"))
    sources = {s["id"]: s for s in read(project / "planning/footage-audit.json")["sources"]}
    results = []
    for scene in read(project / "planning/scene-bindings.json")["scenes"]:
        game = scene.get("actualGamePart")
        if not game:
            continue
        if shutil.disk_usage(folder).free < 45 * 1024**3:
            raise RuntimeError("Preserve space for the full lecture masters")
        source = sources[game["sourceId"]]
        assert game["playbackRate"] == 1 and not game["loop"] and not game["freezePadding"]
        assert game["sourceSha256"] == source["sha256"] == sha(ROOT / source["file"])
        cut = dict(scene=scene["id"], sourceIn=game["sourceIn"], sourceOut=game["sourceOut"],
                   frames=int((game["sourceOut"] - game["sourceIn"]) * 60 + .0001))
        if game.get("nativeDetailInset"):
            cut["nativeDetailInset"] = game["nativeDetailInset"]
        work = folder / scene["id"]
        work.mkdir(exist_ok=True)
        target = work / "picture.mkv"
        receipt = work / "receipt.json"
        overlay = work / "track.ass"
        compose["annotation_ass"](cut, source, overlay)
        graph = compose["game_filters"](cut, "track.ass")
        signature = dict(sourceSha256=source["sha256"], start=cut["sourceIn"], end=cut["sourceOut"],
                         frames=cut["frames"], filter=graph, annotationSha256=sha(overlay))
        if receipt.is_file() and target.is_file():
            old = read(receipt)
            assert old["input"] == signature and old["pictureSha256"] == sha(target)
            results.append(old)
            continue
        if target.exists():
            raise RuntimeError(f"Inspect unfinished insert: {target}")
        # Video only. No reservation of the GPU or use of hardware codecs. Limit
        # filter and codec threads to let TTS and the user's other jobs proceed.
        candidate = work / f"picture-{os.getpid()}.mkv"
        args = [str(compose["FF"]), "-hide_banner", "-nostdin", "-n", "-threads", "2",
                "-ss", str(cut["sourceIn"]), "-i", str(ROOT / source["file"]), "-an",
                "-filter_threads", "2", "-vf", graph, "-frames:v", str(cut["frames"]),
                "-c:v", "libx264", "-threads", "2", "-preset", "veryfast", "-qp", "0",
                "-pix_fmt", "yuv420p", str(candidate)]
        with (work / "render.log").open("wb") as out:
            subprocess.run(args, cwd=work, stdout=out, stderr=subprocess.STDOUT, check=True,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        ffprobe = str(Path(compose["FF"]).with_name("ffprobe.exe"))
        stream = json.loads(subprocess.check_output([ffprobe, "-v", "error", "-threads", "2", "-count_frames",
            "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate,nb_read_frames",
            "-of", "json", str(candidate)]))["streams"][0]
        assert (stream["width"],stream["height"],stream["r_frame_rate"],int(stream["nb_read_frames"])) == (1920,1080,"60/1",cut["frames"])
        os.replace(candidate, target)
        data = dict(episode=episode, scene=scene["id"], input=signature, pictureSha256=sha(target),
                    bytes=target.stat().st_size, sourceGame=source["game"], verifiedStream=stream,
                    audio="Use native synchronized source in the final mix", finalMaster=False)
        save(receipt, data)
        results.append(data)
        print(episode, scene["id"], source["game"], cut["frames"], "FHD frames", flush=True)
    assert len(results) >= 3
    save(project/"production/part2-review/game-inserts.json",dict(episode=episode,shots=results,finalMaster=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("episodes", nargs="+")
    for episode_id in parser.parse_args().episodes:
        render_episode(episode_id)
