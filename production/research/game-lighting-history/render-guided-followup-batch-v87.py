"""One exclusive lease for scoped failed retakes and six inspected additions."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[3]; BASE=ROOT/'projects/game-lighting-history-04/production'
EXECUTION=BASE/'guided-followup-batch-execution-v87.json'; dry='--dry-run' in sys.argv
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text('utf-8-sig'))
stamp=lambda:datetime.now(timezone.utc).isoformat()
requests=[BASE/'guided-tail-repair-request-v83.json',BASE/'hogwarts-observation-tts-request-v85.json']
bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in requests]
def verify():
    a=read(BASE/'part3-guided-actions-tts-execution-v69.json')
    if not a.get('endedAt') or a.get('exitCode')!=1 or len(a.get('results',[]))!=37 or 'observed tail failure' not in a.get('error',''): raise RuntimeError('Inspect the actual completed37 failure first')
    if read(ROOT/'shared/output/gpu-handoff'/f"{a['leaseToken']}.json").get('state')!='research_resume_verified': raise RuntimeError('Observe original research restoration first')
    for b in bindings:
        if sha(ROOT/b['path'])!=b['sha256']: raise RuntimeError('Followup request changed')
    for p in requests:
        r=read(p)
        for x in r['protectedInputs']:
            if sha(ROOT/x['path'])!=x['sha256']: raise RuntimeError('Protected input changed '+x['path'])
    if EXECUTION.exists(): raise RuntimeError('Preserve previous combined execution')
verify()
sys.path.insert(0,str(ROOT/'qwen3-tts'))
from gpu_tts_hold import check_gpu_tts_hold
from gpu_handoff_guard import schedule_gpu_handoff
check_gpu_tts_hold('game-lighting-history-04','cuda:0',dry); schedule_gpu_handoff('game-lighting-history-04','cuda:0',dry)
verify()
if dry:
    print(json.dumps(dict(requests=bindings,ttsStarted=False))); raise SystemExit(0)
import psutil
me=psutil.Process(); lease=read(ROOT/'shared/output/GPU_HANDOFF.json')
state=dict(schemaVersion=1,startedAt=stamp(),actualIdentity=dict(pid=me.pid,createTime=me.create_time(),command=me.cmdline(),cwd=me.cwd(),exe=me.exe()),leaseToken=lease['token'],requests=bindings,status='single-exclusive-followup-batch',cpuThreads=2,gpuJobs=1,currentChild=None,jobs=[],generationComplete=False,researchRestorationObserved=False,wholeAsrApproved=False,finalMixedAsrApproved=False,uploaded=False)
def save():
    tmp=EXECUTION.with_name(EXECUTION.name+'.writing-'+str(os.getpid())); tmp.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8'); os.replace(tmp,EXECUTION)
save()
try:
    scripts=['render-guided-tail-repair-v83.py','render-hogwarts-observation-v85.py']
    for script in scripts:
        command=[sys.executable,'-X','utf8','production/research/game-lighting-history/'+script]
        child=subprocess.Popen(command,cwd=ROOT,creationflags=subprocess.CREATE_NO_WINDOW)
        p=psutil.Process(child.pid); row=dict(script=script,startedAt=stamp(),pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd(),exe=p.exe())
        state['currentChild']=row; save()
        code=child.wait(); row.update(exitCode=code,endedAt=stamp()); state['jobs'].append(row); state['currentChild']=None; save()
    failed=[j['script'] for j in state['jobs'] if j['exitCode']]
    state.update(status='followup-generated-awaiting-actual-research-restoration-and-ASR' if not failed else 'followup-failed-preserve-all-takes',generationComplete=not failed,exitCode=1 if failed else 0,endedAt=stamp(),gpuJobs=0); save()
    if failed: raise RuntimeError('Scoped followup failures: '+','.join(failed))
except BaseException as exc:
    state.update(status='followup-failed-preserve-all-takes',error=repr(exc),exitCode=1,endedAt=stamp(),gpuJobs=0); save(); raise
