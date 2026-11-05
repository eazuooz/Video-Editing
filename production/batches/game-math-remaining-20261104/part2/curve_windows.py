"""Give each curve lesson a distinct observed game operation and attached guide."""
import argparse
import subprocess
from pathlib import Path
from edition import ROOT, BATCH, read, save, sha

# Centres were inspected in 400×225 native, aspect-preserving frames at 0.25s intervals.
STARS = {
    "M32": dict(start=188.25, end=195.75, result=194.0, mark=189.5,
        centers=[(192,126),(193,125),(193,125),(193,125),(193,125),(193,125),
                 (193,125),(192,127),(195,125),(194,132),(193,144)],
        radius=25, label="별에서 출발하는 지점", proof="sling.jpg",
        observation="A Luma turns into a yellow Sling Star. Mario enters its center, launches up toward the underside of the next body, and settles onto its surface.",
        role="The launch direction is visible before our Bézier endpoint-tangent construction."),
    "M33": dict(start=137.5, end=144.5, result=142.8, mark=140.25,
        centers=[(190,146),(191,111),(190,106),(191,115),(193,116),(195,118),
                 (196,121),(198,119),(198,111),(198,84),(199,88),(202,98)],
        radius=16, label="다음 행성으로 향하는 마리오", proof="launch.jpg",
        observation="Mario approaches the orange Launch Star on the rocky planet, departs along a blue arc, and lands on a separate golden planet.",
        role="Observe the continuous flight over successive positions before deriving tangents from knots.")
}

RAILS = {
    "M32": dict(sid="022", start=222.0,end=231.5,result=230.5,mark=224.5,
        centers=[(200,112)]*5,radius=20,label="다음 선로 조각의 연결점",proof="anchor-222.jpg",
        observation="A cyan rail hologram is aimed against the existing rail. Placing it produces orange construction effects, then the completed piece extends through the water.",
        role="The player works on one selected rail section; the next Unity scene constructs an independent subcurve.",
        old=[270,282]),
    "M33": dict(sid="042",start=804.25,end=816.25,result=811.5,mark=806,
        centers=[(237,164),(242,164),(242,155),(246,161),(252,158)],
        radius=28,label="굽은 길을 따르는 기관차",proof="anchor-806.jpg",
        observation="Two connected train cars emerge from a curve, straighten beside the rocks, then follow the next rise. The outline clears before the foreground trunk occludes the locomotive.",
        role="Show the changing heading of a train on a completed, multi-section railway at the end of the lesson.",
        old=[702,720])
}

def bind(ep,kind):
    spec=(STARS if kind=="galaxy" else RAILS)[ep]
    sid=spec.get("sid","017");row=next(r for r in read(BATCH/"batch.json")["items"] if r["id"]==ep)
    p=ROOT/"projects"/row["slug"];path=p/"planning/scene-bindings.json"
    binding=read(path);g=next(s for s in binding["scenes"] if s["id"]==sid)["actualGamePart"]
    folder=p/("production/local/part2-"+kind+"-window");folder.mkdir(parents=True,exist_ok=True)
    source=ROOT/g["sourceFile"];assert source.is_file() and g["sourceSha256"]==sha(source)
    board=(ROOT/"projects/game-math-splines-continuity/production/local/part2-galaxy-review" if kind=="galaxy" else
           ROOT/"projects/game-math-bezier-subdivision/production/local/part2-rail-distinct")/spec["proof"]
    assert board.is_file()
    start,end=spec["start"],spec["end"]; identity=ep+"-"+sid+"-"+kind
    command=["ffmpeg","-loglevel","error","-nostdin","-threads","2","-ss",str(start),"-i",str(source),
             "-t",str(end-start),"-map","0:v:0","-map","0:a:0","-f","null","-"]
    result=subprocess.run(command,capture_output=True,check=True)
    decode=folder/"native-decode.json"
    save(decode,[dict(clip=identity,sourceSha256=g["sourceSha256"],sourceIn=start,sourceOut=end,
                     exitCode=result.returncode,errorOutput=result.stderr.decode(errors="replace"))])
    tf=p/("planning/part2-"+kind+"-guide.json");frames=[]
    for i,(x,y) in enumerate(spec["centers"]):
        r=spec["radius"]
        frames.append(dict(time=spec["mark"]+(.25 if kind=="galaxy" else .5)*i,bbox=[round(v*4.8,2) for v in (x-r,y-r,2*r,2*r)],visible=True))
    track=dict(id=identity,sourceId=g["sourceId"],sourceSha256=g["sourceSha256"],sourceFile=g["sourceFile"],
               start=frames[0]["time"],end=frames[-1]["time"],label=spec["label"],keyframes=frames,
               shape="hollow-ellipse",fps=60 if kind=="galaxy" else 24000/1001,coordinates="1920x1080 native decoded source",
               method="Manually anchored editorial guide at native sample positions; clear before occlusions or cuts.",
               uses=[dict(episode=ep,scene=sid,project=p.name)],failedSamples=0,
               visualQa=dict(status="temporal-samples-reviewed-final-encoded-pending",scope="Actual native target positions at sampled times; final master pending.",
                   evidence=[str(board.relative_to(ROOT).as_posix())],sourceBoardSha256=sha(board)))
    save(tf,track)
    labelsfile=p/"planning/game-annotation-tracks.json";labels=read(labelsfile)
    labels["windows"]=[w for w in labels["windows"] if not (w["sourceId"]==g["sourceId"] and sid in w["scenes"])]
    labels["windows"].append(dict(**{k:track[k] for k in ("id","sourceId","sourceSha256","start","end","label","shape","fps","coordinates","method","visualQa","failedSamples")},
                 scenes=[sid],trackFile=tf.relative_to(ROOT).as_posix(),sourceTrackSha256=sha(tf)))
    save(labelsfile,labels)
    g.update(sourceIn=start,sourceOut=end,fullOriginalAudioIn=start,fullOriginalAudioOut=end,
             minimumObservedResultOut=spec["result"],observed=spec["observation"],role=spec["role"],
             insertVersion="distinct-star" if kind=="galaxy" else "distinct-rail",reviewEvidence=[board.relative_to(ROOT).as_posix()],
             nativeDecodeEvidence=dict(file=decode.relative_to(ROOT).as_posix(),clip=identity,exitCode=0),
             annotationPlan={"plan":spec["label"]+" · 화면의 실제 대상에 연결하고 컷 전에 지운다."})
    save(path,binding)
    planpath=p/"planning/production-plan.json";plan=read(planpath)
    plan["nativeGameCueBindings"]=[g if s["sceneId"]==sid else s for s in plan["nativeGameCueBindings"]]
    plan["sceneBindingsSha256"]=sha(path);save(planpath,plan)
    ppath=p/"planning/part2-picture-plan.json";picture=read(ppath);picture["sourceBindingsSha256"]=sha(path);save(ppath,picture)
    save(p/("production/part2-review/"+kind+"-window.json"),dict(episode=ep,scope="Visual-only alternate independent recording window",sourceSha256=g["sourceSha256"],
         previousWindow=spec.get("old",[93,104]),selectedWindow=[start,end],beforeActionResult=spec["observation"],role=spec["role"],
         nativeAudio="Same muxed original audio, shifted to the exact selected window.",guideSha256=sha(tf),nativeDecodeSha256=sha(decode),userReview=False))

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("kind",choices=["galaxy","rail"]);ap.add_argument("episodes",nargs="+",choices=STARS)
    a=ap.parse_args()
    for ep in a.episodes:bind(ep,a.kind)
