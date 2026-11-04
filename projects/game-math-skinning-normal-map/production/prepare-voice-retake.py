"""Additive retake for verified runaway paragraph 023; preserve all other raw PCM."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
P=Path(__file__).resolve().parents[1];R=P.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=P/'production/local/audio-v1';new=P/'production/local/audio-v2'
assert not new.exists(),'Preserve existing revision'
e=read(old/'review/paragraphs/023-01.json');assert len(e['text'])>2*len(e['entry']['text'])
new.mkdir();(new/'chunks').mkdir();copied=[]
for f in sorted((old/'chunks').glob('*.wav')):
 if f.name=='023-01-scene.wav':continue
 target=new/'chunks'/f.name;shutil.copy2(f,target);assert sha(f)==sha(target);copied.append(dict(file=f.name,sha256=sha(f)))
assert len(copied)==35
m=read(P/'production/tts-manifest.json');m['tts']['outputDir']=new.relative_to(R).as_posix();m['tts']['status']='additive-targeted-retake';m['retake']={'scene':'023','reason':'Original raw take hit token cap and repeated unrelated endings; full actual ASR confirms missing latter explanation. Same complete narration and voice; stochastic retake only.','preservedOriginal':old.relative_to(R).as_posix()}
(P/'production/tts-manifest-audio-v2.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(new/'retake-plan.json').write_text(json.dumps(dict(at=datetime.now(timezone.utc).isoformat(),sourceAsrSha256=sha(old/'review/paragraphs/023-01.json'),copiedUnchangedRawTakes=copied,retakeScene='023',humanListening=False,sourceAudioPreserved=True),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('35 unchanged raw takes preserved; only 023 prepared for additive retake')
