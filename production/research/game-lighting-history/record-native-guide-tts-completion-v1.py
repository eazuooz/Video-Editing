from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,psutil,os
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'production/research/game-lighting-history'
PROD=ROOT/'projects/game-lighting-history-03/production'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
    tmp=p.with_name(p.name+'.writing-'+str(os.getpid()))
    tmp.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,p)
now=datetime.now(timezone.utc).isoformat()
tts=read(PROD/'native-guides-tts-execution-v1.json');asr=read(PROD/'native-guides-asr-execution-v1.json')
handoffPath=ROOT/'shared/output/gpu-handoff'/(tts['leaseToken']+'.json');h=read(handoffPath)
q=read(Path('C:/Users/eazuo/renderformer/tmp/placement_focus_20261008/status.json'))
assert tts['generationComplete'] and tts['exitCode']==0 and len(tts['results'])==20
assert h['state']=='research_resume_verified' and h['ttsExitCode']==0
r=h['resumedQueue'];owner=psutil.Process(r['pid'])
assert abs(owner.create_time()-r['createTime'])<.1 and owner.cmdline()==r['command'] and owner.cwd().lower()==r['cwd'].lower()
assert q['owner_pid']==owner.pid and q['status'] in ['running','waiting_for_resources']
if q['status']=='running':assert psutil.Process(q['child_pid']).ppid()==owner.pid
assert not (ROOT/'shared/output/GPU_HANDOFF.json').exists()
for x in tts['results']:assert sha(ROOT/x['path'])==x['sha256']
worker=psutil.Process(asr['actualPid']);assert abs(worker.create_time()-asr['createTime'])<.1 and worker.cmdline()==asr['commandLine']
out=PROD/'native-guides-tts-completion-and-research-resume-v1.json'
assert not out.exists(),'Preserve completed verification'
record=dict(schemaVersion=1,verifiedAt=now,ttsSession=76471,observedSessionExitCode=0,
    execution=dict(path='projects/game-lighting-history-03/production/native-guides-tts-execution-v1.json',sha256=sha(PROD/'native-guides-tts-execution-v1.json')),
    guideCount=20,rawGuideSeconds=sum(x['seconds'] for x in tts['results']),rawGuideSamples=sum(x['samples'] for x in tts['results']),results=tts['results'],
    handoff=dict(path=handoffPath.relative_to(ROOT).as_posix(),sha256=sha(handoffPath),state=h['state']),
    restoredResearchOwner=r,actualCurrentResearchStatus=q,actualOriginalCommandAndCwdVerified=True,actualOwnerCreationTimeVerified=True,
    ownedPauseRequestsRemovedByCoordinator=True,foreignPauseControlsRemoved=False,
    original84Regenerated=False,allGuideAsrDirectlyCompared=False,allGuideAudioApproved=False,
    finalVideoProduced=False,humanWholeListening='pending',humanPronunciation='pending')
save(out,record)
session=read(PROD/'native-guides-tts-session-v1.json');session.update(finishedAt=now,stage='20-guide-PCM-generated-research-actually-running',exitCode=0,ttsModelLoaded=True,generatedGuides=20,
    actualResearchRestored=r,completionEvidence=out.relative_to(ROOT).as_posix());save(PROD/'native-guides-tts-session-v1.json',session)
asrSession=dict(schemaVersion=1,observedAt=now,sessionId=58325,actualPid=asr['actualPid'],createTime=asr['createTime'],commandLine=asr['commandLine'],cwd=asr['cwd'],
    stage=asr['stage'],structuredExecutionLog='projects/game-lighting-history-03/production/native-guides-asr-execution-v1.json',cpuThreads=2,gpuJobs=0,totalWindows=40,
    initialPreStateRefusal=dict(reason='Own PowerShell ancestor matched script text in process guard; no state/model/result created. Guard now excludes actual process ancestors and checks Python executable names.',exitCode=1))
save(PROD/'native-guides-asr-session-v1.json',asrSession)
cp=read(BASE/'checkpoint.json');job=dict(pid=asr['actualPid'],createTime=asr['createTime'],commandLine=asr['commandLine'],sessionId=58325,
    state=asrSession['structuredExecutionLog'],log=asrSession['structuredExecutionLog'],cpuThreads=2,gpuJobs=0,completed=len(asr['results']),total=40)
cp.update(updatedAt=now,stage='episode03-new-guide-only-40-window-CPU-ASR',ownedJobsRunning=[job],ownedActiveWork=[job],
    episode03GuideVoiceCompletion=dict(path=out.relative_to(ROOT).as_posix(),sha256=sha(out),guides=20,seconds=record['rawGuideSeconds'],researchRestored=True),
    next='Directly compare40 current guide windows and complete actual join/mix review. Sample-accurate original paragraph cuts are prepared for direct PCM review; preserve original84 samples. Then measured native60:40, current2.5D render/pair/pixel QA/output/private/scheduling/Git. All4 finals remain pending.')
save(BASE/'checkpoint.json',cp)
print(json.dumps(dict(guides=20,rawGuideSeconds=record['rawGuideSeconds'],researchOwner=owner.pid,researchChild=q.get('child_pid'),researchStatus=q['status'],asrPid=worker.pid,asrSession=58325,finalApproved=False)))
