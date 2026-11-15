"""Exact12 Horizon placement-rule teaching pilot. Default read-only; --stage is CPU-only.

--execute starts one bounded Unity job only after the unchanged existing full
resource guard plus8GiB/<15% headroom, singleton and shared lease checks. No app
is stopped, no foreign lease reclaimed, no voice or final film is accepted here.
"""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,os,shutil,subprocess,sys,time,uuid
import psutil
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
PROJECT=ROOT/'projects/shorts-horizon-gpu-placement';SOURCE=HERE/'placement-source-v1'
BASE=MEDIA/PROJECT.name/'native-v1';LEASE=ROOT/'shared/output/GPU_HANDOFF.json'
KEY='explicitOriginalTechTwelve20261115';PROTOCOL='original-tech-twelve-placement-native-v1';OWNER='original-tech-twelve-placement-native'
LEGACY=ROOT/'production/batches/architectural-111-20261106'
sys.path.insert(0,str(LEGACY))
def module(name,p):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
guard=module('ot12_existing_full_native_guard',LEGACY/'run-solution-path-native-v4.py')
runtime=guard.rt;runtime.PROTOCOL=PROTOCOL;runtime.OWNER=OWNER
EDITOR=Path(runtime.EDITOR);CREATE=getattr(subprocess,'CREATE_NO_WINDOW',0)

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    with Path(p).open('rb') as h:return hashlib.file_digest(h,'sha256').hexdigest()
def pin(p):return dict(path=str(Path(p).resolve()),sha256=sha(p))
def digest(d):return hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def save(p,d):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);temp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp')
    temp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8');os.replace(temp,p)
def identity(pid=None):
    p=psutil.Process(os.getpid() if pid is None else pid);return dict(pid=p.pid,createTime=p.create_time())
def authority():
    auth=read(ROOT/'shared/publishing/video-production-control.json')[KEY]
    assert auth.get('automaticAdvanceWithinExactList') and auth.get('intermediateApprovalRequired') is False
    assert auth.get('status') not in ['stopped','paused','cancelled']
    batch=read(HERE/'batch.json');assert len(batch['projects'])==12 and batch['projects'][3]['slug']==PROJECT.name
    assert batch['authorization']['fullProductionAuthorized'] and not batch['authorization']['youtubeAuthorized']
    return batch
def prepare():
    authority();files=[]
    for name in ['PlacementModel.cs','PlacementLesson.cs','Editor/PlacementCapture.cs']:
        files.append(dict(source=str(SOURCE/name),target='Assets/OriginalTechTwelve/PlacementV1/'+name,sha256=sha(SOURCE/name)))
    asset_plan=PROJECT/'planning/asset-selection-v1.json'
    plan=read(asset_plan);assert plan['productId']=='084' and not plan['originalFilesModified']
    for entry in plan['sharedAssetPaths']:
        assert sha(entry['path'])==entry['sha256'] and sha(entry['metaPath'])==entry['metaSHA256']
        files.append(dict(source=entry['path'],target=entry['target'],sha256=entry['sha256']))
        files.append(dict(source=entry['metaPath'],target=entry['target']+'.meta',sha256=entry['metaSHA256']))
    files.append(dict(source=str(asset_plan),target='Assets/OriginalTechTwelve/PlacementV1/asset-provenance.json',sha256=sha(asset_plan)))
    shader=ROOT/'unity/VideoEditing/Assets/VideoScenes/architectural-111-20261106/ArchitecturalSurface.shader'
    files.append(dict(source=str(shader),target='Assets/OriginalTechTwelve/PlacementV1/ArchitecturalSurface.shader',sha256=sha(shader)))
    packages={'dependencies':{k:'1.0.0' for k in ['com.unity.modules.physics','com.unity.modules.animation','com.unity.modules.imgui','com.unity.modules.jsonserialize','com.unity.modules.imageconversion']}}
    generated={'Packages/manifest.json':json.dumps(packages,indent=2)+'\n','ProjectSettings/ProjectVersion.txt':'m_EditorVersion: 6000.6.0f1\n'}
    compilers=[]
    for p in MEDIA.glob('production-resume-*/placement-static-*/compile-receipt.json'):
        d=read(p)
        expected={str(Path(f['source']).relative_to(SOURCE)).replace('\\','/'):f['sha256'] for f in files[:3]}
        if d.get('staticCompilationPassed') and d.get('modelChecks')==10 and d.get('sourceHashes')==expected:
            assert Path(d['actualResponseFile']).is_file() and 'CHECKS=10' in Path(d['modelTestLog']).read_text(encoding='utf-8-sig')
            compilers.append(pin(p))
    assert compilers,'Exact current static compiler and independent model fixture proof required'
    contract=dict(modes=['all-candidates','density-map','road-water-exclusion','terrain-aligned','two-placement-layers'],cameras=['forest','map'],fps=60,width=1080,height=1080,modelSeconds=12,pilotFrames=[0,90,150,240,330,420,510,600,660,719])
    fingerprint=digest(dict(files=files,generated=generated,contract=contract,editorVersion='6000.6.0f1'))
    project=BASE/'projects'/fingerprint[:16]
    return dict(protocol=PROTOCOL,fingerprint=fingerprint,files=files,generated=generated,contract=contract,project=str(project),compilerProof=compilers[-1],editor=pin(EDITOR),guard=pin(LEGACY/'run-solution-path-native-v4.py'),sourceStageComplete=False,nativeCaptureComplete=False)
def stage(prep):
    project=Path(prep['project']).resolve();assert project.is_relative_to((BASE/'projects').resolve())
    for f in prep['files']:
        src=Path(f['source']);dst=project/f['target'];assert dst.resolve().is_relative_to(project) and sha(src)==f['sha256']
        assert not dst.exists() or sha(dst)==f['sha256'],'Preserve altered staged input'
        dst.parent.mkdir(parents=True,exist_ok=True)
        if not dst.exists():shutil.copy2(src,dst)
    for name,text in prep['generated'].items():
        p=project/name;assert not p.exists() or p.read_bytes()==text.encode('utf8')
        p.parent.mkdir(parents=True,exist_ok=True)
        if not p.exists():p.write_bytes(text.encode('utf8'))
    prep['sourceStageComplete']=True;save(BASE/'source-preparation.json',prep)
def busy(token=None):
    reason=guard.busy_reason(token)
    if reason:return reason
    raw=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True,creationflags=CREATE)
    free,use=map(int,raw.splitlines()[0].replace(' ','').split(','))
    return f'Strict native headroom: {free}MiB/{use}% need8192MiB and below15%' if free<8192 or use>=15 else None
def verify(capture,prep,mode):
    record=read(capture/'complete.json');assert record['fingerprint']==prep['fingerprint'] and record['actualUnityCapture']
    frames=list(range(720)) if mode=='full' else prep['contract']['pilotFrames']
    from PIL import Image
    for name in prep['contract']['modes']:
        scene=Path(prep['project'])/'Assets/OriginalTechTwelve/PlacementV1/Scenes'/(name+'.unity');assert scene.is_file()
        for camera in prep['contract']['cameras']:
            folder=capture/name/camera;files=sorted(folder.glob('*.png'));assert [f.stem for f in files]==[f'{n:05}' for n in frames]
            trace=read(folder/'trace.json');assert trace['fingerprint']==prep['fingerprint'] and [r['frame'] for r in trace['frames']]==frames
            for f in files:
                with Image.open(f) as im:assert im.size==(1080,1080);im.verify()
    return dict(fingerprint=prep['fingerprint'],mode=mode,modes=5,camerasPerMode=2,framesPerCamera=len(frames),actualUnityCapture=True,sceneFilesSaved=True,visualQaPassed=False,finalFilmComplete=False,humanApproval=False)
def execute(prep,mode):
    stored=read(BASE/'source-preparation.json');assert stored['fingerprint']==prep['fingerprint'] and stored['sourceStageComplete']
    for f in prep['files']:assert sha(Path(prep['project'])/f['target'])==f['sha256']
    if (BASE/('accepted-'+mode+'.json')).exists():
        accepted=read(BASE/('accepted-'+mode+'.json'))
        if accepted['fingerprint']==prep['fingerprint']:
            return dict(reusedExisting=True,proof=verify(Path(accepted['capture']),prep,mode))
        raise RuntimeError('Prior capture with another source preserved; inspect before new version')
    reason=busy()
    if reason:return dict(started=False,reason=reason,sourceReady=True,mode=mode)
    worker=runtime.SingleWorker(path=BASE/'worker.json')
    owned=None;child=None
    try:
        worker.acquire();reason=busy()
        if reason:return dict(started=False,reason=reason,sourceReady=True,mode=mode)
        assert prepare()['fingerprint']==prep['fingerprint'];authority()
        attempt=BASE/'attempts'/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8]);attempt.mkdir(parents=True,exist_ok=False)
        token=worker.record['token'];lease=dict(protocol=PROTOCOL,owner=OWNER,token=token,**identity(),phase='reserved',child=None,fingerprint=prep['fingerprint'],output=str(attempt))
        try:
            with LEASE.open('x',encoding='utf8') as h:json.dump(lease,h)
        except FileExistsError:return dict(started=False,reason='Concurrent foreign lease preserved')
        owned=token;reason=busy(token)
        if reason:return dict(started=False,reason=reason,sourceReady=True,mode=mode)
        capture=attempt/'capture';job=attempt/'job.json';save(job,dict(output=str(capture),fingerprint=prep['fingerprint'],mode=mode))
        args=[str(EDITOR),'-batchmode','-projectPath',prep['project'],'-executeMethod','Yamyam.OriginalTechTwelve.Placement.Editor.PlacementCapture.Run','-ot12Job',str(job),'-logFile',str(attempt/'unity.log')]
        lease.update(phase='launching');save(LEASE,lease);save(attempt/'launch.json',dict(protocol=PROTOCOL,fingerprint=prep['fingerprint'],command=args,modelStarted=False,unityStarted=False))
        child=subprocess.Popen(args,cwd=ROOT,creationflags=CREATE);ci=identity(child.pid);worker.update(child=ci);lease.update(phase='running',child=ci);save(LEASE,lease)
        save(BASE/'current-run.json',dict(status='native-'+mode+'-running',protocol=PROTOCOL,**identity(),child=ci,attempt=str(attempt),fingerprint=prep['fingerprint']))
        print(json.dumps(dict(started=True,mode=mode,child=ci,attempt=str(attempt))),flush=True)
        code=child.wait() # The API yields the active cell; no unattended retry loop.
        save(attempt/'process-exit.json',dict(exitCode=code,child=ci,finishedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
        if code:raise RuntimeError('Native Unity job exited '+str(code)+'; preserve attempt and inspect log')
        proof=verify(capture,prep,mode);proof['capture']=str(capture);save(attempt/'verification.json',proof);save(BASE/('accepted-'+mode+'.json'),proof)
        save(BASE/'current-run.json',dict(status='native-'+mode+'-captured-visual-review-pending',attempt=str(attempt),fingerprint=prep['fingerprint'],child=ci,completed=True))
        return dict(started=True,completed=True,proof=proof)
    finally:
        child_live=child is not None and child.poll() is None
        if owned and not child_live and LEASE.exists():
            current=read(LEASE)
            if current.get('protocol')==PROTOCOL and current.get('owner')==OWNER and current.get('token')==owned:LEASE.unlink()
        if worker.handle is not None:worker.close(remove=not child_live)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',action='store_true');p.add_argument('--execute',action='store_true');p.add_argument('--mode',choices=['pilot','full'],default='pilot');p.add_argument('--wait-minutes',type=float,default=0);a=p.parse_args()
    assert not(a.stage and a.execute)
    prep=prepare()
    if a.stage:stage(prep)
    if a.execute and a.wait_minutes>0:
        assert 0<a.wait_minutes<=180,'Bounded finite wait only'
        waiter=runtime.SingleWorker(path=BASE/'waiter.json');waiter.acquire()
        try:
            deadline=time.monotonic()+a.wait_minutes*60;last=None
            while True:
                assert prepare()['fingerprint']==prep['fingerprint'],'Source changed during resource wait'
                result=execute(prep,a.mode)
                if result.get('started') or result.get('reusedExisting'):break
                status=dict(status='finite-native-pilot-resource-wait',protocol=PROTOCOL,**identity(),fingerprint=prep['fingerprint'],reason=result.get('reason'),mode=a.mode,modelStarted=False,unityStarted=False,newRecurringAutomation=False,updatedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat())
                save(BASE/'wait-status.json',status)
                if result.get('reason')!=last:print(json.dumps(status,ensure_ascii=False),flush=True);last=result.get('reason')
                if time.monotonic()>=deadline:result.update(boundedWaitExpired=True);break
                time.sleep(min(30,max(0,deadline-time.monotonic())))
        finally:waiter.close()
    else:result=execute(prep,a.mode) if a.execute else dict(sourceReady=True,staged=a.stage,fingerprint=prep['fingerprint'],project=prep['project'],compilerProof=prep['compilerProof'],guardReason=busy(),unityStarted=False,modelStarted=False)
    print(json.dumps(result,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
