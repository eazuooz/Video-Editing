"""Full decode/PTS evidence and changed-picture review sheets, never human approval."""
import argparse
from datetime import datetime,timezone
import io
import json
import math
import os
from pathlib import Path
import re
import subprocess
import uuid

from PIL import Image,ImageDraw

from inventory import ROOT,HERE,read,save,sha
from render_revision import FF,CREATE,REVISION,guard,authorized,check_stream,additions


def audio_hash(file):
    return subprocess.check_output([str(FF),"-v","error","-nostdin","-threads","2","-i",str(file),
        "-map","0:a:0","-c:a","copy","-f","hash","-hash","sha256","-"],creationflags=CREATE).decode().strip()


def decode(file,frames,folder,kind):
    args=[str(FF),"-hide_banner","-nostdin","-threads","2","-err_detect","explode","-i",str(file),
        "-map","0:v:0","-map","0:a:0","-vf","showinfo=checksum=0","-fps_mode","passthrough",
        "-f","null","-"]
    process=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,
        encoding="utf8",errors="replace",creationflags=CREATE)
    count=0;first=last=None;low=high=None;bad=[];messages=[]
    timebase=None
    pattern=re.compile(r"\bn:\s*(\d+)\s+pts:\s*(-?\d+)")
    for line in process.stdout:
        match=pattern.search(line) if "showinfo" in line else None
        if match:
            n,pts=map(int,match.groups())
            if n!=count:bad.append(dict(frame=count,observedIndex=n))
            if first is None:first=pts
            if last is not None:
                delta=pts-last;low=delta if low is None else min(low,delta);high=delta if high is None else max(high,delta)
                if delta!=1500:bad.append(dict(frame=n,ptsDelta=delta))
            last=pts;count+=1
        elif "config in time_base:" in line:
            timebase=line.strip()
        elif any(s in line.lower() for s in ("error","invalid","corrupt","non-monoton")):
            messages.append(line.strip())
    code=process.wait()
    report=dict(file=str(file),returncode=code,decodedFrames=count,expectedFrames=frames,
        firstPts=first,lastPts=last,minPtsDelta=low,maxPtsDelta=high,timebase=timebase,
        invalidPts=bad[:30],errors=messages[:30],fullVideoAndAudioDecode=True)
    save(folder/("decode-"+kind+".json"),report)
    assert code==0 and count==frames and first==0 and not bad and not messages,report
    return report


def technical(episode,folder):
    record=read(folder/"encoded.json");frames=record["frames"];results={}
    for kind in ("clean","captioned"):
        file=Path(record["files"][kind]["path"])
        assert sha(file)==record["files"][kind]["sha256"]
        meta=check_stream(file,frames)
        results[kind]=dict(stream=meta,decode=decode(file,frames,folder,kind),audioHash=audio_hash(file))
    assert results["clean"]["audioHash"]==results["captioned"]["audioHash"]
    if not record["addedGameAudioIntervals"]:
        baseline=audio_hash(Path(episode["baselineOutputs"]["clean"]))
        assert baseline==results["clean"]["audioHash"],"Unchanged voice/game mix must remain the same compressed audio stream"
    else:baseline=None
    for lang in ("ko","en"):
        assert sha(Path(record["files"][lang]["path"]))==sha(Path(episode["baselineOutputs"][lang]))
    report=dict(status="pass",checkedAt=datetime.now(timezone.utc).isoformat(),episode=episode["id"],
        files=record["files"],media=results,pairedAudioIdentical=True,
        unchangedAudioBitstream=baseline is not None,narrationTempo=1,
        subtitleTimingsPreserved=True,addedBackgroundMusic=False,
        speechMixReview="Reused unchanged baseline audio evidence" if baseline else "New native-game beds: local speech-level and recognition comparison pending",
        actualHumanListening=False,actualHumanViewing=False,finalReviewReady=False)
    save(folder/"technical-qa.json",report)
    return report


def frame(file,t):
    data=subprocess.check_output([str(FF),"-v","error","-nostdin","-threads","1","-ss",str(t),"-i",str(file),
        "-frames:v","1","-threads","1","-c:v","png","-f","image2pipe","-"],creationflags=CREATE)
    return Image.open(io.BytesIO(data)).convert("RGB")


def pictures(episode,folder):
    preparation=read(folder/"preparation.json");encoded=read(folder/"encoded.json")
    file=Path(encoded["files"]["captioned"]["path"]);out=folder/"picture-review";out.mkdir(exist_ok=True)
    points=[]
    for operation in preparation["workings"]:
        a,z=operation["start"],operation["end"]
        if z-a<.02:continue
        points.append(dict(scene=operation["scene"],time=min(z-.01,a+min(.5,(z-a)*.35)),
            role="workings",cue=operation["anchor"],dwell=z-a,operation=operation["operation"]))
    for game in additions(episode):
        moments=sorted(set([.15*game["duration"],.5*game["duration"],.85*game["duration"]]+
            [i+.25 for i in range(math.ceil(game["duration"])) if i+.25<game["duration"]]))
        for t in moments:points.append(dict(scene=game["scene"],time=game["start"]+t,
            role="paired-game",cue=game["label"],sourceTime=game["sourceIn"]+t))
    # All changed cut joins are represented. Unchanged pictures/audio retain
    # their previous edition's review evidence, not a fabricated new viewing.
    byscene={s["scene"]:s for s in episode["scenes"]}
    changed={p["scene"] for p in points}
    for sid in changed:
        s=byscene[sid]
        for t in (max(0,s["start"]-.06),s["end"]-.06):points.append(dict(scene=sid,time=t,role="join",cue="changed scene boundary"))
    points.sort(key=lambda r:(r["time"],r["role"]))
    seen=set();results=[];boards=[]
    for point in points:
        key=round(point["time"]*60)
        if key in seen:continue
        seen.add(key)
        picture=out/f"frame-{key:07}.png"
        if not picture.exists():frame(file,key/60).save(picture)
        results.append(dict(**point,frame=key,png=str(picture),sha256=sha(picture)))
    for start in range(0,len(results),12):
        selected=results[start:start+12];image=Image.new("RGB",(375*3,240*math.ceil(len(selected)/3)),"#080808");draw=ImageDraw.Draw(image)
        for i,result in enumerate(selected):
            x=i%3*375;y=i//3*240
            with Image.open(result["png"]) as im:image.paste(im.resize((375,211),Image.Resampling.LANCZOS),(x,y))
            draw.text((x+5,y+216),f'{episode["id"]}/{result["scene"]} {result["time"]:.2f}s {result["role"]}',fill="white")
        path=out/f"mobile-{start//12+1:02}.jpg";image.save(path,quality=95);boards.append(str(path))
    report=dict(status="images-ready-not-visually-approved",episode=episode["id"],
        captionedSha256=encoded["files"]["captioned"]["sha256"],frames=results,mobileBoards=boards,
        changedScenes=sorted(changed),imageCount=len(results),actualVisualReview=False,actualAudioListening=False)
    save(folder/"picture-review.json",report)
    return report


def run(episode,make_pictures):
    authorized(episode);folder=ROOT/"projects"/episode["slug"] / ("production/local/"+REVISION)
    G=guard();reason=G.idle_reason()
    if reason:raise RuntimeError(reason)
    owned=str(uuid.uuid4())
    with G.LEASE.open("x",encoding="utf8") as stream:json.dump(dict(id=owned,owner=episode["slug"]+"-teaching-sync-QA",pid=os.getpid(),createdAt=G.now()),stream)
    try:
        if not (folder/"technical-qa.json").exists():technical(episode,folder)
        else:
            existing=read(folder/"technical-qa.json");assert existing["status"]=="pass"
            for f in existing["files"].values():assert sha(Path(f["path"]))==f["sha256"]
        if make_pictures:pictures(episode,folder)
    except BaseException as exc:
        save(folder/"qa-failure.json",dict(status="fail",error=repr(exc),finalReviewReady=False));raise
    finally:G.release_lease(owned)
    print(episode["id"],"technical checks passed; visual/audio review remains separate",flush=True)


if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("episodes",nargs="+");ap.add_argument("--pictures",action="store_true");args=ap.parse_args()
    inventory={e["id"]:e for e in read(HERE/"inventory.json")["episodes"]}
    for eid in args.episodes:run(inventory[eid],args.pictures)
