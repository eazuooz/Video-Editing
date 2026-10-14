"""Read-only bounded fresh GPU idle observation after the v4 content failure."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,time,psutil
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=R/'voice-retry-resource-verification-v6.json';assert not out.exists()
old=read(R/'voice-retry-resource-verification-v5.json');failure=read(R/'research-handoff-premodel-failure-verification-v4.json')
assert failure['restorationVerified'] and failure['newPcmCount']==0
hp=ROOT/'shared/output/gpu-handoff/a5373dcb-af59-4431-b6b9-41eb1b89f07a.json';h=read(hp);assert h['state']=='research_resume_verified'
ident=h['resumedQueue'];p=psutil.Process(ident['pid']);assert abs(p.create_time()-ident['createTime'])<.01 and p.cmdline()==ident['command'] and p.cwd()==ident['cwd']
rows=[];start=time.monotonic();idle=None;stable=False;lease=None
while True:
    lp=ROOT/'shared/output/GPU_HANDOFF.json'
    if lp.exists():lease=read(lp);break
    vals=[int(x.strip()) for x in subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip().split(',')]
    stamp=time.monotonic();rows.append(dict(observedAt=datetime.now(timezone.utc).isoformat(),elapsedSeconds=stamp-start,freeMiB=vals[0],utilization=vals[1]))
    if vals[0]>=18000 and vals[1]<15:
        if idle is None:idle=stamp
        stable=stamp-idle>=20
    else:idle=None
    if stable or stamp-start>=56:break
    time.sleep(2)
for x in old['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
proof=dict(schemaVersion=1,observedAt=datetime.now(timezone.utc).isoformat(),previousObservation='voice-retry-resource-verification-v5.json',
    restorationVerified=True,restorationScope='Verified actual own v4 restoration; earlier foreign restoration remains separate history.',
    historyPath=hp.relative_to(ROOT).as_posix(),historySha256=sha(hp),currentOriginalResearch=dict(pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd()),
    currentResearchStatus=read(Path(h['queueDir'])/'status.json'),gpuObservations=rows,stableGpuIdle20SecondsVerified=stable,currentForeignLease=lease,
    currentOriginalQueueAlive=p.is_running(),all68ProtectedHashesMatched=True,protectedInputs=old['protectedInputs'],
    freePhysicalMemoryKiB=psutil.virtual_memory().available//1024,ownHeavyCpuJobs=0,processOrPauseOrLeaseMutations=0,voiceRequestStarted=False)
out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(stableGpuIdle20SecondsVerified=stable,observations=len(rows),utilizations=[x['utilization'] for x in rows],foreignLease=lease is not None)))
