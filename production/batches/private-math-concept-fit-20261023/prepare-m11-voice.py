"""Freeze the small, evidence-backed M11 narration delta; never regenerate unchanged speech."""
from common import *
import copy
P=R/'projects/game-math-plane-distances-v2'
H=P/'production/concept-fit-v2'; O=P/'production/local/concept-fit-v2/audio'
authorized('M11')
edit=read(B/'m11-narration-edits.json'); base={lang:read(P/f'script/narration.{lang}.json') for lang in ('ko','en')}
titles={'02': '다리 표면과 그 위의 점', 'PG01': '표면을 따라가는 이동과 수직 이동', 'PG02': '다리가 기울면 법선도 바뀝니다', '05': '같은 기준면의 위와 아래', '08': '세 연결점에서 삼각형으로', 'PG03': '다섯 꼭짓점의 판과 둘레 순서'}
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
 'delta':B/'m11-narration-edits.json','timeline':P/'production/timeline.json',
 'reference':R/manifest['reference'],'referenceText':R/manifest['referenceText']}.items()}
identity=hashlib.sha256(json.dumps(dict(inputs=inputs,jobs=jobs,tts=manifest),ensure_ascii=False,sort_keys=True).encode()).hexdigest()
plan=dict(episode='M11',slug=P.name,revision='concept-fit-v2',preparedAt=now(),identitySha256=identity,
 inputs=inputs,jobs=jobs,tts=manifest,changedParagraphCount=len(jobs),
 unchangedParagraphCount=sum(len(x['lines']) for x in base['ko']['scenes'])-len(jobs),
 preservation='Original mathematics, ordering and unchanged narration reused from recovered AAC; only these game-specific complete paragraphs synthesized.',
 resources=dict(allocatorCapMiB=6144,minimumFreeMiB=6912,maximumConcurrentModels=1),
 resourceReason='6144 MiB allocator cap plus 768 MiB free headroom; stable utilization and no foreign GPU Python required. No other process is stopped.',
 sourcePcm='Raw FLOAT takes preserved without trimming, fades or speed adjustment.',review='pending source ASR and listening')
target=H/'voice-plan.json'
if target.exists():assert read(target)['identitySha256']==identity
else:save(target,plan)
O.mkdir(parents=True,exist_ok=True)
print(json.dumps(dict(changed=len(jobs),unchanged=plan['unchangedParagraphCount'],plan=rel(target),identity=identity),ensure_ascii=False))
