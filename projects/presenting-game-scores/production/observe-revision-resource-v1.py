from pathlib import Path
from datetime import datetime, timezone
import json, psutil, subprocess
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).parent/'revision-balatro60-v2'
ap=__import__('argparse').ArgumentParser();ap.add_argument('--output',default='voice-resource-before-v1.json');args=ap.parse_args()
rows=[];heavy=[]
for p in psutil.process_iter(['pid','ppid','name','cmdline','create_time']):
 try:
  i=p.info;cmd=' '.join(i['cmdline'] or [])
  if 'presenting-game-scores' in cmd or 'placement_focus' in cmd or 'train_multiview.py' in cmd or 'phase1_train_all_modes.py' in cmd or 'GPU_HANDOFF' in cmd or 'gpu-handoff.py' in cmd:
   row=dict(pid=i['pid'],parentPid=i['ppid'],name=i['name'],createTime=i['create_time'],commandLine=i['cmdline'],cwd=p.cwd());rows.append(row)
   # Match the executable/script, not shell text or a snapshot filename.
   # Windows venv launchers also expose the observer as a parent Python process.
   scripts=[Path(x).name for x in (i['cmdline'] or []) if x.lower().endswith('.py')]
   is_worker=any(x.startswith(('render-','review-','build-','repair-','extract-')) for x in scripts)
   is_observer=any(x.startswith(('observe-','record-','prepare-')) for x in scripts)
   is_encoder=(i['name'] or '').lower()=='ffmpeg.exe'
   if p.pid!=psutil.Process().pid and 'presenting-game-scores' in cmd and ((is_worker and not is_observer and (i['name'] or '').lower()=='python.exe') or is_encoder):heavy.append(row)
 except (psutil.AccessDenied,psutil.NoSuchProcess):pass
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.used,memory.free,utilization.gpu','--format=csv,noheader'],text=True)
queue=Path('C:/Users/eazuo/renderformer/tmp/placement_focus_20261008/status.json')
lease=ROOT/'shared/output/GPU_HANDOFF.json'
cim=subprocess.check_output(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'placement_focus|train_multiview.py|phase1_train_all_modes.py|presenting-game-scores|gpu-handoff.py' -and $_.Name -match 'python|node|ffmpeg' } | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 4"],text=True,encoding='utf-8',errors='replace')
mem=psutil.virtual_memory();cpu=psutil.cpu_percent(interval=1)
j=dict(schemaVersion=1,observedAt=datetime.now(timezone.utc).isoformat(),ownHeavyJobs=len(heavy),ownHeavyProcesses=heavy,cpuLoadPercent=cpu,freePhysicalMemoryKiB=mem.available//1024,processes=rows,cimProcesses=json.loads(cim),gpuObservation=gpu.strip(),researchStatus=json.loads(queue.read_text('utf-8-sig')),foreignLease=json.loads(lease.read_text('utf-8-sig')) if lease.exists() else None,processOrControlChanges=0)
p=BASE/args.output;assert not p.exists(),'Keep previous resource snapshots';p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({k:j[k] for k in ['observedAt','ownHeavyJobs','cpuLoadPercent','freePhysicalMemoryKiB','gpuObservation','researchStatus']},ensure_ascii=False))
