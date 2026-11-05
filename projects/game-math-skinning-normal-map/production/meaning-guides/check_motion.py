"""Inspect native motion in each commercial game excerpt of the final captioned file."""
from pathlib import Path
import subprocess

import numpy as np

from prepare import P, read, save


def main():
    work = P / "production/local/render-v2"
    queue = read(work / "queue.json")
    master = read(work / "final-qa/report.json")["files"]["captioned"]
    ffmpeg = read(Path(queue["jobs"][0]))["ffmpeg"]
    motion = []
    for clip in queue["cuts"]:
        if clip["kind"] != "actual-gameplay":
            continue
        offset = (120 + clip["globalStartFrame"]) / 60
        length = clip["frames"] / 60
        video = subprocess.check_output([
            ffmpeg,"-nostdin","-loglevel","error","-threads","2","-ss",str(offset),
            "-t",str(length),"-i",master["path"],"-an","-vf",
            "crop=1440:740:240:135,fps=4,scale=96:48,format=gray",
            "-f","rawvideo","-threads","1","pipe:1"])
        pixels = np.frombuffer(video,dtype=np.uint8).reshape(-1,48,96).astype(np.int16)
        diffs = np.abs(np.diff(pixels,axis=0)).mean(axis=(1,2))
        motion.append(dict(scene=clip["scene"],sourceId=clip["sourceId"],seconds=length,
                           nativeSpeed=clip["nativeSpeed"],sourceIn=clip["sourceIn"],sourceOut=clip["sourceOut"],
                           intervals=len(diffs),movingIntervals=int((diffs>.25).sum()),
                           medianLumaDifference=round(float(np.median(diffs)),2)))
    assert len(motion)==3 and all(s["nativeSpeed"] and s["movingIntervals"]>s["intervals"]*.55 for s in motion)
    save(work/"final-qa/game-motion.json",dict(masterSha256=master["sha256"],
         method="4 fps grayscale differences inside the game picture, excluding captions and labels",cuts=motion))
    print(motion)


if __name__=="__main__":
    main()
