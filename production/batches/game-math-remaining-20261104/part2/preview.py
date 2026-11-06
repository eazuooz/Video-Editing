"""Create a short source-matched sample queue for a revised Unity lecture."""
from edition import BATCH, ROOT, read, save, retain_circle_speed
from pathlib import Path
import argparse,re

def build(episode,sample_ids,folder_name=None):
    ep=next(x for x in read(BATCH/"batch.json")["items"] if x["id"]==episode)
    project=ROOT/"projects"/ep["slug"]
    stage=project/"production/unity-staging"
    marker=read(stage/"sandbox-preparation.json")
    source=sorted(stage.glob("local-preflight-v*/queue.json"),key=lambda p:int(p.parent.name.split("-v")[-1]))[-1]
    base=read(source)
    if not folder_name:
        picture=project/"planning/part2-picture-plan.json"
        folder_name=Path(read(picture)["preflightQueue"]).parent.name if picture.is_file() else "local-preflight-part2-v1"
    assert re.fullmatch(r"local-preflight-part2-v[1-9]\d*",folder_name)
    folder=stage/folder_name
    if (folder/"queue.json").exists():
        assert read(folder/"queue.json")["fingerprint"]==marker["fingerprint"]
        return
    template=read(Path(base["jobs"][0]))
    scenes={s["id"]:s for s in read(project/"planning/scene-bindings.json")["scenes"]}
    jobs=[]
    for sid in sample_ids:
        scene=scenes[sid]; shot=dict(scene["shot"],durationSeconds=8)
        picture=project/"planning/part2-picture-plan.json"
        current=read(picture) if picture.is_file() else {}
        if sid in current.get("fixedSpeedRadiusComparisons",{}).get(current.get("renderRevision"),[]):
            retain_circle_speed(shot)
        for field in scene.get("clockFields",["phaseSeconds","phasePositions"]):
            shot[field]=[]
        shotpath=folder/(sid+".shot.json"); save(shotpath,shot)
        job=dict(template,id=episode.lower()+"-part2-"+sid,output=str(folder/sid),shotFile=str(shotpath),
                 expectedFingerprint=marker["fingerprint"],sampleFrames=[78,247,430],frames=480)
        path=folder/(sid+".job.json"); save(path,job);jobs.append(str(path))
    save(folder/"queue.json",dict(base,sandbox=marker["sandbox"],fingerprint=marker["fingerprint"],
         jobs=jobs,scope="Revised purpose-first picture and attached symbols",actualSpeech=False))
    print(folder,len(jobs))
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("episode");ap.add_argument("scenes",nargs="+");ap.add_argument("--folder")
    a=ap.parse_args();build(a.episode,a.scenes,a.folder)
