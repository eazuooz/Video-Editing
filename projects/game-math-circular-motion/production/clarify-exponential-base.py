"""Distinguish Euler's number from the spoken integer two before M26 TTS."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
P=Path(__file__).resolve().parents[1]
changes=[
('이를 이용해 이의 아이 엑스 제곱의 급수를 펼쳐 보겠습니다.','자연상수 이, 약 이 점 칠일팔의 지수를 아이 엑스로 둔 지수 함수를 급수로 펼쳐 보겠습니다.'),
('그래서 이의 아이 엑스 제곱은 코사인 엑스 더하기 아이 사인 엑스와 같습니다.','그래서 자연상수 이의 지수를 아이 엑스로 둔 값은 코사인 엑스 더하기 아이 사인 엑스와 같습니다.'),
('Substitute i x into the exponential series: one plus i x plus i x squared over two factorial, and so on.','Use the exponential with base e, approximately two point seven one eight, and substitute i x into its series: one plus i x plus the square of i x over two factorial, and so on.')]
files=['script/narration.ko.json','script/narration.en.json','script/draft-narration.ko.json','script/draft-narration.en.json','script/draft-author.py','planning/scene-bindings.json','planning/production-plan.json']
proof=[]
for name in files:
 p=P/name;s=p.read_text(encoding='utf-8');before=s;digest=hashlib.sha256(p.read_bytes()).hexdigest()
 for old,new in changes:s=s.replace(old,new)
 if s!=before:proof.append(dict(file=name,beforeSha256=digest));p.write_text(s,encoding='utf-8')
assert proof,'Already applied or input changed'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=P/'planning/scene-bindings.json';d=read(p);d['sourceNarrationSha256']=sha(P/'script/narration.ko.json');save(p,d)
p=P/'planning/script-integration.json';d=read(p)
for lang in ('ko','en'):d['readThrough'][lang+'Sha256']=sha(P/f'script/narration.{lang}.json')
d.setdefault('preVoiceCorrections',[]).append(dict(scenes=['035','036'],changes=changes,reason='Define e rather than leave spoken 이 ambiguous with integer two; disambiguate the square of the product i*x.',evidence='exp(i*x)=sum((i*x)^n/n!); e≈2.718281828; exp(i*x)=cos(x)+i*sin(x)',files=proof,at=datetime.now(timezone.utc).isoformat(),learningOrderUnchanged=True,audioChanged=False));save(p,d)
print('Euler base and parenthesized product clarified before voice production')
