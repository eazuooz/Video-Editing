"""Exact07.04 SDK crop: read-only readiness by default; one finite owned job.

No browser/model/media process is started without --execute and real ASR-bound
authored cues. Failed/older attempts, foreign jobs, user apps and leases persist.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,math,os,shutil,subprocess,time,uuid
from pathlib import Path
import psutil
from initialize import ROOT,HERE,MEDIA,AUTH_KEY,read,save

spec=importlib.util.spec_from_file_location('zen_diagram_native_resource',HERE/'run-zen-view-native.py')
native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
PROTOCOL='architectural111-07-04-mc-crop-v1';OWNER='architectural-111-07-04-mc-crop'
native.runtime.PROTOCOL=PROTOCOL;native.runtime.OWNER=OWNER
runtime=native.runtime
PROJECT=ROOT/'projects/shorts-leveldesign-07-04'
TOPIC=MEDIA/'shorts-leveldesign-07-04'
ATTEMPTS=TOPIC/'mc-render-attempts';WORKER=MEDIA/'07-04-mc-worker.json';STATE=MEDIA/'07-04-mc-progress.json'
SOURCE=ROOT/'motion-canvas/src/projects/shorts-leveldesign-07-04'
NODE_SOURCE=HERE/'render-zen-view-diagrams.cjs'
CREATE=getattr(subprocess,'CREATE_NO_WINDOW',0)

def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def digest(j):return hashlib.sha256(json.dumps(j,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def pinned(row):
 p=Path(row['path']).resolve()
 if not p.is_file() or len(row.get('sha256',''))!=64 or sha(p)!=row['sha256']:raise ValueError('Pinned input changed: '+str(p))
 return dict(path=str(p),sha256=row['sha256'])

def cue_map(cues,total,expected):
 if type(total)is not int or total<6:raise ValueError('Finite positive actual segment frame count required')
 if not isinstance(cues,list) or [c.get('id') for c in cues]!=[c['id'] for c in expected]:raise ValueError('Exact ordered authored cue IDs required')
 points={0:0.0,total-1:1.0};last=-1
 for item,source in zip(cues,expected):
  f=item.get('frame')
  if type(f)is not int or not 0<=f<total or f<=last:raise ValueError('Authored cue frames must increase within segment')
  points[f]=source['draftNormalizedAt'];last=f
 result=[dict(frame=f,phase=v) for f,v in sorted(points.items())]
 if any(a['phase']>=b['phase'] for a,b in zip(result,result[1:])):raise ValueError('Authored semantic phase order changed')
 return result

def actual_segment(cue,timing,expected):
 """Only current word-derived bounds may become local animation frames."""
 paragraph=int(cue['segment'][1:]);rows=[p for p in timing['paragraphs']if p['paragraph']==paragraph]
 if len(rows)!=1:raise ValueError('Actual paragraph bounds missing')
 actual=[next((c for c in timing['diagramCues']if c['id']==e['id']),None)for e in expected]
 if any(c is None or c['paragraph']!=paragraph for c in actual):raise ValueError('Actual diagram word cues missing')
 start=actual[0]['startFrame']if paragraph==6 else rows[0]['startFrame']
 end=rows[0]['endFrameExclusive']
 if cue.get('segmentStartGlobalFrame')!=start or cue.get('segmentEndGlobalFrameExclusive')!=end or cue['totalFrames']!=end-start:raise ValueError('Segment must use exact actual paragraph/diagram-entry bounds')
 derived=[dict(id=c['id'],frame=c['startFrame']-start)for c in actual]
 if cue['cues']!=derived:raise ValueError('Authored animation frame differs from actual blind-ASR word boundary')
 return dict(startFrame=start,endFrameExclusive=end,localCueFrames=derived,source='Verified current blind-ASR caption builder; P6 begins at first treasure-room diagram cue')

def prepare(cue_path=None):
 auth=read(ROOT/'shared/publishing/video-production-control.json')[AUTH_KEY]
 if auth['status'] in ('paused','stopped','cancelled') or not auth['automaticAdvanceWithinExactList'] or auth['automaticAdvanceOutsideList']:raise ValueError('Exact111 authorization inactive')
 batch=read(HERE/'batch.json')
 if len(batch['projects'])!=111 or not batch['localFinalReviewOnly'] or not any(x['topicId']=='07.04' for x in batch['projects']):raise ValueError('Selected topic outside exact111')
 plan_path=PROJECT/'2d-scene-plan-v1.json';plan=read(plan_path)
 if plan['topicId']!='07.04':raise ValueError('Wrong diagram scene plan')
 pins=[pinned(x) for x in plan['sourceFiles']]+[pinned(plan['narrationInput'])]
 pins.append(dict(path=str(plan_path),sha256=sha(plan_path)))
 if cue_path is None:return dict(ready=False,topicId='07.04',requires='Actual current voice + blind-ASR authored cue-plan, one selected segment',rendererStarted=False,frameTimingFabricated=False)
 cue_path=Path(cue_path).resolve();cue=read(cue_path)
 if cue.get('schemaVersion')!='07-04-authored-diagram-cues-v1' or cue.get('topicId')!='07.04' or cue.get('segment') not in ('p2','p6','p7'):raise ValueError('Wrong scoped authored cue plan')
 if cue.get('timingStatus')!='actual-asr-clause-aligned':raise ValueError('Draft logical durations cannot launch rendering')
 if pinned(cue['scenePlan'])['sha256']!=sha(plan_path) or Path(cue['scenePlan']['path']).resolve()!=plan_path.resolve():raise ValueError('Cue plan scene source changed')
 if pinned(cue['narration'])!=pinned(plan['narrationInput']):raise ValueError('Cue narration differs from current selected prose')
 voice_pin=pinned(cue['voiceEvidence']);voice=read(voice_pin['path']);wav=pinned(cue['voiceWav'])
 if voice.get('topicId')!='07.04' or voice.get('aggregateWav',{}).get('sha256')!=wav['sha256'] or Path(voice['aggregateWav']['path']).resolve()!=Path(wav['path']):raise ValueError('Cue audio is not exact selected canonical voice')
 alignment=cue['alignment']
 if alignment.get('kind')!='actual-blind-asr-word-timestamps' or alignment.get('voiceFingerprint')!=voice['fingerprint'] or alignment.get('voicePcmSHA256')!=voice['aggregateWav']['pcmSHA256'] or alignment.get('narrationSHA256')!=plan['narrationInput']['sha256']:raise ValueError('Actual ASR voice/prose binding missing')
 asr=pinned(alignment['review']);builder_path=HERE/'build-selected-caption-timing.py'
 alignment_sources=plan['renderSupport'].get('alignmentSourcePins',[])
 required_sources={builder_path.resolve(),(HERE/'run-selected-voice-qa.py').resolve(),(PROJECT/'caption-clauses-v1.json').resolve()}
 if not required_sources.issubset({Path(r['path']).resolve()for r in alignment_sources}):raise ValueError('Pinned current caption builder/clauses/raw-ASR source required')
 pins.extend(pinned(row)for row in alignment_sources)
 bsp=importlib.util.spec_from_file_location('zen_crop_verified_caption_builder',builder_path)
 builder=importlib.util.module_from_spec(bsp);bsp.loader.exec_module(builder)
 # This verifies the current canonical take/join caches, selected14raw takes,
 # aggregate PCM, exact paragraph prose and the immutable summary; no ASR/model.
 review=builder.verified_asr_review(asr['path'])
 draft=read(PROJECT/'narration-draft.json');binding=builder.voice_binding(voice,review,draft)
 clauses_path=PROJECT/'caption-clauses-v1.json';clauses=read(clauses_path)
 fresh=builder.build(draft,clauses,review,plan)
 timing_pin=pinned(cue['captionTiming']);timing=read(timing_pin['path'])
 if not Path(timing_pin['path']).is_relative_to((TOPIC/'caption-timing').resolve()):raise ValueError('Use selected canonical caption-timing output')
 if any(timing.get(k)!=v for k,v in fresh.items())or timing.get('voiceBinding')!=binding:raise ValueError('Caption timing differs from current verified raw-ASR words')
 if not timing.get('inputs')or timing.get('fingerprint')!=builder.digest(timing['inputs'])or Path(timing_pin['path']).parent.name!=timing['fingerprint'][:24]:raise ValueError('Canonical caption timing provenance differs')
 timing_inputs=[pinned(row)for row in timing['inputs']]
 required={str(x.resolve())for x in [builder_path,clauses_path,PROJECT/'narration-draft.json',PROJECT/'2d-scene-plan-v1.json',Path(asr['path']),Path(voice_pin['path'])]}
 if not required.issubset({str(Path(x['path']).resolve())for x in timing_inputs}):raise ValueError('Canonical timing lacks required current source/ASR provenance')
 # No automatic listening or pronunciation pass is inferred by time alignment.
 pins.extend([voice_pin,wav,asr,pinned(voice['timing']),timing_pin,dict(path=str(cue_path),sha256=sha(cue_path)),dict(path=str(builder_path),sha256=sha(builder_path)),dict(path=str(clauses_path),sha256=sha(clauses_path))]+timing_inputs)
 segment=cue['segment'];expected=[x for x in plan['cueKeyframes'] if x['paragraph']==int(segment[1:])]
 actual_bounds=actual_segment(cue,fresh,expected)
 phase=cue_map(cue['cues'],cue['totalFrames'],expected)
 duration=voice['aggregateWav']['frames']/voice['aggregateWav']['sampleRate']
 if cue['totalFrames']>math.ceil(duration*60)+1:raise ValueError('Diagram segment exceeds exact voice duration')
 motion=ROOT/'motion-canvas/node_modules';versions={k:read(motion/f'@motion-canvas/{k}/package.json')['version'] for k in ('core','2d')}
 sdk_files=['@motion-canvas/core/lib/app/Renderer.js','@motion-canvas/core/lib/app/Stage.js','@motion-canvas/core/lib/app/bootstrap.js','@motion-canvas/vite-plugin/lib/partials/scenes.js','@motion-canvas/vite-plugin/lib/partials/meta.js','@motion-canvas/vite-plugin/lib/partials/webgl.js','vite/dist/node/index.js','puppeteer/package.json']
 for p in [Path(__file__),NODE_SOURCE,HERE/'run-first-native.py',HERE/'run-zen-view-native.py',Path('C:/Windows/Fonts/NotoSansKR-VF.ttf')]+[motion/f for f in sdk_files]:pins.append(dict(path=str(p.resolve()),sha256=sha(p)))
 for tool in ('node','ffmpeg','ffprobe'):
  if not shutil.which(tool):raise ValueError('Installed tool missing: '+tool)
 result=dict(ready=True,topicId='07.04',segment=segment,contract=dict(width=1080,height=900,fps=60,frames=cue['totalFrames'],audio=False,alpha=False),variables=dict(segment=segment,timingMode='authored-cue-frames',segmentFrames=cue['totalFrames'],phaseFrameMap=phase),cueFrames=cue['cues'],actualCaptionBinding=actual_bounds,inputPins=pins,versions=dict(core=versions['core'],two=versions['2d'],ui=None,vitePlugin=read(motion/'@motion-canvas/vite-plugin/package.json')['version']),humanListening=False,actualRendered=False)
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
  job=dict(prov,schemaVersion='07-04-mc-render-job-v1',attempt=str(attempt),output=str(attempt/f'{prov["segment"]}.silent.mp4'),stagedSources=[dict(path=str(SOURCE/n),name=n) for n in ['project.ts','reward-diagrams.tsx']],font=dict(path='C:/Windows/Fonts/NotoSansKR-VF.ttf'),ffmpeg=shutil.which('ffmpeg'),ffprobe=shutil.which('ffprobe'))
  save(attempt/'job.json',job)
  command=[shutil.which('node'),str(NODE_SOURCE),str(attempt/'job.json'),sha(attempt/'job.json')];save(attempt/'launch.json',dict(command=command,nodeSourceSHA256=sha(NODE_SOURCE),scope='Only one07.04 silent MC crop'))
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
