from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,psutil,os
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,d):
 t=p.with_name(p.name+'.writing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
waiting=read(BASE/'causal-bridge-tts-waiting-v1.json');proc=psutil.Process(waiting['actualPid'])
assert abs(proc.create_time()-waiting['createTime'])<.01 and proc.cmdline()==waiting['commandLine'] and Path(proc.cwd()).resolve()==ROOT
assert not (BASE/'causal-bridge-tts-execution-v1.json').exists()
request=read(BASE/'causal-bridge-tts-request-v1.json');assert all(sha(ROOT/x['path'])==x['sha256'] for x in request['protectedInputs'])
session=BASE/'causal-bridge-tts-session-v1.json';assert not session.exists()
data=dict(schemaVersion=1,recordedAt=now(),sessionId=11634,actualPid=proc.pid,createTime=proc.create_time(),commandLine=proc.cmdline(),cwd=proc.cwd(),proxyParentPid=proc.ppid(),
 actualLaunchTool='5853b1',actualCimVerificationTool='372587',request='projects/limited-color-world/production/causal-bridge-tts-request-v1.json',requestSha256=sha(BASE/'causal-bridge-tts-request-v1.json'),
 existingForeignLease=waiting['foreignLease'],modelLoaded=False,ownGpuJobs=0,ownResearchPauseOrResumeClaim=False,protectedInputsUnchanged=True)
save(session,data)
cp=read(BASE/'latest-checkpoint.json');cp.update(recordedAt=now(),stage='serialized-additive3bridge-request-waiting-before-model',bridgeRequestStarted=True,bridgeTtsStarted=False,
 bridgeRequest=data,ownedJob=dict(pid=proc.pid,createTime=proc.create_time(),commandLine=proc.cmdline(),cwd=proc.cwd(),sessionId=11634,cpuThreads=2,gpuJobs=0,state='projects/limited-color-world/production/causal-bridge-tts-waiting-v1.json',workerExpectedRunning=True,exitCode=None),
 nextAction='Reuse serialized bridge request11634; preserve foreign58196216 lease. After its actual completion and original restoration, own coordinator alone requests safe boundary and one3bridge batch. Verify actual own exit/research restoration, then new3 whole/context ASR. No original8 voice/32ASR or source extraction repeat.')
save(BASE/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
for _ in range(10):
 raw=qp.read_bytes();q=json.loads(raw);item=next(x for x in q['items'] if x['slug']=='limited-color-world')
 item.update(stage=cp['stage'],currentExecution=cp['ownedJob'],nextAction=cp['nextAction'],bridgeRequestStarted=True,bridgeTtsStarted=False);q['lastProgressAt']=q['updatedAt']=now()
 if qp.read_bytes()==raw:save(qp,q);break
else:raise RuntimeError('Concurrent queue change')
print(json.dumps(dict(session=11634,actualPid=proc.pid,createTime=proc.create_time(),protectedInputs=len(request['protectedInputs']),ownGpu=0,ownResearchManipulation=0)))
