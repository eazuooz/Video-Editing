"""Stage only unchanged, already word-timed scenes preceding M23's isolated retake."""
import math
from datetime import datetime,timezone
from pathlib import Path
from edition import ROOT,BATCH,read,save,sha

def prepare():
    project=ROOT/"projects/game-math-pipeline-shaders"
    auth=read(ROOT/"shared/publishing/video-production-control.json")["explicitMathRemainingBatch20261104"]
    assert auth["productionAllowedNow"] and project.name in auth["projectSlugs"]
    change=read(project/"production/part2-review/targeted-recording.json")
    edition=read(project/"planning/part2-delivery-edition.json")
    assert change["scenes"]==edition["targetedRetakes"]==["020"] and edition["audioRevision"]==change["targetRevision"]
    local=project/"production/local";old=local/change["sourceRevision"];new=local/change["targetRevision"]
    basepath=local/change["sourceRevision"].replace("audio-","edit-")/"word-aligned-timeline.json"
    old_timeline=read(basepath);inputs=read(old/"narration.timing.json")
    assert sha(old/"narration.wav")==old_timeline["narrationSha256"]
    assert sha(old/"narration.timing.json")==old_timeline["timingSha256"]
    cutoff=int(change["scenes"][0]);prefix=old_timeline["scenes"][:cutoff]
    ids=[r["id"] for r in prefix];assert ids==[f"{n:03d}" for n in range(cutoff)]
    assert not [flag for flag in old_timeline["flags"] if flag["scene"] in ids]
    bindings=read(project/"planning/scene-bindings.json")["scenes"]
    reusable={x["scene"]:x for x in edition["copiedTakes"]}
    stage=project/"production/unity-staging";picture=read(project/"planning/part2-picture-plan.json")
    preflight=read(stage/picture["preflightQueue"]);template=read(Path(preflight["jobs"][0]))
    assert read(Path(preflight["sandbox"])/"MATH_CAPTURE_SANDBOX.json")["fingerprint"]==preflight["fingerprint"]==picture["fingerprint"]
    out=local/"preserved-prefix-v1";queue=out/"queue.json"
    if queue.exists():
        assert read(queue)["sourceWordAlignmentSha256"]==sha(basepath)
        return
    jobs=[];confirmed=[]
    for row in prefix:
        sid=row["id"];raw=old/"chunks"/(sid+"-01-scene.wav");copy=new/"chunks"/raw.name
        current=bindings[int(sid)]
        assert sha(raw)==sha(copy)==reusable[sid]["sha256"]
        assert inputs["entries"][int(sid)]["text"]==current["speech"]
        clocks=set(current.get("clockFields",["phaseSeconds","phasePositions"]))|{"durationSeconds"}
        for key in set(current["shot"])|set(row["shot"]):
            if key not in clocks:assert current["shot"].get(key)==row["shot"].get(key),(sid,key)
        frames=row["endFrame"]-row["startFrame"];game=row.get("actualGamePart");gameframes=0
        if game:
            end=row.get("actualGameEndFrame");start=row.get("actualGameStartFrame",0)
            gameframes=min((frames if end is None else end)-start,math.floor((game["sourceOut"]-game["sourceIn"])*60+.0001))
        confirmed.append(dict(scene=sid,frames=frames,sourceTakeSha256=sha(raw),newTakeSha256=sha(copy)))
        if frames==gameframes:continue
        shot=out/"shots"/(sid+".json");save(shot,dict(row["shot"],durationSeconds=frames/60))
        job=dict(template,command="render",id="m23-preserved-prefix-"+sid,output=str(out/"unity"/sid),
                 frames=frames,shotFile=str(shot),sampleFrames=[0,frames//2,frames-1],speechTimingVerified=True,sceneId=sid)
        jobpath=out/"jobs"/(sid+".json");save(jobpath,job);jobs.append(str(jobpath))
    alignment=out/"measured-prefix.json"
    save(alignment,dict(scope="Only the preserved prefix; not a complete aligned lecture",scenes=prefix,flags=[],
        originalWholeTimeline=str(basepath),wholeTimelineSha256=sha(basepath),wholeTimelineFlags=old_timeline["flags"],confirmed=confirmed))
    save(queue,dict(project=project.name,episode="M23",sandbox=preflight["sandbox"],fingerprint=preflight["fingerprint"],
        unity=preflight["unity"],jobs=jobs,wordAlignment=str(alignment),wordAlignmentSha256=sha(alignment),
        sourceWordAlignmentSha256=sha(basepath),targetAudioDirectory=str(new),preservedPrefix=True,
        mayDeliver=False,scope="Intermediate Unity captures only. Final edition must independently match the complete measured shots before adoption."))
    save(project/"production/part2-review/preserved-prefix.json",dict(episode="M23",stage="prepared",
        createdAt=datetime.now(timezone.utc).isoformat(),scenes=confirmed,unityJobs=len(jobs),queueSha256=sha(queue),
        rendererFingerprint=preflight["fingerprint"],finalMaster=False))
    print(len(jobs),"eligible Unity shots before the corrected paragraph")

if __name__=="__main__":prepare()
