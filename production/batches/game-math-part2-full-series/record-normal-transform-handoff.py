"""Pin actual completed-run GPU handoffs without changing any research file."""
from pathlib import Path
import json,hashlib,datetime
import psutil
R=Path(__file__).resolve().parents[3];slug='game-math-normal-transform-uv'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
tokens=['4268a965-8abb-4f8e-9df8-f3e46b16444e','ef5dedb6-b781-4803-97f8-d55a587cd4f4']
rows=[]
for token in tokens:
    f=R/f'shared/output/gpu-handoff/{token}.json';s=read(f)
    assert s['project']==slug and s['state']=='research_resume_verified' and s['ttsExitCode']==0
    done=s['completedJobEvidence'];marker=Path(done['marker'])
    assert sha(marker)==done['markerSha256'] and read(marker)['validation']==done['validation']
    assert done['validation']['checkpoint_finite'] and done['validation']['exact_component_keys'] and done['validation']['numerically_finite']
    weights=Path(next(p for p in done['outputs'] if p.endswith('lora_weights.pt')))
    assert sha(weights)==done['validation']['checkpoint_sha256']
    assert s['gpuBeforeTts']['freeMiB']>=18432 and s['gpuBeforeTts']['utilization']<15
    assert s['resumedQueue']['command']==s['queueOwner']['command'] and s['resumedQueue']['cwd']==s['queueOwner']['cwd']
    remainingOwn=[];foreign=[]
    for flag in s['ownedFiles']:
        p=Path(flag)
        if not p.exists():continue
        if token in p.read_text(encoding='utf-8-sig'):remainingOwn.append(flag)
        else:foreign.append(flag)
    assert not remainingOwn
    rows.append({'token':token,'history':f.relative_to(R).as_posix(),'historySha256':sha(f),
        'originalStatus':s['originalStatus'],'completedBoundary':s['boundaryStatus'],'completedJobEvidence':done,
        'gpuBeforeTts':s['gpuBeforeTts'],'ttsExitCode':s['ttsExitCode'],'resumedQueue':s['resumedQueue'],
        'firstFreshResumedStatus':s['resumedStatus'],'ownedFlagsRemoved':True,'foreignFlagsPreserved':foreign})
q=Path(rows[-1]['completedJobEvidence']['marker']).parents[1]
progress=[]
for job,kind in [('infer_val_normal_p112_42','validation inference'),('metrics_val_normal_p112_42','validation metrics')]:
    f=q/'done'/f'{job}.json';value=read(f);assert value['job']==job
    progress.append({'job':job,'kind':kind,'marker':str(f),'sha256':sha(f),'time':value['time'],'seconds':value['seconds'],'validation':value['validation']})
latest=read(q/'status.json');proc=psutil.Process(rows[-1]['resumedQueue']['pid'])
afterSecond=[]
for job,kind in [('infer_val_normal_p112_43','validation inference'),('metrics_val_normal_p112_43','validation metrics')]:
    f=q/'done'/f'{job}.json'
    if not f.exists():continue
    value=read(f);assert value['job']==job
    afterSecond.append({'job':job,'kind':kind,'marker':str(f),'sha256':sha(f),'time':value['time'],'seconds':value['seconds'],'validation':value['validation']})
assert abs(proc.create_time()-rows[-1]['resumedQueue']['createTime'])<.02
assert latest.get('owner_pid')==proc.pid and latest['status'] in ('running','waiting_for_resources')
record={'status':'both-completed-training-boundaries-and-original-queue-restoration-verified',
    'atUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'project':slug,'handoffs':rows,
    'betweenHandoffsActualCompletedJobs':progress,
    'afterSecondHandoffActualCompletedJobs':afterSecond,
    'normalizedProgressCorrection':'The two completed jobs after the first handoff were one validation inference and one metrics computation, not two inference jobs. Preserve the original coordinator argv unchanged.',
    'latestQueueStatus':latest,'currentQueueProcessAlive':True,
    'queueRunningVersusWaiting':'Only status running with a child job proves active research execution; waiting_for_resources is recorded as waiting.',
    'trainingResumeMethod':'Finish whole existing2000step run, post-training validation/save/done; resume exact original command/cwd and captured environment between jobs. No optimizer-state claim or forced termination.',
    'humanListening':'pending'}
(R/f'projects/{slug}/production/gpu-handoff-review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print({'handoffs':len(rows),'betweenJobs':[p['kind'] for p in progress],'latestStatus':latest['status'],'latestJob':latest.get('job')})
