"""Seal only the completed, directly compared corrected contexts; no final audio approval."""
from pathlib import Path
import datetime, hashlib, json, os, psutil
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/game-lighting-history-04/production'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rec(p):return dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p))
def write(p,x):
    t=p.with_name(p.name+'.writing-'+str(os.getpid()))
    t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
state=read(BASE/'additive-context-execution-v2.json');identity=state['actualIdentity']
if state.get('exitCode')!=0 or len(state['completed'])!=24:raise RuntimeError('Actual exit0/24 required')
if psutil.pid_exists(identity['pid']):
    p=psutil.Process(identity['pid'])
    if abs(p.create_time()-identity['createTime'])<.1 and p.cmdline()==identity['command']:raise RuntimeError('Owned worker still live')
direct_path=BASE/'additive-context-direct-progress-v2.json';direct=read(direct_path)
if len(direct['records'])!=24:raise RuntimeError('All24 complete texts and word times must be directly read')
assembly=read(BASE/'additive-unmixed-review-assembly-v2.json')
if not assembly['original87FullPcmByteIdentical'] or not assembly['new24SelectedPcmByteIdentical']:raise RuntimeError('All preserved PCM required')
if sha(ROOT/assembly['audio']['path'])!=assembly['audio']['sha256']:raise RuntimeError('Current PCM changed')
for r in direct['records']:
    c=next(x for x in state['completed'] if x['label']==r['label'])
    if c['sha256']!=r['sha256'] or sha(ROOT/c['result'])!=r['sha256'] or not r['completeContextTextCompared']:raise RuntimeError('Directly compared unchanged result required')
    r['technicalCompleteContextTextAccepted']=True
whole=read(BASE/'additive-asr-direct-progress-v1.json')
if len([r for r in whole['records'] if r['label'].startswith('whole-') and r['expectedWholeTextDirectlyRead'] and r['actualWholeTextAndAllWordTimesDirectlyRead']])!=24:raise RuntimeError('Preserved directly compared24 whole takes required')
for r in whole['records']:
    if sha(ROOT/r['path'])!=r['sha256']:raise RuntimeError('Preserved ASR result changed')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
direct.update(reviewedAt=now,all24DirectlyCompared=True,correctedContextsApproved=True,
    approvalScope='Technical complete-text/order/no-omission comparison over current unchanged unmixed PCM only. Recognition/pronunciation variants and listening remain pending; this is not final Nimbus-mix approval.',
    duplicateSourceContexts=[dict(jobs=[18,19],reason='Adjacent additions share one complete four-paragraph acoustic context.'),dict(jobs=[23,24],reason='Adjacent additions share one complete four-paragraph acoustic context; identical recognition is not an independent source.')],
    completedExecution=rec(BASE/'additive-context-execution-v2.json'),currentAssembly=rec(BASE/'additive-unmixed-review-assembly-v2.json'),
    wholeTakeDirectReview=rec(BASE/'additive-asr-direct-progress-v1.json'),
    wholeNewAsrApproved=False,finalMixedAsrApproved=False,humanWholeListeningApproved=False,humanPronunciationApproved=False)
write(direct_path,direct)
session_path=BASE/'additive-context-session-v2.json';session=read(session_path)
session.update(observedAt=now,actualIdentityLive=False,sessionClosed=True,status=state['status'],exitCode=0,completedWindows=24,execution=rec(BASE/'additive-context-execution-v2.json'),directReview=rec(direct_path),correctedContextsApproved=True,finalMixedAsrApproved=False)
write(session_path,session)
cp=ROOT/'production/research/game-lighting-history/checkpoint.json';c=read(cp)
c.update(updatedAt=now,stage='episode04-corrected24-contexts-directly-compared-preparing-native-and-word-timed-scenes',ownedJobsRunning=[],ownedGpuJobs=0)
c['episode04AdditiveNarration'].update(currentState='original87-selected24-byte-preserved-corrected24-technical-context-review-complete',currentAsrSession=session,correctedContextDirectReview=rec(direct_path),fullNewAsrApproved=False,finalMixedAsrApproved=False,finalApproved=False)
c['next']='Select and review concept-matched native intervals; integrate111 independent word-timed black projected2.5D paragraphs and KO/EN captions into a measured60:40 plan. Final mix ASR, animated pixels, render/QA, collection, private settings and Git remain pending.'
write(cp,c)
print(json.dumps(dict(session=22557,closed=True,completed=24,allDirectlyCompared=True,technicalContextAccepted=True,finalMixedApproved=False)))
