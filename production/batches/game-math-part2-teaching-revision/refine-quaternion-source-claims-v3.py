"""Repair directly observed crop limits and avoid asserting an unmeasured inverse."""
from pathlib import Path
import copy,datetime,json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
R=B/'cross-game-review-20261011/quaternion-four-game-v3'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
data=read(R/'additions.json');before=copy.deepcopy(data)
cuts=[(172,175.15,[480,320,960,540]),(176.95,178.9,[160,220,1280,720]),(178.9,181.9,[160,220,1280,720])]
changes={}
for s in data['scenes']:
 if s['id'] in ['QF20','QC20']:
  s['intervals']=[[a,b] for a,b,c in cuts];s['maximumSeconds']=sum(b-a for a,b,c in cuts)
  s['sourceSegments']=[dict(sourceId=s['sourceId'],sourceFile=s['sourceFile'],sourceSha256=s['sourceSha256'],**{'in':a,'maxSeconds':b-a,'crop':c}) for a,b,c in cuts]
  s['annotation']['hideAtCut']=True
  s['selection']['observedLimits']='Upright long axis does not prove identical full orientation. Size switch begins before175.65; excluded from175.15. Larger preview and placed result need taller crop.'
  if s['id']=='QF20':
   s['ko']=['부품을 눕혔다 세웁니다. 같은 자세인지 옆면도 확인하세요.']
   s['en']=['The component is turned sideways and upright. Inspect its other faces before calling the full orientation identical.']
 if s['id']=='QF11':
  s['ko']=[x.replace('오른쪽 날개','한쪽 날개') for x in s['ko']]
  s['en']=[x.replace('the right wing','one wing').replace('the right-wing direction','that wing direction') for x in s['en']]
  s['axisLabelClarification']='One model wing is+y; no forward/right/up aviation convention is asserted. Mathematical basis remains right-handed.'
 if s['id']=='QF21':
  s['ko'][0]='세워졌다고 방향이 모두 같지는 않습니다. 정확히 되돌리는 계산은 모형에서 확인하겠습니다. '+s['ko'][0]
  s['en'][0]='Standing upright alone does not establish an identical full orientation. We verify an exact inverse using the defined model. '+s['en'][0]
 if s['id'] in ['QF20','QC20','QF11','QF21']:changes[s['id']]=copy.deepcopy(s)
assert changes
write(R/'before-source-claim-refinement.json',before);write(R/'additions.json',data)
for ep in read(R/'baseline.json')['episodes']:
 p=ROOT/'projects'/ep['newSlug'];lesson=read(p/'production/lesson.json')
 lesson['scenes']=[copy.deepcopy(changes.get(s['id'],s)) for s in lesson['scenes']]
 original=read(R/'baseline'/ep['slug']/'production/lesson.json')['scenes'];ids={s['id'] for s in original}
 assert [s for s in lesson['scenes'] if s['id'] in ids]==original
 write(p/'production/lesson.json',lesson)
 for lang in ['ko','en']:
  script=read(p/f'script/narration.{lang}.json');script['scenes']=[dict(id=s['id'],title=s['title'],lines=s[lang]) for s in lesson['scenes']];write(p/f'script/narration.{lang}.json',script)
master=ROOT/'projects/game-math-quaternion-cross-game-additions-v3';mapping=read(R/'tts-map.json')
for lang in ['ko','en']:
 path=master/f'script/narration.{lang}.json';script=read(path)
 for item in mapping:
  if item['additionId'] in changes:next(s for s in script['scenes'] if s['id']==item['ttsScene'])['lines']=changes[item['additionId']][lang]
 write(path,script)
write(R/'source-claim-refinement.json',dict(recordedAt=datetime.datetime.now().astimezone().isoformat(),original80Exact=True,selectedCuts=cuts,actualSeconds=sum(b-a for a,b,c in cuts),sourceAnglesMeasured=False,gameFullInverseAsserted=False,changes=list(changes),movingReview=False))
print('Observed source limits corrected; original80 unchanged; new-only scripts synchronized.')
