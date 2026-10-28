"""Provisional visual inspection only. Cannot authorize a final native render."""
from pathlib import Path
import json,hashlib
HERE=Path(__file__).resolve().parent
def save(name,d):(HERE/name).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
TITLES={'intent':'같은 레이스, 다른 첫 목표','goal':'첫 코너 하나를 직접 돌아보기','onboarding':'온보딩 · 첫 재미까지 가는 길','steering':'Smart Steering · 방향 조절 보조','acceleration':'Auto-Accelerate · 가속 유지','turbo':'드리프트에서 미니 터보로','placement':'조작은 가볍게, 놓을 자리는 직접','choice':'길을 알려 준 뒤에는 물러서기','summary':'다음 한 판을 스스로 고르게'}
plan=json.loads((HERE/'production-plan.json').read_text('utf-8'));jobs=[];cues=[]
for cut in plan['cuts']:
 if cut['kind']!='explanation':continue
 seconds=cut['provisionalDurationSeconds']or 8
 frames=round(seconds*60)
 cues.append({'id':cut['id'],'mode':cut['mode'],'title':TITLES[cut['mode']],'phaseSeconds':[seconds*.28,seconds*.62,seconds*.92],'basis':'Provisional inspection phases only; replace with measured overlapping speech cues before timing lock.'})
 jobs.append({'slug':'kind-to-beginners','cutId':cut['id'],'frames':frames,'stageClass':'D29ClarityStage','sampleFrames':[0,round(frames*.25),round(frames*.5),round(frames*.75),frames-1]})
save('unity-cues.json',{'revision':'clarity-v3','timingLocked':False,'purpose':'preflight-composition-and-mechanic-only','cuts':cues})
save('capture-jobs.json',{'revision':'clarity-v3','timingLocked':False,'purpose':'provisional-preflight-only','jobs':jobs})
print(len(jobs),'provisional native visual jobs; final render explicitly not allowed')
