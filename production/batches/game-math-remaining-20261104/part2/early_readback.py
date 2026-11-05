"""Recognize settled takes on two CPU cores, only during this lesson's own GPU recording.

The full speech pass verifies the hash against actual assembled PCM before reusing
any word timings. A failed early pass never blocks recording or the normal review.
"""
import argparse
import hashlib
import json
import os
import runpy
import sys
import time
from pathlib import Path
from edition import ROOT,BATCH,read,sha

os.environ.update(CUDA_VISIBLE_DEVICES="",OMP_NUM_THREADS="2",MKL_NUM_THREADS="2",
                  OPENBLAS_NUM_THREADS="2",NUMEXPR_NUM_THREADS="2",HF_HUB_OFFLINE="1",TRANSFORMERS_OFFLINE="1")
import psutil
import numpy as np
import soundfile as sf
sys.path.insert(0,str(BATCH))
sys.path.insert(0,str(ROOT/"qwen3-tts"))
from paragraph_level import level_paragraph
import render_narration
render_narration.np=np
asr=runpy.run_path(str(BATCH/"review-source-voice.py"))

def active(project,token):
    lease=ROOT/"shared/output/GPU_HANDOFF.json"
    if not lease.is_file():return False
    current=read(lease)
    return current.get("project")==project and current.get("token")==token

def review(slug,token):
    project=ROOT/"projects"/slug
    assert slug in read(ROOT/"shared/publishing/video-production-control.json")["explicitMathRemainingBatch20261104"]["projectSlugs"]
    edition=read(project/"planning/part2-delivery-edition.json");manifest=read(ROOT/edition["manifest"])
    target=project/"production/local"/edition["audioRevision"]
    output=target/"review/early-pcm";output.mkdir(parents=True,exist_ok=True)
    original=read(project/"script/narration.ko.json")["scenes"]
    retained={t["scene"] for t in edition["copiedTakes"]}
    lines=[(f"{s['id']}-{j:02}",line) for s in original if s['id'] not in retained for j,line in enumerate(s['lines'],1)]
    process=psutil.Process();process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    pipe=None
    while active(slug,token):
        if not read(ROOT/"shared/publishing/video-production-control.json")["explicitMathRemainingBatch20261104"]["productionAllowedNow"]:return
        if psutil.virtual_memory().available<8*1024**3:
            time.sleep(8);continue
        unfinished=[]
        for key,line in lines:
            raw=target/"chunks"/(key+"-scene.wav");cache=output/(key+".json")
            if cache.is_file():continue
            unfinished.append(key)
            if not raw.is_file() or time.time()-raw.stat().st_mtime<4:continue
            if pipe is None:
                import torch
                assert not torch.cuda.is_initialized() and torch.cuda.device_count()==0
                pipe=asr["load_recognizer"]("cpu")
            digest=sha(raw);x,sr=sf.read(raw,dtype="float32");assert x.ndim==1
            samples,_,_=level_paragraph(x,sr,manifest["tts"]["lineLevelEqualization"],render_narration._apply_edge_fades)
            result=asr["recognize"](pipe,samples,sr)
            if sha(raw)!=digest:continue
            record=dict(scene=key,model=str(asr["MODEL"]),sourceText=line,sampleRate=sr,rawSha256=digest,
                samples=len(samples),pcmSha256=hashlib.sha256(samples.tobytes()).hexdigest(),
                recognized=result,method="Two-core local CPU ASR of gain- and fade-matched PCM; verify exact assembled samples before adopting.",humanListening=False)
            temp=cache.with_suffix(".tmp");temp.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n","utf8");os.replace(temp,cache)
            print(slug,key,result["text"],flush=True)
            break
        else:
            if not unfinished:return
            time.sleep(5)

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--project",required=True);ap.add_argument("--lease-token",required=True)
    args=ap.parse_args()
    import msvcrt
    edition=read(ROOT/"projects"/args.project/"planning/part2-delivery-edition.json")
    lockpath=ROOT/"projects"/args.project/"production/local"/edition["audioRevision"]/"early-readback.lock"
    with lockpath.open("a+b") as lock:
        if not lock.tell():lock.write(b"1");lock.flush()
        lock.seek(0)
        try:msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
        except OSError:sys.exit(0)
        review(args.project,args.lease_token)
