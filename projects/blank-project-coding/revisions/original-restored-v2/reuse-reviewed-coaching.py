"""Reuse the already reviewed, relevant coaching invitation after original24."""
from pathlib import Path
import json,hashlib,datetime,shutil
import soundfile as sf,numpy as np
W=Path(__file__).resolve().parent;R=W.parents[3]
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def write(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
old=R/'shared/output/narration/blank-project-coding/qwen3-1.7b-balanced-v1'
source=old/'chunks/33-scene.wav';digest=hashlib.sha256(source.read_bytes()).hexdigest()
asr=read(old/'asr/33.json');assert asr['audio_sha256']==digest
assert '얌얌코딩 프로그래밍 코칭과 과외 안내도 확인해' in asr['text']
for language in ['ko','en']:
 baseline=read(W/f'baseline/script/narration.{language}.json')
 lines=next(s['lines'][1:] for s in baseline['scenes'] if s['id']=='33');assert len(lines)==2
 p=W/f'narration.{language}.json';j=read(p);next(s for s in j['scenes'] if s['id']=='56')['lines']=lines;write(p,j)
 if language=='ko':
  p=W/'narration.tts.ko.json';j=read(p);next(s for s in j['scenes'] if s['id']=='56')['lines']=lines;write(p,j)
data,rate=sf.read(source,dtype='float32');assert rate==24000
# Midpoint of the sentence pause: previous sentence ends11.26, next starts11.62.
data=data[round(11.44*rate):].copy();n=round(.008*rate);data[:n]*=np.linspace(0,1,n)
dest=R/'shared/output/narration/blank-project-coding/original-restored-v2/chunks/56-scene.wav'
if dest.exists():
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');shutil.copy2(dest,dest.with_name(f'56-scene-previous-before-coaching-reuse-{stamp}.wav'))
sf.write(dest,data,rate,subtype='PCM_16')
write(W/'voice56-reuse.json',{'recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':source.relative_to(R).as_posix(),'sourceSha256':digest,'sourceIn':11.44,'sourceOut':sf.info(source).duration,'outputSha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'seconds':len(data)/rate,'scope':'Only the authorized appended coaching invitation; original chapters0–24 remain unchanged','wording':'Reuse existing reviewed invitation and description/ending/pinned-comment guidance verbatim','wholeCurrentSceneAsr':'pending','humanListening':'pending'})
s=read(W/'narration.ko.json');audit=read(W/'original-preservation-audit.json');audit['narrationCharacters']=sum(len(t) for sc in s['scenes'] for t in sc['lines']);audit['coachingAppendix']='Existing reviewed invitation reused after original24; does not alter original chapters';write(W/'original-preservation-audit.json',audit)
(W/'narration.review.txt').write_text('\n\n'.join(f"[{sc['id']}] {sc['title']}\n"+'\n\n'.join(sc['lines']) for sc in s['scenes'])+'\n',encoding='utf-8')
print(f'Reused verified coaching sentences, {len(data)/rate:.3f}s; current whole-scene ASR remains required.')
