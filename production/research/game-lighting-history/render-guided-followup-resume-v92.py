"""Resume only two pre-model children; keep failed v87 execution and lease history."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[3]; BASE=ROOT/'projects/game-lighting-history-04/production'
EXECUTION=BASE/'guided-followup-resume-execution-v92.json'; dry='--dry-run' in sys.argv
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text('utf-8-sig'))
stamp=lambda:datetime.now(timezone.utc).isoformat()
requests=[BASE/'guided-tail-repair-request-v83.json',BASE/'hogwarts-observation-tts-request-v85.json']
bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in requests]
def duplicate():
    p=subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe','scripts/review-video-duplicates.cjs','game-lighting-history-04','--candidate-file','production/research/game-lighting-history/candidate-04.json','--check'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW)
    print(p.stdout,end='',flush=True)
    if p.returncode:
        print(p.stderr,file=sys.stderr,flush=True); raise SystemExit(p.returncode)
def verify():
    old=read(BASE/'guided-followup-batch-execution-v87.json')
    if old.get('exitCode')!=1 or not old.get('endedAt') or len(old.get('jobs',[]))!=2 or any(j['exitCode']!=1 for j in old['jobs']): raise RuntimeError('Inspect original pre-model failure first')
    if read(ROOT/'shared/output/gpu-handoff'/f"{old['leaseToken']}.json").get('state')!='research_resume_verified': raise RuntimeError('Observe original research restoration first')
    for b in bindings:
        if sha(ROOT/b['path'])!=b['sha256']: raise RuntimeError('Followup request changed')
    for p in requests:
        r=read(p)
        for x in r['protectedInputs']:
            if sha(ROOT/x['path'])!=x['sha256']: raise RuntimeError('Protected input changed '+x['path'])
        for x in r['scenes']:
            if (ROOT/x['path']).exists(): raise RuntimeError('Preserve existing child take '+x['id'])
    if any((BASE/name).exists() for name in ['guided-tail-repair-execution-v83.json','hogwarts-observation-tts-execution-v85.json']): raise RuntimeError('Child execution exists: inspect partial work before resume')
    if EXECUTION.exists(): raise RuntimeError('Preserve previous resume execution')
verify(); duplicate()
sys.path.insert(0,str(ROOT/'qwen3-tts'))
from gpu_tts_hold import check_gpu_tts_hold
from gpu_handoff_guard import schedule_gpu_handoff
check_gpu_tts_hold('game-lighting-history-04','cuda:0',dry); schedule_gpu_handoff('game-lighting-history-04','cuda:0',dry)
verify(); duplicate()
if dry:
    print(json.dumps(dict(requests=bindings,ttsStarted=False))); raise SystemExit(0)
import psutil
me=psutil.Process(); lease=read(ROOT/'shared/output/GPU_HANDOFF.json')
state=dict(schemaVersion=1,startedAt=stamp(),actualIdentity=dict(pid=me.pid,createTime=me.create_time(),command=me.cmdline(),cwd=me.cwd(),exe=me.exe()),leaseToken=lease['token'],requests=bindings,previousPreModelFailure=dict(path='projects/game-lighting-history-04/production/guided-followup-batch-execution-v87.json',sha256=sha(BASE/'guided-followup-batch-execution-v87.json')),status='single-exclusive-followup-resume',cpuThreads=2,gpuJobs=1,currentChild=None,jobs=[],generationComplete=False,researchRestorationObserved=False,wholeAsrApproved=False,finalMixedAsrApproved=False,uploaded=False)
def save():
    tmp=EXECUTION.with_name(EXECUTION.name+'.writing-'+str(os.getpid())); tmp.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8'); os.replace(tmp,EXECUTION)
save()
try:
    for script in ['render-guided-tail-repair-v83.py','render-hogwarts-observation-v85.py']:
        command=[me.exe(),'-X','utf8','production/research/game-lighting-history/'+script]
        log=BASE/'local'/('followup-v92-'+script.removesuffix('.py')+'.log'); log.parent.mkdir(parents=True,exist_ok=True)
        with log.open('x',encoding='utf-8') as out:
            child=subprocess.Popen(command,cwd=ROOT,stdout=out,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            p=psutil.Process(child.pid); row=dict(script=script,startedAt=stamp(),pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd(),exe=p.exe(),log=log.relative_to(ROOT).as_posix())
            state['currentChild']=row; save(); code=child.wait()
        row.update(exitCode=code,endedAt=stamp()); state['jobs'].append(row); state['currentChild']=None; save()
    failed=[j['script'] for j in state['jobs'] if j['exitCode']]
    state.update(status='followup-generated-awaiting-actual-research-restoration-and-ASR' if not failed else 'followup-failed-preserve-all-takes',generationComplete=not failed,exitCode=1 if failed else 0,endedAt=stamp(),gpuJobs=0); save()
    if failed: raise RuntimeError('Scoped followup failures: '+','.join(failed))
except BaseException as exc:
    state.update(status='followup-failed-preserve-all-takes',error=repr(exc),exitCode=1,endedAt=stamp(),gpuJobs=0); save(); raise
