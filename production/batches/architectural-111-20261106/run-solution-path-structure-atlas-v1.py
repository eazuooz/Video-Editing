"""11.05 finite source PNG atlas. Inert import/read-only default; --execute only.

No model, voice clock, editor UI, FFmpeg, user profile, automatic queue or next
topic. A fresh current caption/mix-backed source job is required before a lease.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,math,os,shutil,subprocess,sys,time,uuid
from pathlib import Path
import psutil
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106/shorts-leveldesign-11-05')
ATTEMPTS=MEDIA/'structure-attempts-v2';WORKER=MEDIA.parent/'11-05-structure-atlas-worker-v1.json';STATE=MEDIA.parent/'11-05-structure-atlas-progress-v1.json'
PROTOCOL='architectural111-11-05-structure-atlas-v1';OWNER='architectural-111-11-05-structure-atlas'
SDK=HERE/'render-solution-path-structure-atlas-v1.cjs'
PINS={'build-solution-path-film-timeline-v2.py':'013eacc0b8e5ebf36cfd410775d33a3a6b74213bb33ea045597922391f6d9c1e',
 'run-solution-path-native-v4.py':'9429b70773f3a334dd5fd45d76ecb6b2fa8b2360dfe576aac341099d7adaea5e',
 'run-first-native.py':'a38205dac134e58da35a772290f0a151c7377b115b89910585277de76983a1f9',
 'prospect-refuge-resource-qualification.py':'2dbb128a891fabf9c440e5790b88481c7901fbf087098557c540b19b8ecd5f5d'}
SDK_SHA='9df6c8a97be04032a5674a406e2ebc55d3e8fb1d4d5ee62b32e16928342c66dc'
SOURCE_NAMES=('project-structure-atlas-v2.ts','solution-path-structure-atlas-v2.tsx','solution-path-structure.tsx')
CREATE=getattr(subprocess,'CREATE_NO_WINDOW',0)
SELF_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
LAST_RESOURCE_CHECK=None
class Pending(ValueError):pass
def need(value,reason):
 if not value:raise Pending(reason)
def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path):
 with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def pin(path):return dict(path=str(Path(path).resolve()),sha256=sha(path))
def load(name,path):
 spec=importlib.util.spec_from_file_location(name+'_'+uuid.uuid4().hex,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
def checked_sources():
 need(sha(__file__)==SELF_SHA,'Imported coordinator source changed')
 for name,expected in PINS.items():need(sha(HERE/name)==expected,'Reviewed source changed: '+name)
 need(sha(SDK)==SDK_SHA,'Reviewed SDK worker changed')
def prepare(source_job=None,caption_timing=None,audio_build=None):
 checked_sources()
 if not(source_job and caption_timing and audio_build):return dict(ready=False,topicId='11.05',reason='Pending actual current caption6, accepted mix5 and immutable finite structural job',rendererStarted=False,jobLaunched=False)
 b=load('solution_atlas_builder',HERE/'build-solution-path-film-timeline-v2.py');b.authority()
 path=Path(source_job).resolve();need(path.is_relative_to(MEDIA/'structure-jobs-v2'),'Source job escaped current ownedV2 scope')
 recipe=read(path);current=b.prepare(caption_timing,audio_build)
 need(current.get('picturePlanReady') is True,current.get('reason','Current actual picture proof missing'))
 fresh=b.structure_job(current['picturePlan'])
 need(recipe==fresh and path==Path(fresh['outputContract']['jobPath']).resolve(),'Finite job differs from fresh current graph/sample clock')
 motion=ROOT/'motion-canvas';node=shutil.which('node');need(node,'Installed Node required; no downloads')
 deps=['@motion-canvas/core/package.json','@motion-canvas/2d/package.json','@motion-canvas/core/lib/app/Renderer.js','@motion-canvas/core/lib/app/Stage.js','@motion-canvas/core/lib/app/bootstrap.js','@motion-canvas/vite-plugin/lib/partials/webgl.js','vite/dist/node/index.js','puppeteer/package.json']
 versions={k:read(motion/'node_modules'/('@motion-canvas/'+k)/'package.json')['version'] for k in ('core','2d')}
 paths=[Path(__file__),SDK,path]+[HERE/n for n in PINS]+[motion/'node_modules'/n for n in deps]
 inputs=current['picturePlan']['inputs']+recipe['inputs']+[pin(p) for p in paths]
 inputs=list({(str(Path(v['path']).resolve()),v['sha256']):v for v in inputs}.values())
 for row in inputs:need(sha(row['path'])==row['sha256'],'Current source pin changed')
 result=dict(ready=True,topicId='11.05',sourceJob=pin(path),recipe=recipe,
  pictureClockInputs=dict(captionTiming=pin(caption_timing),audioBuild=pin(audio_build)),
  contract=dict(width=1080,height=900,fps=60,frames=recipe['assetFrames'],audio=False,alpha=True),
  variables=dict(renderMode='source-pinned-structural-atlas-v2',jobFingerprint=recipe['fingerprint'],sourcePackets=recipe['packets']),
  stagedSources=[dict(path=str(b.MC_SOURCE/name),name=name) for name in SOURCE_NAMES],
  font=next(row for row in recipe['inputs'] if Path(row['path']).name=='NotoSansKR-VF.ttf'),
  versions=dict(core=versions['core'],two=versions['2d'],ui=None,vitePlugin=read(motion/'node_modules/@motion-canvas/vite-plugin/package.json')['version']),
  tools=dict(node=pin(node)),inputPins=inputs,producer=dict(coordinator=pin(__file__),sdkWorker=pin(SDK),builder=pin(HERE/'build-solution-path-film-timeline-v2.py')),
  actualSpeechTimingVerified=False,nativePixelVisibilityClaim=False,humanApproval=False)
 result['fingerprint']=digest(result);checked_sources();return result
def identity(pid=None):
 p=psutil.Process(os.getpid() if pid is None else pid);argv=p.cmdline()
 return dict(pid=p.pid,createTime=p.create_time(),ppid=p.ppid(),exe=p.exe(),argv=argv,commandSHA256=digest(argv))
def save(path,value):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
 with temp.open('x',encoding='utf8') as stream:json.dump(value,stream,ensure_ascii=False,indent=2)
 os.replace(temp,path)
def matching_owned(attempt,known=(),ignore_pid=None):
 """Read-only uncertainty keeps the lease; it never grants termination rights."""
 result=[row for row in known if alive(row)];needle=str(Path(attempt).resolve()).replace('\\','/').lower()
 for p in psutil.process_iter(['pid','name','cmdline']):
  if p.pid==ignore_pid:continue
  try:
   name=(p.info.get('name')or'').lower();args=p.info.get('cmdline')
   if name not in ('node.exe','node','chrome.exe','chromium.exe','chrome','chromium','esbuild.exe','esbuild'):continue
   if args is None:result.append(dict(pid=p.pid,unknown=True));continue
   if needle in ' '.join(args).replace('\\','/').lower():result.append(identity(p.pid))
  except psutil.NoSuchProcess:continue
  except psutil.AccessDenied:result.append(dict(pid=p.pid,unknown=True))
 return result
def alive(record):
 if not record:return False
 try:
  p=psutil.Process(record['pid'])
  if record.get('unknown')or'createTime'not in record:return True
  # Changed/unreadable argv never proves a same-birth process dead.
  return abs(p.create_time()-record['createTime'])<.001
 except psutil.NoSuchProcess:return False
 except(psutil.AccessDenied,KeyError,TypeError):return True
def libraries():
 checked_sources();native=load('solution_atlas_private_resource',HERE/'run-solution-path-native-v4.py');rt=native.rt
 rt.PROTOCOL,rt.OWNER=PROTOCOL,OWNER;rt.identity=identity;return native,rt
def resource_reason(native,token=None):
 global LAST_RESOURCE_CHECK
 reason=native.busy_reason(token)
 LAST_RESOURCE_CHECK=dict(time=time.time(),nativeReason=reason,classifier=getattr(native,'LAST_RESOURCE_CLASSIFICATION',None),
  policy=dict(minimumFreeMiB=8192,maximumUtilizationExclusive=15),ownershipGranted=False,terminationGranted=False)
 if reason:return reason
 # Stricter local SDK rule; the original native8GiB guard/classifier is intact.
 raw=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True,creationflags=CREATE)
 free,use=map(int,raw.splitlines()[0].split(','))
 LAST_RESOURCE_CHECK.update(freeMiB=free,utilizationPercent=use)
 return f'SDK headroom insufficient ({free}MiB,{use}%; requires8GiB and <15%)' if free<8192 or use>=15 else None
def recover_own(rt,known):
 if not rt.LEASE.exists():return
 rec=read(rt.LEASE)
 if not(rt.ours(rec) and rec.get('token')in known)or alive(rec)or alive(rec.get('child')):return
 attempt=rec.get('output')
 if not attempt or not Path(attempt).resolve().is_relative_to(ATTEMPTS)or matching_owned(attempt,rec.get('children',[]),os.getpid()):return
 rt.archive(rt.LEASE,rec['token'])
def update_lease(rt,rec):
 current=read(rt.LEASE);need(rt.ours(current)and current.get('token')==rec['token'],'Preserve changed/foreign lease')
 save(rt.LEASE,rec)
def validate_manifest(path,prov):
 m=read(path);need(Path(path).resolve().is_relative_to(ATTEMPTS),'Manifest outside owned atlas attempts')
 need(m.get('complete') is True and m.get('schemaVersion')=='11.05-structure-atlas-manifest-v2'
  and m.get('job')==prov['sourceJob'] and m.get('jobFingerprint')==prov['recipe']['fingerprint']
  and m.get('picturePlanFingerprint')==prov['recipe']['picturePlanFingerprint'] and m.get('producer')==prov['producer']
  and m.get('inputPins')==prov['inputPins'] and m.get('aliases')==prov['recipe']['aliases']
  and m.get('canvas')==[1080,900] and m.get('assetFrames')==len(prov['recipe']['packets']), 'Current exact atlas provenance incomplete')
 execution=Path(m['executionJob']['path']).resolve()
 need(execution==Path(path).resolve().parent/'execution-job.json'and sha(execution)==m['executionJob']['sha256'],'Actual execution job changed')
 stored=read(execution)
 need(all(stored.get(k)==v for k,v in prov.items())and stored.get('schemaVersion')=='11.05-structure-atlas-execution-job-v1'
  and stored.get('attempt')==str(Path(path).resolve().parent),'Execution recipe/provenance differs')
 life=stored['lifecycle'];parent=life['parent']
 need(life['protocol']==PROTOCOL and life['owner']==OWNER and isinstance(life['token'],str)and bool(life['token'])
  and Path(life['leasePath']).resolve()==(ROOT/'shared/output/GPU_HANDOFF.json').resolve()
  and type(parent['pid'])is int and parent['pid']>0 and type(parent['createTime'])in(int,float)
  and math.isfinite(parent['createTime'])and parent['createTime']>0 and isinstance(parent['argv'],list)
  and all(isinstance(x,str)for x in parent['argv'])and digest(parent['argv'])==parent['commandSHA256'],
  'Actual source coordinator PID/birth/argv/lease provenance missing')
 settings=m['actualSdk']['settings']
 need(m['actualSdk']['result']==0 and settings['fps']==60 and settings['size']==dict(x=1080,y=900)
  and settings['background']is None and settings['range']==[0,max(0,(m['assetFrames']-1.25)/60)],'Actual SDK settings/count/alpha differ')
 need([r['name'] for r in m['stagedSources']]==list(SOURCE_NAMES),'Actually rendered source snapshots missing')
 for row in m['stagedSources']:
  original=next(r for r in prov['stagedSources']if r['name']==row['name']);snapshot=Path(row['path']).resolve()
  expected=next(r['sha256']for r in prov['inputPins']if Path(r['path']).resolve()==Path(original['path']).resolve())
  need(snapshot==Path(path).resolve().parent/'staged'/row['name']and row['sha256']==expected and sha(snapshot)==expected,'Rendered staged source differs')
 font=Path(m['stagedFont']['path']).resolve()
 need(font==Path(path).resolve().parent/'staged/NotoSansKR-VF.ttf'and m['stagedFont']['sha256']==prov['font']['sha256']
  and sha(font)==prov['font']['sha256'],'Actually rendered font differs')
 need(len(m['frames'])==m['assetFrames'],'Actual asset frame count differs')
 seen=set()
 for i,(row,packet)in enumerate(zip(m['frames'],prov['recipe']['packets'])):
  image=Path(row['image']['path']).resolve()
  need(row['atlasIndex']==i and row['packetFingerprint']==packet['fingerprint'] and row['mode']==packet['mode']and row['nativeFrame']==packet['nativeFrame']
   and image==Path(path).resolve().parent/f'atlas-{i:06}.png' and image not in seen and sha(image)==row['image']['sha256'],'Actual atlas image/source binding differs')
  seen.add(image)
  with image.open('rb')as stream:header=stream.read(26)
  need(len(header)==26 and header[:8]==b'\x89PNG\r\n\x1a\n'and int.from_bytes(header[16:20],'big')==1080
   and int.from_bytes(header[20:24],'big')==900 and header[25]==6,'Actual RGBA PNG dimensions differ')
 for flag in ('actualVisualReview','actual375Reviewed','actualSpeechTimingVerified','nativePixelVisibilityClaim','humanApproval'):need(m.get(flag)is False,'Producer cannot approve final visuals/speech')
 return m
def execute(source_job,caption_timing,audio_build):
 prov=prepare(source_job,caption_timing,audio_build);need(prov.get('ready'),prov.get('reason','Pending actual finite job'))
 native,rt=libraries();worker=rt.SingleWorker(WORKER,is_alive=alive).acquire();token=None;rec=None;child=None;attempt=None;known=set()
 try:
  previous=worker.previous or{};known=set(previous.get('recoverableLeaseTokens',[]))
  if previous.get('leaseToken'):known.add(previous['leaseToken'])
  worker.update(recoverableLeaseTokens=sorted(known));recover_own(rt,known)
  reason=resource_reason(native)
  if reason:return dict(ready=False,status='resource-declined-no-process',reason=reason,exitCode=75,rendererStarted=False)
  need(shutil.disk_usage(MEDIA).free>=4*1024**3,'Preserve originals and4GiB C reserve')
  attempt=ATTEMPTS/(time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:10]);attempt.mkdir(parents=True,exist_ok=False)
  rec=dict(protocol=PROTOCOL,owner=OWNER,topicId='11.05',token=uuid.uuid4().hex,**identity(),child=None,children=[],phase='reserved',output=str(attempt),fingerprint=prov['fingerprint'])
  try:
   with rt.LEASE.open('x',encoding='utf8')as stream:json.dump(rec,stream)
  except FileExistsError:return dict(ready=False,status='foreign-lease-race-no-process',exitCode=75,rendererStarted=False)
  token=rec['token'];known.add(token);worker.update(leaseToken=token,recoverableLeaseTokens=sorted(known),attempt=str(attempt))
  before=LAST_RESOURCE_CHECK
  need(resource_reason(native,token)is None,'Resources changed after lease reservation; no renderer launched')
  save(attempt/'resource-readiness.json',dict(beforeReservation=before,afterReservation=LAST_RESOURCE_CHECK,newQueue=False))
  need(prepare(source_job,caption_timing,audio_build)==prov,'Actual source changed before launch')
  job=dict(prov,schemaVersion='11.05-structure-atlas-execution-job-v1',attempt=str(attempt),lifecycle=dict(leasePath=str(rt.LEASE),protocol=PROTOCOL,owner=OWNER,token=token,parent=identity()))
  job_path=attempt/'execution-job.json';save(job_path,job)
  command=[prov['tools']['node']['path'],str(SDK),str(job_path),sha(job_path)]
  save(attempt/'launch.json',dict(command=command,commandSHA256=digest(command),producer=prov['producer'],newQueue=False))
  rec.update(phase='launching',pendingCommand=command,pendingAfter=time.time());update_lease(rt,rec)
  worker.update(pendingCommand=command,pendingAfter=rec['pendingAfter'])
  with(attempt/'stdout.log').open('xb')as out,(attempt/'stderr.log').open('xb')as err:
   child=subprocess.Popen(command,stdout=out,stderr=err,creationflags=CREATE);rec.update(child=identity(child.pid),phase='running',pendingCommand=None);update_lease(rt,rec);worker.update(child=rec['child'],pendingCommand=None)
   save(STATE,dict(rec,status='owned-finite-png-atlas',complete=False,rendererStarted=True,finalMovieComplete=False))
   while child.poll()is None:
    try:descendants=psutil.Process(child.pid).children(recursive=True)
    except psutil.NoSuchProcess:descendants=[]
    rows=[]
    for process in descendants:
     try:rows.append(identity(process.pid))
     except psutil.NoSuchProcess:pass
     except psutil.AccessDenied:rows.append(dict(pid=process.pid,unknown=True))
    rec['children']=list({(r['pid'],r.get('createTime')):r for r in rec['children']+rows}.values());update_lease(rt,rec);worker.update(children=rec['children']);time.sleep(.2)
  need(child.returncode==0,'Actual owned SDK child failed; preserve partials/logs')
  need(prepare(source_job,caption_timing,audio_build)==prov,'Actual source changed during render')
  manifest=validate_manifest(attempt/'render-manifest.json',prov)
  save(STATE,dict(rec,status='finite-atlas-complete-visual-review-pending',complete=True,manifest=pin(attempt/'render-manifest.json'),actualVisualReview=False,humanApproval=False,finalMovieComplete=False))
  return dict(ready=True,manifest=pin(attempt/'render-manifest.json'),assetFrames=manifest['assetFrames'],actualVisualReview=False,finalMovieComplete=False)
 except BaseException as error:
  if token and rec:save(STATE,dict(rec,status='failed-preserved',complete=False,error=str(error),rendererStarted=bool(child),finalMovieComplete=False))
  raise
 finally:
  live=bool(child and child.poll()is None)or bool(attempt and matching_owned(attempt,rec.get('children',[])if rec else[],os.getpid()))
  if token and not live and rt.LEASE.exists():
   current=read(rt.LEASE)
   if rt.ours(current)and current.get('token')==token:rt.LEASE.unlink()
  unresolved=rt.LEASE.exists()and rt.ours(read(rt.LEASE))and read(rt.LEASE).get('token')in known
  worker.close(remove=not live and not unresolved)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-job');p.add_argument('--caption-timing');p.add_argument('--audio-build');p.add_argument('--execute',action='store_true');a=p.parse_args()
 if a.execute:result=execute(a.source_job,a.caption_timing,a.audio_build)
 else:
  try:result=prepare(a.source_job,a.caption_timing,a.audio_build)
  except(Pending,OSError,KeyError)as error:result=dict(ready=False,reason=str(error),rendererStarted=False,jobLaunched=False)
 print(json.dumps(result,ensure_ascii=False,indent=2));return result.get('exitCode',0)
if __name__=='__main__':raise SystemExit(main())
