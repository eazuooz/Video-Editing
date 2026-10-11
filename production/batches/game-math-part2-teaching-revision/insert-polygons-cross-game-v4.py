"""Insert approved-script additions beside the exact frozen earlier lessons."""
from pathlib import Path
import copy,json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;R=B/'cross-game-review-20261011'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
data=read(R/'polygon-cross-game-content-v4.json');frozen=read(R/'before-polygon-v4-insertions.json')
flow=read(B/'polygons-episode-flow-audit.json')
for episode in flow['episodes']:
 slug=episode['slug'];P=ROOT/'projects'/slug;lesson=read(P/'production/lesson.json')
 additions=[s for s in data['scenes'] if s['episode'] in slug]
 new_ids={s['id'] for s in additions}
 assert [s for s in lesson['scenes'] if s['id'] not in new_ids]==frozen[slug]['scenes']
 scenes=copy.deepcopy(frozen[slug]['scenes'])
 for s in additions:
  index=next(i for i,old in enumerate(scenes) if old['id']==s['insertAfter']);scenes.insert(index+1,copy.deepcopy(s))
 assert [s for s in scenes if s['id'] not in new_ids]==frozen[slug]['scenes']
 lesson['scenes']=scenes;lesson['crossGameAdditions']='cross-game-review-20261011/polygon-cross-game-content-v4.json'
 write(P/'production/lesson.json',lesson)
 for lang in ['ko','en']:
  path=P/f'script/narration.{lang}.json';script=read(path)
  script['scenes']=[{'id':s['id'],'title':s['title'],'lines':s[lang]} for s in scenes];write(path,script)
 episode['order']=[s['id'] for s in scenes]
 episode['newActualCapacitySeconds']=sum(s.get('maximumSeconds',0) for s in scenes if s['kind']=='actual' and s['id'] not in episode['originalIds'])
 episode['mediaQaComplete']=False
flow['crossGameAdditionsPreserveEveryEarlierScene']=True;flow['finalContinuousReview']=False
write(B/'polygons-episode-flow-audit.json',flow)
print('Seven independent additions inserted; exact earlier dictionaries and order retained.')
