"""Freeze the small, evidence-backed M04 narration delta; never regenerate unchanged speech."""
from common import *
import copy
P=R/'projects/game-math-euler-axis-angle'
H=P/'production/concept-fit-v2'; O=P/'production/local/concept-fit-v2/audio'
authorized('M04')
edit=read(B/'m04-narration-edits.json'); base={lang:read(P/f'script/narration.{lang}.json') for lang in ('ko','en')}
titles={'02':'조립 물체의 회전을 나눠 보기','05':'물체 축과 고정축','08':'돌아간 앞쪽 주위의 비틀림','11':'화면의 수직과 짐벌락','14':'타일 방향과 회전 경로','17':'같은 끝 자세와 다른 경로','20':'조립 물체의 이동과 회전','23':'두 회전의 합성과 벡터의 합'}
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
 'delta':B/'m04-narration-edits.json','timeline':P/'production/timeline.json',
 'reference':R/manifest['reference'],'referenceText':R/manifest['referenceText']}.items()}
identity=hashlib.sha256(json.dumps(dict(inputs=inputs,jobs=jobs,tts=manifest),ensure_ascii=False,sort_keys=True).encode()).hexdigest()
plan=dict(episode='M04',slug=P.name,revision='concept-fit-v2',preparedAt=now(),identitySha256=identity,
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
