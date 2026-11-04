"""Connect authored M24–M33 source beats, games and phrase clocks without TTS."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,copy,hashlib,json
R=Path(__file__).resolve().parents[3]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
FILES={
'game-math-velocity-derivatives':'derivative-shots.json',
'game-math-acceleration-integration':'integration-shots.json',
'game-math-circular-motion':'circular-shots.json',
'game-math-forces-friction':'force-shots.json',
'game-math-springs-damping':'spring-shots.json',
'game-math-momentum-collisions':'dynamics-shots.json',
'game-math-rigid-body-inertia':'rigid-shots.json',
'game-math-parametric-hermite':'curve-shots.json',
'game-math-bezier-subdivision':'curve-shots.json',
'game-math-splines-continuity':'curve-shots.json'}
# Repeated terms and suffix matches (e.g. 5 within 6.5) need explicit,
# context-reviewed phrases. Never silently take the first substring match.
SPECIFIC={
('velocity-derivatives','006','제곱미터'):'제곱미터이고',
('velocity-derivatives','006','초당 미터'):'초당 미터죠',
('velocity-derivatives','014','평균속력은'):'평균속력은 초속 삼 미터',
('velocity-derivatives','036','팩토리얼'):'팩토리얼은 그 자연수까지',
('velocity-derivatives','038','마이너스 사인'):'마이너스 사인이 됩니다',
('velocity-derivatives','044','사인 삼 엑스'):'사인 삼 엑스는',
('velocity-derivatives','044','사인 엑스 제곱'):'사인 엑스 제곱도',
('acceleration-integration','019','정점 시간'):'정점 시간은',
('acceleration-integration','035','현재 함수 값'):'간격을 영으로 보내면 현재 함수 값',
('acceleration-integration','036','정적분은'):'정적분은 주어진 구간',
('circular-motion','008','주기는'):'주기는 이 파이 알',
('circular-motion','008','진동수는'):'진동수는 그 역수',
('circular-motion','009','이십사 시간'):'이십사 시간이라는 근삿값',
('circular-motion','026','오 초에서는'):'오 초에서는 코사인 오 파이',
('circular-motion','028','오 초에는'):'오 초에는 사인이 영',
('forces-friction','006','일 뉴턴'):'일 뉴턴입니다',
('forces-friction','016','중력과 마찰'):'중력과 마찰을 차례로',
('forces-friction','019','약 구점팔삼'):'약 구점팔삼이라는 가속도',
('momentum-collisions','034','한 번 적용'):'충격량 방식이라면 한 번 적용',
('springs-damping','005','코사인 티'):'위치를 코사인 티라고',
('springs-damping','015','초기 속도'):'초기 속도를 마이너스 십',
('springs-damping','018','현재 값'):'현재 값, 목표값, 현재 변화 속도'}
ap=argparse.ArgumentParser();ap.add_argument('--project',required=True,choices=list(FILES));args=ap.parse_args()
c=read(R/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104'];assert c['productionAllowedNow'] and args.project in c['projectSlugs']
P=R/'projects'/args.project;source=P/'production/unity-staging'/FILES[P.name];design=read(source);script=read(P/'script/narration.ko.json');plan=read(P/'planning/production-plan.json')
assert sha(P/'script/narration.ko.json')==design['scriptSha256'],'Source wording changed; inspect anchors before binding'
models={s['sceneId']:s for s in design['shots']};games={g['sceneId']:g for g in plan['nativeGameCueBindings']};learning={s['id']:s for s in plan['learningSteps']};rows=[]
assert len(models)==len(script['scenes'])-1 and '000' in games
for scene in script['scenes']:
 sid=scene['id'];speech=' '.join(scene['lines']);shot=copy.deepcopy(models['001' if sid=='000' else sid]['shot']);anchors=[]
 if sid!='000':
  model_id=models[sid]['sourceBeatId'];source_id=scene['sourceBeatId']
  assert model_id==source_id or (P.name=='game-math-momentum-collisions' and model_id=='M29-'+sid and source_id.startswith(model_id+'-'))
  for i,step in enumerate(shot['steps']):
   original=step['anchor'];phrase=SPECIFIC.get((P.name.removeprefix('game-math-'),sid,original),original)
   assert speech.count(phrase)==1,(sid,phrase,speech.count(phrase))
   anchors.append(dict(phrase=phrase,position=i/len(shot['steps']),character=speech.index(phrase)))
  assert all(a['character']<b['character'] for a,b in zip(anchors,anchors[1:])),sid
 shot['beatId']=scene['sourceBeatId']
 row=dict(id=sid,sourceBeatId=scene['sourceBeatId'],speech=speech,sourceParagraphs=learning[scene['sourceBeatId']]['sourceParagraphs'],renderer='Unity',classification='our-implementation',shot=shot,speechPhaseAnchors=anchors,clockFields=['stepSeconds','stepPositions'],hold=0,independentEditableSceneRequired=True,status='source-implemented-runtime-and-speech-QA-pending',timing='Actual words required; no automatic observation silence')
 if sid in games:row['actualGamePart']=dict(copy.deepcopy(games[sid]),duration=games[sid]['sourceOut']-games[sid]['sourceIn'])
 if sid=='000':row['classification']='actual-game-thesis-abstract-with-explanation-handoff'
 rows.append(row)
record=dict(schemaVersion=1,project=P.name,updatedAt=datetime.now(timezone.utc).isoformat(),sourceNarrationSha256=sha(P/'script/narration.ko.json'),sourceModelsSha256=sha(source),sourceModels=str(source.relative_to(R)),status='complete-design-awaiting-runtime-and-speech-QA',allBodyParagraphsRetained=True,pendingImplementationBeatCount=0,actualNativeGameParts=len(games),humanViewed=False,scenes=rows)
(P/'planning/scene-bindings.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(P.name,len(rows),'source paragraphs,',sum(len(r['speechPhaseAnchors']) for r in rows),'phrase anchors; no media approval.')
