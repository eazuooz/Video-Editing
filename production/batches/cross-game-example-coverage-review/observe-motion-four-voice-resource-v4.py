"""Read-only foreign restoration and one bounded stable-GPU observation."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,time,psutil
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=R/'voice-retry-resource-verification-v4.json';assert not out.exists()
failed=read(R/'research-handoff-premodel-timeout-verification-v3.json')
assert failed['restorationVerified'] and failed['newPcmCount']==0
hp=ROOT/'shared/output/gpu-handoff/d18ea27f-8070-4d80-bccb-1d6e582366e5.json';h=read(hp)
assert h['state']=='research_resume_verified' and h['ttsExitCode']==0
orig=h['queueOwner'];ident=h['resumedQueue']
assert ident['command']==orig['command'] and Path(ident['cwd']).resolve()==Path(orig['cwd']).resolve()
p=psutil.Process(ident['pid'])
assert abs(p.create_time()-ident['createTime'])<.01 and p.cmdline()==ident['command']
assert Path(p.cwd()).resolve()==Path(orig['cwd']).resolve()
status=read(Path(h['queueDir'])/'status.json');assert status['owner_pid']==p.pid
assert status['status'] in ['running','waiting_for_resources']
assert not (ROOT/'shared/output/GPU_HANDOFF.json').exists(),'Foreign lease still active; do not request another handoff.'
rows=[];start=time.monotonic()
while True:
    values=[int(x.strip()) for x in subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip().split(',')]
    rows.append(dict(observedAt=datetime.now(timezone.utc).isoformat(),elapsedSeconds=time.monotonic()-start,freeMiB=values[0],utilization=values[1]))
    if rows[-1]['elapsedSeconds']>=20:break
    time.sleep(2)
stable=all(x['freeMiB']>=18000 and x['utilization']<15 for x in rows)
protected=read(R/'narration-tts-waiting-v3.json')['protectedInputs'];assert len(protected)==68
for x in protected:assert sha(ROOT/x['path'])==x['sha256'],x['path']
proof=dict(schemaVersion=1,observedAt=datetime.now(timezone.utc).isoformat(),
    foreignHistoryPath=str(hp.relative_to(ROOT)),foreignHistorySha256=sha(hp),
    foreignRestorationVerified=True,currentOriginalResearch=dict(pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd()),
    currentResearchStatus=status,ownResearchResumeClaim=False,
    gpuObservations=rows,stableGpuIdle20SecondsVerified=stable,
    freePhysicalMemoryKiB=psutil.virtual_memory().available//1024,
    ownHeavyCpuJobs=0,all68ProtectedHashesMatched=True,protectedInputs=protected,
    processOrPauseOrLeaseMutations=0,voiceRequestStarted=False)
out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(stableGpuIdle20SecondsVerified=stable,observations=len(rows),utilizations=[x['utilization'] for x in rows],currentResearchPid=p.pid)))
