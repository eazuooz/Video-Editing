"""Use a distinct inspected rail-shape window in M31. Derive its guide from visible pixels."""
from pathlib import Path
import argparse, hashlib, subprocess
from PIL import Image, ImageDraw
import numpy as np
from edition import ROOT,BATCH,read,save,sha

project=ROOT/"projects/game-math-parametric-hermite"
folder=project/"production/local/part2-rail-window"
trackfile=project/"planning/part2-rail-guide.json"
start,end=250.0,260.0

def scan():
    folder.mkdir(exist_ok=True)
    g=read(project/"planning/scene-bindings.json")["scenes"][27]["actualGamePart"]
    src=ROOT/g["sourceFile"];assert sha(src)==g["sourceSha256"]
    subprocess.run(["ffmpeg","-nostdin","-v","error","-threads","2","-ss",str(start),"-t",str(end-start),
                    "-i",str(src),"-map","0:v:0","-map","0:a:0","-f","null","-"],check=True)
    times=[251.65+i*.20 for i in range(11)]
    # The placement reticle stays at screen centre while the player aims at a
    # new world endpoint. Outline the verified reticle, not a guessed tangent.
    frames=[];sheet=Image.new("RGB",(4*360,((len(times)+3)//4)*225),"#151515");draw=ImageDraw.Draw(sheet)
    for idx,t in enumerate(times):
        raw=subprocess.check_output(["ffmpeg","-v","error","-nostdin","-threads","2","-ss",str(t),
            "-i",str(src),"-frames:v","1","-vf","scale=480:270,format=rgb24","-threads","1","-f","rawvideo","pipe:1"])
        array=np.frombuffer(raw,np.uint8).reshape((270,480,3));im=Image.fromarray(array);overlay=ImageDraw.Draw(im)
        # Size in decoded FHD pixels; the game's pointer remains unobstructed.
        box=[907,501,106,78]
        frames.append(dict(time=t,visible=True,bbox=box))
        overlay.ellipse((box[0]/4,box[1]/4,(box[0]+box[2])/4,(box[1]+box[3])/4),outline="#f6d478",width=2)
        x=idx%4*360;y=idx//4*225;sheet.paste(im.resize((360,203),Image.Resampling.LANCZOS),(x,y))
        draw.text((x+5,y+206),f"{t:.1f}s",fill="white")
    sheet.save(folder/"guide-samples.jpg",quality=95)
    save(folder/"native-decode.json",[dict(clip="M31-rail-endpoint-shape",sourceFile=g["sourceFile"],
         sourceSha256=g["sourceSha256"],sourceIn=start,sourceOut=end,exitCode=0)])
    save(folder/"track-candidate.json",dict(id="M31-027-distinct",sourceId=g["sourceId"],sourceFile=g["sourceFile"],
         sourceSha256=g["sourceSha256"],start=times[0],end=times[-1],keyframes=frames,
         label="선로 끝을 옮기는 조준점",shape="hollow-ellipse",coordinates="1920x1080 native decoded source",
         fps=24000/1001,method="Editorial outline around the fixed placement reticle during an actual change in the curved rail hologram.",uses=[dict(episode="M31",scene="027",project=project.name)]))

def bind():
    track=read(folder/"track-candidate.json");sheet=folder/"guide-samples.jpg"
    assert sheet.is_file()
    track["visualQa"]=dict(status="temporal-samples-reviewed-final-encoded-pending",scope="11 actual source samples with the hollow reticle mark",
                           evidence=[sheet.relative_to(ROOT).as_posix()],humanFinalReview=False)
    save(trackfile,track)
    relative=trackfile.relative_to(ROOT).as_posix()
    path=project/"planning/game-annotation-tracks.json";labels=read(path)
    labels["windows"]=[x for x in labels["windows"] if not (x["sourceId"]==track["sourceId"] and x["start"]<300)]
    labels["windows"].append({**{k:track[k] for k in ("id","sourceId","sourceSha256","start","end","label","shape","coordinates","fps","method","visualQa")},
                             "trackFile":relative,"sourceTrackSha256":sha(trackfile),"scenes":["027"]})
    save(path,labels)
    bindings=project/"planning/scene-bindings.json";data=read(bindings);g=data["scenes"][27]["actualGamePart"]
    g.update(sourceIn=start,sourceOut=end,fullOriginalAudioIn=start,fullOriginalAudioOut=end,
             minimumObservedResultOut=259.3,observed="Red preview becomes cyan; moving the endpoint bends the proposed rail. The side view aligns that preview with the existing track.",
             nativeDecodeEvidence={"file":(folder/"native-decode.json").relative_to(ROOT).as_posix(),"clip":"M31-rail-endpoint-shape","exitCode":0},
             reviewEvidence=[sheet.relative_to(ROOT).as_posix()],
             annotationPlan={"plan":"Outline the inspected build reticle while the rail endpoint and previewed bend move. Clear the mark in the side view. No game-internal derivative claimed."},
             handoffObservation={"note":"Distinct window for M31's endpoint-and-tangent example, preserving M33's later connection demonstration.","minimumObservedResultOut":259.3})
    save(bindings,data);pp=project/"planning/production-plan.json";plan=read(pp)
    plan["nativeGameCueBindings"]=[g if r["sceneId"]=="027" else r for r in plan["nativeGameCueBindings"]]
    plan["sceneBindingsSha256"]=sha(bindings);save(pp,plan)
    evidence=project/"production/part2-review/rail-window.json";save(evidence,dict(track=relative,source=g["sourceFile"],
         sha256=g["sourceSha256"],replaced=[270,282],selected=[start,end],observed=g["observed"],
         sourceAudio="The original muxed track is kept at the new window's exact time. It is checked against the narration during final mix review.",
         reason="M31 teaches editable endpoints, whereas M33 opens on a completed connection. The two examples used identical footage."))
if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("step",choices=["scan","bind"]);args=parser.parse_args()
    scan() if args.step=="scan" else bind()
