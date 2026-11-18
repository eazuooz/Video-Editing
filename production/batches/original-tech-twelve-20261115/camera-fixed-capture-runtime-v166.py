"""One selected native fixed-shot capture; reuse the exact approved player world."""
from pathlib import Path
import argparse,datetime,importlib.util,json,os,shutil,subprocess,time,uuid
H=Path(__file__).resolve().parent;ROOT=H.parents[2];M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');SLUG='shorts-mario64-lakitu-camera';BASE=M/SLUG/'camera-paired-v164/native-v166'
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
stream=module('fixed166_existing_stream_verifier',H/'run-streamed-native-v2.py');n=stream.native
module('fixed166_cooperative_policy',H/'cooperative-resource-policy-v19.py').install(n)
read,sha,pin,save,digest=n.read,n.sha,n.pin,n.save,n.digest
def authority():
 n.authority();own=read(ROOT/'shared/publishing/video-production-control.json')['explicitOriginalTechTwelve20261115'];assert own['currentSelectedProject']==SLUG and own['activeRevisionScope']==[SLUG];return own
def prepare():
 authority();oldp=M/SLUG/'native-stream-v2/source-preparation.json';old=read(oldp);files=[]
 for row in old['files']:
  assert sha(row['source'])==row['sha256'];r=dict(row);r['target']=r['target'].replace('CameraV1','CameraV164')
  if Path(r['source']).name=='CameraCapture.cs':r.update(source=str(H/'camera-paired-source-v164/Editor/FixedShotCapture.cs'),sha256=sha(H/'camera-paired-source-v164/Editor/FixedShotCapture.cs'));r['target']=r['target'].replace('CameraCapture.cs','FixedShotCapture.cs')
  files.append(r)
 model=H/'camera-paired-source-v164/FixedShotModel.cs';files.append(dict(source=str(model),target='Assets/OriginalTechTwelve/CameraV164/FixedShotModel.cs',sha256=sha(model)))
 compiler=M/'camera-side-by-side-v164/cpu-compile-v165/compile-receipt.json';c=read(compiler);assert c['staticCompilationPassed']and c['modelFixtureExecuted']and c['sampledStates']==3600
 assert {str(Path(x['source']).resolve()):x['sha256']for x in files if Path(x['source']).suffix=='.cs'}=={x['path']:x['sha256']for x in c['sourceInputs']}
 codec=Path(old['codecFixture']['path']);assert pin(codec)==old['codecFixture']and read(codec)['allDecodedRgbBytesExact'];encoder=old['encoder'];assert pin(encoder['path'])==encoder
 playerp=M/SLUG/'native-stream-v2/accepted-full.json';player=read(playerp);assert player['actualUnityCapture']and player['allPixelsRoundTripVerified']and player['framesPerCamera']==720
 contract=dict(old['contract'],cameras=['fixed'],fullFrames=720,smokeFrames=32,worldModelAndAssetsUnchanged=True,pairedPlayerProof=pin(playerp),fixedZoneBoundary='authored heroX>=0; not original RE2 trigger data')
 adapters=[H/'camera-fixed-capture-runtime-v166.py',H/'run-camera-fixed-smoke-v166.py',H/'run-camera-fixed-full-v166.py'];identity=dict(files=files,generated=old['generated'],contract=contract,compiler=pin(compiler),codec=pin(codec),adapters=[pin(p)for p in adapters],executionResourcePolicy=n.cooperative_policy_proof,request=pin(H/'user-camera-paired-revision-v164.json'));fp=digest(identity)
 return dict(fingerprint=fp,files=files,generated=old['generated'],contract=contract,identity=identity,project=str(BASE/'projects'/fp[:16]),sceneRoot='Assets/OriginalTechTwelve/CameraV164',entry='Yamyam.OriginalTechTwelve.Camera.Editor.FixedShotCapture.Run',editor=old['editor'],encoder=encoder,sourceStageComplete=False)
def stage(prep):
 project=Path(prep['project']).resolve();assert project.is_relative_to((BASE/'projects').resolve())
 for r in prep['files']:
  src=Path(r['source']);dst=project/r['target'];assert sha(src)==r['sha256']and dst.resolve().is_relative_to(project);assert not dst.exists()or sha(dst)==r['sha256'];dst.parent.mkdir(parents=True,exist_ok=True)
  if not dst.exists():shutil.copy2(src,dst)
 for name,text in prep['generated'].items():
  p=project/name;assert p.resolve().is_relative_to(project)and(not p.exists()or p.read_bytes()==text.encode('utf8'));p.parent.mkdir(parents=True,exist_ok=True)
  if not p.exists():p.write_bytes(text.encode('utf8'))
 prep['sourceStageComplete']=True;save(BASE/'source-preparation.json',prep)
def busy(token=None):
 authority()
 if shutil.disk_usage(M).free<2*1073741824:return'Preserve2GiB media reserve'
 return n.busy(token)
def compare(proof,prep):
 old=read(prep['contract']['pairedPlayerProof']['path']);matches=[]
 for clip in proof['clips']:
  player=next(x for x in old['clips']if x['mode']==clip['mode']and x['camera']=='player');left=read(clip['trace']['path'])['frames'];right=read(player['trace']['path'])['frames'];cuts=[]
  for i,row in enumerate(left):
   assert row['frame']==right[i]['frame']==i
   assert row['model'].keys()==right[i]['model'].keys()
   for key,value in row['model'].items():
    if isinstance(value,bool):assert value==right[i]['model'][key]
    else:assert abs(value-right[i]['model'][key])<1e-5,(clip['mode'],i,key)
   if i:
    previous=left[i-1]['shot'];shot=row['shot']
    if previous['zone']==shot['zone']:assert previous==shot,'Fixed camera moved within its zone'
    else:cuts.append(i)
  if len(left)==720:assert len(cuts)==(1 if clip['mode']=='follow'else 0)
  matches.append(dict(mode=clip['mode'],comparedStates=len(left),sameActorAndRequestedCameraState=True,fixedShotCuts=cuts,actualNewFixedView=clip['video'],retainedActualPlayerView=player['video']))
 return dict(actualUnityTraceComparison=True,pairedPlayerProof=prep['contract']['pairedPlayerProof'],modes=matches,worldModelAndAssetsByteExact=True,notCommercialGameEngineCode=True)
def execute(prep,purpose,script,wait):
 assert wait==15;protocol='original-tech-twelve-camera-fixed-'+purpose+'-v166';owner='original-tech-twelve-camera-fixed';rt=n.runtime;rt.PROTOCOL=protocol;rt.OWNER=owner;n.guard.qualifier.BASE=BASE/'resource-observations';bootstrap=module('fixed166_bootstrap',H/'bootstrap-parent-identity-v1.py').install(n,script,SLUG,BASE,protocol,owner)
 worker=rt.SingleWorker(path=BASE/'worker.json');owned=None;child=None;deadline=time.monotonic()+wait*60;accepted=BASE/('accepted-'+purpose+'.json')
 try:
  worker.acquire();argv=n.guard.psutil.Process().cmdline();worker.update(project=SLUG,stage='targeted-source',argv=argv,commandSHA256=digest(argv),**bootstrap)
  assert not accepted.exists(),'Completed native capture is not repeated';assert not(BASE/('failure-'+purpose+'.json')).exists(),'Prior failed identity is preserved'
  if purpose=='full':
   review=read(BASE/'smoke-visual-review-v166.json');assert review['allowedForFullCapture']and review['smokeProof']==pin(BASE/'accepted-smoke.json')and review['fingerprint']==prep['fingerprint']
  last=''
  while True:
   reason=busy()
   if reason is None:
    token=worker.record['token'];lease=dict(protocol=protocol,owner=owner,token=token,**n.identity(),phase='reserved',fingerprint=prep['fingerprint'])
    try:
     with n.LEASE.open('x',encoding='utf8')as f:json.dump(lease,f)
    except FileExistsError:reason='Concurrent foreign lease preserved'
    else:
     owned=token;reason=busy(token)
     if reason is None:break
     if read(n.LEASE).get('token')==owned:n.LEASE.unlink()
     owned=None
   if reason!=last:print(json.dumps(dict(wait=reason,unityStarted=False)),flush=True);last=reason
   if time.monotonic()>=deadline:return dict(started=False,boundedWaitExpired=True,reason=reason)
   time.sleep(20)
  assert prepare()['fingerprint']==prep['fingerprint']and read(BASE/'source-preparation.json')['fingerprint']==prep['fingerprint']
  for r in prep['files']:assert sha(Path(prep['project'])/r['target'])==r['sha256']
  attempt=BASE/'attempts'/(purpose+'-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'));attempt.mkdir(parents=True,exist_ok=False);capture=attempt/'capture';job=attempt/'job.json';save(job,dict(output=str(capture),fingerprint=prep['fingerprint'],mode='full',frameLimit=32 if purpose=='smoke'else 720,ffmpeg=prep['encoder']['path']))
  args=[prep['editor']['path'],'-batchmode','-projectPath',prep['project'],'-executeMethod',prep['entry'],'-ot12Job',str(job),'-logFile',str(attempt/'unity.log')];save(attempt/'launch.json',dict(argv=args,sourcePreparation=pin(BASE/'source-preparation.json'),executionResourcePolicy=n.cooperative_policy_proof));child=subprocess.Popen(args,cwd=ROOT,creationflags=n.CREATE);ci=n.identity(child.pid);worker.update(child=ci);lease.update(phase='native-capture',child=ci);save(n.LEASE,lease);save(BASE/'current-run.json',dict(purpose=purpose,child=ci,attempt=str(attempt),fingerprint=prep['fingerprint']));print(json.dumps(dict(unityStarted=True,purpose=purpose,attempt=str(attempt))),flush=True)
  code=child.wait();save(attempt/'exit.json',dict(exitCode=code,child=ci));assert code==0,'Preserve native failure log and partial source'
  stream.CASE='camera';proof=stream.verify(capture,prep,purpose);comparison=compare(proof,prep);save(attempt/'paired-state-comparison.json',comparison);proof['pairedStateComparison']=pin(attempt/'paired-state-comparison.json');save(accepted,proof);return dict(completed=True,proof=pin(accepted))
 except Exception as e:
  if child is not None and child.poll()is not None:save(BASE/('failure-'+purpose+'.json'),dict(error=str(e),partialOutputsPreserved=True))
  raise
 finally:
  live=child is not None and child.poll()is None
  if owned and not live and n.LEASE.exists()and read(n.LEASE).get('token')==owned:n.LEASE.unlink()
  if worker.handle is not None:worker.close(remove=not live)
def main(purpose,script):
 ap=argparse.ArgumentParser();ap.add_argument('--project',required=True);ap.add_argument('--stage',action='store_true');ap.add_argument('--execute',action='store_true');ap.add_argument('--wait-minutes',type=float,default=0);a=ap.parse_args();assert a.project==SLUG and not(a.stage and a.execute);prep=prepare()
 if a.stage:stage(prep)
 result=execute(prep,purpose,script,a.wait_minutes)if a.execute else dict(sourceReady=True,staged=a.stage,fingerprint=prep['fingerprint'],guardReason=busy(),unityStarted=False)
 print(json.dumps(result),flush=True)
