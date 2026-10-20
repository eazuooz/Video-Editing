"""Prepare V6 finite clips from measured beats; explicit --run needs GPU handoff.

No main-editor control, installs, foreign process termination, or automatic jobs.
"""
from pathlib import Path
import argparse, hashlib, json, os, shutil, subprocess, sys, time, uuid
import psutil

ROOT=Path(__file__).resolve().parents[4]
P=ROOT/'projects/game-math-euler-axis-angle'
H=P/'production/revision-v6';LOCAL=P/'production/local/revision-v6'
OWN=ROOT/'unity/VideoEditing/Assets/VideoScenes/game-math-euler-axis-angle/revision-v6'
ISO=LOCAL/'unity-capture';REL=Path('Assets/VideoScenes/game-math-euler-axis-angle/revision-v6')
UNITY=Path('C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe')
LEASE=ROOT/'shared/output/GPU_HANDOFF.json'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def gpu():
    text=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip()
    free,used,util=map(int,text.split(','));return dict(freeMiB=free,usedMiB=used,utilizationPercent=util)
def normalize(s):return str(s).lower().replace('\\','/')
def dedicated_mib(pid):
    # WDDM nvidia-smi commonly reports N/A per process. Read only our exact PID.
    command=f"$m=Get-CimInstance Win32_PerfFormattedData_GPUPerformanceCounters_GPUProcessMemory -ErrorAction Stop | Where-Object {{$_.Name -like 'pid_{int(pid)}_*'}} | Measure-Object -Property DedicatedUsage -Sum; if($null -ne $m.Sum){{[math]::Round($m.Sum/1MB,2)}}"
    try:
        result=subprocess.check_output(['powershell','-NoProfile','-Command',command],text=True,stderr=subprocess.DEVNULL,timeout=12).strip()
        return float(result) if result else None
    except (subprocess.SubprocessError,ValueError):return None
def prepare(args):
    plan=json.loads((H/'spatial-plan.json').read_text(encoding='utf8'));clips=[]
    timeline=None
    if not args.sample:
        path=Path(args.timeline).resolve()
        if not path.exists():raise RuntimeError('Measured timeline is not ready; sample or prepare after actual speech timing.')
        timeline=json.loads(path.read_text(encoding='utf-8-sig'))
        by_scene={s['id']:s for s in timeline['scenes']}
    for scene in plan['scenes']:
        if args.scene and scene['id'] not in args.scene:continue
        for beat in scene['beats']:
            if beat['renderer']!='Unity':continue
            if args.sample and beat['id']!='v6-04.B01':continue
            frames=beat['durationFrames']
            if timeline is not None:
                measured=by_scene[scene['id']]
                found=next((b for b in measured['teachingBeats'] if b['id']==beat['id']),None)
                if found is None:
                    # Accept a numeric beat index only when its actual index matches exactly.
                    number=int(beat['id'].rsplit('B',1)[1]);found=next((b for b in measured['teachingBeats'] if str(b['id']) in [str(number),f'B{number:02}']),None)
                if found is None:raise RuntimeError('Measured teaching beat missing: '+beat['id'])
                frames=(int(found['visualEndFrame'])-int(found['visualStartFrame'])) if 'visualEndFrame' in found and 'visualStartFrame' in found else round(float(found['visualEnd'])*60)-round(float(found['visualStart'])*60)
                if frames<2:raise RuntimeError('Physical motion has no measured interval: '+beat['id'])
            clips.append(dict(shotId=beat['id'],frames=180 if args.sample else frames))
    if not args.sample:
        for auxiliary in plan.get('auxiliaryClips',[]):
            if args.scene and auxiliary['sceneId'] not in args.scene:continue
            candidates=timeline.get('auxiliaryVisuals',[])+by_scene[auxiliary['sceneId']].get('auxiliaryVisuals',[])
            found=next((b for b in candidates if b['id']==auxiliary['id']),None)
            if found is None:raise RuntimeError('Measured auxiliary interval missing: '+auxiliary['id'])
            frames=int(found['visualEndFrame'])-int(found['visualStartFrame'])
            if frames!=auxiliary['durationFrames']:raise RuntimeError('Auxiliary finite frame budget changed: '+auxiliary['id'])
            clips.append(dict(shotId=auxiliary['id'],frames=frames))
    if not clips:raise RuntimeError('No selected V6 physical shots.')
    out=LOCAL/('spatial-sample' if args.sample else 'spatial-clips');out.mkdir(parents=True,exist_ok=True)
    job=dict(outputDirectory=str(out),ffmpegPath=shutil.which('ffmpeg'),bakeScenes=args.bake,captureTestbed=args.sample,clips=clips)
    if not job['ffmpegPath']:raise RuntimeError('Existing FFmpeg is required; no install performed.')
    path=LOCAL/('spatial-sample-job.json' if args.sample else 'spatial-capture-job.json')
    path.write_text(json.dumps(job,indent=2)+'\n',encoding='utf8')
    return path,job

def run(path,job,args):
    control=json.loads((ROOT/'shared/publishing/video-production-control.json').read_text(encoding='utf-8-sig'))
    if control.get('selectedVideo')!='game-math-euler-axis-angle':raise RuntimeError('M04 is no longer selected.')
    if LEASE.exists():raise RuntimeError('Existing GPU lease preserved; wait for explicit handoff.')
    for p in psutil.process_iter(['pid','name','cmdline']):
        if p.info['name'] and p.info['name'].lower()=='unity.exe' and normalize(ISO) in normalize(' '.join(p.info['cmdline'] or [])):
            raise RuntimeError('The V6 isolated project already has an owner; preserved.')
    before=gpu()
    if before['freeMiB']<4096:raise RuntimeError('Less than4GiB GPU memory free; no foreign editor/process changed.')
    applications=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True)
    if any('python' in line.lower() for line in applications.splitlines()):raise RuntimeError('GPU Python/compute owner still visible; foreign process preserved, wait for handoff.')
    # Only explicit already-authored owned sources are copied; no foreign Library/binaries.
    shutil.copytree(OWN,ISO/REL,dirs_exist_ok=True)
    token=str(uuid.uuid4());me=psutil.Process();proc=None
    record=dict(schemaVersion=1,token=token,project='game-math-euler-axis-angle',state='render_running',purpose='Explicit M04 V6 finite spatial capture',coordinator=dict(pid=me.pid,createTime=me.create_time()),job=str(path),jobSha256=sha(path),gpuBefore=before,foreignProcessesChanged=False,observations=[])
    with LEASE.open('x',encoding='utf8') as f:json.dump(record,f,indent=2)
    out=Path(job['outputDirectory']);log=out/('sample-editor.log' if args.sample else 'capture-editor.log')
    try:
        command=[str(UNITY),'-batchmode','-projectPath',str(ISO),'-force-d3d11','-job-worker-count','2','-background-job-worker-count','1','-executeMethod','YamyamCoding.GameMath.EulerAxisAngle.V6.Editor.EulerV6Capture.Run','-m04V6Job',str(path),'-logFile',str(log)]
        proc=subprocess.Popen(command,cwd=ROOT,creationflags=subprocess.CREATE_NO_WINDOW)
        identity=psutil.Process(proc.pid)
        record['unity']=dict(pid=proc.pid,createTime=identity.create_time(),project=str(ISO),log=str(log),argumentsContainTokens=False)
        (out/'spatial-process.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf8')
        print(json.dumps(dict(status='running',pid=proc.pid,log=str(log))),flush=True)
        start=time.monotonic()
        while proc.poll() is None:
            if time.monotonic()-start>args.timeout:
                identity.terminate();proc.wait(timeout=30);raise RuntimeError('Own V6 capture timed out; only the recorded own process was terminated.')
            record['observations'].append(dict(elapsedSeconds=round(time.monotonic()-start,2),ownUnityDedicatedMiB=dedicated_mib(proc.pid),**gpu()))
            time.sleep(5)
        record['exitCode']=proc.returncode;record['gpuAfter']=gpu();record['ownEditorExited']=not identity.is_running()
        own=[s['ownUnityDedicatedMiB'] for s in record['observations'] if s['ownUnityDedicatedMiB'] is not None]
        record['ownUnityPeakDedicatedMiB']=max(own) if own else None
        record['vramMeasurement']='Windows WDDM dedicated GPU memory counter for exact own Unity PID' if own else 'Per-process counter unavailable; only total GPU observations recorded, no own-VRAM claim'
        if proc.returncode:raise RuntimeError('V6 Unity exited '+str(proc.returncode)+'; inspect owned log.')
        record['captureSuccess']=json.loads((out/'capture-success.json').read_text())
        actual=[]
        for c in job['clips']:
            files={kind:out/(c['shotId']+suffix) for kind,suffix in [('clip','.mp4'),('firstFrame','.first.png'),('lastFrame','.last.png'),('anchors','.anchors.ndjson')]}
            for f in files.values():
                if not f.exists():raise RuntimeError('V6 capture output is missing: '+str(f))
            n=sum(1 for _ in files['anchors'].open(encoding='utf8'))
            probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,avg_frame_rate,nb_frames','-of','json',str(files['clip'])],text=True))['streams'][0]
            if n!=c['frames'] or int(probe['nb_frames'])!=c['frames'] or [probe['width'],probe['height']]!=[1920,1080] or probe['avg_frame_rate']!='60/1':raise RuntimeError('V6 clip/anchors fail the exact FHD60 frame contract.')
            actual.append(dict(id=c['shotId'],frames=n,probe=probe,files={k:dict(path=str(v),sha256=sha(v)) for k,v in files.items()}))
        receipt=dict(schemaVersion=1,jobSha256=sha(path),sampleOnly=args.sample,outputs=actual,ownEditorExited=record['ownEditorExited'],fullDecodePerformed=False,visualReview='pending native/mobile inspection',sourceMath='left-handed,row,object-to-upright; native engine transpose',timelineSha256=sha(Path(args.timeline)) if not args.sample else None)
        (out/'spatial-capture-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
        if args.sample:
            shared=LOCAL/'spatial-clips';shared.mkdir(exist_ok=True)
            shutil.copy2(out/'testbed-still.png',shared/'testbed-still.png')
            record['sharedTestbedStill']=dict(file=str(shared/'testbed-still.png'),sha256=sha(shared/'testbed-still.png'),source='same aircraft/camera in neutral identity pose; axes/active arc hidden for parent2D background; not a full production timing approval')
        return 0
    finally:
        if proc is not None and proc.poll() is None:
            try:
                owner=psutil.Process(proc.pid)
                if owner.create_time()==record['unity']['createTime']:owner.terminate();proc.wait(timeout=30)
            except psutil.NoSuchProcess:pass
        record['finishedAt']=time.time();(out/'spatial-process.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf8')
        if LEASE.exists() and json.loads(LEASE.read_text(encoding='utf-8-sig')).get('token')==token:
            history=ROOT/'shared/output/gpu-handoff';history.mkdir(exist_ok=True)
            (history/(token+'.json')).write_text(json.dumps(record,indent=2)+'\n',encoding='utf8');LEASE.unlink()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--timeline',default=str(H/'timeline.json'));ap.add_argument('--scene',action='append');ap.add_argument('--sample',action='store_true');ap.add_argument('--bake',action='store_true');ap.add_argument('--run',action='store_true');ap.add_argument('--timeout',type=int,default=3600);args=ap.parse_args()
    path,job=prepare(args);print(json.dumps(dict(job=str(path),clips=len(job['clips']),frames=sum(c['frames'] for c in job['clips']),launched=args.run)),flush=True)
    return run(path,job,args) if args.run else 0

if __name__=='__main__':sys.exit(main())
