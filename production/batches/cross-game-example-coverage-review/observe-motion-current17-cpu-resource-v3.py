"""Read actual resources/process identities for one serial CPU mix; no controls."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,psutil
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
protected=read(R/'narration-first-paragraph-repair-execution-v1.json')['protectedInputs'];assert len(protected)==71
for p in protected:assert sha(ROOT/p['path'])==p['sha256']
heavy=[];processes=[]
for p in psutil.process_iter(['pid','create_time','name','cmdline']):
 try:
  cmd=' '.join(p.info['cmdline'] or []);name=(p.info['name'] or '').lower()
  if name in ('python.exe','ffmpeg.exe','node.exe'):
   processes.append(dict(pid=p.pid,createTime=p.info['create_time'],commandLine=p.info['cmdline'],cwd=p.cwd()))
   if p.pid!=psutil.Process().pid and 'cross-game-example-coverage-review' in cmd and any(s in cmd for s in ['render-motion','build-motion-current17','review-motion','extract-motion','assemble-motion-current17']):heavy.append(p.pid)
 except (psutil.NoSuchProcess,psutil.AccessDenied):pass
cim=subprocess.check_output(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -in @('python.exe','ffmpeg.exe','node.exe') } | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3"],text=True,encoding='utf-8',errors='replace')
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip()
cpu=psutil.cpu_percent(interval=2);mem=psutil.virtual_memory().available//1024
status=Path('D:/Github/RenderFormer')
out=R/'current17-cpu-resource-v3.json';assert not out.exists()
data=dict(observedAt=datetime.now(timezone.utc).isoformat(),cpuLoadPercent=cpu,freePhysicalMemoryKiB=mem,ownHeavyCpuJobs=len(heavy),ownHeavyPids=heavy,gpuObservation=gpu,processes=processes,cimActual=cim,protectedInputCount=71,protectedShaMatched=True,researchManipulations=0,foreignLeaseManipulations=0,cpuThreads=2,gpuJobs=0)
out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
assert not heavy and cpu<85 and mem>8_000_000
print(json.dumps(dict(resource=out.relative_to(ROOT).as_posix(),cpu=cpu,freeRamKiB=mem,gpu=gpu,ownHeavy=0,protected=71)))
