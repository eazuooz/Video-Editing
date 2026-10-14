"""Record actual closed v1 and live corrected-context v2 identities, preserving other checkpoint fields."""
from pathlib import Path
import datetime,hashlib,json,os,psutil
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'projects/game-lighting-history-04/production'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rec(p):return dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p))
def write(p,x):
 t=p.with_name(p.name+'.writing-'+str(os.getpid()));t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
def alive(i):
 if not psutil.pid_exists(i['pid']):return False
 p=psutil.Process(i['pid']);return abs(p.create_time()-i['createTime'])<.1 and p.cmdline()==i['command']
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
old=read(BASE/'additive-asr-execution-v1.json');review=read(BASE/'additive-asr-direct-progress-v1.json')
if old.get('exitCode')!=0 or alive(old['actualIdentity']) or not review['all48DirectlyCompared']:raise RuntimeError('Closed directly compared v1 required')
closed=read(BASE/'additive-asr-session-v1.json')
closed.update(observedAt=now,actualIdentityLive=False,execution=rec(BASE/'additive-asr-execution-v1.json'),status=old['status'],exitCode=0,completedWindows=48,sessionClosed=True,all48DirectlyCompared=True,independentContextsApproved=False)
write(BASE/'additive-asr-session-v1.json',closed)
state=read(BASE/'additive-context-execution-v2.json');live=alive(state['actualIdentity'])
if not live or state.get('exitCode') is not None:raise RuntimeError('Actual live corrected-context worker required')
record=dict(observedAt=now,session=22557,actualIdentity=state['actualIdentity'],actualIdentityLive=live,execution=rec(BASE/'additive-context-execution-v2.json'),status=state['status'],completedWindows=len(state['completed']),expectedWindows=24,log='projects/game-lighting-history-04/production/local/additive-context-v2-resume.log',cpuThreads=2,gpuJobs=0,original87AsrRepeated=False,new24WholeAsrRepeated=False,correctedContextsApproved=False,finalMixedAsrApproved=False,finalVideoProduced=False,importFailureHistory=rec(BASE/'additive-context-import-failure-v2.json'))
write(BASE/'additive-context-session-v2.json',record)
cp=ROOT/'production/research/game-lighting-history/checkpoint.json';c=read(cp)
c.update(updatedAt=now,stage='episode04-corrected-measured-boundaries-24-complete-context-CPU-ASR',ownedJobsRunning=[record],ownedGpuJobs=0)
c['episode04AdditiveNarration'].update(currentState='original87-and-selected24-byte-preserved-corrected24-contexts-running',previousAsrSessionClosed=closed,currentAsrSession=record,measuredReviewAssembly=rec(BASE/'additive-unmixed-review-assembly-v2.json'),measuredUnmixedSeconds=1680.440125,fullNewAsrApproved=False,finalMixedAsrApproved=False,finalApproved=False)
c['next']='Directly compare only24 corrected complete contexts; prepare word-timed black projected2.5D scenes, independent KO/EN captions, and concept-matched native intervals. Final timing, mix, render, collection, private settings and Git remain pending.'
write(cp,c);print(json.dumps(dict(session=22557,pid=record['actualIdentity']['pid'],completed=record['completedWindows'],live=live,gpuJobs=0)))
