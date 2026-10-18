"""Root-invoked finite Unity FOV capture; no work starts when imported.

--prepare only creates this Short's minimal disposable built-in project.
--preview captures the two endpoints; --capture captures frame000..060.
Never clones M04, touches a live editor, pauses work or removes foreign leases.
"""
from __future__ import annotations
import argparse, hashlib, json, os, shutil, subprocess, sys, time, uuid
from pathlib import Path
import psutil

ROOT = Path(__file__).resolve().parents[3]
SLUG = 'shorts-fov-one-change'
PROJECT = ROOT/'projects'/SLUG
OWN = ROOT/'unity/VideoEditing/Assets/VideoScenes'/SLUG
ISO = PROJECT/'production/local/unity-capture'
LEASE = ROOT/'shared/output/GPU_HANDOFF.json'
UNITY = Path('C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe')
SOURCE_SCENE = OWN/'Scenes/FovOneChange.unity'

def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(8*1024*1024),b''): h.update(chunk)
    return h.hexdigest()
def check_selection():
    control=read(ROOT/'shared/publishing/video-production-control.json')
    if control.get('shortsRecurringAuthorization',{}).get('selectedShort')!=SLUG:
        raise RuntimeError('This exact Short must be selected before capture. Other work is preserved.')
def inside(path,parent):
    if not Path(path).resolve().is_relative_to(Path(parent).resolve()):
        raise RuntimeError('Resolved path is outside this Short\'s owned workspace: '+str(path))
def existing_owner():
    needle=str(ISO.resolve()).replace('\\','/').lower()
    for process in psutil.process_iter(['pid','name','cmdline']):
        try:
            if (process.info['name'] or '').lower()=='unity.exe' and needle in ' '.join(process.info['cmdline'] or []).replace('\\','/').lower():
                raise RuntimeError('This isolated project already has a Unity owner; it is preserved.')
        except (psutil.NoSuchProcess,psutil.AccessDenied): pass
def prepare():
    check_selection();inside(ISO,PROJECT/'production/local');inside(OWN,ROOT/'unity/VideoEditing/Assets/VideoScenes')
    existing_owner()
    if not SOURCE_SCENE.exists(): raise RuntimeError('Owned editable scene file is missing.')
    target=ISO/'Assets/VideoScenes'/SLUG
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copytree(OWN,target,dirs_exist_ok=True)
    shutil.copy2(Path(str(OWN)+'.meta'),Path(str(target)+'.meta'))
    packages=ISO/'Packages';packages.mkdir(parents=True,exist_ok=True)
    package_file=packages/'manifest.json'
    # Official module already shipped with this installed Unity editor. This
    # enables CreatePrimitive/Collider references; it is not an external asset
    # or a registry package installation. Preserve the one earlier own empty
    # bootstrap manifest when upgrading it, and reject any foreign additions.
    minimal={'dependencies':{'com.unity.modules.physics':'1.0.0','com.unity.modules.imageconversion':'1.0.0'}}
    if package_file.exists() and read(package_file)!=minimal:
        prior=read(package_file)
        if prior not in ({'dependencies':{}},{'dependencies':{'com.unity.modules.physics':'1.0.0'}}):
            raise RuntimeError('Existing isolated package configuration differs; preserve it for inspection.')
        previous=packages/('manifest.before-builtin-physics.json' if prior=={'dependencies':{}} else 'manifest.before-builtin-imageconversion.json')
        if previous.exists():
            if previous.read_bytes()!=package_file.read_bytes():
                raise RuntimeError('Earlier own-manifest backup differs; preserve both for inspection.')
        else: shutil.copy2(package_file,previous)
    write(package_file,minimal)
    settings=ISO/'ProjectSettings';settings.mkdir(parents=True,exist_ok=True)
    version=(ROOT/'unity/VideoEditing/ProjectSettings/ProjectVersion.txt').read_text(encoding='utf8')
    if '6000.6.0f1' not in version: raise RuntimeError('Source editor version changed; inspect before capture.')
    (settings/'ProjectVersion.txt').write_text(version,encoding='utf8')
    # No URP/external packages or settings are copied. Unity generates defaults here;
    # the explicit batch entry selects built-in, Linear,4xMSAA and fixed light.
    sources=[p for p in OWN.rglob('*') if p.is_file() and p.suffix in {'.cs','.unity','.meta','.md','.json','.mat','.asset'}]
    signature=[dict(path=p.relative_to(OWN).as_posix(),sha256=sha(p)) for p in sorted(sources)]
    write(ISO/'prepare-receipt.json',dict(slug=SLUG,editorVersion='6000.6.0f1',renderPipeline='built-in only',builtinModuleDependencies=minimal['dependencies'],sourceFiles=signature,
        foreignProjectCopied=False,liveEditorModified=False,sceneIsBootstrapUntilFirstSuccessfulBatchBake=True))
    return signature
def free_gpu():
    text=subprocess.check_output(['nvidia-smi','--id=0','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip()
    free,utilization=map(int,text.replace(' ','').split(','))
    if free<2048: raise RuntimeError('At least2GiB free VRAM is required; foreign work is preserved.')
    return dict(index=0,freeMiB=free,utilizationPercent=utilization)
def copy_back_saved_scene():
    isolated=ISO/'Assets/VideoScenes'/SLUG
    scene=isolated/'Scenes/FovOneChange.unity'
    if not scene.exists(): raise RuntimeError('No saved scene was produced.')
    # Only scene/material/mesh serialization generated for this owned scene.
    # Do not propagate disposable project settings, packages, Library or PNGs.
    copied=[]
    for folder in ['Scenes','Baked']:
        origin=isolated/folder
        if not origin.exists(): continue
        for path in origin.rglob('*'):
            if path.is_file() and path.suffix in {'.unity','.mat','.asset','.meta'}:
                relative=path.relative_to(isolated);target=OWN/relative;inside(target,OWN)
                target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target);copied.append(dict(path=str(target.relative_to(ROOT)),sha256=sha(target)))
        folder_meta=isolated/(folder+'.meta')
        if folder_meta.exists(): shutil.copy2(folder_meta,OWN/(folder+'.meta'))
    return copied
def capture(mode,timeout):
    check_selection()
    if LEASE.exists(): raise RuntimeError('Another GPU lease exists; do not remove or replace it.')
    signature=prepare();check_selection();existing_owner();gpu=free_gpu()
    if not UNITY.exists(): raise RuntimeError('Unity6000.6.0f1 executable is not installed at the explicit path.')
    samples=2 if mode=='preview' else 61
    output=ISO/'output'/mode;inside(output,ISO)
    receipt=output/'capture-receipt.json'
    request=dict(mode=mode,samples=samples,sourceFiles=signature,runnerSha256=sha(__file__))
    if receipt.exists():
        previous=read(receipt)
        if previous.get('request')==request and all(Path(row['path']).exists() and sha(row['path'])==row['sha256'] for row in previous['files']):
            print(json.dumps(dict(status='reused-identical-capture',receipt=str(receipt))));return 0
        raise RuntimeError('An earlier capture exists with different inputs; preserve it in a versioned output before repeating.')
    if output.exists() and any(output.glob('*.png')):
        raise RuntimeError('Partial PNG evidence exists without a complete receipt; inspect it rather than overwriting.')
    output.mkdir(parents=True,exist_ok=True)
    job=ISO/(mode+'-job.json');write(job,dict(outputDirectory=str(output.resolve()),mode=mode,samples=samples))
    log=output/'unity-editor.log';coordinator=psutil.Process();token=str(uuid.uuid4());process=None
    record=dict(schemaVersion=1,token=token,project=SLUG,state='render_running',purpose='Explicit bounded FOV endpoints' if mode=='preview' else 'Explicit61-frame FOV capture',
        coordinator=dict(pid=coordinator.pid,createTime=coordinator.create_time()),requestedAt=time.time(),gpuBefore=gpu,
        foreignApplicationsClosed=False,foreignProcessesPaused=False,job=str(job.resolve()))
    LEASE.parent.mkdir(parents=True,exist_ok=True)
    with LEASE.open('x',encoding='utf8') as stream:json.dump(record,stream,indent=2)
    try:
        command=[str(UNITY),'-batchmode','-projectPath',str(ISO.resolve()),'-force-d3d11','-executeMethod',
                 'YamyamCoding.Shorts.FovOneChange.Editor.FovCapture.Run','-fovJob',str(job.resolve()),'-logFile',str(log.resolve())]
        startup=None;flags=0
        if os.name=='nt':
            flags=subprocess.CREATE_NO_WINDOW;startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
        process=subprocess.Popen(command,cwd=ROOT,creationflags=flags,startupinfo=startup)
        record['unity']=dict(pid=process.pid,createTime=psutil.Process(process.pid).create_time(),command=command,log=str(log))
        write(output/'process.json',record);print(json.dumps(dict(status='running',mode=mode,pid=process.pid,log=str(log))),flush=True)
        began=time.monotonic()
        while process.poll() is None:
            if time.monotonic()-began>timeout:
                process.terminate();process.wait(timeout=30);raise RuntimeError('Only this task\'s isolated process was stopped after its configured timeout.')
            time.sleep(2)
        record.update(exitCode=process.returncode,finishedAt=time.time());write(output/'process.json',record)
        if process.returncode:raise RuntimeError('Own isolated Unity failed; inspect '+str(log))
        success=read(output/'capture-success.json');projection=read(output/'capture-projection.json')
        expected=[0,60] if samples==2 else list(range(61))
        if success['frames']!=samples or [f['index'] for f in projection['frames']]!=expected or not projection['allTransformsUnchanged']:
            raise RuntimeError('Capture count/transform invariance receipt failed.')
        pngs=[output/f'frame-{i:03}.png' for i in expected]
        if not all(p.exists() for p in pngs):raise RuntimeError('Some finite capture PNGs are missing.')
        copied=copy_back_saved_scene()
        files=pngs+[output/'capture-projection.json',output/'capture-success.json']
        result=dict(status='captured-pixel-review-pending',request=request,output=str(output.resolve()),
            files=[dict(path=str(p.resolve()),sha256=sha(p),bytes=p.stat().st_size) for p in files],savedSourceScene=str(SOURCE_SCENE.relative_to(ROOT)),
            copiedOwnedSourceAssets=copied,editorVersion='6000.6.0f1',pipeline='built-in',width=1920,height=1080,
            onlyVariable='horizontal FOV60→100 using Camera.HorizontalToVerticalFieldOfView',frames=samples,
            assetProvenance='Original Yamyam Coding procedural meshes/materials; Unity built-in primitive meshes. No external downloaded assets.',
            currentNativePixelReview='pending',foreignEditorModified=False)
        write(receipt,result);print(json.dumps(dict(status=result['status'],frames=samples,receipt=str(receipt))),flush=True);return 0
    finally:
        if process is not None and process.poll() is None:process.terminate();process.wait(timeout=30)
        if LEASE.exists():
            current=read(LEASE)
            if current.get('token')==token:
                record.update(state='own-capture-exited',finishedAt=time.time());write(output/'gpu-lease-history.json',record);LEASE.unlink()

def main():
    parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--prepare',action='store_true');group.add_argument('--preview',action='store_true');group.add_argument('--capture',action='store_true')
    parser.add_argument('--timeout-seconds',type=int,default=900);args=parser.parse_args()
    if args.prepare:prepare();print(json.dumps(dict(status='prepared-no-Unity-or-GPU-job',project=str(ISO))));return 0
    return capture('preview' if args.preview else 'capture',args.timeout_seconds)
if __name__=='__main__':sys.exit(main())
