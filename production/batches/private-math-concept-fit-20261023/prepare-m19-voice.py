"""Freeze the small, evidence-backed M19 narration delta; never regenerate unchanged speech."""
from common import *
import copy
P=R/'projects/game-math-mesh-uv'
H=P/'production/concept-fit-v2'; O=P/'production/local/concept-fit-v2/audio'
authorized('M19')
edit=read(B/'m19-narration-edits.json'); base={lang:read(P/f'script/narration.{lang}.json') for lang in ('ko','en')}
titles={'02':'지붕의 윤곽과 표면 무늬','06':'판의 이음선과 삼각형 연결','07':'우주선의 형태와 면의 밝기','10':'벽·지붕·탑이 만나는 경계'}
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
 'delta':B/'m19-narration-edits.json','timeline':P/'production/timeline.json',
 'reference':R/manifest['reference'],'referenceText':R/manifest['referenceText']}.items()}
identity=hashlib.sha256(json.dumps(dict(inputs=inputs,jobs=jobs,tts=manifest),ensure_ascii=False,sort_keys=True).encode()).hexdigest()
plan=dict(episode='M19',slug=P.name,revision='concept-fit-v2',preparedAt=now(),identitySha256=identity,
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
