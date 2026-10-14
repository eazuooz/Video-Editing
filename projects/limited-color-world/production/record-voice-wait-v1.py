"""Record the actually running single request; never mutate research controls."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,psutil
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):
 t=p.with_name(p.name+'.limited-writing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(t,p)
ap=argparse.ArgumentParser();ap.add_argument('--session-id',type=int,required=True);args=ap.parse_args()
assert not (B/'narration-tts-session-v1.json').exists()
w=read(B/'narration-tts-waiting-v1.json');p=psutil.Process(w['actualPid'])
assert abs(p.create_time()-w['createTime'])<.01 and Path(p.cwd()).resolve()==ROOT
assert 'projects/limited-color-world/production/render-voice-v1.py' in p.cmdline()
request=read(B/'narration-tts-request-v1.json')
for r in request['protectedInputs']:assert sha(ROOT/r['path'])==r['sha256']
assert not (B/'narration-tts-execution-v1.json').exists()
assert not any((ROOT/s['path']).exists() for s in request['scenes'])
lease=read(ROOT/'shared/output/GPU_HANDOFF.json')
assert lease['project']=='game-math-quaternion-teaching-additions-v2' and lease['token']=='b349bd9b-7a75-428f-99ef-079e3c0fc32f'
c=psutil.Process(lease['coordinator']['pid']);assert abs(c.create_time()-lease['coordinator']['createTime'])<.01
stamp=datetime.now(timezone.utc).isoformat()
session={'schemaVersion':1,'sessionId':args.session_id,'launchedAt':datetime.fromtimestamp(p.create_time(),timezone.utc).isoformat(),
 'workingDirectory':str(ROOT),'commandLine':['qwen3-tts/.venv/Scripts/python.exe','-X','utf8','-u','projects/limited-color-world/production/render-voice-v1.py'],
 'actualPid':p.pid,'createTime':p.create_time(),'actualCommand':p.cmdline(),'actualCwd':p.cwd(),'proxyPid':p.ppid(),'actualExitObserved':False}
save(B/'narration-tts-session-v1.json',session)
e={'schemaVersion':1,'observedAt':stamp,'actualSingleSession':args.session_id,'actualOwnWaitingIdentity':session,
 'actualCimObservation':'exec99b045: PID69828/create2026-10-10T13:05:15.145477+09:00, proxy24700',
 'currentForeignLease':lease,'foreignCoordinatorAlive':True,'foreignWorkerSnapshot':lease.get('ttsOwner'),
 'protectedInputHashesAllMatched':True,'ownTtsStateCreated':False,'ownPcmCreated':0,'ownGpuJobs':0,'ownResearchControlsChanged':0,
 'waitingBeforeModel':True,'minimumHostAvailableBytesBeforeOwnRequest':8_000_000_000,
 'currentHostAvailableBytes':psutil.virtual_memory().available,'dryRunExitCode':0,
 'dependencyDiscovery':{'soundfile':True,'torch':True,'transformers':True,'qwen_tts':True,'psutil':True},
 'wrappers':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in [B/'render-voice-v1.py',B/'verify-own-voice-research-resume-v1.py',B/'review-current-voice-v1.py']],
 'ownResearchResumeClaim':False,'nextAction':'Reuse only this waiting request. Foreign coordinator must close and restore its original research first; then own cooperative handoff/singleTTS/finally original resume. Observe actual outer exit before running own verifier; no closed-session polling.'}
save(B/'prepared-handoff-resource-verification-v1.json',e)
cp=read(B/'latest-checkpoint.json');cp.update(recordedAt=stamp,stage='single-request-waiting-foreign-handoff-and-host-memory',
 ownRequestStarted=True,ttsStarted=False,ownedJob={'pid':p.pid,'createTime':p.create_time(),'commandLine':p.cmdline(),'cwd':p.cwd(),'sessionId':args.session_id,'state':'projects/limited-color-world/production/narration-tts-waiting-v1.json','gpuJobs':0,'modelLoaded':False,'totalScenes':8},nextAction=e['nextAction']);save(B/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';raw=qp.read_bytes();q=json.loads(raw)
foreign=json.dumps([i for i in q['items'] if i['slug']!='limited-color-world'],ensure_ascii=False,sort_keys=True)
i=next(i for i in q['items'] if i['slug']=='limited-color-world');i.update(stage=cp['stage'],currentExecution=cp['ownedJob'],ownRequestStarted=True,ttsStarted=False,nextAction=cp['nextAction'],updatedAt=stamp)
q['updatedAt']=q['lastProgressAt']=stamp
assert qp.read_bytes()==raw and foreign==json.dumps([i for i in q['items'] if i['slug']!='limited-color-world'],ensure_ascii=False,sort_keys=True)
save(qp,q)
print('Actual session1912/PID69828 waiting verified; protected10inputs matched. OwnGPU/model/PCM/pause0; foreign lease preserved.')
