"""Adopt only native shots whose original recording, editable scene and timing are identical."""
import argparse
import os
from pathlib import Path
from edition import BATCH, ROOT, read, save, sha
from queue_state import live

def adopt(episode):
    row=next(r for r in read(BATCH/"batch.json")["items"] if r["id"]==episode)
    p=ROOT/"projects"/row["slug"];local=p/"production/local"
    old=local/"render-v2";new=local/"render-v3"
    oldq=read(old/"queue.json");q=read(new/"queue.json")
    assert q["project"]==oldq["project"]==p.name and q["sandbox"]==oldq["sandbox"] and q["fingerprint"]==oldq["fingerprint"]
    assert read(old/"part2-delivery-evidence.json")["frames"]>0
    if (new/"progress.json").is_file():
        assert not live(read(new/"progress.json")), "An active capture owns this folder"
    earlier={j["sceneId"]:j for j in map(read,map(Path,oldq["jobs"]))}
    adopted=[]
    for jobfile in map(Path,q["jobs"]):
        job=read(jobfile);sid=job["sceneId"]
        job["id"]=f"{episode.lower()}-render-v3-body-{sid}";save(jobfile,job)
        prior=earlier[sid];before=Path(prior["output"]);after=Path(job["output"])
        assert before.is_relative_to(old) and after.is_relative_to(new)
        chunk=sid+"-01-scene.wav"
        native_sha=sha(Path(job["shotFile"])); audio_sha=sha(Path(q["audioDirectory"])/"chunks"/chunk)
        if (prior["frames"]!=job["frames"] or sha(Path(prior["shotFile"]))!=native_sha or
                sha(Path(oldq["audioDirectory"])/"chunks"/chunk)!=audio_sha):
            continue
        saved=read(before/"capture-success.json");structure=read(before/"encoded-structure.json")
        editable=Path(q["sandbox"])/saved["scene"]
        assert editable.is_file() and saved["fingerprint"]==q["fingerprint"]
        assert saved["completed"]==job["frames"]==structure["frames"] and structure["size"]==[1920,1080] and structure["fps"]=="60/1"
        after.mkdir(parents=True,exist_ok=True)
        for name in ["unity.mp4","capture-success.json"]:
            if (after/name).is_file():
                assert sha(after/name)==sha(before/name)
            else:
                os.link(before/name,after/name)
        proof=dict(scene=sid,editableSource=str(editable),frames=job["frames"],sourceTakeSha256=audio_sha,
                   nativeShotSha256=native_sha,videoSha256=sha(after/"unity.mp4"))
        save(after/"source-reuse.json",proof);adopted.append(proof)
    save(new/"native-reuse.json",dict(sourceRevision=old.name,reused=adopted))
    print(episode,len(adopted),"verified source shots;",len(q["jobs"])-len(adopted),"new captures")

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("episode",choices=["M32","M33"])
    adopt(parser.parse_args().episode)
