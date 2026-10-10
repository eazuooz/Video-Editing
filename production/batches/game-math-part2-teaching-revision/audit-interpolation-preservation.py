"""Verify all baseline dictionaries/order/contracts and original PCM samples."""
from pathlib import Path
import json,hashlib
import numpy as np
import soundfile as sf
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
baseline=read(B/'baselines/game-math-rotation-interpolation/lesson.json')
old=read(B/'baselines/game-math-rotation-interpolation/production/timeline.json')
source,sr=sf.read(ROOT/'shared/output/game-math-rotation-interpolation/narration-final.wav',dtype='float32')
assert sr==24000
combined=[];checks=[]
for slug in ['game-math-interpolation-paths-v2','game-math-rotation-conversions-v2']:
 P=ROOT/'projects'/slug;m=read(P/'project.json');lesson=read(P/'production/lesson.json');t=read(P/'production/timeline.json')
 assert lesson['contract']==baseline['contract'];combined.extend(s for s in lesson['scenes'] if s['id'].isdigit())
 new,rate=sf.read(ROOT/m['paths']['narration'],dtype='float32');assert rate==sr
 rows=[]
 for s in t['scenes']:
  if not s['preservedOriginal']:continue
  prior=next(x for x in old['scenes'] if x['id']==s['id'])
  a=source[round(prior['start']*sr):round((prior['start']+prior['seconds'])*sr)]
  b=new[round(s['start']*sr):round((s['start']+s['seconds'])*sr)]
  assert np.array_equal(a,b),(slug,s['id'])
  assert s['frames']==prior['frames'] and s['lineStarts']==prior['lineStarts']
  rows.append({'scene':s['id'],'samples':len(a),'sha256':hashlib.sha256(a.tobytes()).hexdigest(),'unchanged':True})
 checks.append({'slug':slug,'preservedPCM':rows,'bodyFrames':t['bodyFrames'],'actualFrames':t['actualFrames'],'explanationFrames':t['explanationFrames']})
assert combined==baseline['scenes']
out={'originalSceneCount':len(combined),'allOriginalSceneDictionariesExact':True,'originalOrderAndContractExact':True,'originalKoLines':sum(len(s['ko']) for s in combined),'originalEnLines':sum(len(s['en']) for s in combined),'allOriginalPCMSamplesAndSceneTimingExact':True,'episodes':checks}
(B/'interpolation-preservation-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Original26 dictionaries/order/contracts,144KO/144EN and all PCM samples verified')
