"""Collect final native-motion, playback, ASR and subtitle evidence for one actual master."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, os, re, subprocess
from urllib.request import Request,urlopen
import numpy as np
from edition import ROOT,BATCH,read,save,sha

def inspect(episode):
    row=next(r for r in read(BATCH/"batch.json")["items"][2:] if r["id"]==episode)
    p=ROOT/"projects"/row["slug"];work=p/"production/local/render-v2"
    queue=read(work/"queue.json"); qa=read(work/"final-qa/report.json"); mix=read(work/"final-mix-review/report.json")
    master=qa["files"]["captioned"];cap=Path(master["path"]); dest=cap.parent;digest=master["sha256"]
    assert digest==sha(cap)==mix["masterSha256"] and queue["project"]==p.name
    alignment=read(Path(queue["wordAlignment"]));assert not alignment["flags"]
    assert len(mix["paragraphs"])==len(alignment["scenes"]) and len(qa["samples"])==3*len(alignment["scenes"])
    assert all(x["fullDecodeExitCode"]==0 for x in qa["files"].values())
    assert qa["originalPcmUnchanged"] and qa["truePeakWithinLimit"]
    for lang in ("ko","en"):assert not qa[lang+"Subtitles"]["issues"],(episode,lang,qa[lang+"Subtitles"]["issues"])
    url="http://127.0.0.1:9347/output/"+dest.name+"/"
    with urlopen(Request(url+cap.name,headers={"Range":"bytes=0-63"}),timeout=6) as response:
        assert response.status==206 and len(response.read())==64
    ff=read(Path(queue["jobs"][0]))["ffmpeg"]
    motion=[]
    for cut in (c for c in queue["cuts"] if c["kind"]=="actual-gameplay"):
        sec=(cut["globalStartFrame"]+120)/60; duration=cut["frames"]/60
        raw=subprocess.check_output([ff,"-loglevel","error","-nostdin","-threads","2","-ss",str(sec),"-i",cap,
             "-t",str(duration),"-an","-vf","crop=1440:740:240:135,fps=4,scale=96:48,format=gray","-threads","1","-f","rawvideo","pipe:1"])
        px=np.frombuffer(raw,np.uint8).reshape(-1,48,96).astype(np.int16)
        diff=np.abs(np.diff(px,axis=0)).mean(axis=(1,2))
        motion.append(dict(scene=cut["scene"],source=cut["sourceId"],sourceWindow=[cut["sourceIn"],cut["sourceOut"]],
                           seconds=duration,nativeSpeed=cut["nativeSpeed"],intervals=len(diff),
                           movingIntervals=int((diff>.25).sum()),medianLumaDifference=round(float(np.median(diff)),3)))
    assert len({c["source"] for c in motion})>=3
    anchors=[w for w in mix["paragraphs"] if w["coverage"]<.94 or w["suspectLevelWindows"]]
    ffplay=str(Path(ff).with_name("ffplay.exe"))
    # Use an isolated native player for the actual local HTTP file at two different
    # positions. The extra evidence doesn't imply a person listened to the full lecture.
    env=dict(os.environ,SDL_VIDEODRIVER="dummy",SDL_AUDIODRIVER="dummy")
    playback=[]
    for i,sec in enumerate([2.2,round((queue["bodyFrames"]/60)*.6+2,2)]):
        log=work/"final-qa"/f"part2-play-{i}.log"
        with log.open("wb") as f: res=subprocess.run([ffplay,"-hide_banner","-loglevel","info","-autoexit","-ss",str(sec),
           "-t","1.4","-vf","showinfo","-x","375","-y","211","-threads","2",url+cap.name],env=env,stdout=f,stderr=f,timeout=90,creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
        stats=re.findall(r"pts_time:([0-9.]+)",log.read_text("utf8",errors="replace"))
        assert res.returncode==0 and len(stats)>=30
        playback.append(dict(requested=sec,decodedFrames=len(stats),lastPTS=float(stats[-1]),log=str(log)))
    receipt=dict(episode=episode,at=datetime.now(timezone.utc).isoformat(),masterSha256=digest,files=qa["files"],
        subtitles={lang:qa[lang+"Subtitles"] for lang in ("ko","en")},frames=qa["expectedFrames"],
        duration=qa["expectedFrames"]/60,actualGameCuts=motion,playerTests=playback,
        integratedLUFS=qa["actualMixLoudness"]["input_i"],truePeak=qa["actualMixLoudness"]["input_tp"],
        fullTranscriptReviewedByMachine=len(mix["paragraphs"]),actualSamples=[s["path"] for s in qa["samples"]],
        speechChecks=[dict(scene=x["entry"]["scene_id"],coverage=x["coverage"],windows=x["suspectLevelWindows"]) for x in anchors],
        localReviewUrl=url+"index.html",continuousHumanListening=False,status="final-picture-and-content-inspection-pending")
    save(work/"part2-delivery-evidence.json",receipt)
    print(episode,len(motion),"game examples;",len(anchors),"speech spots to inspect")
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("episode");inspect(ap.parse_args().episode)
