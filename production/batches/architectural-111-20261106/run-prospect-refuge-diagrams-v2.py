"""Exact06.02 SDK crop: read-only readiness by default; one finite owned job.

No browser/model/media process is started without --execute and real ASR-bound
authored cues. Failed/older attempts, foreign jobs, user apps and leases persist.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,math,os,shutil,subprocess,time,uuid
from pathlib import Path
import psutil
from initialize import ROOT,HERE,MEDIA,AUTH_KEY,read,save

spec=importlib.util.spec_from_file_location('prospect_diagram_native_resource',HERE/'run-prospect-refuge-native.py')
native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
PROTOCOL='architectural111-06-02-mc-crop-v2';OWNER='architectural-111-06-02-mc-crop-v2'
native.runtime.PROTOCOL=PROTOCOL;native.runtime.OWNER=OWNER
runtime=native.runtime
PROJECT=ROOT/'projects/shorts-leveldesign-06-02'
TOPIC=MEDIA/'shorts-leveldesign-06-02'
ATTEMPTS=TOPIC/'mc-render-attempts-v2';WORKER=MEDIA/'06-02-mc-v2-worker.json';STATE=MEDIA/'06-02-mc-v2-progress.json'
SOURCE=ROOT/'motion-canvas/src/projects/shorts-leveldesign-06-02'
NODE_SOURCE=HERE/'render-prospect-refuge-diagrams-v2.cjs'
CREATE=getattr(subprocess,'CREATE_NO_WINDOW',0)

def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def digest(j):return hashlib.sha256(json.dumps(j,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def pinned(row):
 p=Path(row['path']).resolve()
 if not p.is_file() or len(row.get('sha256',''))!=64 or sha(p)!=row['sha256']:raise ValueError('Pinned input changed: '+str(p))
 return dict(path=str(p),sha256=row['sha256'])

def prepare(cue_path=None):
 auth=read(ROOT/'shared/publishing/video-production-control.json')[AUTH_KEY]
 if auth['status'] in ('paused','stopped','cancelled') or not auth['automaticAdvanceWithinExactList'] or auth['automaticAdvanceOutsideList']:raise ValueError('Exact111 authorization inactive')
 batch=read(HERE/'batch.json');checkpoint=read(HERE/'checkpoint.json')
 if len(batch['projects'])!=111 or not batch['localFinalReviewOnly'] or checkpoint.get('currentTopicId')!='06.02' or not any(x['topicId']=='06.02'for x in batch['projects']):raise ValueError('Only current06.02 inside exact111 can render')
 library_pins={'run-zen-view-diagrams.py':'2b88ec28db07e136e2969140dab39ae6673ac39a9102f1de750cc74744cce62e','render-zen-view-diagrams.cjs':'fb811f9166908f18d8242713272bdfe9715095f872a2b58ce3aa3d4b2b40dd2d','run-prospect-refuge-native.py':'4c7a90bcc4857a643703791db3f03373cdafc7aabc5631d52aaa6dbc2657b0a4','prospect-refuge-resource-qualification.py':'2dbb128a891fabf9c440e5790b88481c7901fbf087098557c540b19b8ecd5f5d'}
 for name,want in library_pins.items():
  if sha(HERE/name)!=want:raise ValueError('Reviewed MC/resource source changed: '+name)
 cue_builder=HERE/'build-prospect-refuge-diagram-cues-v2.py'
 sp=importlib.util.spec_from_file_location('prospect_owned_actual_mc_cues',cue_builder);builder=importlib.util.module_from_spec(sp);sp.loader.exec_module(builder)
 builder.source_contract()
 if cue_path is None:return dict(ready=False,topicId='06.02',requires='Actual current103physical/96logical/25-paragraph voice + blind-ASR caption timing and one P04/P25 word-bound cue-plan',rendererStarted=False,frameTimingFabricated=False)
 cue_path=Path(cue_path).resolve();cue=builder.verify_existing(cue_path)
 motion=ROOT/'motion-canvas/node_modules';versions={k:read(motion/f'@motion-canvas/{k}/package.json')['version']for k in ('core','2d')}
 sdk_files=['@motion-canvas/core/lib/app/Renderer.js','@motion-canvas/core/lib/app/Stage.js','@motion-canvas/core/lib/app/bootstrap.js','@motion-canvas/vite-plugin/lib/partials/scenes.js','@motion-canvas/vite-plugin/lib/partials/meta.js','@motion-canvas/vite-plugin/lib/partials/webgl.js','vite/dist/node/index.js','puppeteer/package.json']
 paths=[Path(__file__),NODE_SOURCE,cue_path,cue_builder,HERE/'run-first-native.py']+[HERE/name for name in library_pins]+[motion/f for f in sdk_files]
 pins=[pinned(row)for row in cue['inputPins']]+[dict(path=str(p.resolve()),sha256=sha(p))for p in paths]
 for tool in ('node','ffmpeg','ffprobe'):
  if not shutil.which(tool):raise ValueError('Installed tool missing: '+tool)
 result=dict(ready=True,topicId='06.02',segment=cue['segment'],contract=dict(width=1080,height=900,fps=60,frames=cue['totalFrames'],audio=False,alpha=False),variables=dict(segment=cue['segment'],timingMode='authored-cue-frames',segmentFrames=cue['totalFrames'],phaseFrameMap=cue['phaseFrameMap']),cueFrames=cue['cues'],actualCaptionBinding=dict(startFrame=cue['segmentStartGlobalFrame'],endFrameExclusive=cue['segmentEndGlobalFrameExclusive'],source='Verified current103physical/96logical raw blind-ASR exact phrase end word/sample anchors'),inputPins=pins,versions=dict(core=versions['core'],two=versions['2d'],ui=None,vitePlugin=read(motion/'@motion-canvas/vite-plugin/package.json')['version']),humanListening=False,actualRendered=False)
 result['fingerprint']=digest(result);return result

def matching_owned_processes(attempt,ignore_pid=None):
 """Node can die leaving owned Chromium/FFmpeg; preserve ownership until gone."""
 needle=str(Path(attempt).resolve()).replace('\\','/').lower();found=[]
 for p in psutil.process_iter(['pid','name','cmdline']):
  if p.pid==ignore_pid:continue
  if (p.info['name']or'').lower()not in ('node.exe','node','chrome.exe','chromium.exe','ffmpeg.exe','ffmpeg'):continue
  try:
   args=' '.join(p.info['cmdline'] or []).replace('\\','/').lower()
   if needle in args:found.append(runtime.identity(p.pid))
  except psutil.NoSuchProcess:continue
  except psutil.AccessDenied:found.append(dict(pid=p.pid,unknown=True))
 return found

def recover_own(known):
 lease=runtime.LEASE
 if not lease.exists():return
 rec=read(lease)
 if not runtime.ours(rec) or rec['token'] not in known:return
 if runtime.alive(rec) or runtime.alive(rec.get('child')):return
 attempt=rec.get('output')
 if not attempt or not Path(attempt).resolve().is_relative_to(ATTEMPTS.resolve()) or matching_owned_processes(attempt):return
 runtime.archive(lease,rec['token'])

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--cue-plan');parser.add_argument('--execute',action='store_true');args=parser.parse_args();prov=prepare(args.cue_plan)
 if not args.execute:print(json.dumps(prov,ensure_ascii=False));return
 if not prov['ready']:raise ValueError(prov['requires'])
 worker=runtime.SingleWorker(WORKER).acquire();owned=None;child=None;attempt=None;known=set()
 try:
  previous=worker.previous or {};known=set(previous.get('recoverableLeaseTokens',[]))
  if previous.get('leaseToken'):known.add(previous['leaseToken'])
  worker.update(recoverableLeaseTokens=sorted(known));recover_own(known)
  reason=native.busy_reason()
  if reason:
   save(STATE,dict(protocol=PROTOCOL,owner=OWNER,**runtime.identity(),status='resource-declined-before-render',reason=reason,child=None,rendererStarted=False,completed=False));print(reason);return 75
  # No implicit wait loop or queue. A new explicit invocation can retry safely.
  if shutil.disk_usage(TOPIC).free<3*1024**3:raise ValueError('C requires3GiB reserve; preserve older media')
  ATTEMPTS.mkdir(parents=True,exist_ok=True);attempt=ATTEMPTS/(time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:10]);attempt.mkdir()
  token=uuid.uuid4().hex;rec=dict(protocol=PROTOCOL,owner=OWNER,token=token,**runtime.identity(),child=None,phase='reserved',output=str(attempt),fingerprint=prov['fingerprint'])
  try:
   with runtime.LEASE.open('x',encoding='utf-8') as f:json.dump(rec,f)
  except FileExistsError:print('Another scoped job acquired lease; nothing launched');return 75
  owned=token;known.add(owned);worker.update(leaseToken=owned,attempt=str(attempt),recoverableLeaseTokens=sorted(known))
  if native.busy_reason(owned):raise RuntimeError('Resources changed after reservation; nothing launched')
  assert prepare(args.cue_plan)['fingerprint']==prov['fingerprint'],'Selected inputs changed before render'
  job=dict(prov,lifecycle=dict(leasePath=str(runtime.LEASE),protocol=PROTOCOL,owner=OWNER,token=owned,parent=runtime.identity()),schemaVersion='06-02-mc-render-job-v2',attempt=str(attempt),output=str(attempt/f'{prov["segment"]}.silent.mp4'),stagedSources=[dict(path=str(SOURCE/n),name=n) for n in ['project.ts','refuge-relationships.tsx']],font=dict(path='C:/Windows/Fonts/NotoSansKR-VF.ttf'),ffmpeg=shutil.which('ffmpeg'),ffprobe=shutil.which('ffprobe'))
  save(attempt/'job.json',job)
  command=[shutil.which('node'),str(NODE_SOURCE),str(attempt/'job.json'),sha(attempt/'job.json')];save(attempt/'launch.json',dict(command=command,nodeSourceSHA256=sha(NODE_SOURCE),scope='Only one06.02 P04/P25 silent MC crop; no next stage'))
  rec['phase']='launching';save(runtime.LEASE,rec)
  with (attempt/'stdout.log').open('wb') as out,(attempt/'stderr.log').open('wb') as err:
   child=subprocess.Popen(command,stdout=out,stderr=err,creationflags=CREATE);cid=runtime.identity(child.pid);worker.update(child=cid)
   rec.update(child=cid,phase='running');save(runtime.LEASE,rec);save(STATE,dict(protocol=PROTOCOL,owner=OWNER,**runtime.identity(),child=cid,status='rendering-one-silent-crop',output=str(attempt),leaseToken=owned,rendererStarted=True,completed=False,fingerprint=prov['fingerprint']))
   code=child.wait()
  if code:raise RuntimeError('Owned MC child failed; preserve attempt and exact logs')
  result=read(attempt/'render-manifest.json')
  assert result.get('complete') and result['fingerprint']==prov['fingerprint'] and sha(result['output']['path'])==result['output']['sha256'],'Completed crop proof differs'
  assert prepare(args.cue_plan)['fingerprint']==prov['fingerprint'],'Selected inputs changed during render'
  save(STATE,dict(protocol=PROTOCOL,owner=OWNER,**runtime.identity(),child=None,status='silent-crop-complete-visual-review-pending',output=str(attempt),completed=True,rendererStarted=True,fingerprint=prov['fingerprint'],manifestSHA256=sha(attempt/'render-manifest.json'),actualVisualReview=False,humanApproval=False,finalMovieComplete=False))
 except BaseException as error:
  save(STATE,dict(protocol=PROTOCOL,owner=OWNER,**runtime.identity(),status='render-failed-attempt-preserved',child=runtime.identity(child.pid)if child and child.poll()is None else None,output=str(attempt)if attempt else None,error=str(error),completed=False,rendererStarted=bool(child),recoverableLeaseTokens=sorted(known)))
  raise
 finally:
  live=bool(child and child.poll()is None) or bool(attempt and matching_owned_processes(attempt,os.getpid()))
  if owned and not live and runtime.LEASE.exists():
   rec=read(runtime.LEASE)
   if runtime.ours(rec) and rec['token']==owned:runtime.LEASE.unlink()
  unresolved=False
  if runtime.LEASE.exists():
   rec=read(runtime.LEASE);unresolved=runtime.ours(rec)and rec.get('token')in known
  worker.close(remove=not live and not unresolved)

if __name__=='__main__':raise SystemExit(main())
