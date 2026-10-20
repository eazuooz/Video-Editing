"""Prepare an independent Y90 recap still; --run needs an explicit GPU handoff."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,shutil,subprocess,time,uuid
import psutil
from PIL import Image

H=Path(__file__).parent
spec=importlib.util.spec_from_file_location('capture_contract',H/'spatial-capture.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
ROOT,OWN,ISO,O=c.ROOT,c.OWN,c.ISO,c.LOCAL
OUT=O/'spatial-recap'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def protected():
    receipt=read(O/'spatial-clips/spatial-capture-receipt.json');assert len(receipt['outputs'])==49
    paths=[Path(v['path']) for row in receipt['outputs'] for v in row['files'].values()]
    paths+=[OWN/'EulerV6Scene.cs',OWN/'EulerV6Math.cs',OWN/'spatial-shots.json']
    paths+=list((OWN/'Scenes').glob('*'))+list((OWN/'Shared').glob('*'))
    return {str(p.relative_to(ROOT)).replace('\\','/'):c.sha(p) for p in paths if p.is_file()}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',action='store_true');a=ap.parse_args()
    OUT.mkdir(exist_ok=True);job=OUT/'job.json';save(job,{'outputDirectory':str(OUT)})
    entry=OWN/'Editor/EulerV6RecapStill.cs';meta=entry.with_suffix('.cs.meta')
    if not meta.exists():
        guid=uuid.uuid5(uuid.NAMESPACE_URL,'yamyam-m04-v6/'+entry.relative_to(OWN).as_posix()).hex
        meta.write_text('fileFormatVersion: 2\nguid: '+guid+'\nMonoImporter:\n  externalObjects: {}\n  serializedVersion: 2\n  defaultReferences: []\n  executionOrder: 0\n  icon: {instanceID: 0}\n  userData:\n  assetBundleName:\n  assetBundleVariant:\n',encoding='utf8')
    if not a.run:
        print(json.dumps({'preparedOnly':True,'output':str(OUT/'summary-y90-neutral.png'),'nativeFrames':1,'GPUStarted':False}));return
    ctl=read(ROOT/'shared/publishing/video-production-control.json')
    assert ctl['selectedVideo']=='game-math-euler-axis-angle' and ctl['newProductionAuthorization']['fullProductionAuthorized']
    if c.LEASE.exists():raise RuntimeError('Existing GPU lease preserved; wait for handoff.')
    for p in psutil.process_iter(['pid','name','cmdline']):
        if (p.info['name'] or '').lower()=='unity.exe' and c.normalize(ISO) in c.normalize(' '.join(p.info['cmdline'] or [])):
            raise RuntimeError('The isolated project is occupied; no process changed.')
    before=c.gpu();assert before['freeMiB']>=4096
    apps=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True)
    if 'python' in apps.lower():raise RuntimeError('GPU compute owner preserved; wait for handoff.')
    original=protected();record={'schemaVersion':1,'project':'game-math-euler-axis-angle','token':uuid.uuid4().hex,'purpose':'one actual auxiliary Y90 still without editorial guides','state':'render_running','gpuBefore':before,'protectedBefore':original,'foreignProcessesChanged':False,'observations':[]}
    with c.LEASE.open('x',encoding='utf8') as f:json.dump(record,f)
    proc=None
    try:
        for source in [entry,meta]:shutil.copy2(source,ISO/c.REL/'Editor'/source.name)
        cmd=[str(c.UNITY),'-batchmode','-noUpm','-projectPath',str(ISO),'-force-d3d11','-job-worker-count','2','-background-job-worker-count','1',
             '-executeMethod','YamyamCoding.GameMath.EulerAxisAngle.V6.Editor.EulerV6RecapStill.Run','-m04V6RecapJob',str(job),'-logFile',str(OUT/'editor.log')]
        proc=subprocess.Popen(cmd,cwd=ROOT,creationflags=subprocess.CREATE_NO_WINDOW);owner=psutil.Process(proc.pid)
        record['unity']={'pid':proc.pid,'createTime':owner.create_time(),'project':str(ISO)};print(json.dumps(record['unity']),flush=True)
        started=time.monotonic()
        while proc.poll() is None:
            if time.monotonic()-started>300:owner.terminate();proc.wait(timeout=30);raise RuntimeError('Own still job timed out.')
            record['observations'].append({'elapsedSeconds':round(time.monotonic()-started,2),'ownUnityDedicatedMiB':c.dedicated_mib(proc.pid)})
            time.sleep(5)
        record['exitCode']=proc.returncode;record['ownEditorExited']=not owner.is_running();assert proc.returncode==0
        png=OUT/'summary-y90-neutral.png'
        with Image.open(png) as im:
            assert im.size==(1920,1080);im.resize((375,211),Image.Resampling.LANCZOS).save(OUT/'summary-y90-neutral.375.png')
        old=json.loads((O/'spatial-clips/v6-41.answer-y90.anchors.ndjson').read_text().splitlines()[-1])
        state=read(OUT/'state.json');error=max(abs(x-y) for x,y in zip(old['rowMatrixA'],state['rowMatrixA']));assert error<1e-6
        after=protected();assert original==after,'Protected captures/assets changed; do not use still.'
        record.update(state='complete',gpuAfter=c.gpu(),pngSha256=c.sha(png),poseMatrixMaximumDifferenceFromActualAuxiliaryEndpoint=error,protectedFilesByteIdentical=True,protectedFileCount=len(original),success=read(OUT/'success.json'),directPixelReview='pending native375 inspection')
    finally:
        if proc is not None and proc.poll() is None:
            try:
                owner=psutil.Process(proc.pid)
                if owner.create_time()==record['unity']['createTime']:owner.terminate();proc.wait(timeout=30)
            except psutil.NoSuchProcess:pass
        if record['state']!='complete':record['state']='failed_or_interrupted'
        record['finishedAt']=time.time();save(OUT/'receipt.json',record)
        if c.LEASE.exists() and read(c.LEASE).get('token')==record['token']:
            save(ROOT/'shared/output/gpu-handoff'/(record['token']+'.json'),record);c.LEASE.unlink()
if __name__=='__main__':main()
