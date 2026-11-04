"""Correct one spoken SI unit before M24 voice generation; preserve lesson scope."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
P=Path(__file__).resolve().parents[1]
old='가속도가 초당 마이너스 일 미터';new='가속도가 마이너스 일 미터 매 초 제곱'
files=['script/narration.ko.json','script/draft-narration.ko.json','script/draft-author.py','planning/scene-bindings.json','planning/production-plan.json']
proof=[]
for name in files:
 p=P/name;s=p.read_text(encoding='utf-8');assert old in s,name
 proof.append(dict(file=name,beforeSha256=hashlib.sha256(p.read_bytes()).hexdigest(),replacements=s.count(old)))
 p.write_text(s.replace(old,new),encoding='utf-8')
digest=hashlib.sha256((P/'script/narration.ko.json').read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=P/'planning/scene-bindings.json';d=read(p);d['sourceNarrationSha256']=digest;save(p,d)
p=P/'planning/script-integration.json';d=read(p);d['readThrough']['koSha256']=digest
d.setdefault('preVoiceCorrections',[]).append(dict(scene='020',old=old,new=new,reason='Acceleration is velocity change per time, m/s²; the prior Korean phrase gave a velocity unit. English and numeric example already correct.',source='https://www.nist.gov/pml/special-publication-811/nist-guide-si-chapter-4-two-classes-si-units-and-si-prefixes',at=datetime.now(timezone.utc).isoformat(),files=proof,learningOrderUnchanged=True,audioChanged=False));save(p,d)
print('One Korean acceleration unit corrected in narration and source design; no voice generated')
