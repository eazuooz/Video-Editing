"""Cut directly to the observed ramp and label the actual jump in three phases."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parents[1];R=P.parents[1];read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert P.name in read(R/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104']['projectSlugs']
assert not (P/'production/local/render-v1').exists()
e=P/'production/local/footage-native-qa/M25-opening-action-phases.jpg';assert e.is_file()
note=dict(originalWindow=[51,65],editedWindow=[58,65],evidence=e.relative_to(R).as_posix(),evidenceSha256=sha(e),observation='57.400 and 58.500: climbing the ramp. 59.683: still on its lip. 59.950: road ends beneath the car. 62.750 and 63.683: descending. 63.817: dust and contact. 64.850: rolling on ground.',reason='Remove the long pre-jump approach so the first narrated action is the actual sustained jump. Keep landing and one second of visible settling.',sourceSpeed=1,syntheticFrames=False,encodedSpeechSyncReviewed=False)
words=read(P/'production/local/audio-v1/review/paragraphs/000-01.json')
def word(k):return next(w['timestamp'] for w in words['chunks'] if w['text'].strip(' .')==k)
air=word('공중으로');land=word('닿습니다')
assert abs((59.95-58)-air[0])<.65 and abs((63.817-58)-land[1])<.5
note.update(spokenEvidence=dict(pcmSha256=words['audio_sha256'],airWord=air,landingWord=land,nativeAirRelative=1.95,nativeLandingRelative=5.817,method='Measured original voice and decoded native action. No respeed; integrated master still needs review.'))
phases=[dict(start=58,end=59.95,label='도약 전 · 경사로를 오르는 차'),dict(start=59.95,end=63.817,label='공중 · 바퀴와 땅이 떨어짐'),dict(start=63.817,end=65,label='착지 · 바퀴가 다시 땅에 닿음')]
for phase,short in zip(phases,['접근','공중','착지']):phase['sideLabel']=short
f=P/'planning/game-annotation-tracks.json';d=read(f);w=next(w for w in d['windows'] if w['id']=='M25-000')
w.update(observedPhases=phases,phaseReview=note);write(f,d)
def update(x):
 if isinstance(x,list):
  for y in x:update(y)
 elif isinstance(x,dict):
  if x.get('beat')=='M25-000' and x.get('sourceId')=='xPnKcvo8A1E' and 'sourceIn' in x:
   assert x['sourceIn'] in (51,57.4,58) and x['sourceOut']==65 and x['nativeDecodeEvidence']['sourceIn']==51
   x.update(sourceIn=58,duration=7,fullOriginalAudioIn=58,minimumObservedResultOut=64.85,openingEdit=note)
   x['annotationPlan'].update(target='Follow the car body with the reviewed hollow contour. Above it, distinguish the approach, airborne interval and landing based on visible ground contact; do not infer a height or an acceleration.')
  else:
   for y in list(x.values()):update(y)
for file in ['planning/scene-bindings.json','planning/production-plan.json']:
 f=P/file;d=read(f);update(d)
 if file.endswith('production-plan.json'):d['sceneBindingsSha256']=sha(P/'planning/scene-bindings.json')
 write(f,d)
assert read(P/'planning/scene-bindings.json')['scenes'][0]['actualGamePart']['sourceIn']==58
print('Native takeoff/landing retained in 7 seconds; no narration change.')
