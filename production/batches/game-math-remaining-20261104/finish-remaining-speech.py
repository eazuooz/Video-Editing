"""Single finite production job: M27–M33 ready previews -> speech -> measured cues.

No scheduler, repeated render, retry after failure, platform write or approval.
The GPU is owned only by the existing per-stage workers. An unresolved
transcript or a missing runtime check stays an explicit editorial work item.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,os,subprocess,time
import psutil

B=Path(__file__).resolve().parent;R=B.parents[2]
C=R/'shared/publishing/video-production-control.json'
TARGETS=[('M27','game-math-forces-friction',2),('M28','game-math-springs-damping',3),
         ('M29','game-math-momentum-collisions',1),('M30','game-math-rigid-body-inertia',1),
         ('M31','game-math-parametric-hermite',1),('M32','game-math-bezier-subdivision',1),
         ('M33','game-math-splines-continuity',1)]
def read(p):
 for attempt in range(6):
  try:return json.loads(p.read_text(encoding='utf-8-sig'))
  except (PermissionError,json.JSONDecodeError):
   if attempt==5:raise
   time.sleep(.2)
def alive(d):
 try:return abs(psutil.Process(d['pid']).create_time()-d['createTime'])<.1
 except (KeyError,psutil.NoSuchProcess):return False
def now():return datetime.now(timezone.utc).isoformat()
def authorized():
 c=read(C)['explicitMathRemainingBatch20261104']
 assert c['productionAllowedNow'] and c['advanceWithinExactBatch'] and all(slug in c['projectSlugs'] and sid in c['itemIds'] for sid,slug,_ in TARGETS)
def args_for(tool,*args):return ['python','-X','utf8',str(B/tool),*args]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--run',action='store_true');a=ap.parse_args();authorized()
 for sid,slug,rev in TARGETS:
  p=R/'projects'/slug;q=read(p/f'production/unity-staging/local-preflight-v{rev}/queue.json')
  assert q['project']==slug and q['jobs'] and all(read(Path(j))['command']=='preflight' for j in q['jobs'])
  assert read(p/'planning/production-plan.json')['episode']==sid
 if not a.run:print('Validated seven exact speech dependencies; no new job started.');return
 statefile=B/'local/remaining-speech-worker.json';statefile.parent.mkdir(exist_ok=True)
 if statefile.exists():
  old=read(statefile);assert not alive(old) and old['status']!='finished','Preserve existing finite worker'
 s=dict(pid=os.getpid(),createTime=psutil.Process().create_time(),status='waiting',startedAt=now(),results={},automation=False,humanListening=False)
 def write(**values):
  s.update(values,checkedAt=now());tmp=statefile.with_suffix('.tmp');tmp.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(tmp,statefile)
 def wait():authorized();write(status='waiting');time.sleep(12)
 def step(cmd,slug,label):
  authorized();folder=B/'local/remaining-speech-logs';folder.mkdir(exist_ok=True)
  with (folder/(slug+'-'+label+'.log')).open('a',encoding='utf-8') as log:
   worker=subprocess.Popen(cmd,cwd=R,stdout=log,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
   write(status='waiting-for-finite-child',childPid=worker.pid,step=label)
   if worker.wait():raise RuntimeError(label+' failed; evidence preserved in '+str(log.name))
 def finished_or_run(statepath,cmd,slug,label,good):
  if statepath.exists():
   existing=read(statepath)
   if alive(existing):
    write(step='Waiting for existing '+label)
    while alive(existing) and existing.get('status')!=good:
     if existing.get('status')=='failed-or-blocked':raise RuntimeError(label+' failed in existing worker')
     wait();existing=read(statepath)
   assert read(statepath)['status']==good,label+' already attempted; inspect before retry'
  else:step(cmd,slug,label);assert read(statepath)['status']==good
 try:
  write()
  for sid,slug,rev in TARGETS:
   try:
    p=R/'projects'/slug;pv=p/f'production/unity-staging/local-preflight-v{rev}';audio=p/'production/local/audio-v1'
    start=time.monotonic();write(status='waiting',current=sid,step='Await exact runtime diagnostic images',childPid=None)
    while not (pv/'progress.json').is_file() or read(pv/'progress.json')['status']!='images-ready-for-internal-visual-QA':
     if (pv/'progress.json').is_file() and read(pv/'progress.json')['status']=='failed-or-blocked':raise RuntimeError('Selected preview failed. Source and prior evidence preserved.')
     dispatcher=read(B/'module-queue-worker.json')
     if not alive(dispatcher) and dispatcher.get('status')!='running-one-preflight':raise RuntimeError('Diagnostic dispatcher stopped; inspect actual progress')
     if time.monotonic()-start>24*3600:raise RuntimeError('Runtime diagnostic still unavailable; retain all other jobs')
     wait()
    for j in read(pv/'queue.json')['jobs']:
     job=read(Path(j));out=Path(job['output']);receipt=read(out/'structural-check.json')
     assert receipt['fingerprint']==job['expectedFingerprint'] and len(receipt['frames'])==len(job['sampleFrames'])
     assert all(Path(x['path']).is_file() for x in receipt['frames'])
    if not read(p/'planning/production-plan.json').get('narrationFinal'):
     step(args_for('freeze-reviewed-module-narration.py','--project',slug),slug,'freeze')
    finished_or_run(audio/'finite-worker.json',args_for('finish-selected-voice.py','--project',slug,'--wait-hours','24'),slug,'voice','voice-generated-review-pending')
    finished_or_run(audio/'finite-word-review.json',args_for('finish-word-review.py','--project',slug,'--wait-hours','24'),slug,'words','word-evidence-ready-content-review-pending')
    measured=p/'production/local/edit-v1/word-aligned-timeline.json'
    if not measured.is_file():step(args_for('align-module-speech.py','--project',slug),slug,'align')
    evidence=read(measured);s['results'][sid]=dict(status=evidence['status'],scenes=len(evidence['scenes']),flags=len(evidence['flags']),evidence=str(measured),finalVideo=False)
   except Exception as exc:s['results'][sid]=dict(status='needs-production-attention',reason=repr(exc),finalVideo=False)
   write(status='waiting',childPid=None)
  write(status='finished',finishedAt=now(),step='Exact seven speech jobs considered; inspect flags and images before final rendering')
 except BaseException as e:write(status='failed-or-blocked',error=repr(e));raise
if __name__=='__main__':main()
