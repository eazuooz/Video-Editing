"""One read-only bounded observation; require a continuous20s idle interval."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,time,psutil
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=R/'voice-retry-resource-verification-v5.json';assert not out.exists()
previous=read(R/'voice-retry-resource-verification-v4.json')
assert not previous['stableGpuIdle20SecondsVerified']
hp=ROOT/previous['foreignHistoryPath'];h=read(hp)
assert h['state']=='research_resume_verified'
ident=h['resumedQueue'];p=psutil.Process(ident['pid'])
assert abs(p.create_time()-ident['createTime'])<.01 and p.cmdline()==ident['command']
assert Path(p.cwd()).resolve()==Path(ident['cwd']).resolve()
rows=[];start=time.monotonic();idle=None;stable=False;foreignLease=None
while True:
    lease=ROOT/'shared/output/GPU_HANDOFF.json'
    if lease.exists():foreignLease=read(lease);break
    vals=[int(x.strip()) for x in subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip().split(',')]
    stamp=time.monotonic();row=dict(observedAt=datetime.now(timezone.utc).isoformat(),elapsedSeconds=stamp-start,freeMiB=vals[0],utilization=vals[1]);rows.append(row)
    if vals[0]>=18000 and vals[1]<15:
        if idle is None:idle=stamp
        stable=stamp-idle>=20
    else:idle=None
    if stable or stamp-start>=56:break
    time.sleep(2)
status=read(Path(h['queueDir'])/'status.json')
for x in previous['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
proof=dict(schemaVersion=1,observedAt=datetime.now(timezone.utc).isoformat(),
    previousObservation='voice-retry-resource-verification-v4.json',foreignHistoryPath=previous['foreignHistoryPath'],foreignHistorySha256=sha(hp),
    foreignRestorationVerified=True,currentOriginalResearch=dict(pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd()),
    currentResearchStatus=status,ownResearchResumeClaim=False,gpuObservations=rows,
    stableGpuIdle20SecondsVerified=stable,currentForeignLease=foreignLease,
    currentOriginalQueueAlive=p.is_running(),freePhysicalMemoryKiB=psutil.virtual_memory().available//1024,
    ownHeavyCpuJobs=0,all68ProtectedHashesMatched=True,protectedInputs=previous['protectedInputs'],
    processOrPauseOrLeaseMutations=0,voiceRequestStarted=False)
out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(stableGpuIdle20SecondsVerified=stable,observations=len(rows),utilizations=[x['utilization'] for x in rows],foreignLease=foreignLease is not None)))
