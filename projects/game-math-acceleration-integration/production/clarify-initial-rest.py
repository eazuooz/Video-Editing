"""Make the initial-rest assumption explicit before M25 voice generation."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
P=Path(__file__).resolve().parents[1]
old='초당 사 미터씩 속도가 늘어난다면';new='정지에서 출발해 초당 사 미터씩 속도가 늘어난다면'
files=['script/narration.ko.json','script/draft-narration.ko.json','script/draft-author.py','planning/scene-bindings.json','planning/production-plan.json']
proof=[]
for name in files:
 p=P/name;s=p.read_text(encoding='utf-8');assert old in s and new not in s,name
 proof.append(dict(file=name,beforeSha256=hashlib.sha256(p.read_bytes()).hexdigest(),replacements=s.count(old)))
 p.write_text(s.replace(old,new),encoding='utf-8')
digest=hashlib.sha256((P/'script/narration.ko.json').read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=P/'planning/scene-bindings.json';d=read(p);d['sourceNarrationSha256']=digest;save(p,d)
p=P/'planning/script-integration.json';d=read(p);d['readThrough']['koSha256']=digest
d.setdefault('preVoiceCorrections',[]).append(dict(scene='002',old=old,new=new,reason='The worked values v(1)=4 and v(2)=8 at acceleration 4 m/s² require initial velocity zero. English already says from rest. Make the Korean prerequisite explicit.',evidence='v(t)=v0+a*t; 0+4*1=4; 0+4*2=8',at=datetime.now(timezone.utc).isoformat(),files=proof,learningOrderUnchanged=True,audioChanged=False));save(p,d)
print('Initial rest made explicit in Korean before TTS; same example and learning order')
