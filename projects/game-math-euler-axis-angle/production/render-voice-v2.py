"""Bounded GPU-only scene batch; preserve all other applications and source PCM."""
from pathlib import Path
import datetime, hashlib, json, os, psutil, subprocess, sys, time, uuid

R = Path(__file__).resolve().parents[3]
P = R / 'projects/game-math-euler-axis-angle'
L = P / 'production/local/revision-v2'
LEASE = R / 'shared/output/GPU_HANDOFF.json'
L.mkdir(parents=True, exist_ok=True)
def read(p): return json.loads(p.read_text(encoding='utf8'))
def save(p, v): p.write_text(json.dumps(v, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
def gpu():
    raw = subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,memory.total,utilization.gpu','--format=csv,noheader,nounits'], text=True)
    return [int(x.strip()) for x in raw.splitlines()[0].split(',')]

control = read(R/'shared/publishing/video-production-control.json')
assert control['selectedVideo'] == P.name
assert control['selectedDelivery']['slug'] == P.name
assert not LEASE.exists(), 'Preserve existing GPU lease'
me = psutil.Process()
family = {p.pid for p in [me, *me.parents()]}
foreign = [p.pid for p in psutil.process_iter(['name']) if p.pid not in family and (p.info['name'] or '').lower().startswith('python')]
assert not foreign, ('Other compute remains untouched', foreign)
allowed = set(('crossdeviceresume.exe explorer.exe startmenuexperiencehost.exe searchhost.exe msedgewebview2.exe chrome.exe phoneexperiencehost.exe chatgpt.exe amdrssrcext.exe textinputhost.exe logioptionsplus_agent.exe codex-computer-use-swift.exe icue.exe steamwebhelper.exe discord.exe razerappengine.exe microsoftsecurityapp.exe applicationframehost.exe todo.exe icloudhome.exe mmgaserver.exe icloudphotos.exe claude.exe msedge.exe parsecd.exe radeonsoftware.exe notion.exe shellexperiencehost.exe obs64.exe obs-browser-page.exe devenv.exe icanscreen.exe icanrecorder.exe shellhost.exe systemsettings.exe snippingtool.exe unity.exe').split())
allowed.update({'nvidia overlay.exe','unity hub.exe','microsoft.media.player.exe','edgegameassist.exe'})
# Edge Game Assist was verified as the installed Microsoft Store-signed
# Microsoft.Edge.GameAssist package. It remains open with all other desktop apps.
raw = subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'], text=True)
clients=[]
for row in raw.splitlines():
    pid, name = row.split(',',1); base=Path(name.strip()).name.lower()
    assert base in allowed, ('Unrecognized GPU client preserved',base)
    clients.append({'pid':int(pid),'name':base})
before = gpu()
assert before[0] >= 8000, ('Bounded profile needs8000MiB free',before)
token = str(uuid.uuid4())
state = dict(schemaVersion=1,token=token,project=P.name,state='gpu_granted_to_tts',requestedAt=time.time(),queueDir=None,coordinator={'pid':me.pid,'createTime':me.create_time()},gpuBeforeTts={'freeMiB':before[0],'totalMiB':before[1],'utilization':before[2]},inspectedClients=clients,foreignProcessesPaused=[],userEvidence='User-selected M04 production; bounded GPU allocation preserves all existing apps',allocatorLimitMiB=7168,profile='bf16-scene-batch1-bounded-8GiB',generations=[])
with LEASE.open('x',encoding='utf8') as f: json.dump(state,f,indent=2)
code=1
try:
    sys.path.insert(0,str(R/'qwen3-tts'))
    import torch
    torch.cuda.set_per_process_memory_fraction(7168*1024*1024/torch.cuda.get_device_properties(0).total_memory,0)
    import render_narration as worker
    worker.configure_project(P.name,'projects/game-math-euler-axis-angle/production/revision-v2/tts-manifest.json')
    worker.load_tts_dependencies()
    generate = worker.Qwen3TTSModel.generate_voice_clone
    def measured(self,*args,**kwargs):
        result=generate(self,*args,**kwargs)
        state['generations'].append({'textSha256':hashlib.sha256(json.dumps(kwargs.get('text'),ensure_ascii=False).encode()).hexdigest(),'peakAllocatedMiB':torch.cuda.max_memory_allocated()/1048576,'peakReservedMiB':torch.cuda.max_memory_reserved()/1048576,'at':time.time()})
        save(L/'tts-gpu-coordination.json',state)
        print('GPU memory:',state['generations'][-1],flush=True)
        return result
    worker.Qwen3TTSModel.generate_voice_clone=measured
    items=worker.build_render_items(worker.load_jobs())
    worker.render_chunks(items,1)
    worker.assemble_outputs(worker.load_jobs())
    code=0
finally:
    state.update(state='finished' if code==0 else 'failed',exitCode=code,finishedAt=time.time(),foreignProcessesRestored=[])
    save(L/'tts-gpu-coordination.json',state)
    if LEASE.exists() and read(LEASE).get('token')==token: LEASE.unlink()
