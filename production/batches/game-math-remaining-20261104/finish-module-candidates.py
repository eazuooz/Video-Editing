"""Finish exact authorized M22–M33 review candidates from actual dependencies.

Finite job, no recurring trigger or platform access. A failed word/visual/input
check stops that version; other approved episodes can still be produced.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,importlib.util,json,os,subprocess,time,uuid
import psutil

B=Path(__file__).resolve().parent;R=B.parents[2];C=R/'shared/publishing/video-production-control.json';LEASE=R/'shared/output/GPU_HANDOFF.json'
# Episode : actual speech revision and required existing Unity diagnostic queues.
# M22 V5 checks the isolated knight correction, V4 the unchanged other layouts.
GATES={22:(3,[4,5]),23:(1,[3]),24:(1,[3]),25:(1,[3]),26:(2,[3]),27:(1,[2]),28:(1,[3]),29:(1,[1]),30:(1,[1]),31:(1,[1]),32:(1,[1]),33:(1,[1])}
def read(p):
 for n in range(12):
  try:return json.loads(p.read_text(encoding='utf-8-sig'))
  except (json.JSONDecodeError,PermissionError):
   if n==11:raise
   time.sleep(.1)
def write(p,d):
 t=p.with_suffix('.tmp');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8');os.replace(t,p)
def live(d):
 try:return abs(psutil.Process(d['pid']).create_time()-d['createTime'])<.1
 except (KeyError,psutil.NoSuchProcess):return False
def now():return datetime.now(timezone.utc).isoformat()
def authorized():
 c=read(C)['explicitMathRemainingBatch20261104']
 assert c['productionAllowedNow'] and c['advanceWithinExactBatch'] and not any(c[k] for k in ['upload','publish','schedule','deleteOrReplace','drive','automationOrHeartbeat'])
 return c
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--run',action='store_true');a=ap.parse_args()
 rows=read(B/'batch.json')['items'][1:];c=authorized();assert [r['id'] for r in rows]==['M'+str(i) for i in GATES] and all(r['slug'] in c['projectSlugs'] for r in rows)
 for row in rows:
  _,pvs=GATES[int(row['id'][1:])];s=R/'projects'/row['slug']/'production/unity-staging'
  for pv in pvs:
   q=read(s/f'local-preflight-v{pv}/queue.json');assert q['project']==row['slug'] and all(read(Path(j))['command']=='preflight' for j in q['jobs'])
 if not a.run:print('Validated exact twelve capture dependencies; no job started');return
 statefile=B/'local/finish-module-candidates.json';statefile.parent.mkdir(exist_ok=True)
 if statefile.is_file():assert not live(read(statefile)) and read(statefile)['status']!='finished','Existing finite finishing job preserved'
 state=dict(pid=os.getpid(),createTime=psutil.Process().create_time(),status='waiting',startedAt=now(),selected=[r['id'] for r in rows],results={},pending={},automation=False,publishing=False,humanListening=False)
 def setstate(**kw):state.update(kw,checkedAt=now());write(statefile,state)
 spec=importlib.util.spec_from_file_location('guard',R/'projects/game-math-shading-lights/production/run-capture-queue.py')
 guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
 def child(slug,tool,args,model=False):
  authorized();folder=B/'local/module-finish-logs';folder.mkdir(exist_ok=True)
  cmd=[str(R/'qwen3-tts/.venv/Scripts/python.exe') if model else 'python','-X','utf8',str(B/tool),*map(str,args)]
  with (folder/(slug+'-'+Path(tool).stem+'.log')).open('a',encoding='utf-8') as log:
   proc=subprocess.Popen(cmd,cwd=R,stdout=log,stderr=subprocess.STDOUT,creationflags=guard.CREATE)
   setstate(status='waiting-for-finite-child',step=tool,childPid=proc.pid)
   if proc.wait():raise RuntimeError(tool+' failed. Inspect '+str(log.name))
   setstate(status='waiting',childPid=None)
 def terminal_bad(folder,names):
  for name in names:
   f=folder/name
   if f.is_file() and read(f).get('status') in {'failed','failed-or-blocked','blocked-or-failed'}:raise RuntimeError('Inspect preserved failed input: '+str(f))
 def verified_inputs(p,checks):
  for folder in checks:
   q=read(folder/'queue.json');snap=read(folder/'progress.json')
   assert len(snap['completed'])==len(q['jobs']) and q['project']==p.name
   for j in q['jobs']:
    job=read(Path(j));out=Path(job['output']);s=read(out/'structural-check.json')
    assert s['fingerprint']==job['expectedFingerprint'] and (Path(q['sandbox'])/s['scene']).is_file()
    assert len(s['frames'])==len(job['sampleFrames']) and all(Path(f['path']).is_file() for f in s['frames'])
 def media_check(slug,q):
  owned=None;deadline=time.monotonic()+24*3600
  try:
   while owned is None:
    authorized();reason=guard.idle_reason();setstate(status='waiting',step='Wait to decode local pair',childPid=None)
    if reason is None:
     token=str(uuid.uuid4())
     try:
      with LEASE.open('x',encoding='utf8') as f:json.dump(dict(owner=slug+'-file-qa',id=token,pid=os.getpid(),createdAt=now()),f)
     except FileExistsError:pass
     else:owned=token;break
    if time.monotonic()>deadline:raise RuntimeError('QA resource wait expired without changing any other process')
    time.sleep(15)
   child(slug,'verify-module-media.py',['--queue',q,'--output',R/'output'/(slug+'-'+q.parent.name)])
  finally:guard.release_lease(owned)
 def consider(row):
  slug=row['slug'];num=int(row['id'][1:]);rev,queues=GATES[num];p=R/'projects'/slug;local=p/'production/local';a=local/f'audio-v{rev}';measured=local/f'edit-v{rev}/word-aligned-timeline.json'
  terminal_bad(a,['finite-worker.json','finite-word-review.json'])
  if not (a/'finite-word-review.json').is_file() or read(a/'finite-word-review.json')['status']!='word-evidence-ready-content-review-pending':
   return None,'Waiting for actual voice and word times'
  if not measured.is_file():
   if num>=27:return None,'Waiting for alignment by existing seven-episode speech job'
   child(slug,'align-module-speech.py',['--project',slug,'--audio-revision',a.name])
  t=read(measured)
  if t['flags']:return dict(status='spoken-timing-or-content-needs-review',flags=len(t['flags']),file=str(measured)),None
  checks=[p/f'production/unity-staging/local-preflight-v{v}' for v in queues]
  for pv in checks:
   terminal_bad(pv,['progress.json'])
   if not (pv/'progress.json').is_file() or read(pv/'progress.json')['status']!='images-ready-for-internal-visual-QA':return None,'Waiting for exact Unity runtime samples'
  verified_inputs(p,checks);sandbox=Path(read(checks[-1]/'queue.json')['sandbox']).name
  out=local/'render-v1';q=out/'queue.json'
  # Never adopt or duplicate an earlier render worker from a different job.
  if out.exists():raise RuntimeError('An existing render revision owns this destination; preserve and inspect: '+str(out))
  child(slug,'prepare-module-render.py',['--project',slug,'--sandbox',sandbox,'--audio-revision',a.name])
  child(slug,'compose-module.py',['--queue',q])   # fixed captions, native tracks and source hashes first
  child(slug,'run-module-render.py',['--queue',q,'--render','--wait-hours','24'])
  child(slug,'compose-module.py',['--queue',q,'--render','--wait-hours','24'])
  media_check(slug,q)
  child(slug,'review-final-mix.py',['--queue',q,'--wait-hours','24'],model=True)
  return dict(status='local-four-files-integrated-content-review-pending',technical=str(out/'final-qa/report.json'),speech=str(out/'final-mix-review/report.json'),finalReviewReady=False),None
 setstate()
 deadline=time.monotonic()+48*3600
 try:
  while len(state['results'])<len(rows):
   authorized()
   for row in rows:
    sid=row['id']
    if sid in state['results']:continue
    setstate(status='waiting',current=sid,step='Inspect actual dependencies',childPid=None)
    try:result,reason=consider(row)
    except Exception as e:result,reason=dict(status='production-attention-required',reason=repr(e),finalReviewReady=False),None
    if result is not None:
     state['results'][sid]=result;state['pending'].pop(sid,None)
     child(row['slug'],'update-preproduction.py',[])
    else:state['pending'][sid]=reason
   setstate(status='waiting',step='Waiting for named finite production dependencies',current=None,childPid=None)
   if len(state['results'])==len(rows):break
   if time.monotonic()>deadline:raise RuntimeError('Finite dependency wait ended. Completed media and other processes preserved.')
   time.sleep(30)
  setstate(status='finished',finishedAt=now())
 except BaseException as exc:setstate(status='failed-or-blocked',error=repr(exc),finishedAt=now());raise
if __name__=='__main__':main()
