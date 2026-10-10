"""Record observed session31318 exit0 and exact cooperative research return."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,os
import psutil
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/game-lighting-history-03/production'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
    tmp=p.with_name(p.name+'.writing-'+str(os.getpid()))
    tmp.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,p)
done=read(BASE/'native-guide-repairs-tts-execution-v2.json')
lease=read(ROOT/'shared/output/gpu-handoff'/(done['leaseToken']+'.json'))
assert done['exitCode']==0 and done['generationComplete'] and len(done['results'])==13 and len(done['joinedGuides'])==2
assert lease['state']=='research_resume_verified' and lease['ttsExitCode']==0
assert not (ROOT/'shared/output/GPU_HANDOFF.json').exists()
for pid,created in [(done['actualPid'],done['createTime']),(lease['coordinator']['pid'],lease['coordinator']['createTime'])]:
    if psutil.pid_exists(pid):assert abs(psutil.Process(pid).create_time()-created)>.1,'Owned process still alive'
q=lease['resumedQueue'];p=psutil.Process(q['pid']);status=read(Path(lease['queueDir'])/'status.json')
assert abs(p.create_time()-q['createTime'])<.1 and p.cmdline()==q['command'] and p.cwd().lower()==q['cwd'].lower()
assert status['owner_pid']==p.pid and status['status'] in ['running','waiting_for_resources']
child=None
if status.get('child_pid'):
    c=psutil.Process(status['child_pid']);child=dict(pid=c.pid,createTime=c.create_time(),command=c.cmdline(),cwd=c.cwd())
request=read(BASE/'native-guide-repairs-tts-request-v2.json')
for x in request['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256']
for x in done['results']+done['joinedGuides']:assert sha(ROOT/x['path'])==x['sha256']
stamp=datetime.now(timezone.utc).isoformat()
record=dict(schemaVersion=1,observedAt=stamp,sessionId=31318,actualToolSessionExitCode=0,
    actualToolSessionExitObserved=True,ttsWorkerGone=True,coordinatorGone=True,
    execution=dict(path='projects/game-lighting-history-03/production/native-guide-repairs-tts-execution-v2.json',sha256=sha(BASE/'native-guide-repairs-tts-execution-v2.json')),
    leaseToken=done['leaseToken'],completedBoundary=lease['completedJobEvidence'],
    resumedQueue=q,resumedStatus=status,resumedChild=child,researchRestored=True,
    guideCandidates=[{k:x[k] for k in ['id','path','sha256','samples','sampleRate','seconds']} for x in done['joinedGuides']],
    sentenceChunks=13,original84Regenerated=False,other18Regenerated=False,protectedInputsUnchanged=True,
    voiceApproved=False,finalMixedAsrApproved=False,humanListening='pending',humanPronunciation='pending',
    next='One CPU2 worker:13 sentences,2 joined whole and2 independent context decodes; directly compare all17 texts.')
out=BASE/'native-guide-repairs-tts-completion-and-research-resume-v2.json';assert not out.exists();save(out,record)
session=read(BASE/'native-guide-repairs-tts-session-v2.json');session.update(finishedObservedAt=stamp,exitCode=0,actualToolSessionExitObserved=True,researchRestored=True,completionRecord=out.relative_to(ROOT).as_posix(),gpuJobs=0,stage='generated-two-candidates-research-restored-awaiting-direct-ASR');save(BASE/'native-guide-repairs-tts-session-v2.json',session)
cp=read(ROOT/'production/research/game-lighting-history/checkpoint.json');cp.update(updatedAt=stamp,stage='two-guide-repair-candidates-ready-for-CPU-ASR',ownedActiveWork=None,ownedJobsRunning=[],episode03GuideRepairCompletion=dict(path=out.relative_to(ROOT).as_posix(),sha256=sha(out),researchRestored=True,voiceApproved=False));save(ROOT/'production/research/game-lighting-history/checkpoint.json',cp)
print(json.dumps(dict(researchRestored=True,queuePid=p.pid,status=status['status'],job=status.get('job'),sentenceChunks=13,joinedCandidates=2,voiceApproved=False),ensure_ascii=False))
