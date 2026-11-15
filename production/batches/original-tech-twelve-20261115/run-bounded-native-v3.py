"""Guarded exact12 native capture with lossless RGB streaming and disk reserve.

Default is read-only; --stage only copies verified source inputs. The32-frame
smoke job checks actual Unity pixels against the encoded RGB stream. Full720
capture requires a separately inspected smoke visual review. No foreign app,
process, lease, original source, prior capture or automation is changed.
"""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,os,shutil,subprocess,sys,time,uuid
import psutil
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
RUN=MEDIA/'production-resume-20261115T055255Z';SOURCE=HERE/'native-bounded-storage-v3'
KEY='explicitOriginalTechTwelve20261115';LEASE=ROOT/'shared/output/GPU_HANDOFF.json'
REGISTRY={
 'lockon':('run-lockon-native-v1.py','shorts-oot-ninja-show-z-targeting','LockOnCapture.cs','LockOn'),
 'sand':('run-sand-native-v1.py','shorts-journey-sand-sparkle','SandCapture.cs','Sand'),
 'placement':('run-placement-native-v1.py','shorts-horizon-gpu-placement','PlacementCapture.cs','Placement'),
 'remaining-seven':('run-remaining-seven-native-v1.py',None,'RemainingCapture.cs','RemainingSeven'),
}
SLUGS=['shorts-oot-ninja-show-z-targeting','shorts-mario64-lakitu-camera','shorts-journey-sand-sparkle','shorts-horizon-gpu-placement','shorts-inside-temporal-antialiasing','shorts-spiderman-swing-anchor','shorts-control-destruction-pipeline','shorts-returnal-particle-tentacles','shorts-ratchet-dimension-streaming','shorts-doom-push-forward-healing','shorts-botw-chemistry-rules','shorts-mariokart8-spin-boost']
def module(name,p):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
native=module('ot12_stream_existing_full_guard',HERE/'run-camera-native-v1.py')
read,sha,pin,save,digest=native.read,native.sha,native.pin,native.save,native.digest
runtime=native.runtime;CASE=None;BASE=None;PROTOCOL=None;OWNER=None
def configure(case):
    global CASE,BASE,PROTOCOL,OWNER
    CASE=case;slug=REGISTRY[case][1];BASE=MEDIA/(slug if slug else'remaining-seven')/'native-bounded-v3'
    PROTOCOL='original-tech-twelve-'+case+'-native-bounded-v3';OWNER='original-tech-twelve-'+case+'-native-stream'
    runtime.PROTOCOL=PROTOCOL;runtime.OWNER=OWNER;native.guard.qualifier.BASE=BASE/'resource-observations'
def authority():
    d=read(ROOT/'shared/publishing/video-production-control.json')[KEY];assert d['automaticAdvanceWithinExactList'] and d['intermediateApprovalRequired']is False
    assert d.get('status')not in['stopped','paused','cancelled'];b=read(HERE/'batch.json');assert[x['slug']for x in b['projects']]==SLUGS
    assert b['authorization']['fullProductionAuthorized'] and not b['authorization']['youtubeAuthorized'];return b
def prepare():
    authority();helper,slug,editor,namespace=REGISTRY[CASE]
    old_path=MEDIA/(slug+'/native-v1'if slug else'remaining-seven-native-v1')/'source-preparation.json';old=read(old_path);assert old['sourceStageComplete']
    # This is an explicit new storage identity, not a broad alias or in-place
    # repin of an accepted old capture. Original model and asset bytes stay put.
    derived=read(SOURCE/'source-derivation.json');entry=next(x for x in derived['sourceDerivations']if x['case']==CASE)
    for row in[entry['original'],entry['derived'],derived['storageSource']]:assert sha(row['path'])==row['sha256']
    files=[]
    for row in old['files']:
        assert sha(row['source'])==row['sha256'];item=dict(row)
        if Path(row['source']).name==editor:item.update(source=entry['derived']['path'],sha256=entry['derived']['sha256'])
        files.append(item)
    files.append(dict(source=str(SOURCE/'LosslessFrameSink.cs'),target='Assets/OriginalTechTwelve/CaptureStorageV2/LosslessFrameSink.cs',sha256=sha(SOURCE/'LosslessFrameSink.cs')))
    compiler=RUN/'native-bounded-static-v3/compile-receipt.json';c=next(x for x in read(compiler)['groups']if x['case']==CASE);assert c['staticCompilationPassed']
    actual={str(Path(x['source']).resolve()):x['sha256']for x in files if Path(x['source']).suffix=='.cs'}
    assert actual=={str(Path(x['path']).resolve()):x['sha256']for x in c['sourceInputs']}
    original_model=c['unchangedModelSemanticProof'];assert sha(original_model['path'])==original_model['sha256']
    codec=RUN/'native-stream-codec-cpu-fixture-v2/receipt.json';test=read(codec);assert test['allDecodedRgbBytesExact'] and test['frameCount']==8 and not test['gpuUsed']
    encoder=Path(test['encoder']['path']);assert sha(encoder)==test['encoder']['sha256']
    contract=dict(old['contract'],storage='lossless-libx264rgb-crf0',fullFrames=(240 if CASE=='sand'else 720),smokeFrames=32,stepsPerEditorCallback=8,minimumFreeMediaBytes=2*1073741824,minimumFreeRepoBytes=512*1048576)
    if CASE=='sand':contract['selectedCameras']={mode:('dune'if mode in ['smooth-surface','masked-glints-broad-light']else'detail')for mode in contract['modes']}
    fingerprint=digest(dict(files=files,generated=old['generated'],contract=contract,adapter=pin(__file__),encoder=pin(encoder),compiler=pin(compiler),codecFixture=pin(codec)))
    project=BASE/'projects'/fingerprint[:16];scene_root=next(x['target'].split('/Editor/')[0]for x in files if Path(x['source']).name==editor)
    return dict(fingerprint=fingerprint,case=CASE,protocol=PROTOCOL,files=files,generated=old['generated'],contract=contract,project=str(project),sceneRoot=scene_root,entry='Yamyam.OriginalTechTwelve.'+namespace+'.Editor.'+editor[:-3]+'.Run',editor=old['editor'],encoder=pin(encoder),compiler=pin(compiler),codecFixture=pin(codec),originalPreparation=pin(old_path),originalModelSemanticProof=original_model,sourceStageComplete=False,actualNativeFullComplete=False)
def stage(prep):
    project=Path(prep['project']).resolve();assert project.is_relative_to((BASE/'projects').resolve())
    for row in prep['files']:
        source=Path(row['source']);target=project/row['target'];assert target.resolve().is_relative_to(project) and sha(source)==row['sha256'];assert not target.exists()or sha(target)==row['sha256'],'Preserve changed staged source'
        target.parent.mkdir(parents=True,exist_ok=True)
        if not target.exists():shutil.copy2(source,target)
    for name,text in prep['generated'].items():
        p=project/name;assert p.resolve().is_relative_to(project) and(not p.exists()or p.read_bytes()==text.encode('utf8'));p.parent.mkdir(parents=True,exist_ok=True)
        if not p.exists():p.write_bytes(text.encode('utf8'))
    prep['sourceStageComplete']=True;save(BASE/'source-preparation.json',prep)
def busy(token=None):
    if shutil.disk_usage(MEDIA).free<2*1073741824:return'Preserve at least2GiB free on the media drive'
    if shutil.disk_usage(ROOT).free<512*1048576:return'Preserve at least512MiB free on the repository drive'
    if CASE=='sand':
        prior=read(BASE.parent/'native-stream-v2/accepted-smoke.json');used=[c for c in prior['clips']if c['camera']==('dune'if c['mode']in ['smooth-surface','masked-glints-broad-light']else'detail')];estimate=sum(Path(c['video']['path']).stat().st_size for c in used)*240/32*1.25+256*1048576
        if shutil.disk_usage(MEDIA).free<2*1073741824+estimate:return'Preserve2GiB plus actual selected-shot storage estimate and25% margin'
    return native.busy(token) # Existing full guard, strict8192MiB/<15%, no bypass.
def reviewed_for_full(prep):
    path=BASE/'smoke-visual-review-v3.json'
    if not path.exists():return False
    d=read(path);assert d['fingerprint']==prep['fingerprint'] and d['actualSourceFramesInspected'];assert sha(d['smokeProof']['path'])==d['smokeProof']['sha256']
    return d['allowedForFullCapture']is True
def verify(capture,prep,purpose):
    import av
    from PIL import Image
    limit=32 if purpose=='smoke'else prep['contract']['fullFrames'];complete=read(capture/'complete.json');assert complete['fingerprint']==prep['fingerprint'] and complete['actualUnityCapture'] and complete['framesPerCamera']==limit
    topics=prep['contract'].get('topics',[None]);result=[]
    for topic in topics:
        for mode in prep['contract']['modes']:
            scene=Path(prep['project'])/prep['sceneRoot']/'Scenes'/((topic+'-'if topic else'')+mode+'.unity');assert scene.is_file()
            for camera in ([prep['contract']['selectedCameras'][mode]]if CASE=='sand'else prep['contract']['cameras']):
                folder=capture
                if topic:folder/=topic
                folder=folder/mode/camera;streamed=read(folder/'streamed-capture.json');trace=read(folder/'trace.json')
                assert streamed['complete'] and streamed['encoderExitCode']==0 and streamed['expectedFrames']==limit and(streamed['width'],streamed['height'],streamed['fps'])==(1080,1080,60)
                assert [x['frame']for x in streamed['frames']]==list(range(limit)) and[x['frame']for x in trace['frames']]==list(range(limit));assert trace['fingerprint']==prep['fingerprint']
                original=read(BASE.parent/'native-stream-v2/accepted-smoke.json');prior=next(c for c in original['clips']if c['topic']==topic and c['mode']==mode and c['camera']==camera);assert sha(prior['frameRgbManifest']['path'])==prior['frameRgbManifest']['sha256']
                prior_frames=read(prior['frameRgbManifest']['path'])['frames'];assert streamed['frames'][:32]==prior_frames,'Per-frame source pixels changed under batched callback scheduling'
                refs={int(p.stem.split('-')[-1]):p for p in folder.glob('reference-*.png')};expected_refs={x for x in prep['contract']['pilotFrames']if x<limit}|{limit-1};assert set(refs)==expected_refs
                video=folder/'frames-lossless-rgb.mp4';checked=0
                with av.open(str(video))as container:
                    stream=container.streams.video[0];assert(stream.width,stream.height)==(1080,1080)and stream.average_rate==60
                    for index,frame in enumerate(container.decode(stream)):
                        assert index<limit;data=frame.to_ndarray(format='rgb24').tobytes();assert hashlib.sha256(data).hexdigest()==streamed['frames'][index]['rgbSHA256'],'Encoded pixels differ from actual Unity source'
                        if index in refs:
                            with Image.open(refs[index])as image:assert image.size==(1080,1080)and image.convert('RGB').tobytes()==data,'Native PNG orientation/colors differ from encoded source'
                        checked+=1
                assert checked==limit
                if CASE=='temporal':assert trace['everyHistoryFrameRendered'] and trace['internalRenderWidth']==540
                result.append(dict(topic=topic,mode=mode,camera=camera,video=pin(video),frameRgbManifest=pin(folder/'streamed-capture.json'),trace=pin(folder/'trace.json'),referenceFrames=[pin(refs[k])for k in sorted(refs)],pixelFramesVerified=checked,allDecodedPixelsExact=True,scene=pin(scene)))
    # A later capture may rebuild generated scenes in the staging project.
    # Keep this attempt's complete editable source separately, without Library.
    snapshot=capture.parent/'editable-project';assert not snapshot.exists();snapshot.mkdir()
    for name in ['Assets','Packages','ProjectSettings']:shutil.copytree(Path(prep['project'])/name,snapshot/name)
    for clip in result:clip['scene']=pin(snapshot/Path(clip['scene']['path']).relative_to(Path(prep['project'])))
    source_assets=[pin(p)for p in sorted(snapshot.rglob('*'))if p.is_file()]
    return dict(fingerprint=prep['fingerprint'],purpose=purpose,capture=str(capture),actualUnityCapture=True,framesPerCamera=limit,fps=60,actualCaptureSeconds=limit/60,allPixelsRoundTripVerified=True,clips=result,editableProject=str(snapshot),editableAssets=source_assets,visualQaPassed=False,finalFilmComplete=False,humanApproval=False)
def release_own_library(prep):
    project=Path(prep['project']).resolve();library=(project/'Library').resolve();assert project.is_relative_to((BASE/'projects').resolve())and project.name==prep['fingerprint'][:16]and library.parent==project and library.name=='Library'
    if not library.exists():return dict(removed=False,reason='No generated Library cache')
    for process in psutil.process_iter(['name','cmdline']):
        if(process.info['name']or'').lower()=='unity.exe':
            args=process.info['cmdline']
            if args is None or any(str(project).lower().replace('\\','/')in str(x).lower().replace('\\','/')for x in args):return dict(removed=False,reason='Project may be open; preserve generated cache')
    total=sum(p.stat().st_size for p in library.rglob('*')if p.is_file());shutil.rmtree(library)
    return dict(removed=True,bytes=total,path=str(library),scope='Only this completed isolated project\'s regenerable Library; Assets/Packages/ProjectSettings and all capture sources retained')
def try_start(prep,purpose):
    authority();stored=read(BASE/'source-preparation.json');assert stored['fingerprint']==prep['fingerprint']and stored['sourceStageComplete']
    prior=BASE.parent/'native-stream-v2/accepted-smoke.json'
    if purpose=='smoke'and not prior.exists():return dict(started=False,reason='Awaiting original32-frame source smoke for exact schedule comparison')
    accepted=BASE/('accepted-'+purpose+'.json')
    if accepted.exists():
        d=read(accepted);assert d['fingerprint']==prep['fingerprint'];return dict(reusedExisting=True,proof=pin(accepted),purpose=purpose)
    failure=BASE/('failure-'+purpose+'.json');assert not failure.exists(),'Preserved failure: inspect before a separate repair identity'
    if purpose=='full'and not reviewed_for_full(prep):return dict(started=False,reason='Own32-frame codec and visual smoke review pending')
    reason=busy()
    if reason:return dict(started=False,reason=reason)
    worker=runtime.SingleWorker(path=BASE/'worker.json');owned=None;child=None
    try:
        worker.acquire();reason=busy()
        if reason:return dict(started=False,reason=reason)
        assert prepare()['fingerprint']==prep['fingerprint']
        for row in prep['files']:assert sha(Path(prep['project'])/row['target'])==row['sha256']
        token=worker.record['token'];lease=dict(protocol=PROTOCOL,owner=OWNER,token=token,**native.identity(),phase='reserved',child=None,fingerprint=prep['fingerprint'])
        try:
            with LEASE.open('x',encoding='utf8')as f:json.dump(lease,f)
        except FileExistsError:return dict(started=False,reason='Concurrent foreign lease preserved')
        owned=token;reason=busy(token)
        if reason:return dict(started=False,reason=reason)
        attempt=BASE/'attempts'/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8]);attempt.mkdir(parents=True,exist_ok=False)
        job=attempt/'job.json';capture=attempt/'capture';save(job,dict(output=str(capture),fingerprint=prep['fingerprint'],mode='full',capturePurpose=purpose,frameLimit=32 if purpose=='smoke'else prep['contract']['fullFrames'],ffmpeg=prep['encoder']['path']))
        args=[prep['editor']['path'],'-batchmode','-projectPath',prep['project'],'-executeMethod',prep['entry'],'-ot12Job',str(job),'-logFile',str(attempt/'unity.log')]
        save(attempt/'launch.json',dict(fingerprint=prep['fingerprint'],purpose=purpose,command=args,encoder=prep['encoder'],resourceGuard=pin(HERE/'run-camera-native-v1.py'),strictFreeGpuMiB=8192,utilizationBelow=15))
        child=subprocess.Popen(args,cwd=ROOT,creationflags=native.CREATE);identity=native.identity(child.pid);worker.update(child=identity);lease.update(phase='running',child=identity);save(LEASE,lease);save(BASE/'current-run.json',dict(status='native-'+purpose+'-running',fingerprint=prep['fingerprint'],purpose=purpose,**native.identity(),child=identity,attempt=str(attempt)))
        print(json.dumps(dict(started=True,purpose=purpose,case=CASE,child=identity)),flush=True);code=child.wait();save(attempt/'process-exit.json',dict(exitCode=code,child=identity))
        if code:raise RuntimeError('Native job failed; original and partial outputs preserved')
        proof=verify(capture,prep,purpose);save(attempt/'verification.json',proof);save(accepted,proof);cache=release_own_library(prep);save(attempt/'regenerable-cache-cleanup.json',cache)
        save(BASE/'current-run.json',dict(status='native-'+purpose+'-captured-review-pending',fingerprint=prep['fingerprint'],purpose=purpose,completed=True,proof=pin(accepted)))
        return dict(started=True,completed=True,case=CASE,purpose=purpose,proof=pin(accepted))
    except Exception as error:
        if child is not None and child.poll()is not None:save(failure,dict(fingerprint=prep['fingerprint'],purpose=purpose,error=type(error).__name__,message=str(error),partialOutputsPreserved=True))
        raise
    finally:
        live=child is not None and child.poll()is None
        if owned and not live and LEASE.exists():
            current=read(LEASE)
            if current.get('protocol')==PROTOCOL and current.get('token')==owned:LEASE.unlink()
        if worker.handle is not None:worker.close(remove=not live)
def execute(prep,purpose,wait_minutes):
    waiter=runtime.SingleWorker(path=BASE/('waiter-'+purpose+'.json'));waiter.acquire()
    try:
        deadline=time.monotonic()+wait_minutes*60;last=None
        while True:
            assert prepare()['fingerprint']==prep['fingerprint'],'Source changed during finite wait'
            result=try_start(prep,purpose)
            if result.get('started')or result.get('reusedExisting'):return result
            state=dict(status='finite-native-stream-resource-wait',case=CASE,purpose=purpose,fingerprint=prep['fingerprint'],reason=result.get('reason'),**native.identity(),modelStarted=False,unityStarted=False,newRecurringAutomation=False,updatedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat());save(BASE/('wait-status-'+purpose+'.json'),state)
            if state['reason']!=last:print(json.dumps(state),flush=True);last=state['reason']
            if time.monotonic()>=deadline:return dict(**result,boundedWaitExpired=True)
            time.sleep(min(30,max(0,deadline-time.monotonic())))
    finally:waiter.close()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--case',choices=REGISTRY,required=True);p.add_argument('--stage',action='store_true');p.add_argument('--execute',action='store_true');p.add_argument('--mode',choices=['smoke','full'],default='smoke');p.add_argument('--wait-minutes',type=float,default=0);a=p.parse_args();assert 0<=a.wait_minutes<=180 and not(a.stage and a.execute);configure(a.case);prep=prepare()
    if a.stage:stage(prep)
    result=execute(prep,a.mode,a.wait_minutes)if a.execute else dict(sourceReady=True,staged=a.stage,fingerprint=prep['fingerprint'],project=prep['project'],guardReason=busy(),encoder=prep['encoder'],gpuStarted=False,unityStarted=False)
    print(json.dumps(result,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
