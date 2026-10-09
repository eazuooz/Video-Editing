from pathlib import Path
from datetime import datetime,timezone
import json,psutil,os,time
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).parent/'revision-balatro60-v2'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def save(p,j):
 t=p.with_name(p.name+'.launch-writing');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
target=BASE/'narration-tts-session-v2.json';assert not target.exists()
w=read(BASE/'narration-tts-waiting-v2.json');p=psutil.Process(w['actualPid']);assert abs(p.create_time()-w['createTime'])<.01 and p.cmdline()==w['commandLine']
lease=read(ROOT/'shared/output/GPU_HANDOFF.json');assert lease['project']=='presenting-game-scores'
c=psutil.Process(lease['coordinator']['pid']);assert abs(c.create_time()-lease['coordinator']['createTime'])<.01
stamp=datetime.now(timezone.utc).isoformat();j=dict(schemaVersion=1,observedAt=stamp,sessionId=22553,actualOuterIdentity=dict(pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd()),actualCoordinator=lease['coordinator'],leaseToken=lease['token'],leaseHistory='shared/output/gpu-handoff/'+lease['token']+'.json',currentState=lease['state'],originalResearch=lease['queueOwner'],originalCurrentJob=lease['originalStatus'].get('job'),workerExpectedRunning=True,actualOuterExitCode=None,modelLoaded=False,gpuTtsJobs=0,preparedItems=11,verifiedDedicatedEnvironment='qwen3-tts/.venv',priorImportFailureRestoration='projects/presenting-game-scores/production/revision-balatro60-v2/voice-runtime-failure-restoration-v1.json')
save(target,j);w['sessionId']=22553;save(BASE/'narration-tts-waiting-v2.json',w)
cpPath=Path(__file__).parent/'latest-checkpoint.json';cp=read(cpPath);job=dict(sessionId=22553,pid=p.pid,createTime=p.create_time(),commandLine=p.cmdline(),cwd=p.cwd(),coordinator=lease['coordinator'],leaseToken=lease['token'],state=target.relative_to(ROOT).as_posix(),log=lease.get('ttsLog'),cpuThreads=2,gpu=0,workerExpectedRunning=True,exitCode=None)
cp.update(recordedAt=stamp,stage='selective-voice-v2-dedicated-runtime-boundary-request',ownedJob=job,nextAction='Observe existing session22553/owned lease. No parallel or repeated TTS. After actual exit verify original research restoration, then all11 whole/current contexts ASR and measured ratios.');save(cpPath,cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
for _ in range(8):
 raw=qp.read_text('utf-8-sig');q=json.loads(raw);item=next(x for x in q['items'] if x['slug']=='presenting-game-scores');item.update(stage=cp['stage'],currentExecution=job,nextAction=cp['nextAction']);q.update(updatedAt=stamp,lastProgressAt=stamp)
 if qp.read_text('utf-8-sig')==raw:save(qp,q);break
 time.sleep(.15)
else:raise RuntimeError('Concurrent queue change')
print(json.dumps(dict(session=22553,outerPid=p.pid,coordinator=c.pid,token=lease['token'],stage=lease['state']),ensure_ascii=False))
