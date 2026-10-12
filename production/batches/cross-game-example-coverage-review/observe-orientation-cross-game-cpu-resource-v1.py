"""Fresh actual CPU resource after voice closure, no GPU model or controls."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,subprocess,psutil,os
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--version',type=int,required=True);a=ap.parse_args()
out=O/f'resource-before-cross-game-CPU-v{a.version}.json';assert not out.exists()
tts=read(O/'narration-cross-game-repair-execution-v1.json');proof=read(O/'cross-game-repair-voice-closure-verification-v1.json');assert tts['actualExitObserved'] and proof['restorationVerified']
for x in tts['protectedInputs']+tts['results']:assert sha(ROOT/x['path'])==x['sha256']
processes=[];own=[]
for p in psutil.process_iter(['pid','create_time','name','cmdline']):
 try:
  cmd=' '.join(p.info['cmdline'] or [])
  if (p.info['name'] or '').lower() in ('python.exe','ffmpeg.exe','node.exe'):
   processes.append(dict(pid=p.pid,createTime=p.info['create_time'],commandLine=p.info['cmdline'],cwd=p.cwd()))
   if p.pid!=os.getpid() and any(s in cmd for s in ['unpublished-teaching-clarity-revision','cross-game-example-coverage-review']) and any(s in cmd for s in ['render-orientation','review-orientation','extract-orientation','render-motion','review-motion','build-motion-current17','assemble-motion-current17','extract-motion']):own.append(p.pid)
 except (psutil.NoSuchProcess,psutil.AccessDenied):pass
cim=subprocess.check_output(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -in @('python.exe','ffmpeg.exe','node.exe') } | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3"],text=True,encoding='utf-8',errors='replace')
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();cpu=psutil.cpu_percent(interval=2);ram=psutil.virtual_memory().available//1024
data=dict(observedAt=datetime.now(timezone.utc).isoformat(),ownHeavyJobs=len(own),ownHeavyPids=own,cpuLoadPercent=cpu,freePhysicalMemoryKiB=ram,processes=processes,cimActual=cim,gpuObservation=gpu,protectedShaMatched=True,protectedCount=len(tts['protectedInputs']),allNewPcmShaMatched=True,researchChanges=0,cpuThreads=2,gpuJobs=0)
out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8');assert not own and cpu<85 and ram>8_000_000
print(json.dumps(dict(resource=out.relative_to(ROOT).as_posix(),cpu=cpu,ramKiB=ram,ownHeavy=0,gpu=gpu)))
