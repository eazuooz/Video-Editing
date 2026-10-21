"""Finite V8 capture runner. Requires root's explicit GPU-slot handoff to run."""
from pathlib import Path
import argparse,copy,importlib.util,json,os,shutil,subprocess,sys,time,uuid
import psutil

sp=importlib.util.spec_from_file_location('v8_unity_prepare',Path(__file__).with_name('unity-prepare.py'))
M=importlib.util.module_from_spec(sp);sp.loader.exec_module(M)
ROOT,H,O,ISO,ASSET=M.ROOT,M.H,M.O,M.ISO,M.ASSET
LEASE=ROOT/'shared/output/GPU_HANDOFF.json'
UNITY=Path('C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe')

def meta(p):return dict(file=M.rel(p),sha256=M.sha(p),bytes=p.stat().st_size)
def gpu():
    s=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True).splitlines()[0]
    a,b,c=map(int,s.replace(' ','').split(','));return dict(freeMiB=a,usedMiB=b,utilization=c)
def probe(p):
    d=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-count_frames','-show_entries','stream=width,height,r_frame_rate,avg_frame_rate,nb_read_frames','-of','json',str(p)],text=True))['streams'][0]
    assert d['width']==1000 and d['height']==700 and d['r_frame_rate']==d['avg_frame_rate']=='60/1',d
    return d

def run(args):
    approval=M.authorized();job=M.read(O/'capture-job.json');assert job['approval']==approval
    for file,expected in job['immutableInputs'].items():assert M.sha(ROOT/file)==expected,'Changed prepared input: '+file
    assert not LEASE.exists(),'Preserve existing GPU owner. Await root handoff.'
    iso=str(ISO).lower().replace('\\','/')
    for p in psutil.process_iter(['name','cmdline']):
        if(p.info['name']or'').lower()=='unity.exe'and iso in' '.join(p.info['cmdline']or[]).lower().replace('\\','/'):
            raise RuntimeError('Own task-local Unity project already in use; preserved')
    clients=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True)
    assert not any('python'in x.lower()for x in clients.splitlines()),'Foreign GPU model remains; preserved'
    before=gpu();assert before['freeMiB']>=4096,'Less than4GiB GPU free; foreign apps preserved'
    if args.sample:
        ids=args.shot or ['intro-translate','intro-orientation','basis-y90','point-sum','projection','arm-hand-sword','pose-context','reflection','stretch-x','orthonormalize']
        known={x['shotId']for x in job['clips']};assert all(x in known for x in ids)
        job['clips']=[dict(shotId=x,frames=3,stillFrames=[])for x in ids]
        job.update(sampleOnly=True,bakeScenes=False,outputDirectory=str(O/'sample-native'/M.sha(O/'capture-job.json')[:12]))
    elif args.shot:
        ids=set(args.shot);job['clips']=[x for x in job['clips']if x['shotId']in ids];assert len(job['clips'])==len(ids)
        job.update(outputDirectory=str(O/'patch-native'/M.sha(O/'capture-job.json')[:12]),bakeScenes=False)
    out=Path(job['outputDirectory']);out.mkdir(parents=True,exist_ok=True)
    assert not any((out/(x['shotId']+'.mp4')).exists()for x in job['clips']),'Existing media preserved; inspect/reuse its receipt'
    # Only this newly owned folder is staged into the task's inactive clone.
    shutil.copytree(O/'prepared-unity',ISO/ASSET,dirs_exist_ok=True)
    jobfile=out/'executed-job.json';M.save(jobfile,job)
    me=psutil.Process();token=str(uuid.uuid4());record=dict(schemaVersion=1,token=token,project=M.P.name,revision='orientation-matrix-v8',purpose='finite native spatial sample'if args.sample else'finite native spatial capture',
        coordinator=dict(pid=me.pid,createTime=me.create_time()),state='render_running',startedAt=time.time(),approval=approval,job=M.rel(jobfile),jobSha256=M.sha(jobfile),gpuBefore=before,foreignProcessesChanged=False)
    LEASE.parent.mkdir(parents=True,exist_ok=True)
    with LEASE.open('x',encoding='utf8')as f:json.dump(record,f,indent=2)
    process=None;code=1;log=out/'capture-editor.log'
    try:
        # The explicit finite slot is acquired before any graphics process.
        M.authorized();cmd=[str(UNITY),'-batchmode','-noUpm','-projectPath',str(ISO),'-force-d3d11','-job-worker-count','2','-background-job-worker-count','1',
            '-executeMethod','YamyamCoding.GameMath.OrientationMatrix.V8.Editor.OrientationMatrixV8Capture.Run','-orientationV8Job',str(jobfile),'-logFile',str(log)]
        env=dict(os.environ,OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2')
        process=subprocess.Popen(cmd,cwd=ROOT,env=env,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
        who=psutil.Process(process.pid);record['unity']=dict(pid=who.pid,createTime=who.create_time(),project=M.rel(ISO),log=M.rel(log));M.save(out/'process.json',record)
        print(json.dumps(dict(phase='started',pid=process.pid,job=M.rel(jobfile),clips=len(job['clips']),frames=sum(x['frames']for x in job['clips'])),ensure_ascii=False),flush=True)
        try:code=process.wait(timeout=1200)
        except subprocess.TimeoutExpired:
            process.terminate();process.wait(timeout=30);raise RuntimeError('Own finite Unity job timed out; foreign editors untouched')
        assert code==0,'Own capture failed; inspect '+M.rel(log)
        success=M.read(out/'capture-success.json');assert success['width']==1000 and success['height']==700 and success['fps']==60
        outputs=[]
        specs={x['id']:x for x in M.S.SHOTS}
        for clip in job['clips']:
            id=clip['shotId'];file=out/(id+'.mp4');p=probe(file);assert int(p['nb_read_frames'])==clip['frames']
            first=out/(id+'.first.png');last=out/(id+'.last.png');middle=out/(id+'.middle.png')
            if not middle.exists():middle=last
            anchors=out/(id+'.anchors.ndjson');rows=anchors.read_text(encoding='utf8').splitlines();assert len(rows)==clip['frames']
            state0=json.loads(rows[0]);state1=json.loads(rows[-1]);assert state0['t']==0 and state1['t']==1
            stills={str(f):meta(out/(id+'.frame-'+str(f).zfill(4)+'.png'))for f in clip.get('stillFrames',[])}
            outputs.append(dict(id=id,sceneId=specs[id]['sceneId'],frames=clip['frames'],width=1000,height=700,fps=60,
                file=meta(file),first=meta(first),last=meta(last),middle=meta(middle),anchors=meta(anchors),frameStills=stills,shaderAudit=meta(out/(id+'.shaders.json')),
                program=specs[id],probe=p,sampleOnly=job['sampleOnly'],actualMatricesFirst=state0['rowMatrix'],actualMatricesLast=state1['rowMatrix']))
        receipt=dict(schemaVersion=1,complete=True,approval=approval,success=success,job=M.rel(jobfile),jobSha256=M.sha(jobfile),
            sampleOnly=job['sampleOnly'],outputs=outputs,totalFrames=sum(x['frames']for x in outputs),
            guideDepth='Axes/paths/projection/point markers are editorial projected overlays with owner-authored ZTestAlways/ZWriteOff shader; world/pixel anchors unchanged. Physical aircraft/mannequin/tool meshes retain ordinary3D depth.',
            mainEditorChanged=False,foreignProcessesChanged=False,pixelReview='pending actual first/mid/last inspection; sample endpoints are not full motion review')
        M.save(out/'capture-receipt.json',receipt)
        if not args.sample and not args.shot:
            scenes=M.read(out/'scenes-saved.json');assert scenes['scriptSceneCount']==13 and scenes['totalSceneFiles']==14
            saved=sorted((ISO/ASSET/'Scenes').glob('*.unity'));assert len(saved)==14
            receipt['actualSavedScenes']=[meta(p)for p in saved];M.save(out/'capture-receipt.json',receipt)
        print(json.dumps(dict(phase='complete',receipt=M.rel(out/'capture-receipt.json'),frames=receipt['totalFrames'],sampleOnly=receipt['sampleOnly']),ensure_ascii=False),flush=True)
    finally:
        record.update(state='complete'if code==0 else'failed',returnCode=code,endedAt=time.time(),foreignProcessesChanged=False)
        M.save(out/'process.json',record)
        if LEASE.exists()and M.read(LEASE).get('token')==token:LEASE.unlink()

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--run',action='store_true');ap.add_argument('--sample',action='store_true');ap.add_argument('--shot',action='append');a=ap.parse_args()
    if a.run:run(a)
    else:print('Prepared runner only. Root GPU handoff is required before --run.')
