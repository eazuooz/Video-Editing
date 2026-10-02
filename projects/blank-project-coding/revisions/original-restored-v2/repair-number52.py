"""Restore the omitted spoken 삼 using the approved same-speaker list take."""
from pathlib import Path
import json,hashlib,datetime,shutil
import soundfile as sf,numpy as np
W=Path(__file__).resolve().parent;R=W.parents[3]
old=R/'shared/output/narration/blank-project-coding/qwen3-1.7b-balanced-v1';new=R/'shared/output/narration/blank-project-coding/original-restored-v2'
source=old/'chunks/29-scene.wav';dest=new/'chunks/52-scene.wav'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
hashfile=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=read(old/'asr/29.json');b=read(new/'asr/52.json');sourceHash=hashfile(source);priorHash=hashfile(dest)
assert a['audio_sha256']==sourceHash and b['audio_sha256']==priorHash
word=next(w for w in a['words'] if w['text'].strip()=='3,');assert word['timestamp']==[23.08,23.66]
assert b['words'][0]['text'].strip()=='4학년이'
x,sr=sf.read(source,dtype='float32');body,br=sf.read(dest,dtype='float32');assert sr==br==24000
prefix=x[round(23.08*sr):round(23.66*sr)].copy();n=round(.005*sr);prefix[:n]*=np.linspace(0,1,n);prefix[-n:]*=np.linspace(1,0,n)
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');shutil.copy2(dest,dest.with_name(f'52-scene-previous-before-number-repair-{stamp}.wav'))
pcm=np.concatenate([prefix,np.zeros(round(.06*sr),dtype=np.float32),body]);sf.write(dest,pcm,sr,subtype='PCM_16')
e={'recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'Restore the exact missing spoken number3 from an independently verified same-speaker 3,4학년 list. Original scene52 remainder preserved.','source':source.relative_to(R).as_posix(),'sourceSha256':sourceHash,'interval':[23.08,23.66],'word':'삼 (3)','prior52Sha256':priorHash,'outputSha256':hashfile(dest),'seconds':len(pcm)/sr,'originalWordingChanged':False,'wholeCurrentSceneAsr':'pending','humanListening':'pending'}
(W/'voice52-editorial-repair.json').write_text(json.dumps(e,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(e,ensure_ascii=False))
