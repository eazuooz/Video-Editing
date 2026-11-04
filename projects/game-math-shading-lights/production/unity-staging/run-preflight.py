"""One finite M21 image preflight job. Wait for the user's game to end.

This does not create a chat automation, synthesize speech, upload, or advance
to another lecture. It exits after these explicitly listed previews or a failure.
"""
from pathlib import Path
import argparse,datetime,json,os,subprocess,time,uuid
import psutil

S=Path(__file__).resolve().parent
ROOT=S.parents[3]
LEASE=ROOT/'shared/output/GPU_HANDOFF.json'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def resource_reason():
    if LEASE.exists():return 'existing GPU lease preserved'
    for proc in psutil.process_iter(['pid','name','exe','cmdline']):
        i=proc.info;name=(i.get('name') or '').lower();exe=(i.get('exe') or '').replace('\\','/').lower()
        if name in ('overwatch.exe','overwatch launcher.exe') or '/steamapps/common/' in exe:return 'game use has not ended'
        if name in ('ffmpeg.exe','blender.exe','unrealeditor.exe'):return 'another render or engine process is present'
        if name in ('python.exe','pythonw.exe') and proc.pid!=os.getpid():
            command=' '.join(i.get('cmdline') or []).lower()
            if any(x in command for x in ('--synthesize','render_narration','whisper','faster_whisper','torchrun')):return 'another GPU inference job is present'
        if name=='unity.exe':
            args=i.get('cmdline') or [];lower=[x.lower() for x in args]
            if '-projectpath' not in lower:return 'unclassified Unity process preserved'
            project=Path(args[lower.index('-projectpath')+1]).resolve()
            if project!=(ROOT/'unity/VideoEditing').resolve():return 'another Unity project is running'
            library=project/'Library';status=library/'AnimationGridV1.status.json'
            if not status.exists() or list(library.glob('*.request')) or list(library.glob('*.request.json')):return 'shared Unity is not proved idle'
            data=read(status)
            if data.get('status')!='complete' or data.get('completed')!=data.get('frames'):return 'shared Unity capture is active'
    result=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True,creationflags=subprocess.CREATE_NO_WINDOW).strip().splitlines()[0]
    free,use=[int(x.strip()) for x in result.split(',')]
    if free<8192 or use>15:return f'insufficient idle GPU headroom ({free} MiB free, {use}%)'
    return None

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--job-folder',required=True);ap.add_argument('--wait-hours',type=float,default=6);args=ap.parse_args()
    folder=Path(args.job_folder).resolve();assert folder.parent==S and folder.name.startswith('local-preflight-')
    manifest=read(folder/'queue.json');marker=read(Path(manifest['sandbox'])/'M21_SANDBOX.json')
    assert marker['fingerprint']==manifest['fingerprint']
    state={'pid':os.getpid(),'status':'waiting-for-idle-resources','completed':[],'failed':[],'finalVideo':False,'nextEpisode':False}
    started=time.monotonic();stable=0;owned=None
    save(folder/'progress.json',state)
    try:
      while True:
        control=read(ROOT/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104']
        if not control.get('productionAllowedNow') or 'game-math-shading-lights' not in control['projectSlugs']:raise RuntimeError('Selected production authorization changed; stop at safe boundary')
        reason=resource_reason();stable=stable+1 if reason is None else 0
        state.update(reason=reason,checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat());save(folder/'progress.json',state)
        if stable>=3:break
        if time.monotonic()-started>args.wait_hours*3600:raise RuntimeError('Resources did not become idle within the bounded wait; no job forced or terminated')
        time.sleep(30)
      owned=str(uuid.uuid4());LEASE.parent.mkdir(parents=True,exist_ok=True)
      with LEASE.open('x',encoding='utf-8') as file:json.dump({'owner':'game-math-shading-lights-preflight','id':owned,'pid':os.getpid(),'output':str(folder)},file)
      for entry in manifest['jobs']:
        control=read(ROOT/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104']
        if not control.get('productionAllowedNow'):raise RuntimeError('Production authorization changed')
        # Recheck game use before every expensive job. Once a Unity job has
        # begun, allow its safe completion; never kill another process.
        if any((p.info.get('name') or '').lower()=='overwatch.exe' for p in psutil.process_iter(['name'])):raise RuntimeError('Game resumed; remaining previews stay queued')
        if read(Path(manifest['sandbox'])/'M21_SANDBOX.json')['fingerprint']!=manifest['fingerprint']:raise RuntimeError('Sandbox source changed; refuse stale job')
        job=read(Path(entry));state.update(status='running-preflight',current=job['id']);save(folder/'progress.json',state)
        env=os.environ.copy();env['YAMYAM_M21_JOB']=entry
        log=folder/(job['id']+'.unity.log')
        process=subprocess.Popen([manifest['unity'],'-batchmode','-job-worker-count','2','-projectPath',manifest['sandbox'],'-executeMethod','Yamyam.GameMath.LightLab.LightLabCapture.Run','-logFile',str(log)],env=env,creationflags=subprocess.CREATE_NO_WINDOW)
        state['unityPid']=process.pid;save(folder/'progress.json',state)
        code=process.wait();result=Path(job['output'])/'capture-success.json'
        if code!=0 or not result.exists():state['failed'].append(job['id']);raise RuntimeError('Preflight failed; preserve log and diagnose before next preview')
        state['completed'].append(job['id']);save(folder/'progress.json',state)
      state.update(status='images-ready-for-internal-visual-QA',reason=None);save(folder/'progress.json',state)
    except Exception as error:
      state.update(status='blocked-or-failed',reason=str(error));save(folder/'progress.json',state)
      raise
    finally:
      if owned and LEASE.exists() and read(LEASE).get('id')==owned:LEASE.unlink()

if __name__=='__main__':main()
