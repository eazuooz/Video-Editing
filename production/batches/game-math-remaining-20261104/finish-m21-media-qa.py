"""Finite M21 encode -> technical QA stage, preserving other jobs and outputs."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,importlib.util,json,os,re,subprocess,time,uuid
import psutil
ap=argparse.ArgumentParser();ap.add_argument('--revision',default='render-v3');args=ap.parse_args();assert re.fullmatch(r'render-v\d+',args.revision)
R=Path(__file__).resolve().parents[3];P=R/'projects/game-math-shading-lights';Q=P/'production/local'/args.revision;L=R/'shared/output/GPU_HANDOFF.json'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def now():return datetime.now(timezone.utc).isoformat()
spec=importlib.util.spec_from_file_location('guard',P/'production/run-capture-queue.py');G=importlib.util.module_from_spec(spec);spec.loader.exec_module(G)
sf=Q/'finite-final-qa.json'
if sf.exists():
 d=read(sf)
 try:assert abs(psutil.Process(d['pid']).create_time()-d['createTime'])>.1,'QA worker already active'
 except psutil.NoSuchProcess:pass
 assert d['status']!='technical-QA-ready-content-review-pending','Preserve completed QA'
s=dict(pid=os.getpid(),createTime=psutil.Process().create_time(),status='waiting-for-encoded-master',startedAt=now(),humanReview=False,automation=False)
def save():sf.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
owned=None;deadline=time.monotonic()+12*3600
try:
 while owned is None:
  G.authorized();current=read(Q/'composite/worker.json');assert current['status']!='failed','Preserve failed encode for repair'
  reason='Waiting for encoded master'
  if current['status']=='encoded':reason=G.idle_reason()
  s.update(reason=reason,checkedAt=now());save()
  if reason is None:
   candidate=str(uuid.uuid4())
   try:
    with L.open('x',encoding='utf-8') as f:json.dump(dict(owner=P.name+'-final-qa',id=candidate,pid=os.getpid(),createdAt=now()),f)
   except FileExistsError:pass
   else:owned=candidate;break
  if time.monotonic()>deadline:raise RuntimeError('Bounded wait ended; no other job changed')
  time.sleep(15)
 s.update(status='checking-final-media');save()
 with (Q/'final-qa.stdout.log').open('w',encoding='utf-8') as out,(Q/'final-qa.stderr.log').open('w',encoding='utf-8') as err:
  child=subprocess.Popen(['python','-X','utf8',str(P/'production/verify-final-media.py'),'--queue',str(Q/'queue.json'),'--output',str(R/'output'/f'{P.name}-{args.revision}')],cwd=R,stdout=out,stderr=err,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));s['qaPid']=child.pid;save();code=child.wait()
 if code:raise RuntimeError('Technical QA failed; inspect original evidence')
 s.update(status='technical-QA-ready-content-review-pending',finishedAt=now());save()
except BaseException as exc:s.update(status='failed-or-blocked',error=repr(exc),finishedAt=now());save();raise
finally:G.release_lease(owned)
