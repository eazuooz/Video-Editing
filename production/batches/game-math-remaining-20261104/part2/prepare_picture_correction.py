"""Keep a rendered lecture intact and build an additive visual-only correction."""
import argparse
import os
import subprocess
import sys
from pathlib import Path
from edition import ROOT,BATCH,read,save,sha,render_revision

def prepare(episode,revision,purposes,finding):
    row=next(r for r in read(BATCH/"batch.json")["items"] if r["id"]==episode)
    p=ROOT/"projects"/row["slug"];local=p/"production/local"
    src=local/render_revision(p);dest=local/revision
    assert src!=dest and not dest.exists()
    source=read(src/"queue.json");qa=read(src/"final-qa/report.json")
    assert sha(Path(qa["files"]["captioned"]["path"]))==qa["files"]["captioned"]["sha256"]
    audio=read(p/"planning/part2-delivery-edition.json")["audioRevision"]
    subprocess.run([sys.executable,"-X","utf8",str(BATCH/"prepare-module-render.py"),
                    "--project",p.name,"--sandbox",Path(source["sandbox"]).name,
                    "--audio-revision",audio,"--revision",revision],check=True,cwd=ROOT)
    new=read(dest/"queue.json")
    for key in ["project","fingerprint","wordAlignmentSha256","bodyFrames","audioDirectory","editDirectory"]:
        assert new[key]==source[key],key
    assert len(new["cuts"])==len(source["cuts"]) and len(new["jobs"])==len(source["jobs"])
    motion={x["scene"]:x["sourceSha256"] for x in read(p/"production/part2-review/game-insert-motion.json")["sourceMotion"]}
    assets={x["id"]:x for x in read(p/"planning/footage-audit.json")["sources"]}
    for before,after in zip(source["cuts"],new["cuts"]):
        expected=dict(before)
        if "file" in before:expected["file"]=str(dest/Path(before["file"]).relative_to(src))
        else:assert sha(ROOT/assets[before["sourceId"]]["file"])==motion[before["scene"]]
        assert after==expected,(before["scene"],after)
    saved=[]
    for old_path,new_path in zip(source["jobs"],new["jobs"]):
        old=read(Path(old_path));job=read(Path(new_path))
        for key in ["sceneId","id","frames","expectedFingerprint"]:assert old[key]==job[key],key
        shot=sha(Path(old["shotFile"]));assert shot==sha(Path(job["shotFile"]))
        earlier=Path(old["output"]);target=Path(job["output"])
        meta=read(earlier/"encoded-structure.json")
        assert meta["fps"]=="60/1" and meta["size"]==[1920,1080] and meta["frames"]==job["frames"]
        target.mkdir(parents=True,exist_ok=False)
        for name in ["unity.mp4","capture-success.json"]:os.link(earlier/name,target/name)
        saved.append(dict(scene=job["sceneId"],frames=job["frames"],videoSha256=sha(target/"unity.mp4"),shotSha256=shot))
    planfile=p/"planning/part2-picture-plan.json";plan=read(planfile)
    additions=plan.setdefault("additionalTeachingDiagrams",{})
    fullfile=p/"planning/production-plan.json";full=read(fullfile)
    for scene,purpose in purposes.items():
        additions[scene]=dict(purpose=purpose,figure="Narration-timed diagram over the existing Unity capture")
        full["learningSteps"][int(scene)]["screenIntent"]=purpose
    save(fullfile,full)
    save(p/"production/part2-review/final-picture-correction.json",dict(episode=episode,sourceRevision=src.name,
         renderRevision=revision,sourceMasterSha256=qa["files"]["captioned"]["sha256"],correctedScenes=sorted(purposes),
         nativeFrames=saved,visualFindings=finding,unchangedVoiceAndCutTimeline=True,
         reuseIdenticalSegments=True,completeCorrectedMasterReviewed=False))
    plan["renderRevision"]=revision;save(planfile,plan)
    print(episode,len(saved),"unchanged native shots verified")

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("episode",choices=["M24"]);ap.add_argument("--revision",required=True)
    args=ap.parse_args()
    from velocity_figures import PURPOSES
    prepare(args.episode,args.revision,PURPOSES,
            "The encoded unit diagrams lacked labels and the announced sine versus Taylor comparison showed only a single function and its derivative. Use common ruler endpoints, measured unit transitions and two calculated curves.")
