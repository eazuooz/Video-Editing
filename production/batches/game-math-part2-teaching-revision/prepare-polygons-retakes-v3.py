"""Retake two ambiguous new phrases; preserve all original22 scenes and v2 WAVs."""
from pathlib import Path
import json,copy,hashlib,datetime
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
OLD='game-math-polygons-teaching-additions-v2';NEW='game-math-polygons-retakes-v3'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(ROOT/f'projects/{OLD}/project.json');new=copy.deepcopy(m);new.update(slug=NEW,title='다각형 추가 설명: 평균과 귀 검사 발화 재녹음')
new['paths']={k:v.replace(OLD,NEW) for k,v in new['paths'].items()}
for k in ['outputDir','filenameStem']:new['tts'][k]=new['tts'][k].replace(OLD,NEW)
write(ROOT/f'projects/{NEW}/project.json',new)
changes={
 'QB01':('세 점을 같은 비중으로 섞습니다. 각 점의 비중이 삼분의 일이면 좌표의 평균입니다. 균일한 종이 삼각형의 균형을 잡는 위치와 연결됩니다. 모든 변까지의 거리나 모든 꼭짓점까지의 거리를 같게 만드는 조건은 넣지 않았습니다.',
 'Mix three points with equal weights. A weight of one third per point gives their coordinate average and connects to the balance point of a uniform paper triangle. Equal distances to every side or every vertex were not imposed.'),
 'QB07':('전체를 한꺼번에 연결하면 빈 곳을 덮을 수 있습니다. 이번에는 이웃한 점 세 개로 작은 조각 하나를 만듭니다. 볼록한 모서리여도 조각이 다른 경계를 가르거나 남은 점을 품으면 뗄 수 없습니다. 안쪽에 놓이고 방해하는 점이 없을 때만 귀로 저장합니다.',
 'Connecting everything at once can cover empty space. Instead, form one small piece from three neighboring points. A convex corner is not enough if the piece crosses another boundary or contains a remaining vertex. Save it as an ear only when it lies inside and has no obstructing vertex.')}
maps=[];scripts={'ko':[],'en':[]};changed=[];flow=read(B/'polygons-flow-draft.json')
for index,(ident,(ko,en)) in enumerate(changes.items(),1):
 ref=next(r for r in read(B/'polygons-addition-tts-map.json') if r['additionId']==ident);original=next(s for s in flow['additions'] if s['id']==ident)
 changed.append({'additionId':ident,'previous':original['ko'],'replacement':[ko],'reason':'Original v2 timing coverage92.3%; phonetic/word ambiguity' if ident=='QB01' else 'Raw read-back writes3번에 instead of한번에; remove the ambiguous new phrase without changing the algorithm'})
 original['ko']=[ko];original['en']=[en]
 for lang,line in [('ko',ko),('en',en)]:scripts[lang].append({'id':f'{index:02}','title':original['title'],'lines':[line]})
 maps.append({**ref,'ttsScene':f'{index:02}','retakesV2Scene':ref['ttsScene']})
 for slug in ['game-math-polygon-centers-v2','game-math-polygon-partition-v2']:
  lp=ROOT/f'projects/{slug}/production/lesson.json';lesson=read(lp);scene=next((s for s in lesson['scenes'] if s['id']==ident),None)
  if not scene:continue
  scene.update(ko=[ko],en=[en]);write(lp,lesson)
  for lang in ['ko','en']:
   sp=ROOT/f'projects/{slug}/script/narration.{lang}.json';script=read(sp);next(s for s in script['scenes'] if s['id']==ident)['lines']=scene[lang];write(sp,script)
write(B/'polygons-flow-draft.json',flow)
for lang,scenes in scripts.items():write(ROOT/f'projects/{NEW}/script/narration.{lang}.json',{'project':NEW,'language':lang,'status':'authorized-new-only-additive-retakes','scenes':scenes})
write(B/'polygons-retakes-v3-tts-map.json',maps)
baseline=read(B/'baselines/game-math-polygons-triangulation/lesson.json');ids={s['id'] for s in baseline['scenes']}
retained=[s for slug in ['game-math-polygon-centers-v2','game-math-polygon-partition-v2'] for s in read(ROOT/f'projects/{slug}/production/lesson.json')['scenes'] if s['id'] in ids];assert retained==baseline['scenes']
write(B/'polygons-retakes-v3-pretts-audit.json',{'project':NEW,'createdAt':datetime.datetime.now().astimezone().isoformat(),'original22DictionariesAndOrderExact':True,'changedNewLines':changed,'existingV2WavsPreserved':True,'scriptSha256':{lang:sha(ROOT/f'projects/{NEW}/script/narration.{lang}.json') for lang in ['ko','en']},'projectManifestSha256':sha(ROOT/f'projects/{NEW}/project.json'),'voiceReferenceSha256':{key:sha(ROOT/new['tts'][key]) for key in ['reference','referenceText']},'voiceSettingsExact':m['tts'],'currentHashAsrAndPixels':'pending'})
runner=(B/'render-planes-retakes-v3.py').read_text(encoding='utf8').replace('planes','polygons');writepath=B/'render-polygons-retakes-v3.py';writepath.write_text(runner,encoding='utf8')
print('Two new-only retakes prepared; original22 scenes, voice and v2 files retained.')
