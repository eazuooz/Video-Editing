"""Finite isolated V7 source capture. Run only after the root's GPU handoff.

The main Unity/Unreal editors and other research jobs are never closed. The
explicit scoped Part1 authorization is accepted without changing the shared
primary selector. A live GPU lease is never overwritten.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, os, shutil, subprocess, sys, time, uuid
import psutil

F=Path(__file__).with_name('right-prepare.py')
sp=importlib.util.spec_from_file_location('right_prepare',F);M=importlib.util.module_from_spec(sp);sp.loader.exec_module(M)
ROOT,H,O,ISO=M.ROOT,M.H,M.O,M.ISO
LEASE=ROOT/'shared/output/GPU_HANDOFF.json'
UNITY=Path('C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe')

def gpu():
    value=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip()
    free,used,util=map(int,value.split(','));return dict(freeMiB=free,usedMiB=used,utilization=util)

def run(args):
    approval=M.authorized()
    if LEASE.exists():raise RuntimeError('Existing GPU lease preserved. Await root handoff after voice/sourceASR.')
    normalized=str(ISO).lower().replace('\\','/')
    for p in psutil.process_iter(['name','cmdline']):
        if (p.info['name']or'').lower()=='unity.exe' and normalized in' '.join(p.info['cmdline']or[]).lower().replace('\\','/'):
            raise RuntimeError('Our isolated capture project already has an owner; preserved.')
    before=gpu()
    if before['freeMiB']<4096:raise RuntimeError('Less than4GiB free GPU memory; no foreign process changed.')
    live=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True)
    if any('python' in l.lower()for l in live.splitlines()):raise RuntimeError('A GPU Python owner remains; await handoff, do not interrupt it.')
    job=M.read(O/'right-native-job.json')
    if job['approval']!=approval:raise RuntimeError('Prepared capture authorization changed; reprepare without starting GPU.')
    plan=M.read(M.PLAN);generated=plan['generatedUnity']
    assert M.sha(ROOT/generated['generatedRuntime'])==generated['generatedRuntimeSha256']
    assert M.sha(ROOT/generated['generatedBridge'])==generated['generatedBridgeSha256']
    assert M.sha(ROOT/generated['catalog'])==generated['catalogSha256']==job['catalogSha256']
    assert M.sha(ROOT/generated['mathSource'])==generated['mathSourceSha256']==job['mathSourceSha256']
    assert job['generatedSourceSha256']==generated['generatedRuntimeSha256']
    assert job['generatedBridgeSha256']==generated['generatedBridgeSha256']
    if args.sample:
        job['clips']=[dict(shotId=k,frames=3)for k in ['v7-sail-raise','v7-log-align','v7-hook-rotate','v6-02.B02','v6-05.B02','v6-20.B01','v6-18.B01']]
        job['bakeScenes']=False;job['outputDirectory']=str(O/'spatial-sample')
        job['sampleOnly']=True
    out=Path(job['outputDirectory']);out.mkdir(parents=True,exist_ok=True)
    for clip in job['clips']:
        if (out/(clip['shotId']+'.mp4')).exists():raise RuntimeError('Capture output already exists; preserve and inspect its receipt, do not rerender: '+clip['shotId'])
    stage=ISO/'Assets/VideoScenes/game-math-euler-axis-angle/revision-v7-part1'
    stage.resolve().relative_to(ISO.resolve())
    shutil.copytree(O/'prepared-unity',stage,dirs_exist_ok=True)
    path=O/('right-sample-job.json'if args.sample else'right-native-job.json');M.save(path,job)
    me=psutil.Process();token=str(uuid.uuid4())
    record={'schemaVersion':1,'token':token,'project':'game-math-euler-axis-angle','part':1,'purpose':'M04-A finite right-pane label-free controlled models',
        'coordinator':{'pid':me.pid,'createTime':me.create_time()},'state':'render_running','job':M.rel(path),'jobSha256':M.sha(path),'authorization':approval,
        'gpuBefore':before,'foreignProcessesChanged':False,'observations':[]}
    with LEASE.open('x',encoding='utf8')as f:json.dump(record,f,indent=2)
    process=None;log=out/'capture-editor.log'
    try:
        cmd=[str(UNITY),'-batchmode','-noUpm','-projectPath',str(ISO),'-force-d3d11','-job-worker-count','2','-background-job-worker-count','1',
             '-executeMethod','YamyamCoding.GameMath.EulerAxisAngle.V7.Editor.EulerV7RightCapture.Run','-m04V7Job',str(path),'-logFile',str(log)]
        process=subprocess.Popen(cmd,cwd=ROOT,creationflags=subprocess.CREATE_NO_WINDOW)
        who=psutil.Process(process.pid);record['unity']={'pid':who.pid,'createTime':who.create_time(),'project':M.rel(ISO),'log':M.rel(log)}
        M.save(out/'process.json',record);print(json.dumps({'status':'running','ownPid':process.pid,'log':M.rel(log)}),flush=True)
        start=time.monotonic()
        while process.poll()is None:
            if time.monotonic()-start>args.timeout:
                # Only the captured exact PID/createTime is this task's process.
                if who.is_running() and who.create_time()==record['unity']['createTime']:who.terminate()
                process.wait(timeout=30);raise RuntimeError('Own finite capture timed out; foreign editors untouched.')
            record['observations'].append({'elapsedSeconds':round(time.monotonic()-start,2),**gpu()});time.sleep(5)
        record['exitCode']=process.returncode;record['gpuAfter']=gpu()
        if process.returncode:raise RuntimeError('Own Unity capture failed; inspect '+M.rel(log))
        success=M.read(out/'capture-success.json');outputs=[]
        for clip in job['clips']:
            key=clip['shotId'];files={kind:out/(key+suffix)for kind,suffix in [('clip','.mp4'),('firstFrame','.first.png'),('lastFrame','.last.png'),('anchors','.anchors.ndjson')]}
            assert all(f.exists()for f in files.values()),key
            probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,avg_frame_rate,nb_frames','-of','json',str(files['clip'])],text=True))['streams'][0]
            assert [probe['width'],probe['height']]==[1920,1080]and probe['avg_frame_rate']=='60/1'and int(probe['nb_frames'])==clip['frames']
            count=sum(1 for _ in files['anchors'].open(encoding='utf8'));assert count==clip['frames']
            outputs.append({'sourceBeatId':key,'frames':count,'files':{k:{'file':M.rel(f),'sha256':M.sha(f)}for k,f in files.items()},'probe':probe})
        M.save(out/'capture-receipt.json',{'schemaVersion':1,'jobSha256':M.sha(path),'authorization':approval,'outputs':outputs,'success':success,
            'sampleOnly':args.sample,'sample3FramesAreEndpointStatesNotContinuousMotion':args.sample,'newEncodedFullDecode':'pending','captionedMovingReview':'pending',
            'savedSceneEvidence':'must inspect actual Assets/VideoScenes/game-math-euler-axis-angle/revision-v7-part1/Scenes files; planned paths are not actual save proof'})
        record['state']='complete';print(json.dumps({'status':'complete','clips':len(outputs),'sampleOnly':args.sample}),flush=True)
    except BaseException:
        record['state']='failed'
        # A failed coordinator must not release its lease while its own Unity
        # process still renders. Only this exact PID/createTime can be stopped.
        if process and process.poll()is None:
            try:
                own=psutil.Process(process.pid)
                if own.create_time()==record.get('unity',{}).get('createTime'):
                    own.terminate();process.wait(timeout=30)
            except(psutil.NoSuchProcess,subprocess.TimeoutExpired):pass
        raise
    finally:
        record['ownProcessExitCode']=process.poll()if process else None;M.save(out/'process.json',record)
        if LEASE.exists()and(not process or process.poll()is not None):
            try:
                if M.read(LEASE).get('token')==token:LEASE.unlink()
            except(OSError,json.JSONDecodeError):pass

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',action='store_true');ap.add_argument('--sample',action='store_true');ap.add_argument('--timeout',type=int,default=2400);args=ap.parse_args()
    if not args.run:ap.print_help();return
    run(args)

if __name__=='__main__':main()
