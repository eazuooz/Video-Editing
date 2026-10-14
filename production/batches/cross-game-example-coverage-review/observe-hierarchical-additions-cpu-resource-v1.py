"""One new named CPU observation after the actual previous owned worker closes."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,subprocess,psutil
ROOT=Path(__file__).resolve().parents[3];V=ROOT/'projects/hierarchical-game-outlines/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for c in iter(lambda:f.read(8*1024*1024),b''):h.update(c)
 return h.hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--purpose',required=True);a=ap.parse_args()
assert a.purpose in ['whole-asr','contexts-asr','annotation-tracks']
out=V/('resource-before-additions-'+a.purpose+'-v1.json');assert not out.exists()
tts=read(V/'narration-additions-execution-v1.json');closure=read(V/'additions-voice-closure-verification-v1.json')
assert tts['actualExitObserved'] and tts['exitCode']==0 and closure['ownedIdleLeaseClosed']
for item in tts['protectedInputs']+tts['results']:assert sha(ROOT/item['path'])==item['sha256'],item['path']
me=psutil.Process();excluded={me.pid,*[p.pid for p in me.parents()]};processes=[];own=[]
for p in psutil.process_iter(['pid','create_time','cmdline','name']):
 try:
  if (p.info['name'] or '').lower() not in ['python.exe','ffmpeg.exe','node.exe']:continue
  row=dict(pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd());processes.append(row)
  cmd=' '.join(p.cmdline())
  if p.pid not in excluded and 'hierarchical' in cmd and any(x in cmd for x in ['render-','review-','extract-','assemble-','acquire-','track-']):own.append(row)
 except (psutil.NoSuchProcess,psutil.AccessDenied):pass
assert not own,own
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True)
cim=subprocess.check_output(['powershell.exe','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -in @('python.exe','ffmpeg.exe','node.exe') } | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3 -Compress"],encoding='utf8',errors='replace')
research=Path('C:/Users/eazuo/renderformer/tmp/placement_focus_20261008/status.json')
assert sha(research)==closure['researchStatusSha256']
cpu=psutil.cpu_percent(interval=.5);ram=psutil.virtual_memory().available//1024
assert cpu<85 and ram>8_000_000
record=dict(observedAt=datetime.now(timezone.utc).isoformat(),purpose=a.purpose,
 cpuLoadPercent=cpu,freePhysicalMemoryKiB=ram,ownHeavyJobs=0,gpuJobs=0,cpuThreads=2,
 processes=processes,cimActual=cim,gpuCsv=gpu.strip(),protectedInputCount=len(tts['protectedInputs']),
 allCurrentProtectedAndNewPcmShaMatched=True,researchStatusSha256=sha(research),researchProcessOrLeaseChanges=0,
 currentOrientationMainTransition='current34-main-schedule-update-v1.json',old79GuardUsed=False)
out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps(dict(resource=out.relative_to(ROOT).as_posix(),cpu=cpu,ramKiB=ram,ownHeavyJobs=0,protected=len(tts['protectedInputs']),gpuJobs=0)))
