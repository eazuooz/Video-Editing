"""Attach the actual single exec session to a still-identical waiting wrapper."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,psutil
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
B=ROOT/'production/batches/unpublished-teaching-clarity-revision'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf8')
ap=argparse.ArgumentParser();ap.add_argument('--session-id',required=True,type=int);a=ap.parse_args()
w=read(R/'narration-tts-waiting-v1.json');p=psutil.Process(w['actualPid'])
assert abs(p.create_time()-w['createTime'])<.01 and p.cmdline()==w['commandLine']
assert Path(p.cwd()).resolve()==ROOT
assert 'render-orientation-additions-v1.py' in ' '.join(p.cmdline())
for x in w['protectedInputs']:assert hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest()==x['sha256'],x['path']
stamp=datetime.now(timezone.utc).isoformat()
job=dict(pid=p.pid,createTime=p.create_time(),commandLine=p.cmdline(),cwd=p.cwd(),sessionId=a.session_id,
    waitingRecord=(R/'narration-tts-waiting-v1.json').relative_to(ROOT).as_posix(),
    state=(R/'narration-tts-execution-v1.json').relative_to(ROOT).as_posix(),cpuThreads=2,gpuJobs=0,
    stage='waiting-for-existing-foreign-lease-before-owned-coordinator',modelLoaded=False,exitCode=None)
save(R/'narration-tts-session-v1.json',dict(**job,recordedAt=stamp))
w['sessionId']=a.session_id;save(R/'narration-tts-waiting-v1.json',w)
cp=read(R/'latest-checkpoint.json');cp.update(observedAt=stamp,stage=job['stage'],ownedJob=job,
    ttsRequestStarted=True,ownTtsModelLoaded=False,newActualId=None,
    next='Keep the single waiting wrapper; preserve foreign polygons handoff. After actual outer exit verify own research restoration and current whole6/independent contexts before animation/mix.')
save(R/'latest-checkpoint.json',cp)
qp=B/'queue.json';raw=qp.read_text('utf-8-sig');q=json.loads(raw)
item=next(x for x in q['items'] if x['slug']=='game-math-orientation-matrices')
item.update(status=job['stage'],currentExecution=job,actualReplacementVideoId=None)
q['execution'].update(currentSlug='game-math-orientation-matrices',stage=job['stage'],ownedJob=job,next=cp['next'])
q['updatedAt']=stamp;assert qp.read_text('utf-8-sig')==raw
save(qp,q)
print(json.dumps(dict(actualSession=a.session_id,pid=p.pid,createTime=p.create_time(),protectedInputs=len(w['protectedInputs']),ownGpuJobs=0,modelLoaded=False,foreignManipulations=0)))
