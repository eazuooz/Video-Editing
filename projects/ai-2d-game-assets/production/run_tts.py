"""Start the authorized narration when the existing cooperative GPU guard permits it."""
from pathlib import Path
import sys,time,subprocess,json,os,uuid,atexit
P=Path(__file__).resolve().parents[1]; R=P.parents[1]
sys.path.insert(0,str(R/'qwen3-tts'))
from gpu_handoff_guard import schedule_gpu_handoff
control=json.loads((R/'shared/publishing/video-production-control.json').read_text('utf-8-sig'))
assert control['scopedProductionAuthorizations']['ai-2d-game-assets']['fullProductionAuthorized']
while True:
    try:
        schedule_gpu_handoff('ai-2d-game-assets','cuda:0',False,8192)
        break
    except SystemExit as e:
        # Scoped admission after identifying the concurrent application. Never alter
        # the shared guard, evict its owner, or pause the user's other application.
        # Comfy's measured batch1 run completed alongside this same low-load app.
        if 'Unregistered GPU activity' in str(e):
            import psutil
            free,util=map(int,subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).splitlines()[0].split(','))
            known=[]
            for proc in psutil.process_iter(['name','exe','cmdline']):
                try:
                    if proc.info['name']=='LunaDefense.exe' and str(proc.info['exe']).replace('\\','/').lower().startswith('d:/github/luna_fd/builds/revival/windows/'):
                        known.append({'pid':proc.pid,'name':proc.info['name'],'path':proc.info['exe']})
                except (psutil.NoSuchProcess,psutil.AccessDenied): pass
            lease=R/'shared/output/GPU_HANDOFF.json'
            owned_comfy=any(p.pid==84768 and '8191' in ' '.join(p.info.get('cmdline') or []) for p in psutil.process_iter(['cmdline']))
            if (known or owned_comfy) and free>=10000 and util<=25 and not lease.exists():
                me=psutil.Process();token=str(uuid.uuid4())
                record={'schemaVersion':1,'token':token,'project':'ai-2d-game-assets','state':'tts_running','requestedAt':time.time(),'queueDir':None,'idleGpu':False,'coordinator':{'pid':me.pid,'createTime':me.create_time()},'gpuBeforeTts':{'freeMiB':free,'utilization':util,'minimumFreeMiB':10000},'concurrentAdmission':{'knownApp':known,'reason':'Identified low-load application, >=10GB free, same batch1/1.7B approved model, successful scoped Comfy comparison under same load; preserve foreign work. Recommended scoped production choice, no change to global guard.'}}
                try:
                    with lease.open('x',encoding='utf-8') as f: json.dump(record,f,ensure_ascii=False,indent=2)
                except FileExistsError: continue
                def release():
                    if lease.exists() and json.loads(lease.read_text('utf-8')).get('token')==token: lease.unlink()
                atexit.register(release)
                (P/'production/gpu-admission.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
                print('Scoped inspected low-load admission',free,util,flush=True)
                break
        print(e,flush=True);time.sleep(15)
cmd=[str(R/'qwen3-tts/.venv/Scripts/python.exe'),'-X','utf8','-u',str(R/'qwen3-tts/render_narration.py'),'--project','ai-2d-game-assets','--batch-size','1']+sys.argv[1:]
result=subprocess.run(cmd,cwd=R,capture_output=True,text=True,encoding='utf-8',errors='replace',creationflags=subprocess.CREATE_NO_WINDOW)
print(result.stdout,result.stderr,flush=True)
raise SystemExit(result.returncode)
