"""One bounded isolated Unity sample with cooperative GPU lease and guaranteed release."""
from pathlib import Path
import datetime, json, os, subprocess, sys, time, uuid
import psutil

ROOT=Path(__file__).resolve().parents[5]
LOCAL=ROOT/'projects/game-math-euler-axis-angle/production/local/revision-v2'
LEASE=ROOT/'shared/output/GPU_HANDOFF.json'
UNITY=Path('C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe')
ISO=LOCAL/'unity-capture'

def main():
    control=json.loads((ROOT/'shared/publishing/video-production-control.json').read_text(encoding='utf-8-sig'))
    if control.get('selectedVideo')!='game-math-euler-axis-angle': raise RuntimeError('M04 is not selected.')
    if LEASE.exists(): raise RuntimeError('Another GPU lease exists; preserved.')
    memory=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip()
    free,util=map(int,memory.replace(' ','').split(','))
    if free<2048: raise RuntimeError('Insufficient VRAM for bounded scene preview; no foreign work touched.')
    me=psutil.Process(); token=str(uuid.uuid4())
    record=dict(schemaVersion=1,token=token,project='game-math-euler-axis-angle',state='render_running',
        purpose='parent-authorized isolated180-frame Unity visual sample only',
        coordinator=dict(pid=me.pid,createTime=me.create_time()),gpuBefore=dict(freeMiB=free,utilization=util),
        foreignProcessesPaused=False,foreignApplicationsClosed=False,requestedAt=time.time())
    LEASE.parent.mkdir(parents=True,exist_ok=True)
    with LEASE.open('x',encoding='utf8') as f: json.dump(record,f,indent=2)
    proc=None
    try:
        log=LOCAL/'unity-preview-editor.log'
        args=[str(UNITY),'-batchmode','-projectPath',str(ISO),'-force-d3d11',
            '-executeMethod','YamyamCoding.GameMath.EulerAxisAngle.Editor.EulerSceneAssetBuilder.BuildAndCaptureInIsolatedProject',
            '-m04Job',str(LOCAL/'unity-preview-job.json'),'-logFile',str(log)]
        proc=subprocess.Popen(args,cwd=ROOT,creationflags=subprocess.CREATE_NO_WINDOW)
        record['unity']=dict(pid=proc.pid,createTime=psutil.Process(proc.pid).create_time(),log=str(log),command=args)
        (LOCAL/'unity-preview-process.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf8')
        print(json.dumps(dict(status='running',pid=proc.pid,log=str(log),gpuFreeMiB=free)),flush=True)
        started=time.monotonic()
        while proc.poll() is None:
            if time.monotonic()-started>1200:
                proc.terminate(); proc.wait(timeout=30)
                raise RuntimeError('Own isolated preview exceeded20minutes; only own process stopped.')
            time.sleep(5)
        record.update(exitCode=proc.returncode,finishedAt=time.time())
        (LOCAL/'unity-preview-process.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf8')
        print(json.dumps(dict(status='completed' if proc.returncode==0 else 'failed',exitCode=proc.returncode,log=str(log))),flush=True)
        return proc.returncode
    finally:
        if proc is not None and proc.poll() is None:
            proc.terminate(); proc.wait(timeout=30)
        if LEASE.exists():
            current=json.loads(LEASE.read_text(encoding='utf8'))
            if current.get('token')==token:
                record.update(state='render_process_exiting',finishedAt=time.time())
                history=ROOT/'shared/output/gpu-handoff';history.mkdir(exist_ok=True)
                (history/(token+'.json')).write_text(json.dumps(record,indent=2)+'\n',encoding='utf8')
                LEASE.unlink()

if __name__=='__main__': sys.exit(main())
