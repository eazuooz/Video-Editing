"""One finite M21 image preflight job. Wait for the user's game to end.

This does not create a chat automation, synthesize speech, upload, or advance
to another lecture. It exits after these explicitly listed previews or a failure.
"""
from pathlib import Path
import argparse,datetime,json,os,subprocess,time,uuid,importlib.util
import psutil

S=Path(__file__).resolve().parent
ROOT=S.parents[3]
LEASE=ROOT/'shared/output/GPU_HANDOFF.json'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def resource_reason():
    # Reuse the current selected-project guard, including proved idle GUI editors.
    # The historical blanket editor-process ban must not stall a finite preview.
    spec=importlib.util.spec_from_file_location('current_capture_guard',S.parent/'run-capture-queue.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.idle_reason()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--job-folder',required=True);ap.add_argument('--wait-hours',type=float,default=6);args=ap.parse_args()
    folder=Path(args.job_folder).resolve();assert folder.parent==S and folder.name.startswith('local-preflight-')
    manifest=read(folder/'queue.json');marker=read(Path(manifest['sandbox'])/'M21_SANDBOX.json')
    assert marker['fingerprint']==manifest['fingerprint']
    if (folder/'progress.json').exists():
        old=read(folder/'progress.json')
        if old.get('createTime'):
            try:assert abs(psutil.Process(old['pid']).create_time()-old['createTime'])>.1,'Same finite preflight already running'
            except psutil.NoSuchProcess:pass
        assert old.get('status')!='images-ready-for-internal-visual-QA','Completed preflight must not be repeated unchanged'
    state={'pid':os.getpid(),'createTime':psutil.Process().create_time(),'status':'waiting-for-idle-resources','completed':[],'failed':[],'finalVideo':False,'nextEpisode':False}
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
