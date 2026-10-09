"""Read-only process/resource verification; records owned TTS closure and actual research restoration."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,psutil
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def save(p,x):
    t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
def alive(x):
    try:return abs(psutil.Process(x['pid']).create_time()-x['createTime'])<.01
    except psutil.NoSuchProcess:return False
state=read(BASE/'fresh-guides-tts-execution-v4.json');assert state['exitCode']==0 and state['generationComplete'] and len(state['results'])==3
histPath=ROOT/'shared/output/gpu-handoff'/f"{state['leaseToken']}.json";h=read(histPath)
assert h['state']=='research_resume_verified' and h['project']=='similar-game-design' and h['ttsExitCode']==0
assert not alive(h['coordinator']) and not alive(h['ttsOwner']) and not alive(dict(pid=state['actualPid'],createTime=state['createTime']))
p=psutil.Process(h['resumedQueue']['pid']);assert abs(p.create_time()-h['resumedQueue']['createTime'])<.01
assert p.cmdline()==h['queueOwner']['command']==h['resumedQueue']['command'] and p.cwd()==h['queueOwner']['cwd']==h['resumedQueue']['cwd']
status=read(Path(h['queueDir'])/'status.json');assert status['owner_pid']==p.pid and status['status'] in ['running','waiting_for_resources']
controls=[]
for item in h['ownedFiles']:
    f=Path(item);current=f.read_text('utf-8-sig') if f.exists() else None
    assert not current or state['leaseToken'] not in current
    controls.append(dict(path=item,ownedTokenAbsent=True,currentForeignControlPreserved=current))
request=read(BASE/'fresh-guides-tts-request-v4.json')
for x in request['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
for x in state['results']:assert sha(ROOT/x['path'])==x['sha256']
proof=dict(schemaVersion=1,verifiedAt=now(),ttsLeaseToken=state['leaseToken'],sessionId=47264,actualExitObserved=True,exitCode=0,
 ownedCoordinatorClosed=True,restorationVerified=True,sameOriginalCommandAndCwd=True,
 history=dict(path=histPath.relative_to(ROOT).as_posix(),sha256=sha(histPath),data=h),
 actualResumedQueue=dict(pid=p.pid,createTime=p.create_time(),commandLine=p.cmdline(),cwd=p.cwd(),status=status),
 ownedControls=controls,forcedKill=0,suspend=0,foreignControlsRemoved=0,allProtectedInputsUnchanged=True,
 measuredGuideSeconds=state['totalRawSceneSeconds'],wholeAsrApproved=False,finalMixedAsrApproved=False,humanListening='pending',humanPronunciation='pending')
save(BASE/'fresh-guides-research-resume-verification-v4.json',proof)
state['actualExitObserved']=True;state['researchResumeVerified']=True;state['researchResumeVerification']='projects/similar-game-design/production/fresh-guides-research-resume-verification-v4.json';save(BASE/'fresh-guides-tts-execution-v4.json',state)
session=read(BASE/'fresh-guides-tts-session-v4.json');session.update(status='closed-three-fresh-guides-TTS-research-resume-verified',actualExitObserved=True,exitCode=0,workerExpectedRunning=False);save(BASE/'fresh-guides-tts-session-v4.json',session)
processes=[]
for q in psutil.process_iter(['pid','name','cmdline','create_time']):
    try:
        cmd=' '.join(q.info['cmdline'] or [])
        if any(x in cmd.lower() for x in ['python','ffmpeg','vite','gpu_queue']):processes.append(q.info)
    except (psutil.AccessDenied,psutil.NoSuchProcess):pass
assert not any(('similar-game-design/production/render-' in ' '.join(x.get('cmdline') or []).replace('\\','/')) for x in processes),'Owned synthesis unexpectedly alive'
raw=subprocess.check_output(['nvidia-smi','--query-gpu=memory.used,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True)
resource=dict(observedAt=now(),ownHeavyJobs=0,cpuLoadPercent=psutil.cpu_percent(interval=.5),freePhysicalMemoryKiB=psutil.virtual_memory().available//1024,
 processes=processes,gpuObservation=raw.strip(),foreignProcessesChanged=0,closedTtsSession=47264)
save(BASE/'resource-before-fresh-guides-asr-v4.json',resource)
cp=read(BASE/'latest-checkpoint.json');cp.update(recordedAt=now(),stage='three-fresh-guides-measured-research-restored-awaiting-six-window-ASR',
 freshGuideResearchRestoration='projects/similar-game-design/production/fresh-guides-research-resume-verification-v4.json',freshGuideVoiceGenerationComplete=True,
 ownedJob=dict(status='closed-three-fresh-guides-TTS',sessionId=47264,actualExitObserved=True,exitCode=0,workerExpectedRunning=False),
 nextAction='Run only six new whole/independent CPU2 ASR windows after fresh resources. Previous21 PCM and finished ASR remain preserved. Final measured 60:40/render/QA/collection/private are pending.');save(BASE/'latest-checkpoint.json',cp)
print(json.dumps(dict(researchResumeVerified=True,actualQueuePid=p.pid,status=status['status'],guideSeconds=state['totalRawSceneSeconds'],cpuLoad=resource['cpuLoadPercent'],freeKiB=resource['freePhysicalMemoryKiB'])))
