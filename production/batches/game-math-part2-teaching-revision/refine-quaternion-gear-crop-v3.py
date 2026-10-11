"""Exclude size switching and give each actual preview its own reviewed crop."""
from pathlib import Path
import copy,datetime,json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;R=B/'cross-game-review-20261011/quaternion-four-game-v3'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
d=read(R/'additions.json');old=copy.deepcopy(d)
cuts=[(172,175.65,[480,320,960,540]),(176.95,178.9,[360,110,1100,618]),(178.9,181.9,[480,320,960,540])]
changes={}
for s in d['scenes']:
 if s['id'] not in ['QF20','QC20']:continue
 s['intervals']=[[a,b] for a,b,c in cuts];s['maximumSeconds']=sum(b-a for a,b,c in cuts)
 s['sourceSegments']=[dict(sourceId=s['sourceId'],sourceFile=s['sourceFile'],sourceSha256=s['sourceSha256'],**{'in':a,'maxSeconds':b-a,'crop':c}) for a,b,c in cuts]
 s['ko']=['옆으로 돌린 우주선 부품을 다시 세우면 방향도 돌아옵니다.'] if s['id']=='QF20' else ['부품을 세우려면 현재와 목표 방향 사이의 회전이 필요합니다.']
 s['en']=['Turning the sideways ship component upright restores its orientation.'] if s['id']=='QF20' else ['Standing the component upright requires a rotation between its current and target orientations.']
 s['annotation']['hideAtCut']=True;changes[s['id']]=copy.deepcopy(s)
write(R/'before-gear-crop-refinement.json',old);write(R/'additions.json',d)
for ep in read(R/'baseline.json')['episodes']:
 P=ROOT/'projects'/ep['newSlug'];lesson=read(P/'production/lesson.json')
 lesson['scenes']=[copy.deepcopy(changes.get(s['id'],s)) for s in lesson['scenes']]
 original=read(R/'baseline'/ep['slug']/'production/lesson.json')['scenes'];oldids={s['id'] for s in original}
 assert [s for s in lesson['scenes'] if s['id'] in oldids]==original
 write(P/'production/lesson.json',lesson)
 for lang in ['ko','en']:
  script=read(P/f'script/narration.{lang}.json');script['scenes']=[dict(id=s['id'],title=s['title'],lines=s[lang]) for s in lesson['scenes']];write(P/f'script/narration.{lang}.json',script)
master='game-math-quaternion-cross-game-additions-v3';maps=read(R/'tts-map.json')
for lang in ['ko','en']:
 p=ROOT/f'projects/{master}/script/narration.{lang}.json';script=read(p)
 for item in maps:
  if item['additionId'] in changes:
   scene=next(s for s in script['scenes'] if s['id']==item['ttsScene']);scene['lines']=changes[item['additionId']][lang]
 write(p,script)
record=dict(recordedAt=datetime.datetime.now().astimezone().isoformat(),reason='The first fixed crop clipped the larger preview during a size change. Exclude that action and use three crops for small preview, rotated larger preview and placed result.',selectedCuts=cuts,seconds=sum(b-a for a,b,c in cuts),sourceAnglesMeasured=False,finalMovingPixelsApproved=False,original80ScenesExact=True)
write(R/'gear-crop-refinement.json',record)
print('Size-switch interval excluded;8.6s of actual rotation/result and three source crops prepared. Original80 dictionaries remain exact.')
