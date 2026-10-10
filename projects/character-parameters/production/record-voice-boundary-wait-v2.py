"""Record the existing live serialized request; never launch a second worker."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,psutil
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,o):
    t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
state=BASE/'narration-tts-execution-v2.json'
if state.exists():raise SystemExit('Actual TTS state already exists; read it instead of overwriting the current checkpoint.')
waiting=read(BASE/'narration-tts-waiting-v2.json');session=read(BASE/'narration-tts-session-v2.json')
lease=read(ROOT/'shared/output/GPU_HANDOFF.json')
assert lease['project']=='character-parameters' and lease['state']=='waiting_for_current_job_boundary'
assert lease['token']=='f1b25da1-321e-4515-9916-4a2a0a21bfcd'
for i in [dict(pid=waiting['actualPid'],createTime=waiting['createTime']),lease['coordinator']]:
    assert abs(psutil.Process(i['pid']).create_time()-i['createTime'])<.01
request=read(BASE/'narration-tts-request-v1.json')
for r in request['protectedInputs']:assert sha(ROOT/r['path'])==r['sha256']
stamp=datetime.now(timezone.utc).isoformat()
job=dict(status=lease['state'],pid=waiting['actualPid'],processCreateTime=waiting['createTime'],
    commandLine=waiting['commandLine'],workingDirectory=psutil.Process(waiting['actualPid']).cwd(),sessionId=session['sessionId'],
    coordinator=lease['coordinator'],leaseToken=lease['token'],cpuThreads=2,gpu=0,modelLoaded=False,
    state='projects/character-parameters/production/narration-tts-waiting-v2.json',
    history='shared/output/gpu-handoff/'+lease['token']+'.json',log=None,workerExpectedRunning=True,exitCode=None)
cp=read(BASE/'latest-checkpoint.json');cp.update(recordedAt=stamp,stage='single-approved-voice-request-waiting-for-training-boundary',
    ownedJob=job,ttsStarted=False,ttsRequestLaunched=True,sourceAdoptionApproved=True,
    failedAttemptRestoration='projects/character-parameters/production/failed-voice-research-restoration-v1.json',
    nextAction='Preserve live session59763 and owned coordinator; current training must finish final checkpoint/validation/done. TTS child then runs exclusively and coordinator restores original research on success/failure. After actual outer exit verify resume and current PCM before whole ASR.')
save(BASE/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';raw=qp.read_text('utf-8-sig');q=json.loads(raw)
item=next(x for x in q['items'] if x['slug']=='character-parameters')
item.update(stage=cp['stage'],currentExecution=job,nextAction=cp['nextAction'],updatedAt=stamp)
q.update(updatedAt=stamp,lastProgressAt=stamp)
assert qp.read_text('utf-8-sig')==raw;save(qp,q)
save(BASE/'voice-boundary-wait-observation-v2.json',dict(observedAt=stamp,ownedJob=job,allTenProtectedInputsUnchanged=True,
    originalResearch=lease['queueOwner'],originalStatus=lease['originalStatus'],currentResearchStatus=read(Path(lease['queueDir'])/'status.json'),
    ownCooperativePauseOwnedFiles=lease['ownedFiles'],foreignPauseFiles=lease['existingPauseFiles'],
    modelLoaded=False,pcmCreated=0,processOrControlChangesByRecorder=0))
print('Live single serialized request and current training boundary wait recorded; no duplicate job or model created.')
