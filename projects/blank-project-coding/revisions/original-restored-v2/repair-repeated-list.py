"""Use the already verified identical sentence take for the repeated list.

Scene43 and scene36 repeat the user's same example. Preserve scene43's exact
opening (테트리스, without scene36's 를) and join at a measured sentence pause.
Independent ASR must approve the resulting whole scene again.
"""
from pathlib import Path
import json,re,hashlib,shutil,datetime
import numpy as np,soundfile as sf
W=Path(__file__).resolve().parent;R=W.parents[3]
A=R/'shared/output/narration/blank-project-coding/original-restored-v2'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
norm=lambda t:re.sub(r'[^a-z0-9가-힣]','',t.lower())
script=read(W/'narration.tts.ko.json')['scenes']
texts={s['id']:' '.join(s['lines']) for s in script}
assert norm(texts['36'].split('영상에서는',1)[1])==norm(texts['43'].split('영상에서는',1)[1])
sources={sid:A/'chunks'/f'{sid}-scene.wav' for sid in ['36','43']}
hashes={sid:hashlib.sha256(p.read_bytes()).hexdigest() for sid,p in sources.items()}
for sid in sources:assert read(A/'asr'/f'{sid}.json')['audio_sha256']==hashes[sid]
head,sr=sf.read(sources['43'],dtype='float32');tail,tr=sf.read(sources['36'],dtype='float32');assert sr==tr==24000
# Both boundaries are inside the independent ASR's silence after 해보겠습니다.
head=head[:round(4.24*sr)].copy();tail=tail[round(4.46*sr):].copy()
n=round(.008*sr);head[-n:]*=np.linspace(1,0,n);tail[:n]*=np.linspace(0,1,n)
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
backup=sources['43'].with_name(f'43-scene-previous-before-verified-list-{stamp}.wav');shutil.copy2(sources['43'],backup)
sf.write(sources['43'],np.concatenate([head,tail]),sr,subtype='PCM_16')
e={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'Exact original scene43 opening + already verified identical scene36 sentences; join only inside the sentence pause','originalWordingChanged':False,'firstTake':{'scene':'43','sha256':hashes['43'],'in':0,'out':4.24},'identicalRemainder':{'scene':'36','sha256':hashes['36'],'in':4.46},'edgeFadeMs':8,'outputSha256':hashlib.sha256(sources['43'].read_bytes()).hexdigest(),'seconds':(len(head)+len(tail))/sr,'independentWholeSceneAsr':'pending','humanListening':'pending'}
(W/'voice43-editorial-repair.json').write_text(json.dumps(e,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(e,ensure_ascii=False))
