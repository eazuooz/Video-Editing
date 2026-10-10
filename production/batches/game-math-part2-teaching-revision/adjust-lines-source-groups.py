"""Fit measured narration to already compared native cuts; preserve supplied text.

Move the fixed45-degree reminder into an independent explanation rather than
implying a measured angle in game pixels. Reuse its exact generated PCM later.
"""
from pathlib import Path
import json,copy,hashlib
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
source=read(B/'lines-game-insertions.json');by_id={s['id']:s for s in source['scenes']}
s=by_id['LG01'];s['intervals']=[[40,56.5],[72,85],[85,98]];s['sourceGroupStartsAtLines']=[0,1,2];s['maximumSeconds']=42.5
s['selection']['chosenReason']+=' The already played P04[70,99.5] also shows85–98 route traversal; its adjacent85 boundary lets the projection reminder follow the visible receiver result without a false new camera cut.'
s['selection']['additionalComparedRange']={'interval':[85,98],'nativeCandidate':'P04[70,99.5]','role':'receiver result → route traversal while distinguishing screen projection','retimingAfterMeasuredAudio':True}
s=by_id['LG07'];s['intervals'][-1]=[719,731];s['maximumSeconds']=36
s['selection']['additionalComparedRange']={'interval':[719,723],'nativeCandidate':'S03[705,740]','role':'approach the same close hut before crossing its visible wall/post','retimingAfterMeasuredAudio':True}
for row in s['selection']['priorUseOverlap']:
 if row['existingLesson']=='game-math-planes-barycentric':row['overlap']=[719,731]
write(B/'lines-game-insertions.json',source)
main=ROOT/'projects/game-math-bounds-transform-v2';lesson=read(main/'production/lesson.json');lg06=next(s for s in lesson['scenes'] if s['id']=='LG06')
if not any(s['id']=='LB06' for s in lesson['scenes']):
 bridge={'id':'LB06','title':'예시 각도와 게임의 화면 관찰을 구분합니다','kind':'explanation','sourceType':'supplement','ko':[lg06['ko'][-1]],'en':[lg06['en'][-1]],'preservation':'Exact last LG06 narration moved beside its game example; use unchanged current generated samples','contract':'same fixed axes and45° square example as original18; no game-world angle inferred'}
 lg06['ko']=lg06['ko'][:-1];lg06['en']=lg06['en'][:-1];at=lesson['scenes'].index(lg06)+1;lesson['scenes'].insert(at,bridge)
for slug in ['game-math-lines-circles-v2','game-math-bounds-transform-v2']:
 P=ROOT/'projects'/slug;l=lesson if slug=='game-math-bounds-transform-v2' else read(P/'production/lesson.json')
 for s in l['scenes']:
  if s['id'] in ['LG01','LG07']:
   for key in ['intervals','sourceGroupStartsAtLines','maximumSeconds','selection']:s[key]=copy.deepcopy(by_id[s['id']][key])
 write(P/'production/lesson.json',l)
 for lang in ['ko','en']:
  p=P/f'script/narration.{lang}.json';script=read(p);script['scenes']=[{'id':s['id'],'title':s['title'],'lines':s[lang]} for s in l['scenes']];write(p,script)
flow=read(B/'lines-episode-flow-audit.json');second=next(e for e in flow['episodes'] if e['slug']=='game-math-bounds-transform-v2')
if 'LB06' not in second['order']:second['order'].insert(second['order'].index('LG06')+1,'LB06')
flow['generatedNarrationPreservation']={'LG06':'first3 original generated lines remain actual footage','LB06':'exact fourth generated line becomes independent explanation','newTtsWordsNeeded':False,'allSuppliedOriginal22ScenesUnchanged':True};write(B/'lines-episode-flow-audit.json',flow)
write(B/'lines-measured-cut-adjustments.json',{'sourceChanges':['LG01 third adjacent85–98 route result from previously playedP04','LG07 approach719–723 from previously playedS03'],'generatedTextAndAudio':'all words retained; LG06 last line reclassified as independent explanation','audioSplit':'not yet performed; exact completed line provenance required','original22DictionariesOrderAndPcm':'preserved','movingPixelsAndRatio':'pending'})
print('Measured cut groups updated; exact last narration line moved to its own explanation. Originals and frozen TTS scripts unchanged.')
