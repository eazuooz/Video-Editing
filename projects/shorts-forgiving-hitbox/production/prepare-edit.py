"""Preserve verified PCM ranges and set one finite30s editorial timeline."""
from pathlib import Path
import json,hashlib,numpy as np,soundfile as sf
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parents[1];L=P/'production/local'
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
parts=[dict(version='v1',start=0,end=2.23,dest=.2),dict(version='v2',start=2.95,end=11.16,dest=4),dict(version='v2',start=11.16,end=17.90,dest=14),dict(version='v2',start=17.90,end=22.56,dest=21.6)]
target=L/'narration-timeline.wav';assert not target.exists(),'Preserve existing assembled source'
pcm=np.zeros(30*24000,dtype=np.float32)
for p in parts:
 f=R/f"shared/output/narration/shorts-forgiving-hitbox/hitbox-{p['version']}/hitbox-{p['version']}.wav";a,sr=sf.read(f,dtype='float32');assert sr==24000
 b=a[round(p['start']*sr):round(p['end']*sr)];i=round(p['dest']*sr);pcm[i:i+len(b)]=b
 p.update(path=f.relative_to(R).as_posix(),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),destinationEnd=(i+len(b))/sr,rate=1,gain=1,fades=False)
sf.write(target,pcm,24000,subtype='FLOAT')
save(L/'pcm-edit.json',dict(parts=parts,seconds=30,reason='v2 full ASR and independent introductory-context ASR confirmed corrupted opening. Restore correctly recognized v1 first question and preserve v2 body. The redundant armor sentence is removed. Cuts use inspected quiet waveform boundaries; comparison pauses let viewers observe actual outcomes. No speech retiming.',humanListening='pending'))
for lang in ['ko','en']:
 p=P/f'script/narration.{lang}.json';j=read(p);j['scenes'][0]['lines'].pop(1);save(p,j);(P/f'script/narration.{lang}.txt').write_text(' '.join(j['scenes'][0]['lines'])+'\n',encoding='utf8')
raw=[(.2,1.02,'분명 닿았는데,','That clearly touched.'),(1.02,2.4,'왜 안 맞았죠?','Why was there no hit?'),(4.01,5.65,'초록색은 피해를 받는 영역,','The green region receives damage:'),(5.65,6.57,'허트박스예요.','the hurtbox.'),(6.69,8.65,'빨간 공격 영역, 히트박스와','The red attack region is the hitbox.'),(8.65,10.15,'겹쳐야 체력이 줄죠.','Overlap makes health drop.'),(10.15,12.2,'같은 공격으로 비교해 볼게요.','Let’s compare the same attack.'),(14.04,15.4,'몸만큼 넓히면 맞고,','As wide as the body: a hit.'),(15.4,17.48,'조금 줄이면 빗나갑니다.','Slightly smaller: a miss.'),(17.48,18.78,'겉모습은 그대로고,','The appearance is unchanged.'),(18.78,20.7,'피격 영역만 바꾼 겁니다.','Only the hurtbox changed.'),(21.8,22.84,'아까 살아남은 이유도,','That character survived'),(22.84,23.92,'보이는 몸이 아니라','because the visible body'),(23.92,24.96,'이 두 영역으로','did not decide the hit.'),(24.96,26.3,'판정했기 때문입니다.','These two regions did.')]
save(P/'script/captions.json',dict(cues=[dict(start=a,end=b,ko=k,en=e) for a,b,k,e in raw],timingBasis='Current complete v2 word ASR; v1 introductory independent context; source/destination map and waveform-safe cuts in pcm-edit.json',finalEncodedAsr='pending'))
shots=[dict(id='01-hook',start=0,end=3.5,attackStart=.15,attackSeconds=1.8,width=.86),dict(id='02-reveal',start=3.5,end=13.25,attackStart=6.7,attackSeconds=3,width=.86),dict(id='03-wide',start=13.25,end=15.4,attackStart=13.75,attackSeconds=1.6,width=1.4),dict(id='04-narrow',start=15.4,end=21.5,attackStart=15.55,attackSeconds=1.5,width=.86),dict(id='05-resolution',start=21.5,end=30,attackStart=22.1,attackSeconds=7.2,width=.86)]
save(L/'visual-timing.json',dict(seconds=30,fps=60,frames=1800,revealStart=3.8,attackRevealStart=6.6,shots=shots,closingReplay='Purposeful slow replay of the opening incident with visible collider boundaries; not unrelated filler.'))
j=read(P/'planning/production-plan.json');j['narrationRevision']=dict(assembly='production/local/pcm-edit.json',current='production/local/narration-timeline.wav',fullSourceAsr='pending current assembly',cutReview='Independent whole introductory contexts plus actual waveform valleys; no endings clipped');j['sceneTiming']='production/local/visual-timing.json';save(P/'planning/production-plan.json',j)
print('30s PCM timeline and caption/collider timing prepared.')
