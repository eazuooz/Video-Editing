"""Freeze the small, evidence-backed M16 narration delta; never regenerate unchanged speech."""
from common import *
import copy
P=R/'projects/game-math-camera-frustum'
H=P/'production/concept-fit-v2'; O=P/'production/local/concept-fit-v2/audio'
authorized('M16')
edit=read(B/'m16-narration-edits.json'); base={lang:read(P/f'script/narration.{lang}.json') for lang in ('ko','en')}
titles={'02': '같은 게임의 두 화면을 따로 보기', '05': '건물 편집과 관찰 방향의 차이', '08': '완성된 건물 주위로 시점 돌리기', '11': '캐릭터 크기와 함께 보이는 공간', '13': '확대 전후 같은 지붕을 따라가기', '16': '앞의 문과 뒤의 지붕 함께 추적하기', '19': '성 가까이에서 주변 탑까지 보기', '21': '건축과 관찰을 따로 기록하기'}
jobs=[]
for lang,source in base.items():
 revised=copy.deepcopy(source)
 for s in revised['scenes']:
  if lang=='ko' and s['id'] in titles:s['title']=titles[s['id']]
  for n,pair in edit['edits'].get(s['id'],{}).items():
   old=s['lines'][int(n)-1]; new=pair[0 if lang=='ko' else 1];s['lines'][int(n)-1]=new
   if lang=='ko':jobs.append(dict(id=f"{s['id']}.L{int(n):02}",scene=s['id'],line=int(n),before=old,text=new,textSha256=hashlib.sha256(new.encode()).hexdigest()))
 target=P/f'script/concept-fit-v2/narration.{lang}.json'
 if target.exists():assert read(target)==revised,'Preserve existing differing revision'
 else:save(target,revised)
manifest=read(R/'projects/game-math-euler-axis-angle/production/revision-v8-orientation-matrix/voice-tts-manifest.json')['tts']
manifest['outputDir']=rel(O)
inputs={name:dict(file=rel(p),sha256=sha(p)) for name,p in {
 'baselineKo':P/'script/narration.ko.json','baselineEn':P/'script/narration.en.json',
 'revisionKo':P/'script/concept-fit-v2/narration.ko.json','revisionEn':P/'script/concept-fit-v2/narration.en.json',
 'delta':B/'m16-narration-edits.json','timeline':P/'production/timeline.json',
 'reference':R/manifest['reference'],'referenceText':R/manifest['referenceText']}.items()}
identity=hashlib.sha256(json.dumps(dict(inputs=inputs,jobs=jobs,tts=manifest),ensure_ascii=False,sort_keys=True).encode()).hexdigest()
plan=dict(episode='M16',slug=P.name,revision='concept-fit-v2',preparedAt=now(),identitySha256=identity,
 inputs=inputs,jobs=jobs,tts=manifest,changedParagraphCount=len(jobs),
 unchangedParagraphCount=sum(len(x['lines']) for x in base['ko']['scenes'])-len(jobs),
 preservation='Original mathematics, ordering and unchanged narration reused from recovered AAC; only these game-specific complete paragraphs synthesized.',
 resources=dict(allocatorCapMiB=5888,minimumFreeMiB=6656,maximumConcurrentModels=1),
 resourceReason='5888 MiB allocator cap; measured M15 peak4756 MiB plus 768 MiB free headroom; stable utilization and no foreign GPU Python required. No other process is stopped.',
 sourcePcm='Raw FLOAT takes preserved without trimming, fades or speed adjustment.',review='pending source ASR and listening')
target=H/'voice-plan.json'
if target.exists():assert read(target)['identitySha256']==identity
else:save(target,plan)
O.mkdir(parents=True,exist_ok=True)
print(json.dumps(dict(changed=len(jobs),unchanged=plan['unchangedParagraphCount'],plan=rel(target),identity=identity),ensure_ascii=False))
