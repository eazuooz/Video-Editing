"""Cooperate with the existing lease after identifying display-only GPU usage.

This allows the inspected browser preview / Windows compositor, not unknown
compute, games, screen sharing or another narration lease. No process is stopped.
"""
from pathlib import Path
import json,subprocess,sys,uuid,time,os,atexit
import psutil
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
L=R/'shared/output/GPU_HANDOFF.json';report=H/'local/full-video-v3/display-gpu-handoff.json';report.parent.mkdir(parents=True,exist_ok=True)
if L.exists():raise SystemExit('Another GPU lease is active; preserve it.')
if any((p.info.get('name') or '').lower()=='unity.exe' and 'Unity Hub' not in (p.info.get('exe') or '') for p in psutil.process_iter(['name','exe'])):
    # Only read process identity. Do not close another editor or game.
    raise SystemExit('An Editor is still open; finish the selected build first.')
cmd=r'''$s=(Get-Counter -Counter '\GPU Engine(*)\Utilization Percentage' -SampleInterval 1 -MaxSamples 1 -ErrorAction Stop).CounterSamples;$s|Where-Object {$_.CookedValue -gt 1 -and $_.InstanceName -match 'pid_(\d+)'}|ForEach-Object {$i=[int]([regex]::Match($_.InstanceName,'pid_(\d+)').Groups[1].Value);[pscustomobject]@{pid=$i;name=(Get-Process -Id $i -ErrorAction SilentlyContinue).ProcessName;engine=([regex]::Match($_.InstanceName,'engtype_(.+)$').Groups[1].Value);percent=[math]::Round($_.CookedValue,2)}}|ConvertTo-Json -Compress'''
out=subprocess.check_output(['powershell','-NoProfile','-Command',cmd],text=True,creationflags=subprocess.CREATE_NO_WINDOW).strip();active=json.loads(out) if out else [];active=active if isinstance(active,list) else [active]
allowed={'chatgpt','dwm','claude','chrome','msedgewebview2','msedge','explorer','icanscreen','system'}
unknown=[a for a in active if a['name'].lower() not in allowed or a['engine'].lower() not in ('3d','copy')]
raw=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True,creationflags=subprocess.CREATE_NO_WINDOW);free,util=map(int,raw.splitlines()[0].replace(' ','').split(','))
if unknown or free<8192 or util>45:raise SystemExit('GPU display-only/capacity checks did not pass; other work remains untouched.')
me=psutil.Process();token=uuid.uuid4().hex;state={'schemaVersion':1,'token':token,'project':'ai-3d-lofi-gaming-room','state':'gpu_granted_to_tts','requestedAt':time.time(),'queueDir':None,'coordinator':{'pid':me.pid,'createTime':me.create_time()},'gpuBeforeTts':{'freeMiB':free,'utilization':util,'minimumFreeMiB':8192},'displayOnlyReview':active,'basis':'Current own web preview and desktop display engines identified; no active compute, game or video-encode engine. User confirmed screen sharing ended and GPU may proceed on 2026-11-17. Only display/copy engines remain; no encode/compute or game. ICanScreen is the existing C:/ICanX/ICanScreen display application. Selected tutorial-v3 uses the same Qwen model and user reference.'}
with L.open('x',encoding='utf-8') as f:json.dump(state,f,ensure_ascii=False,indent=2)
report.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8')
def release():
    if L.exists() and json.loads(L.read_text('utf-8-sig')).get('token')==token:
        state['state']='tts_process_exited';state['finishedAt']=time.time();report.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8');L.unlink()
atexit.register(release)
print(json.dumps({'knownDisplayEngines':len(active),'freeMiB':free,'utilization':util,'foreignProcessesChanged':False}),flush=True)
code=subprocess.call([sys.executable,'-X','utf8','-u',str(R/'qwen3-tts/render_narration.py'),'--project','ai-3d-lofi-gaming-room','--batch-size','1'],cwd=R,creationflags=subprocess.CREATE_NO_WINDOW)
sys.exit(code)
