"""One finite serial run of twelve prepared diagnostic queues, never a scheduler.

Wait for the current M21 master edit before competing for the GPU. Failures are
recorded per queue and preserved; another prepared, authorized queue may follow.
These pictures are candidates for inspection, not automatic final-video passes.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,os,subprocess,time
import psutil
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def now():return datetime.now(timezone.utc).isoformat()
CHOICES=[('skinning-normal-map',4),('pipeline-shaders',3),('velocity-derivatives',3),('acceleration-integration',3),('circular-motion',3),('forces-friction',2),('springs-damping',3),('momentum-collisions',1),('rigid-body-inertia',1),('parametric-hermite',1),('bezier-subdivision',1),('splines-continuity',1)]
ap=argparse.ArgumentParser();ap.add_argument('--run',action='store_true');ap.add_argument('--wait-hours',type=float,default=12);a=ap.parse_args()
queues=[R/'projects'/('game-math-'+slug)/'production/unity-staging'/f'local-preflight-v{revision}/queue.json' for slug,revision in CHOICES]
def authorized():
 c=read(R/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104'];assert c['productionAllowedNow']
 assert all(read(q)['project'] in c['projectSlugs'] for q in queues)
authorized()
for q in queues:
 data=read(q);assert Path(data['sandbox']).is_dir()
 assert read(Path(data['sandbox'])/'MATH_CAPTURE_SANDBOX.json')['fingerprint']==data['fingerprint']
 assert all(read(Path(j))['command']=='preflight' for j in data['jobs'])
if not a.run:print('12 exact prepared queues validated; no renderer started.');raise SystemExit(0)
statefile=B/'module-queue-worker.json'
if statefile.exists():
 old=read(statefile)
 try:assert abs(psutil.Process(old['pid']).create_time()-old['createTime'])>.1,'Same finite dispatcher already active'
 except psutil.NoSuchProcess:pass
 assert old['status']!='prepared-previews-finished-review-pending','Do not repeat unchanged completed work'
s=dict(pid=os.getpid(),createTime=psutil.Process().create_time(),status='waiting-for-m21-edit',startedAt=now(),completed=[],failed=[],automation=False,finalVideo=False,humanReview=False)
save(statefile,s);deadline=time.monotonic()+a.wait_hours*3600
try:
 m21=R/'projects/game-math-shading-lights/production/local/render-v3/composite/worker.json'
 while True:
  authorized();status=read(m21).get('status') if m21.exists() else None
  if status=='encoded':break
  if status=='failed':raise RuntimeError('M21 edit needs repair; preserve current output before new diagnostic work')
  if time.monotonic()>deadline:raise RuntimeError('Bounded wait ended; no jobs terminated')
  s.update(checkedAt=now());save(statefile,s);time.sleep(20)
 for q in queues:
  authorized();p=q.parent/'progress.json';prior=read(p) if p.exists() else None
  if prior:
   try:active=abs(psutil.Process(prior['pid']).create_time()-prior['createTime'])<.1
   except psutil.NoSuchProcess:active=False
   if active:raise RuntimeError('Prepared queue already running; no duplicate launched: '+str(q))
   if prior['status']=='images-ready-for-internal-visual-QA':s['completed'].append(dict(queue=str(q),disposition='prior-complete-preserved'));save(statefile,s);continue
   if prior['status']=='failed-or-blocked':s['failed'].append(dict(queue=str(q),reason='Prior partial attempt preserved for inspection'));save(statefile,s);continue
  s.update(status='running-one-preflight',current=str(q));save(statefile,s)
  with (q.parent/'queue.stdout.log').open('w',encoding='utf-8') as out,(q.parent/'queue.stderr.log').open('w',encoding='utf-8') as err:
   child=subprocess.Popen(['python','-X','utf8',str(B/'run-module-preflight.py'),'--queue',str(q),'--run','--wait-hours',str(a.wait_hours)],cwd=R,stdout=out,stderr=err,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
   s['childPid']=child.pid;save(statefile,s);code=child.wait()
  if code:s['failed'].append(dict(queue=str(q),exitCode=code))
  else:s['completed'].append(dict(queue=str(q),disposition='images-generated-review-pending'))
  save(statefile,s)
 s.update(status='prepared-previews-finished-review-pending',finishedAt=now());save(statefile,s)
except BaseException as exc:s.update(status='failed-or-blocked',error=repr(exc),finishedAt=now());save(statefile,s);raise
