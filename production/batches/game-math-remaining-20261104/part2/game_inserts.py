"""Render the actual annotated game inserts while the lecture narration is recording.

Each video-only intermediate preserves the compositor's pixels losslessly. An edit can
reuse it only if its exact frames, source, annotation and filter still match. Game audio
is mixed from the synchronized original source at the final speech-approved time.
"""
import argparse
import io
import json
import os
import shutil
import subprocess
import sys
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
        work = folder / (scene["id"]+("-"+game["insertVersion"] if game.get("insertVersion") else ""))
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
        data = dict(episode=episode, scene=scene["id"], pictureFolder=work.name, input=signature, pictureSha256=sha(target),
                    bytes=target.stat().st_size, sourceGame=source["game"], verifiedStream=stream,
                    audio="Use native synchronized source in the final mix", finalMaster=False)
        save(receipt, data)
        results.append(data)
        print(episode, scene["id"], source["game"], cut["frames"], "FHD frames", flush=True)
    assert len(results) >= 3
    save(project/"production/part2-review/game-inserts.json",dict(episode=episode,shots=results,finalMaster=False))

def inspect_inserts(episode):
    import numpy as np
    from PIL import Image, ImageDraw
    row=next(r for r in read(BATCH/"batch.json")["items"] if r["id"]==episode)
    project=ROOT/"projects"/row["slug"]
    work=project/"production/local/part2-game-inserts"
    shots=read(project/"production/part2-review/game-inserts.json")["shots"]
    sources={s["sha256"]:s for s in read(project/"planning/footage-audit.json")["sources"]}
    ffmpeg=shutil.which("ffmpeg")
    assert ffmpeg,"FFmpeg required for native game-motion inspection"
    board=Image.new("RGB",(375*4,236*len(shots)),"#141414");draw=ImageDraw.Draw(board)
    evidence=[]
    for row_number,shot in enumerate(shots):
        signature=shot["input"];sid=shot["scene"];duration=signature["frames"]/60
        source=sources[signature["sourceSha256"]]
        # Measure the original pixels, without the title, guide, captions or timer.
        raw=subprocess.check_output([ffmpeg,"-loglevel","error","-nostdin","-threads","2",
            "-ss",str(signature["start"]),"-i",str(ROOT/source["file"]),"-t",str(duration),
            "-an","-vf","crop=iw*.76:ih*.66:iw*.12:ih*.17,fps=4,scale=96:48,format=gray",
            "-filter_threads","1","-threads","1","-f","rawvideo","pipe:1"])
        pixels=np.frombuffer(raw,np.uint8).reshape(-1,48,96).astype(np.int16)
        differences=np.abs(np.diff(pixels,axis=0)).mean(axis=(1,2))
        positions=[min(duration-.1,t) for t in (.4,duration*.31,duration*.58,duration*.87)]
        for col,t in enumerate(positions):
            image=subprocess.check_output([ffmpeg,"-loglevel","error","-nostdin","-threads","2",
                "-ss",str(t),"-i",str(work/shot.get("pictureFolder",sid)/"picture.mkv"),"-vf","scale=375:211",
                "-frames:v","1","-threads","1","-c:v","png","-f","image2pipe","pipe:1"])
            with Image.open(io.BytesIO(image)) as frame:board.paste(frame,(375*col,236*row_number))
            draw.text((375*col+8,236*row_number+214),f"{episode}/{sid} {source['game']} | {signature['start']+t:.1f}s",fill="white")
        evidence.append(dict(scene=sid,game=source["game"],sourceSha256=signature["sourceSha256"],
             nativeSeconds=duration,sampledFrames=len(pixels),quarterSecondMovingIntervals=int((differences>.25).sum()),
             totalIntervals=len(differences),medianLumaDifference=round(float(np.median(differences)),3),
             inspectedFrameTimesInSource=[round(signature["start"]+t,3) for t in positions]))
    destination=work/"mobile-game-cuts.jpg";board.save(destination,quality=95)
    save(project/"production/part2-review/game-insert-motion.json",
         dict(episode=episode,sourceMotion=evidence,annotatedSampleBoardSha256=sha(destination),
              method="Original center-region quarter-second luma differences; annotated board at 375px width. Final mixed lecture QA is separate."))
    print(episode,[(s["scene"],s["quarterSecondMovingIntervals"],s["totalIntervals"]) for s in evidence],flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--inspect",action="store_true")
    parser.add_argument("episodes", nargs="+")
    args=parser.parse_args()
    for episode_id in args.episodes:
        if args.inspect:inspect_inserts(episode_id)
        else:render_episode(episode_id)
