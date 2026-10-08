"""Preserve a pre-state resource rejection; no media or foreign process changes."""
from pathlib import Path
from datetime import datetime, timezone
import json, os
ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,j):
    t=p.with_name(p.name+f'.{os.getpid()}.writing')
    t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8'); os.replace(t,p)
resource='shared/output/player-customization/research/resources-before-yareli155-native-v1.json'
r=read(ROOT/resource)
assert not (BASE/'yareli155-native-inspection-execution-v1.json').exists()
assert not (ROOT/'shared/output/player-customization/research/yareli-devstream155-native-v1').exists()
record=dict(schemaVersion=1,slug='player-customization',recordedAt=now(),
    attemptedAt='2026-10-08T02:39:46+00:00',actualPreStateExitCode=1,
    reason='CPU85 failed strict CPU<85 guard before state/media directory creation.',
    latestResourceEvidence=resource,latestObservedAt=r['observedAt'],
    latestCpuLoadPercent=r['cpuLoadPercent'],ownHeavyJobs=r['ownHeavyJobs'],
    workerStarted=False,stateCreated=False,mediaOutputCreated=False,
    thresholdWeakened=False,foreignProcessesTerminated=0,
    next='Recheck real resources; run the prepared single CPU2/GPU0 native inspection only when strict guard passes. Continue light source/role preparation meanwhile.')
p=BASE/'yareli155-native-prestart-resource-wait-v1.json';save(p,record)
cp=read(BASE/'latest-checkpoint.json')
cp.update(stage='fresh-yareli-native-prestart-resource-wait',recordedAt=now(),
    nativeResourceWait=p.relative_to(ROOT).as_posix(),latestResources=resource,
    nextAction=record['next'])
save(BASE/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp)
i=next(i for i in q['items'] if i['slug']=='player-customization')
i.update(stage=cp['stage'],nativeResourceWait=cp['nativeResourceWait'],nextAction=cp['nextAction'])
q['updatedAt']=now();save(qp,q)
print(json.dumps({'workerStarted':False,'resourceCpu':r['cpuLoadPercent'],'stateCreated':False}))
