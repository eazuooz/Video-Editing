"""State the perpendicular axis offset required by the worked example."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
P=Path(__file__).resolve().parents[1]
old='물체의 축을 한 미터 옮기면';new='물체의 축을 축에 수직인 방향으로 한 미터 옮기면'
files=['script/narration.ko.json','script/draft-narration.ko.json','planning/scene-bindings.json','planning/production-plan.json']
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
d.setdefault('preVoiceCorrections',[]).append(dict(scene='018',old=old,new=new,reason='The scalar parallel-axis example I=0.2+2*1^2 requires a perpendicular separation of parallel axes. English already specifies perpendicular. Make the same condition explicit in Korean.',evidence='I_new=I_cm+m*d_perpendicular^2=0.2+2*1^2=2.2',at=datetime.now(timezone.utc).isoformat(),files=proof,learningOrderUnchanged=True,audioChanged=False));save(p,d)
print('Perpendicular shift prerequisite made explicit before TTS')
