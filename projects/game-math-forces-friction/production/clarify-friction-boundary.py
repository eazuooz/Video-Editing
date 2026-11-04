"""Small pre-voice inequality/English-spacing corrections, unchanged teaching order."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
P=Path(__file__).resolve().parents[1]
changes=[('정지 마찰 한도보다 작아야 합니다.','정지 마찰 한도 이하여야 합니다.'),('mass of5.98 times10 to the24 kilograms','mass of 5.98 times 10 to the 24 kilograms'),('radius of6,371kilometres','radius of 6,371 kilometres'),('about9.83metres','about 9.83 metres'),('roughly0.034','roughly 0.034'),('gives9.796','gives 9.796'),('about9.78','about 9.78'),('and9.83','and 9.83'),('gravity,9.80665','gravity, 9.80665'),('in0.4seconds','in 0.4 seconds'),('minus25metres','minus 25 metres'),('coefficient of0.5','coefficient of 0.5'),('from0.61','from 0.61'),('to0.04','to 0.04')]
files=['script/narration.ko.json','script/narration.en.json','script/draft-narration.ko.json','script/draft-narration.en.json','script/draft-author.py','planning/scene-bindings.json','planning/production-plan.json']
proof=[]
prior=json.loads((P/'planning/script-integration.json').read_text(encoding='utf-8'))['readThrough']
for name in files:
 p=P/name
 if not p.exists():continue
 s=p.read_text(encoding='utf-8');before=s;digest=hashlib.sha256(p.read_bytes()).hexdigest()
 for old,new in changes:s=s.replace(old,new)
 if s!=before:proof.append(dict(file=name,beforeSha256=digest));p.write_text(s,encoding='utf-8')
for lang in ('ko','en'):
 proof.append(dict(file=f'script/narration.{lang}.json',beforeSha256=prior[lang+'Sha256'],note='Prior integration hash preserved; first invocation changed narration before discovering absent optional draft-author.py. Continuation updates remaining bindings and this audit.'))
assert proof
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=P/'planning/scene-bindings.json';d=read(p);d['sourceNarrationSha256']=sha(P/'script/narration.ko.json');save(p,d)
p=P/'planning/script-integration.json';d=read(p)
for lang in ('ko','en'):d['readThrough'][lang+'Sha256']=sha(P/f'script/narration.{lang}.json')
d.setdefault('preVoiceCorrections',[]).append(dict(scenes=['019','022','025','026','028'],changes=changes,reason='Static-friction equilibrium includes its limiting value; match the following ≤ statement and English. Restore missing English number/unit spaces.',evidence='|F_static| ≤ mu_s*N; on slope tan(theta) ≤ mu_s',files=proof,at=datetime.now(timezone.utc).isoformat(),learningOrderUnchanged=True,audioChanged=False));save(p,d)
print('Static-friction boundary and English spacing clarified before voice generation')
