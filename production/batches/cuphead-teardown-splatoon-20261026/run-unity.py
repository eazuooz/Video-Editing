"""One explicitly selected isolated Unity capture, preserving all other jobs."""
from pathlib import Path
import argparse, importlib.util, json, os, shutil, stat, subprocess, time, uuid
import psutil
R=Path(__file__).resolve().parents[3]
BASE=Path('C:/Users/1/Videos/YamyamProduction/cuphead-teardown-splatoon-20261026')
ISO=BASE/'unity-capture'
UNITY=Path('C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe')
LEASE=R/'shared/output/GPU_HANDOFF.json'
ENTRIES={
    'shorts-splatoon-surface-ink':('Yamyam.Video.SurfaceInk.Editor.SurfaceInkCapture.Run','-inkJob'),
    'shorts-splatoon-ink-readability':('YamyamCoding.Shorts.SplatoonInkReadability.Editor.InkReadabilityCapture.Run','-inkReadabilityJob'),
}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('slug',choices=ENTRIES);ap.add_argument('--job',required=True);args=ap.parse_args()
    spec=importlib.util.spec_from_file_location('batch_preflight',Path(__file__).with_name('preflight.py'))
    preflight=importlib.util.module_from_spec(spec);spec.loader.exec_module(preflight)
    preflight.check(args.slug,True)
    job=Path(args.job).resolve();assert job.is_relative_to((BASE/args.slug/'local').resolve())
    data=json.loads(job.read_text(encoding='utf8'));out=Path(data.get('output') or data['outputDirectory']).resolve()
    assert out.is_relative_to((BASE/args.slug/'local').resolve())
    assert not (out/'success.json').exists(),'Preserve successful capture'
    assert shutil.disk_usage(BASE).free>8*1024**3,'Require 8GB on C for isolated import/capture'
    source=R/'unity/VideoEditing/Assets/VideoScenes'/args.slug
    destination=ISO/'Assets/VideoScenes'/args.slug
    # Update only this selected source. Runtime outputs are preserved in Generated/Scenes.
    for path in source.rglob('*'):
        if path.is_file():
            target=destination/path.relative_to(source);target.parent.mkdir(parents=True,exist_ok=True)
            if target.exists() and target.read_bytes()==path.read_bytes(): continue
            if target.exists() and target.read_bytes()!=path.read_bytes() and target.suffix not in {'.cs','.shader','.md','.meta'}:
                raise RuntimeError('Preserve different generated asset: '+str(target))
            if target.exists(): target.chmod(target.stat().st_mode | stat.S_IWRITE)
            shutil.copy2(path,target)
    memory=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip()
    free,util=map(int,memory.split(','));assert free>=3000 and util<35,(free,util)
    me=psutil.Process();record=dict(token=str(uuid.uuid4()),project=args.slug,coordinator=dict(pid=me.pid,createTime=me.create_time()),purpose='Finite isolated Unity source capture',startedAt=time.time())
    LEASE.parent.mkdir(parents=True,exist_ok=True)
    with LEASE.open('x',encoding='utf8') as f:json.dump(record,f)
    proc=None;out.mkdir(parents=True,exist_ok=True)
    try:
        entry,flag=ENTRIES[args.slug]
        command=[str(UNITY),'-batchmode','-projectPath',str(ISO),'-force-d3d11','-executeMethod',entry,flag,str(job),'-logFile',str(out/'unity-editor.log')]
        proc=subprocess.Popen(command,cwd=R,creationflags=subprocess.CREATE_NO_WINDOW)
        record.update(unityPid=proc.pid,command=command)
        (out/'process.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf8')
        print(json.dumps(dict(pid=proc.pid,log=str(out/'unity-editor.log'))),flush=True)
        began=time.monotonic()
        while proc.poll() is None:
            games=[p.info for p in psutil.process_iter(['pid','name']) if (p.info['name'] or '').lower() in {'overwatch.exe','d2r.exe','cuphead.exe','teardown.exe','monsterhunterwilds.exe'}]
            if games: raise RuntimeError('User game resumed; stop only our isolated capture at safe process boundary: '+str(games))
            if time.monotonic()-began>2400:raise RuntimeError('Own capture timeout; preserve diagnostics')
            time.sleep(3)
        record.update(exitCode=proc.returncode,finishedAt=time.time())
        (out/'process.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf8')
        if proc.returncode or not (out/'success.json').exists():raise RuntimeError('Unity did not finish successfully; inspect own log')
        print(json.dumps(dict(status='completed',output=str(out))),flush=True)
    finally:
        if proc is not None and proc.poll() is None:proc.terminate();proc.wait(timeout=30)
        if LEASE.exists() and json.loads(LEASE.read_text(encoding='utf8')).get('token')==record['token']:LEASE.unlink()

if __name__=='__main__':main()
