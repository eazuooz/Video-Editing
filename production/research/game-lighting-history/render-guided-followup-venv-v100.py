"""Resume ten unstarted takes after a verified pre-model import failure using the virtual environment.

The wait only reruns --check against a human/assistant-reviewed preflight file.
It never changes/approves a preflight itself or starts a model on stale evidence.
Research always restores through the original handoff coordinator on exit.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[3]; BASE=ROOT/'projects/game-lighting-history-04/production'
EXECUTION=BASE/'guided-followup-venv-execution-v100.json'; dry='--dry-run' in sys.argv
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text('utf-8-sig'))
stamp=lambda:datetime.now(timezone.utc).isoformat()
requests=[BASE/'guided-tail-repair-request-v83.json',BASE/'hogwarts-observation-tts-request-v85.json']
bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in requests]
failed_history=ROOT/'shared/output/gpu-handoff/648db43a-6f24-4a4c-8bd2-cb37c8f3a5ef.json'
def duplicate():
    p=subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe','scripts/review-video-duplicates.cjs','game-lighting-history-04','--candidate-file','production/research/game-lighting-history/candidate-04.json','--check'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace',creationflags=subprocess.CREATE_NO_WINDOW)
    return p.returncode,p.stdout,p.stderr
def verify():
    old=read(failed_history)
    if old.get('state')!='research_resume_verified' or old.get('ttsExitCode')!=1: raise RuntimeError('Verify prior pre-model failure and actual research restoration first')
    previous=read(BASE/'guided-followup-current-execution-v98.json')
    if previous.get('exitCode')!=1 or previous.get('generationComplete') or len(previous.get('jobs',[]))!=1 or previous['jobs'][0]['exitCode']!=1: raise RuntimeError('Inspect previous dependency failure first')
    dependency_log=ROOT/previous['jobs'][0]['log']
    if "ModuleNotFoundError: No module named 'soundfile'" not in dependency_log.read_text('utf-8'): raise RuntimeError('Only pre-model soundfile import recovery authorized')
    for b in bindings:
        if sha(ROOT/b['path'])!=b['sha256']: raise RuntimeError('Request changed')
    for p in requests:
        r=read(p)
        for x in r['protectedInputs']:
            if sha(ROOT/x['path'])!=x['sha256']: raise RuntimeError('Protected input changed '+x['path'])
        for x in r['scenes']:
            if (ROOT/x['path']).exists(): raise RuntimeError('Preserve existing take '+x['id'])
    if any((BASE/name).exists() for name in ['guided-tail-repair-execution-v83.json','hogwarts-observation-tts-execution-v85.json']): raise RuntimeError('Inspect existing partial child work')
    if EXECUTION.exists(): raise RuntimeError('Preserve previous current execution')
verify()
# Probe the same virtual environment before leasing research resources.
venv=ROOT/'qwen3-tts/.venv/Scripts/python.exe'
if Path(sys.executable).resolve()!=venv.resolve(): raise RuntimeError('Launch through the approved Qwen virtual environment')
probe=subprocess.run([str(venv),'-X','utf8','-c',"import sys,soundfile,psutil,torch,qwen_tts; print(sys.executable); print(soundfile.__file__); print(qwen_tts.__file__)"],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace',creationflags=subprocess.CREATE_NO_WINDOW)
if probe.returncode: print(probe.stderr,file=sys.stderr); raise RuntimeError('Virtual-environment dependencies failed before handoff')
print(probe.stdout,flush=True)
code,out,err=duplicate()
if code: print(err,file=sys.stderr);raise SystemExit(code)
print(out,end='',flush=True)
sys.path.insert(0,str(ROOT/'qwen3-tts'))
from gpu_tts_hold import check_gpu_tts_hold
from gpu_handoff_guard import schedule_gpu_handoff
check_gpu_tts_hold('game-lighting-history-04','cuda:0',dry);schedule_gpu_handoff('game-lighting-history-04','cuda:0',dry)
verify()
if dry: print(json.dumps(dict(requests=bindings,ttsStarted=False)));raise SystemExit(0)
import psutil
me=psutil.Process();lease=read(ROOT/'shared/output/GPU_HANDOFF.json')
state=dict(schemaVersion=1,startedAt=stamp(),actualIdentity=dict(pid=me.pid,createTime=me.create_time(),command=me.cmdline(),cwd=me.cwd(),exe=me.exe()),leaseToken=lease['token'],requests=bindings,runtimeDependencyProbe=dict(executable=str(venv),exitCode=probe.returncode,stdout=probe.stdout),previousPreModelFailure=dict(path=failed_history.relative_to(ROOT).as_posix(),sha256=sha(failed_history)),status='waiting-for-current-content-review',cpuThreads=0,gpuJobs=0,currentChild=None,jobs=[],generationComplete=False,wholeAsrApproved=False,finalMixedAsrApproved=False,uploaded=False)
def save():
    tmp=EXECUTION.with_name(EXECUTION.name+'.writing-'+str(os.getpid()));tmp.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,EXECUTION)
def current_review():
    deadline=time.monotonic()+600
    while True:
        code,out,err=duplicate()
        if not code:
            print(out,end='',flush=True)
            state['lastCurrentPreflight']=dict(path='production/preflight/game-lighting-history-04.json',sha256=sha(ROOT/'production/preflight/game-lighting-history-04.json'),checkedAt=stamp())
            save();return
        state.update(status='waiting-for-manually-refreshed-content-review',cpuThreads=0,gpuJobs=0,lastCheckError=err[-2000:]);save()
        if time.monotonic()>=deadline: raise RuntimeError('Current content review unavailable after bounded10-minute wait; restore research')
        time.sleep(10)
save()
try:
    for script in ['render-guided-tail-repair-v83.py','render-hogwarts-observation-v85.py']:
        current_review()
        command=[str(venv),'-X','utf8','production/research/game-lighting-history/'+script]
        log=BASE/'local'/('followup-v100-'+script.removesuffix('.py')+'.log');log.parent.mkdir(parents=True,exist_ok=True)
        with log.open('x',encoding='utf-8') as out:
            child=subprocess.Popen(command,cwd=ROOT,stdout=out,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            p=psutil.Process(child.pid);row=dict(script=script,startedAt=stamp(),pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd(),exe=p.exe(),log=log.relative_to(ROOT).as_posix())
            state.update(status='single-exclusive-followup-running',cpuThreads=2,gpuJobs=1,currentChild=row);save();code=child.wait()
        row.update(exitCode=code,endedAt=stamp());state['jobs'].append(row);state.update(currentChild=None,cpuThreads=0,gpuJobs=0);save()
        if code: raise RuntimeError('Preserve scoped child failure: '+script)
    state.update(status='followup-generated-awaiting-research-restoration-and-ASR',generationComplete=True,exitCode=0,endedAt=stamp(),gpuJobs=0);save()
except BaseException as exc:
    state.update(status='followup-failed-preserve-all-takes',error=repr(exc),exitCode=1,endedAt=stamp(),gpuJobs=0);save();raise
