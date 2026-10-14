"""Record the single retry after actual failed-exit/restoration verification."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, psutil
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
def save(p,d):
    t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(t,p)
req=read(BASE/'narration-tts-request-v1.json')
assert all(sha(ROOT/x['path'])==x['sha256'] for x in req['protectedInputs'])
failed=read(BASE/'failed-request-research-resume-verification-v1.json')
assert failed['actualOuterExitCode']==1 and failed['originalCommandCwdQueueRestorationVerified'] and failed['ownPcmCount']==0
me=psutil.Process(37804);assert abs(me.create_time()-1791607006.431256)<.01
assert 'render-voice-v1.py' in ' '.join(me.cmdline()) and Path(me.cwd()).resolve()==ROOT.resolve()
lease=read(ROOT/'shared/output/GPU_HANDOFF.json')
assert lease['token']=='dd368c6a-79b4-4dbd-8870-a6412834dd39' and lease['project']=='limited-color-world'
coord=psutil.Process(lease['coordinator']['pid']);assert abs(coord.create_time()-lease['coordinator']['createTime'])<.01
previous=BASE/'narration-tts-session-v1.json';archive=BASE/'narration-tts-session-attempt1-closed.json'
assert not archive.exists();archive.write_bytes(previous.read_bytes())
session=dict(schemaVersion=2,attempt=2,sessionId=91184,launchedAt=datetime.fromtimestamp(me.create_time(),timezone.utc).isoformat(),
    workingDirectory=str(ROOT),commandLine=['qwen3-tts/.venv/Scripts/python.exe','-X','utf8','-u','projects/limited-color-world/production/render-voice-v1.py'],
    actualPid=me.pid,createTime=me.create_time(),actualCommand=me.cmdline(),actualCwd=me.cwd(),proxyPid=48140,
    actualExitObserved=False,previousFailedSession=1912,previousFailureVerification=rel(BASE/'failed-request-research-resume-verification-v1.json'),
    leaseToken=lease['token'],wrapperSha256=sha(BASE/'render-voice-v1.py'))
assert not (BASE/'narration-tts-session-v2.json').exists();save(BASE/'narration-tts-session-v2.json',session);save(previous,session)
snapshot=dict(schemaVersion=3,observedAt=datetime.now(timezone.utc).isoformat(),actualOuterSession=91184,actualOuterIdentity=session,
    actualOwnCoordinator=dict(pid=coord.pid,createTime=coord.create_time(),command=coord.cmdline(),cwd=coord.cwd()),currentOwnLease=lease,
    actualFailedFirstRequestVerification=failed,currentHostAvailableBytes=psutil.virtual_memory().available,
    protected10InputsAllMatched=True,currentDuplicateReview='production/batches/sakurai-planning-game-design/proof-limited-color-world/content-studio-change-review-v4.json',
    inputsDigest='176082991351a51cef66607e137ab02342f865315e10ba627406f021721a9411',actualCheckExitCode=0,actualCheckObservation='980562',
    ownExecutionStateCreated=(BASE/'narration-tts-execution-v1.json').exists(),currentPcmCount=sum((ROOT/x['path']).exists() for x in req['scenes']),
    originalResearchOwner=lease['queueOwner'],boundaryStatus=lease.get('boundaryStatus'),completedTrainingJobEvidence=lease.get('completedJobEvidence'),
    foreignHandoffClosed=True,foreignRestorationNotClaimedAsOwn=True,
    preparedScenes=8,scopedTypescriptExitCode=0,prototypePixelReview=False,preparedBridges=3,bridgeTtsStarted=False,
    additionalActionCandidates=10,additionalCandidateSeconds=49.5,additionalAdoption=False,
    thumbnailPrepared=True,platformThumbnailSaved=False,actualId=None,finalApproval=False,
    nextAction='Observe single91184 and exact own lease/worker log. Actual exit0 then verify-own-voice-research-resume-v1.py --outer-exit-code 0 --session-id 91184. On failure preserve state/PCM and verify exact own restoration. Do not rerun1912. Whole current8 plus independent ASR contexts, serialized3additive bridges, required unique action adoption, measured60:40 and all final timing/mix/pixels/QA/collection/publishing/Git/schedule remain pending.')
out=BASE/'prepared-handoff-resource-verification-v3.json';assert not out.exists();save(out,snapshot)
cp_path=BASE/'latest-checkpoint.json';raw=cp_path.read_bytes();cp=json.loads(raw)
if not (BASE/'narration-tts-execution-v1.json').exists():
    cp.update(recordedAt=snapshot['observedAt'],stage='retry-after-gate-failure-owned-cooperative-boundary',
        preparationVerification=rel(out),nextAction=snapshot['nextAction'],
        ownedJob=dict(pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=91184,
                     state='shared/output/GPU_HANDOFF.json',leaseToken=lease['token'],gpuJobs=0,modelLoaded=False,totalScenes=8))
    assert cp_path.read_bytes()==raw;save(cp_path,cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';raw=qp.read_bytes();q=json.loads(raw)
i=next(x for x in q['items'] if x['slug']=='limited-color-world')
i.update(preparationVerification=rel(out),voiceRequestSession=91184,previousFailedSession=1912,
         failedRequestRestorationVerified=True,nextAction=snapshot['nextAction'])
if not (BASE/'narration-tts-execution-v1.json').exists():i.update(stage=cp['stage'],currentExecution=cp['ownedJob'])
q['updatedAt']=q['lastProgressAt']=snapshot['observedAt'];assert qp.read_bytes()==raw;save(qp,q)
print(json.dumps(dict(singleSession=91184,actualPid=me.pid,actualCoordinator=coord.pid,ownToken=lease['token'],protected10=True,
                     executionStateCreated=snapshot['ownExecutionStateCreated'],currentPcm=snapshot['currentPcmCount'])))
