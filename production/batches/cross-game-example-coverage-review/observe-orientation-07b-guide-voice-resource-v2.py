"""One fresh read-only observation; never manipulate research or foreign controls."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,psutil,time,os
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.now(timezone.utc).isoformat()
out=O/'resource-before-07b-guide-repair-voice-v2.json';assert not out.exists()
request=read(O/'narration-07b-guide-repair-request-v1.json');protected=request['protectedInputs'];assert len(protected)==76
for x in protected:assert sha(ROOT/x['path'])==x['sha256'],x['path']
processes=[];own=[]
for p in psutil.process_iter(['pid','create_time','name','cmdline']):
 try:
  cmd=' '.join(p.info['cmdline'] or [])
  if (p.info['name'] or '').lower() in ('python.exe','ffmpeg.exe','node.exe'):
   processes.append(dict(pid=p.pid,createTime=p.info['create_time'],commandLine=p.info['cmdline'],cwd=p.cwd()))
   if p.pid!=os.getpid() and any(s in cmd for s in ['unpublished-teaching-clarity-revision','cross-game-example-coverage-review']) and any(s in cmd for s in ['render-orientation','review-orientation','extract-orientation','render-motion','review-motion','build-motion-current17','assemble-motion-current17','extract-motion']):own.append(p.pid)
 except (psutil.NoSuchProcess,psutil.AccessDenied):pass
cim=subprocess.check_output(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -in @('python.exe','ffmpeg.exe','node.exe') } | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3"],text=True,encoding='utf-8',errors='replace')
statusp=Path('C:/Users/eazuo/renderformer/tmp/placement_focus_20261008/status.json');status=read(statusp)
ownerpid=status.get('owner_pid');owner=next((x for x in processes if x['pid']==ownerpid),None)
leasep=ROOT/'shared/output/GPU_HANDOFF.json';lease=read(leasep) if leasep.exists() else None
cpu=psutil.cpu_percent(interval=2);ram=psutil.virtual_memory().available//1024
samples=[];stable=None;started=time.monotonic();ok=False
while True:
 raw=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();free,util=map(int,raw.splitlines()[0].replace(' ','').split(','));stamp=time.monotonic()
 samples.append(dict(observedAt=now(),freeMiB=free,utilization=util))
 if free>=18000 and util<15:
  if stable is None:stable=stamp
  if stamp-stable>=20:ok=True;break
 else:stable=None
 if lease or own or stamp-started>=56:break
 time.sleep(2)
current=read(statusp);assert current==status,'Research state changed during observation; inspect its new exact identity before requesting.'
researchComplete=status.get('status')=='complete_pending_visual_review' and status.get('completed')==status.get('total')==1088 and owner is None
for x in protected:assert sha(ROOT/x['path'])==x['sha256'],x['path']
lease_after=read(leasep) if leasep.exists() else None
data=dict(observedAt=now(),cpuLoadPercent=cpu,freePhysicalMemoryKiB=ram,processes=processes,cimActual=cim,ownHeavyPids=own,ownHeavyJobs=len(own),gpuSamples=samples,stableGpuIdle20SecondsVerified=ok,foreignLeaseBefore=lease,foreignLeaseAfter=lease_after,research=dict(statusPath=str(statusp),statusSha256=sha(statusp),status=status,actualOwnerProcess=owner,completedQueuePreserved=researchComplete),protectedInputs=protected,protectedShaMatched=True,voiceEligibleAtObservation=ok and not own and not lease_after and researchComplete and cpu<85 and ram>8_000_000,modelLoaded=False,newRequestCount=0,researchProcessOrControlChanges=0)
out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(resource=out.relative_to(ROOT).as_posix(),samples=len(samples),stable20s=ok,voiceEligible=data['voiceEligibleAtObservation'],researchCompletePreserved=researchComplete,ownHeavy=len(own),cpu=cpu,ramKiB=ram,lastGpu=samples[-1],protected=len(protected))))
