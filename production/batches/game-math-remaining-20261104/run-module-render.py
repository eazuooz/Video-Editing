"""One finite actual-speech capture queue; no automatic next lecture or upload."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,errno,hashlib,importlib.util,json,os,shutil,subprocess,tempfile,time,uuid
import psutil
R=Path(__file__).resolve().parents[3];LEASE=R/'shared/output/GPU_HANDOFF.json';CREATE=getattr(subprocess,'CREATE_NO_WINDOW',0)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
spec=importlib.util.spec_from_file_location('guard',R/'projects/game-math-shading-lights/production/run-capture-queue.py');G=importlib.util.module_from_spec(spec);spec.loader.exec_module(G)
def verify(job,folder):
 p=folder/'capture-success.json'
 if not p.exists():return False
 d=read(p);assert d['fingerprint']==job['expectedFingerprint'] and d['completed']==job['frames']
 meta=json.loads(subprocess.check_output([str(Path(job['ffmpeg']).with_name('ffprobe.exe')),'-v','error','-show_streams','-of','json',str(folder/'unity.mp4')],creationflags=CREATE))
 s=next(s for s in meta['streams'] if s['codec_type']=='video');assert (s['width'],s['height'],s['r_frame_rate'],int(s['nb_frames']))==(1920,1080,'60/1',job['frames'])
 save(folder/'encoded-structure.json',dict(fingerprint=job['expectedFingerprint'],frames=job['frames'],size=[1920,1080],fps='60/1',fullDecodeQa=False,visualQa=False));return True

def adopt_prefix(q,job,folder):
 if q.get('preservedPrefix') or q['project']!='game-math-pipeline-shaders' or folder.exists():return False
 project=R/'projects'/q['project'];prefix=project/'production/local/preserved-prefix-v1'
 sid=job['sceneId'];prior=prefix/'jobs'/(sid+'.json')
 if not prior.exists():return False
 saved=read(prior);source=Path(saved['output']);receipt=source/'capture-success.json'
 if not receipt.exists():return False
 if saved['frames']!=job['frames'] or saved['expectedFingerprint']!=job['expectedFingerprint']:return False
 if sha(Path(saved['shotFile']))!=sha(Path(job['shotFile'])):return False
 proof=read(prefix/'measured-prefix.json')
 chunk=next(row for row in proof['confirmed'] if row['scene']==sid)
 if sha(Path(q['audioDirectory'])/'chunks'/(sid+'-01-scene.wav'))!=chunk['sourceTakeSha256']:return False
 assert verify(saved,source);folder.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(dir=folder.parent,prefix='.adopt-prefix-') as work:
  candidate=Path(work)/sid;candidate.mkdir()
  for name in ['unity.mp4','capture-success.json']:
   try:os.link(source/name,candidate/name)
   except OSError as exc:
    if exc.errno!=errno.EXDEV and getattr(exc,'winerror',None)!=17:raise
    shutil.copy2(source/name,candidate/name)
  save(candidate/'source-reuse.json',dict(originalCapture=str(source),originalJob=saved['id'],
         finalJob=job['id'],scene=sid,shotSha256=sha(Path(job['shotFile'])),actualTakeSha256=chunk['sourceTakeSha256'],
         imageSha256=sha(source/'unity.mp4'),method='Same measured shot JSON, footage length, renderer fingerprint and raw PCM. Original capture receipt and editable scene are preserved.'))
  os.rename(candidate,folder)
 return verify(job,folder)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--queue',required=True);ap.add_argument('--render',action='store_true');ap.add_argument('--wait-hours',type=float,default=6);a=ap.parse_args()
 qpath=Path(a.queue).resolve();q=read(qpath);P=R/'projects'/q['project'];assert qpath.is_relative_to(P/'production/local')
 def authorized():
  c=read(R/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104'];assert c['productionAllowedNow'] and P.name in c['projectSlugs'] and P.name!='game-math-shading-lights'
  assert read(Path(q['sandbox'])/'MATH_CAPTURE_SANDBOX.json')['fingerprint']==q['fingerprint']
 authorized();assert sha(Path(q['wordAlignment']))==q['wordAlignmentSha256'] and not read(Path(q['wordAlignment']))['flags']
 if not a.render:print(f"{len(q['jobs'])} jobs validated; no renderer started");return
 statefile=qpath.parent/'progress.json'
 if statefile.exists():
  old=read(statefile)
  try:assert abs(psutil.Process(old['pid']).create_time()-old['createTime'])>.1,'Capture queue already active'
  except psutil.NoSuchProcess:pass
 s=dict(pid=os.getpid(),createTime=psutil.Process().create_time(),status='waiting',completed=[],startedAt=now(),finalReviewReady=False,automation=False);owned=None
 episode=int(q['episode'][1:]);prefix='RemainingMath' if episode<=23 else 'MotionMath' if episode<=26 else 'Mechanics' if episode<=28 else 'Dynamics' if episode<=30 else 'Curve'
 try:
  for jp in q['jobs']:
   authorized();job=read(Path(jp));folder=Path(job['output'])
   assert job['command']=='render' and job['speechTimingVerified'] and job['expectedFingerprint']==q['fingerprint']
   if q.get('preservedPrefix') and (Path(q['targetAudioDirectory'])/'narration.wav').is_file():
    s.update(status='prefix-stopped-at-final-audio-boundary',finishedAt=now());save(statefile,s);return
   if verify(job,folder) or adopt_prefix(q,job,folder):s['completed'].append(job['id']);save(statefile,s);continue
   assert not folder.exists() or not any(folder.iterdir()),'Preserve partial capture and inspect before retry'
   deadline=time.monotonic()+a.wait_hours*3600
   while owned is None:
    if q.get('preservedPrefix') and (Path(q['targetAudioDirectory'])/'narration.wav').is_file():
     s.update(status='prefix-stopped-at-final-audio-boundary',finishedAt=now());save(statefile,s);return
    authorized();reason=G.idle_reason();s.update(status='waiting',reason=reason,current=job['id'],checkedAt=now());save(statefile,s)
    if reason is None:
     candidate=str(uuid.uuid4())
     try:
      with LEASE.open('x',encoding='utf-8') as f:json.dump(dict(owner=P.name+'-capture',id=candidate,pid=os.getpid(),createdAt=now()),f)
     except FileExistsError:pass
     else:owned=candidate;break
    if time.monotonic()>deadline:raise RuntimeError('Bounded resource wait ended; other jobs preserved')
    time.sleep(5)
   if adopt_prefix(q,job,folder):
    G.release_lease(owned);owned=None;s['completed'].append(job['id']);save(statefile,s);continue
   env=os.environ.copy();env['YAMYAM_MATH_CAPTURE_JOB']=jp
   child=subprocess.Popen([q['unity'],'-batchmode','-job-worker-count','2','-projectPath',q['sandbox'],'-executeMethod',f'Yamyam.{prefix}Capture.UnityLectureCapture.Run','-logFile',str(qpath.parent/(job['id']+'.unity.log'))],env=env,creationflags=CREATE)
   s.update(status='capturing',unityPid=child.pid);save(statefile,s)
   if child.wait() or not verify(job,folder):raise RuntimeError('Owned capture failed; inspect preserved logs')
   G.release_lease(owned);owned=None;s['completed'].append(job['id']);save(statefile,s)
  s.update(status='preserved-prefix-captures-complete' if q.get('preservedPrefix') else 'body-captures-complete-compositing-and-QA-pending',finishedAt=now());save(statefile,s)
 except BaseException as exc:s.update(status='failed-or-blocked',error=repr(exc),finishedAt=now());save(statefile,s);raise
 finally:G.release_lease(owned)
if __name__=='__main__':main()
