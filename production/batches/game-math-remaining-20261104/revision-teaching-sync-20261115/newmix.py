"""Recognize the actual new game/voice mix in the existing offline Qwen environment.

The voice itself is unchanged. Recheck the final encoded sound and local levels
where a native game bed was added; never call recognition human listening.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse
import difflib
import importlib.util
import json
import os
import subprocess
import uuid

from inventory import ROOT,HERE,read,save,sha

FF=Path("C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe")
CREATE=getattr(subprocess,"CREATE_NO_WINDOW",0)
REVISION="teaching-sync-v2"


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result


def run(episode):
    from render_revision import authorized
    authorized(episode)
    project=ROOT/"projects"/episode["slug"];folder=project/"production/local"/REVISION
    encoded=read(folder/"encoded.json");master=Path(encoded["files"]["captioned"]["path"])
    assert sha(master)==encoded["files"]["captioned"]["sha256"]
    assert read(folder/"technical-qa.json")["status"]=="pass"
    if not encoded["addedGameAudioIntervals"]:
        assert read(folder/"technical-qa.json")["unchangedAudioBitstream"]
        save(folder/"mix-review.json",dict(status="reused",method="Same full compressed audio stream and origin as the delivered baseline",actualHumanListening=False))
        return
    report_path=folder/"mix-evidence.json"
    if report_path.exists():
        existing=read(report_path);assert existing["captionedSha256"]==sha(master)
        print(episode["id"],"existing recognition retained for direct review");return
    G=module("new_math_mix_guard",ROOT/"projects/game-math-shading-lights/production/run-capture-queue.py")
    reason=G.idle_reason()
    if reason:raise RuntimeError(reason)
    owned=str(uuid.uuid4())
    with G.LEASE.open("x",encoding="utf8") as stream:json.dump(dict(id=owned,owner=episode["slug"]+"-new-mix-recognition",pid=os.getpid(),createdAt=G.now()),stream)
    try:
        previous=project/"production/local"/episode["baselineRevision"]
        queue=read(previous/"queue.json");audio=Path(queue["audioDirectory"]);timing=read(audio/"narration.timing.json")
        prior=read(previous/"final-mix-review/report.json")
        prior_text={(r["entry"]["scene_id"],r["entry"]["paragraph"]):r.get("text","") for r in prior["paragraphs"]}
        work=folder/"mix-recognition";work.mkdir(exist_ok=True)
        # These are regenerable checking samples, separate from every approved
        # source WAV. Keep them on C while the D output volume is nearly full.
        scratch=Path(os.environ["LOCALAPPDATA"])/"YamyamCoding/VideoEditingScratch/math-teaching-sync-v2"/episode["slug"]
        scratch.mkdir(parents=True,exist_ok=True);pcm=scratch/"actual-final-body-mono.wav"
        identity=scratch/"identity.json"
        if pcm.exists():assert read(identity)["masterSha256"]==sha(master)
        else:
            subprocess.run([str(FF),"-v","error","-nostdin","-n","-threads","2","-i",str(master),"-ss","2","-t",str(timing["duration_seconds"]),
                "-vn","-ar","48000","-ac","1","-c:a","pcm_f32le",str(pcm)],check=True,creationflags=CREATE)
            save(identity,dict(masterSha256=sha(master),file=str(pcm),sourceMaster=str(master)))
        os.environ.update(OMP_NUM_THREADS="2",MKL_NUM_THREADS="2",OPENBLAS_NUM_THREADS="2",NUMEXPR_NUM_THREADS="2",HF_HUB_OFFLINE="1",TRANSFORMERS_OFFLINE="1")
        import numpy as np
        import soundfile as sf
        normalizer=module("existing_math_speech_aliases",ROOT/"projects/game-math-shading-lights/production/align-captions-and-cues.py")
        recognizer=module("existing_offline_math_recognizer",HERE.parent/"review-source-voice.py")
        pipe=recognizer.load_recognizer("cuda")
        state=dict(pid=os.getpid(),status="recognizing-actual-final-mix",completed=0,total=len(timing["entries"]),humanListening=False)
        save(work/"worker.json",state);results=[]
        with sf.SoundFile(pcm) as final,sf.SoundFile(previous/"composite/narration-normalized.wav") as reference:
            assert final.samplerate==reference.samplerate==48000
            for e in timing["entries"]:
                target=work/(e["scene_id"]+"-"+str(e["paragraph"])+".json")
                if target.exists():
                    result=read(target);assert result["masterSha256"]==encoded["files"]["captioned"]["sha256"]
                    results.append(result);continue
                start=round(e["start"]*48000);length=round(e["end"]*48000)-start
                final.seek(start);x=final.read(length,dtype="float32")
                reference.seek(start);ref=reference.read(length,dtype="float32")
                if ref.ndim==2:ref=ref.sum(axis=1)*(2**-.5)
                observed=recognizer.recognize(pipe,x,48000)
                expected=normalizer.normalized(e["text"]);got=normalizer.normalized(observed["text"])
                match=difflib.SequenceMatcher(None,expected,got,autojunk=False)
                before=normalizer.normalized(prior_text.get((e["scene_id"],e["paragraph"]),""))
                windows=[]
                for first in range(0,min(len(x),len(ref))-4800,4800):
                    r=ref[first:first+4800].astype(np.float64);y=x[first:first+4800].astype(np.float64)
                    power=float(np.mean(r*r))
                    if power<10**(-35/10):continue
                    gain=float(np.sum(y*r)/(np.sum(r*r)+1e-12))
                    windows.append(dict(time=2+e["start"]+first/48000,gainDb=20*math_log10(max(abs(gain),1e-9))))
                result=dict(scene=e["scene_id"],paragraph=e["paragraph"],start=2+e["start"],end=2+e["end"],
                    expected=e["text"],recognized=observed["text"],priorRecognized=prior_text.get((e["scene_id"],e["paragraph"])),
                    normalizedRecognitionUnchanged=got==before,coverage=sum(n for _,_,n in match.get_matching_blocks())/max(1,len(expected)),
                    localGainRange=[min(w["gainDb"] for w in windows),max(w["gainDb"] for w in windows)] if windows else None,
                    suspectLevelWindows=[w for w in windows if abs(w["gainDb"])>3],
                    masterSha256=encoded["files"]["captioned"]["sha256"],actualHumanListening=False)
                save(target,result);results.append(result)
                state.update(completed=len(results),last=e["scene_id"]);save(work/"worker.json",state)
                print(episode["id"],len(results),"/",len(timing["entries"]),e["scene_id"],round(result["coverage"],3),flush=True)
        report=dict(status="evidence-ready-direct-comparison-pending",episode=episode["id"],captionedSha256=encoded["files"]["captioned"]["sha256"],
            paragraphs=results,changedRecognition=[r["scene"] for r in results if not r["normalizedRecognitionUnchanged"]],
            levelFlagScenes=[r["scene"] for r in results if r["suspectLevelWindows"]],
            actualHumanListening=False,expectedTextPromptUsed=False,wholeFinalMixRecognized=True,newTts=False)
        save(report_path,report);state["status"]="evidence-ready-direct-comparison-pending";save(work/"worker.json",state)
    finally:G.release_lease(owned)


def math_log10(value):
    import math
    return math.log10(value)


if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("episodes",nargs="+");args=ap.parse_args()
    episodes={e["id"]:e for e in read(HERE/"inventory.json")["episodes"]}
    for eid in args.episodes:run(episodes[eid])
