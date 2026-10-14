"""Read actual identities; update only this series checkpoint without media work."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,psutil
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
stamp=lambda:datetime.now(timezone.utc).isoformat()
execution=BASE/'native-followup-execution-v121.json'
state=read(execution)
history_path=ROOT/'shared/output/gpu-handoff'/(state['leaseToken']+'.json')
history=read(history_path)
identity=state['actualIdentity'];alive=False
try:
    p=psutil.Process(identity['pid'])
    alive=abs(p.create_time()-identity['createTime'])<.01 and p.cmdline()==identity['command'] and p.cwd()==identity['cwd']
except (psutil.NoSuchProcess,psutil.AccessDenied):pass
record=dict(recordedAt=stamp(),sessionId=72065,execution=dict(path=execution.relative_to(ROOT).as_posix(),sha256=sha(execution)),status=state['status'],actualIdentity=identity,identityMatchedAlive=alive,gpuJobs=1 if alive else 0,cpuThreads=2 if alive else 0,researchHistory=dict(path=history_path.relative_to(ROOT).as_posix(),sha256=sha(history_path),state=history['state']),completedTechnicalTakes=len(state['results']),generationComplete=state['generationComplete'],researchRestorationObserved=history['state']=='research_resume_verified',wholeAsrApproved=False,independentContextAsrApproved=False,finalMixedAsrApproved=False,allFinalPixelsReviewed=False,uploaded=False,next='Preserve all generated takes; accept individual technical passes only. After actual research restoration select five passing takes and recognize only ten full/context windows, then current classified native/moving production.')
out=BASE/'native-followup-progress-v125.json'
out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
checkpoint=ROOT/'production/research/game-lighting-history/checkpoint.json'
before=sha(checkpoint);j=read(checkpoint)
j['episode04NativeFollowupV125']={**record,'record':out.relative_to(ROOT).as_posix()}
j['updatedAt']=record['recordedAt']
tmp=checkpoint.with_name(checkpoint.name+'.writing-'+str(os.getpid()))
tmp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
if sha(checkpoint)!=before:raise RuntimeError('Concurrent checkpoint edit; preserve without overwrite')
os.replace(tmp,checkpoint)
print(json.dumps({k:record[k] for k in ['status','identityMatchedAlive','gpuJobs','completedTechnicalTakes','researchRestorationObserved']},ensure_ascii=False))
