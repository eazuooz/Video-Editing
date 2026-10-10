"""Record actual waiting/running identities without changing research controls."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,psutil,subprocess,time
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;FOLDER=BASE/'voice-clarity-v2'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,d):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
def identity(r):
 try:
  p=psutil.Process(r['pid']);same=abs(p.create_time()-r['createTime'])<.01
  return dict(pid=r['pid'],createTime=r['createTime'],alive=same,commandLine=p.cmdline() if same else None,cwd=p.cwd() if same else None)
 except psutil.NoSuchProcess:return dict(**r,alive=False)
ap=argparse.ArgumentParser();ap.add_argument('--session-id',type=int,required=True);args=ap.parse_args()
waiting=read(FOLDER/'waiting.json');wrapper=identity(waiting)
sp=FOLDER/'session.json'
if sp.exists():assert read(sp)['sessionId']==args.session_id
else:save(sp,dict(recordedAt=now(),sessionId=args.session_id,outerWrapperIdentity=wrapper,actualOuterExitCode=None,actualExitObserved=False))
request=read(FOLDER/'request.json')
for r in request['protectedInputs']:assert sha(ROOT/r['path'])==r['sha256'],r['path']
leasePath=ROOT/'shared/output/GPU_HANDOFF.json';lease=read(leasePath) if leasePath.exists() else None
assert lease and lease['project']=='character-parameters' and 'render-voice-clarity-v2.py' in ' '.join(lease.get('ttsCommand',[])), 'Read actual later history before claiming owned handoff'
coordinator=identity(lease['coordinator']);assert coordinator['alive']
statePath=FOLDER/'execution.json';state=read(statePath) if statePath.exists() else None
job=identity(dict(pid=state['actualPid'],createTime=state['createTime'])) if state else wrapper
assert job['alive'],'Inspect actual exit rather than recording a live worker'
status=read(Path(lease['queueDir'])/'status.json') if lease.get('queueDir') else None
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.used,memory.free,utilization.gpu','--format=csv,noheader'],text=True).strip()
proof=dict(observedAt=now(),sessionId=args.session_id,outerWrapper=wrapper,actualCurrentWorker=job,coordinator=coordinator,leaseToken=lease['token'],leaseState=lease['state'],originalResearch=lease.get('queueOwner'),currentResearchStatus=status,ownedControls=lease.get('ownedFiles'),protectedInputs=request['protectedInputs'],allProtectedInputsUnchanged=True,modelLoaded=state is not None,gpuJobs=state['gpuJobs'] if state else 0,completed=len(state['results']) if state else 0,total=2,actualOuterExitCode=None,researchRestorationVerified=False,processOrControlChangesByRecorder=0,gpu=gpu,candidateAdopted=False,finalTiming=False,mixedAsr=False,allFinalPixels=False,qa=False,collected=False,uploaded=False,actualId=None)
save(FOLDER/'resource-handoff-live.json',proof)
job.update(sessionId=args.session_id,state='projects/character-parameters/production/voice-clarity-v2/execution.json' if state else 'projects/character-parameters/production/voice-clarity-v2/waiting.json',leaseToken=lease['token'],leaseState=lease['state'],modelLoaded=state is not None,gpu=state['gpuJobs'] if state else 0,total=2,completed=len(state['results']) if state else 0,workerExpectedRunning=True,actualOuterExitCode=None)
cpPath=BASE/'latest-checkpoint.json';cp=read(cpPath)
cp.update(recordedAt=now(),stage='voice-clarity-two-paragraphs-'+lease['state'],ownedJob=job,narrationApproved=False,asrApproved=False,priorOriginalVoiceResearchResumeVerification='projects/character-parameters/production/research-handoff-verification-v2.json',researchResumeVerification=None,researchRestorationVerified=False,voiceClarityRequest='projects/character-parameters/production/voice-clarity-v2/request.json',voiceClarityResource='projects/character-parameters/production/voice-clarity-v2/resource-handoff-live.json',nextAction='Read exact live session33582 and owned lease; current research must finish its checkpoint/validation/done boundary. After actual TTS exit verify original research resume, then fresh whole and independent complete contexts before adopting two paragraphs. Original12 PCM/main script preserved.');save(cpPath,cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
for _ in range(10):
 raw=qp.read_text('utf-8-sig');q=json.loads(raw);item=next(x for x in q['items'] if x['slug']=='character-parameters')
 item.update(stage=cp['stage'],currentExecution=job,voiceClarityRequest=cp['voiceClarityRequest'],researchResumeVerification=None,researchRestorationVerified=False,priorOriginalVoiceResearchResumeVerification=cp['priorOriginalVoiceResearchResumeVerification'],nextAction=cp['nextAction']);item['checkpoints']['narration']=False;q['updatedAt']=now()
 if qp.read_text('utf-8-sig')==raw:save(qp,q);break
 time.sleep(.15)
else:raise RuntimeError('Concurrent writer; preserve queue')
print(json.dumps(dict(sessionId=args.session_id,job=job,coordinator=coordinator,originalResearchStatus=status,protectedInputs=len(request['protectedInputs']),processMutations=0),ensure_ascii=False))
