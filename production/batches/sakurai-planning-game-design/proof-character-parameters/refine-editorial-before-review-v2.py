"""Preserve the initial draft and refine the independent paired editorial."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
ROOT=Path(__file__).resolve().parents[4];T=ROOT/'projects/character-parameters';P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
history=T/'production/editorial-initial-v1';assert not history.exists();history.mkdir(parents=True)
paths=[T/'script/narration.ko.json',T/'script/narration.en.json',T/'planning/scene-intents-v1.json',T/'planning/outline.md']
before=[]
for p in paths:
 target=history/p.name;shutil.copyfile(p,target);before.append({'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'preserved':target.relative_to(ROOT).as_posix()})
ko=json.loads(paths[0].read_text('utf-8'));en=json.loads(paths[1].read_text('utf-8'))
ks=next(s for s in ko['scenes'] if s['id']=='06-role-and-limitation');es=next(s for s in en['scenes'] if s['id']=='06-role-and-limitation')
ks['lines'].append('플레이어 캐릭터와 적의 역할도 구분해 보세요. 설계 예시로, 단순히 돌진하는 적도 좁은 통로에 배치하거나 다른 적과 조합하면 다른 대응을 요구할 수 있습니다. 배치의 효과는 실제 플레이테스트로 확인해야 합니다.')
es['lines'].append('Distinguish a playable character’s role from an enemy’s role too. In a hypothetical design, even a simple charging enemy can demand a different response in a narrow corridor or in combination with another enemy. Verify the placement’s effect through actual playtests.')
titles=['From Numbers to Playstyle','Establish a Shared Baseline','Differences Beyond Scaling','Changing What the Opponent Reads','Does a Strength Change Choices?','Keep a Role Within Limitations','Base Capabilities and Current State','When Abilities Change Parameters','Conditions and Timing','Preserve Identity While Tuning','The Cost of Unique Rules','A Role Players Can Describe']
for s,t in zip(en['scenes'],titles):s['title']=t
write(paths[0],ko);write(paths[1],en)
intents=json.loads(paths[2].read_text('utf-8'))
for s,k in zip(intents['scenes'],ko['scenes']):s['paragraphs']=len(k['lines'])
s=next(s for s in intents['scenes'] if s['id']=='06-role-and-limitation')
s['projectedMotion']+=' 마지막에는 설계 예시라고 표시한 좁은 통로의 투영된 벽과 돌진 경로, 다른 적의 차단 영역을 비교한다. 선정 footage가 배치 효과를 실험했다고 주장하지 않는다.'
write(paths[2],intents)
outline=paths[3].read_text('utf-8')+'\n06장 마지막 문단에 플레이어/적의 역할 구분과 배치·조합의 설계 예시를 추가했다. 실제 샷은 이 배치 실험의 증거가 아니며 별도 검정2.5D 도식으로 보여 준다. 현재12씬37KOEN문단이고36문단 초기본은production/editorial-initial-v1에 보존했다.\n'
paths[3].write_text(outline,encoding='utf-8')
write(P/'editorial-refinement-v2.json',{'recordedAt':datetime.now(timezone.utc).isoformat(),'before':before,
 'after':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in paths],
 'scenes':12,'pairedParagraphs':37,'koCharacters':sum(len(x) for s in ko['scenes'] for x in s['lines']),
 'changes':['Independent English scene headings.','Preserved counterplay paragraph and added playable/enemy distinction plus explicitly hypothetical placement/combination example.'],
 'ttsStarted':False,'newMedia':0,'foreignChanges':0})
print('Prepared12 scenes/37 paired paragraphs; initial draft preserved. TTS0.')
