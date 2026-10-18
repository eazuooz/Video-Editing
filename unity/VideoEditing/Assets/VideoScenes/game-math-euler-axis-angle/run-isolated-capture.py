"""Explicit parent-coordinated finite Unity capture, with own GPU lease.

This never installs packages, pauses foreign work, modifies the main editor,
chooses a next video, or launches itself automatically.
"""
from pathlib import Path
import argparse,json,shutil,subprocess,sys,time,uuid
import psutil

ROOT=Path(__file__).resolve().parents[5]
OWN=Path(__file__).resolve().parent
LOCAL=ROOT/'projects/game-math-euler-axis-angle/production/local/revision-v2'
ISO=LOCAL/'unity-capture'
LEASE=ROOT/'shared/output/GPU_HANDOFF.json'
UNITY=Path('C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--job',required=True);ap.add_argument('--bake',action='store_true')
    ap.add_argument('--timeout-seconds',type=int,default=3600);args=ap.parse_args()
    job_path=Path(args.job).resolve();job=json.loads(job_path.read_text(encoding='utf-8-sig'))
    out=Path(job['outputDirectory']).resolve();out.mkdir(parents=True,exist_ok=True)
    if not out.is_relative_to(LOCAL.resolve()):raise RuntimeError('Capture output must remain inside selected revision-v2 local staging.')
    control=json.loads((ROOT/'shared/publishing/video-production-control.json').read_text(encoding='utf-8-sig'))
    if control.get('selectedVideo')!='game-math-euler-axis-angle':raise RuntimeError('M04 is not selected.')
    if LEASE.exists():raise RuntimeError('Another GPU lease exists; preserved.')
    for process in psutil.process_iter(['pid','name','cmdline']):
        if (process.info['name'] or '').lower()=='unity.exe' and not any('-adb' in a.lower() for a in (process.info['cmdline'] or [])):
            if str(ISO).lower().replace('\\','/') in ' '.join(process.info['cmdline'] or []).lower().replace('\\','/'):
                raise RuntimeError('The isolated project already has a Unity owner; preserved.')
    free,util=map(int,subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip().replace(' ','').split(','))
    if free<2048:raise RuntimeError('Less than2GiB VRAM free for bounded procedural capture; foreign work preserved.')
    # Sync owned sources only. Keep warmed isolated Packages/Library/settings.
    target=ISO/'Assets/VideoScenes/game-math-euler-axis-angle'
    shutil.copytree(OWN,target,dirs_exist_ok=True)
    shutil.copy2(Path(str(OWN)+'.meta'),Path(str(target)+'.meta'))
    me=psutil.Process();token=str(uuid.uuid4());proc=None
    record=dict(schemaVersion=1,token=token,project='game-math-euler-axis-angle',state='render_running',
        coordinator=dict(pid=me.pid,createTime=me.create_time()),purpose='Explicit selected M04 finite spatial capture',
        requestedAt=time.time(),job=str(job_path),gpuBefore=dict(freeMiB=free,utilization=util),
        foreignApplicationsClosed=False,foreignProcessesPaused=False)
    with LEASE.open('x',encoding='utf8') as f:json.dump(record,f,indent=2)
    try:
        entry='YamyamCoding.GameMath.EulerAxisAngle.Editor.'+('EulerSceneAssetBuilder.BuildAndCaptureInIsolatedProject' if args.bake else 'EulerCaptureBatch.Run')
        log=out/'unity-editor.log'
        command=[str(UNITY),'-batchmode','-projectPath',str(ISO),'-force-d3d11','-executeMethod',entry,'-m04Job',str(job_path),'-logFile',str(log)]
        proc=subprocess.Popen(command,cwd=ROOT,creationflags=subprocess.CREATE_NO_WINDOW)
        record['unity']=dict(pid=proc.pid,createTime=psutil.Process(proc.pid).create_time(),log=str(log),command=command)
        (out/'process.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf8')
        print(json.dumps(dict(status='running',pid=proc.pid,log=str(log))),flush=True)
        began=time.monotonic()
        while proc.poll() is None:
            if time.monotonic()-began>args.timeout_seconds:
                proc.terminate();proc.wait(timeout=30);raise RuntimeError('Own isolated capture exceeded configured timeout; only its own Unity process stopped.')
            time.sleep(5)
        record.update(exitCode=proc.returncode,finishedAt=time.time())
        (out/'process.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf8')
        print(json.dumps(dict(status='completed' if proc.returncode==0 else 'failed',exitCode=proc.returncode,output=str(out))),flush=True)
        return proc.returncode
    finally:
        if proc is not None and proc.poll() is None:proc.terminate();proc.wait(timeout=30)
        if LEASE.exists():
            current=json.loads(LEASE.read_text(encoding='utf8'))
            if current.get('token')==token:
                record.update(state='render_process_exiting',finishedAt=time.time())
                history=ROOT/'shared/output/gpu-handoff';history.mkdir(exist_ok=True)
                (history/(token+'.json')).write_text(json.dumps(record,indent=2)+'\n',encoding='utf8')
                LEASE.unlink()

if __name__=='__main__':sys.exit(main())
