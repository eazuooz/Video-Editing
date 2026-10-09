from pathlib import Path
from datetime import datetime,timezone
import json,psutil,os,time
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).parent/'revision-balatro60-v2'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def save(p,j):
 t=p.with_name(p.name+'.launch-writing');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
target=BASE/'narration-tts-session-v1.json';assert not target.exists()
w=read(BASE/'narration-tts-waiting-v1.json');p=psutil.Process(w['actualPid']);assert abs(p.create_time()-w['createTime'])<.01 and p.cmdline()==w['commandLine']
lease=read(ROOT/'shared/output/GPU_HANDOFF.json');assert lease['project']=='presenting-game-scores'
c=psutil.Process(lease['coordinator']['pid']);assert abs(c.create_time()-lease['coordinator']['createTime'])<.01
stamp=datetime.now(timezone.utc).isoformat();j=dict(schemaVersion=1,observedAt=stamp,sessionId=39486,actualOuterIdentity=dict(pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd()),actualCoordinator=lease['coordinator'],leaseToken=lease['token'],leaseHistory='shared/output/gpu-handoff/'+lease['token']+'.json',currentState=lease['state'],originalResearch=lease['queueOwner'],originalCurrentJob=lease['originalStatus']['job'],workerExpectedRunning=True,actualOuterExitCode=None,modelLoaded=False,gpuTtsJobs=0,preparedItems=11,priorLaunchBeforeResourceCompleted=dict(actualExitCode=1,modelLoaded=False,gpuJobs=0,stateCreated=False,reason='Read-only resource collection had not finished. Its actual exit0 was observed before this successful boundary request; no TTS or controls were created by the failed wrapper.'))
save(target,j);w['sessionId']=39486;save(BASE/'narration-tts-waiting-v1.json',w)
cpPath=Path(__file__).parent/'latest-checkpoint.json';cp=read(cpPath);job=dict(sessionId=39486,pid=p.pid,createTime=p.create_time(),commandLine=p.cmdline(),cwd=p.cwd(),coordinator=lease['coordinator'],leaseToken=lease['token'],state=target.relative_to(ROOT).as_posix(),log=lease.get('ttsLog'),cpuThreads=2,gpu=0,workerExpectedRunning=True,exitCode=None)
cp.update(recordedAt=stamp,stage='selective-voice-waiting-current-training-final-boundary',ownedJob=job,nextAction='Observe existing session39486 and own lease only. Current train_wireframe_p004_43 finishes checkpoint/validation/done; coordinator then grants single11-item TTS and restores original research on success/failure. No duplicate TTS. Full current whole/context ASR and measured ratios remain pending.');save(cpPath,cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
for _ in range(8):
 raw=qp.read_text('utf-8-sig');q=json.loads(raw);item=next(x for x in q['items'] if x['slug']=='presenting-game-scores');item.update(stage=cp['stage'],currentExecution=job,nextAction=cp['nextAction']);q.update(updatedAt=stamp,lastProgressAt=stamp)
 if qp.read_text('utf-8-sig')==raw:save(qp,q);break
 time.sleep(.15)
else:raise RuntimeError('Concurrent queue change')
print('Actual outer65080/coordinator68524/session39486 and owned lease recorded. Training continues to its normal boundary; TTS model0.')
