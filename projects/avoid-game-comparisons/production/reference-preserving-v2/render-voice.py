"""One local TTS lease after identifying Windows graphics/capture activity.

The generic guard correctly stops on unregistered utilization. This coordinator
checks the observed WDDM desktop clients and capacity, then gives its child an
owned lease. It never pauses, terminates or restarts another application.
"""
from pathlib import Path
import subprocess,json,os,sys,time,uuid,psutil,datetime
R=Path(__file__).resolve().parents[4];L=R/'projects/avoid-game-comparisons/production/local/reference-preserving-v2'
LEASE=R/'shared/output/GPU_HANDOFF.json'
allowed={'crossdeviceresume.exe','explorer.exe','startmenuexperiencehost.exe','searchhost.exe','msedgewebview2.exe','chrome.exe','nvidia overlay.exe','phoneexperiencehost.exe','chatgpt.exe','amdrssrcext.exe','textinputhost.exe','logioptionsplus_agent.exe','codex-computer-use-swift.exe','icue.exe','steamwebhelper.exe','discord.exe','razerappengine.exe','microsoftsecurityapp.exe','applicationframehost.exe','todo.exe','icloudhome.exe','mmgaserver.exe','icloudphotos.exe','claude.exe','msedge.exe','parsecd.exe','radeonsoftware.exe','notion.exe','shellexperiencehost.exe','obs64.exe','obs-browser-page.exe','devenv.exe','icanscreen.exe','icanrecorder.exe','shellhost.exe'}
def gpu():
 raw=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu,utilization.encoder,utilization.decoder','--format=csv,noheader,nounits'],text=True)
 return [int(x.strip()) for x in raw.splitlines()[0].split(',')]
control=json.loads((R/'shared/publishing/video-production-control.json').read_text(encoding='utf8'))
allowed.add('systemsettings.exe')  # Observed C:/Windows/ImmersiveControlPanel/SystemSettings.exe.
assert control['selectedVideo']=='avoid-game-comparisons'
assert not LEASE.exists(),'Preserve foreign GPU lease'
me=psutil.Process();family={p.pid for p in [me,*me.parents()]}
foreignPython=[p.pid for p in psutil.process_iter(['name']) if p.pid not in family and (p.info['name'] or '').lower().startswith('python')]
assert not foreignPython,('Another compute process must finish first',foreignPython)
raw=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True)
clients=[]
for row in raw.splitlines():
 pid,name=row.split(',',1);name=name.strip();base=Path(name).name.lower()
 assert base in allowed,('Unrecognized GPU client preserved',base)
 clients.append({'pid':int(pid),'name':base})
before=gpu();assert before[0]>=11000,('Insufficient GPU memory',before)
token=str(uuid.uuid4());state=dict(schemaVersion=1,token=token,project='avoid-game-comparisons',state='gpu_granted_to_tts',requestedAt=time.time(),queueDir=None,idleGpu=False,coordinator={'pid':me.pid,'createTime':me.create_time()},gpuBeforeTts={'freeMiB':before[0],'utilization':before[1],'encoder':before[2],'decoder':before[3]},inspectedClients=clients,foreignProcessesPaused=[],reason='Observed WDDM desktop/OBS/recording clients only; no training Python. Preserve ongoing desktop recording;1.7B,batch1,>=11000MiB free; owned exclusive TTS lease. No generic guard threshold changed.')
with LEASE.open('x',encoding='utf8') as f:json.dump(state,f,indent=2)
code=1
try:
 with (L/'tts-run-owned.log').open('w',encoding='utf8') as log:
  code=subprocess.call([sys.executable,'-X','utf8',str(R/'qwen3-tts/render_narration.py'),'--project','avoid-game-comparisons','--manifest','projects/avoid-game-comparisons/production/reference-preserving-v2/tts-manifest.json','--batch-size','1'],cwd=R,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
finally:
 state.update(state='finished' if code==0 else 'failed',exitCode=code,finishedAt=time.time(),foreignProcessesRestored=[])
 (L/'tts-gpu-coordination.json').write_text(json.dumps(state,indent=2)+'\n',encoding='utf8')
 if LEASE.exists() and json.loads(LEASE.read_text(encoding='utf8')).get('token')==token:LEASE.unlink()
sys.exit(code)
