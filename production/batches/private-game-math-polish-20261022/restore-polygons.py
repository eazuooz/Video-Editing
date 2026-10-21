"""Finite source recovery after the existing serial queue; no TTS or QA autopass."""
import ctypes,ctypes.wintypes as wt,datetime,time,sys,ast
from polish_common import *
e=Episode('M13');e.authorized();lock=e.O/'polygon-restoration.lock'
fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.write(fd,str(os.getpid()).encode());os.close(fd)
status=B/'polygon-restoration-job.json';results={};handle=None
def report(stage,**extra):
 save(status,{'pid':os.getpid(),'updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stage':stage,'results':results,'newTts':False,'platformMutation':False,'visualApprovalGranted':False,**extra})
try:
 if '--after-pid' in sys.argv:
  pid=int(sys.argv[sys.argv.index('--after-pid')+1]);actual=subprocess.check_output(['powershell','-NoProfile','-Command',f"(Get-CimInstance Win32_Process -Filter 'ProcessId={pid}').CommandLine"],text=True).strip()
  if actual:
   assert 'continue-restoration.py' in actual,('Dependency is another job',pid)
   kernel=ctypes.WinDLL('kernel32',use_last_error=True);kernel.OpenProcess.argtypes=[wt.DWORD,wt.BOOL,wt.DWORD];kernel.OpenProcess.restype=wt.HANDLE
   kernel.WaitForSingleObject.argtypes=[wt.HANDLE,wt.DWORD];kernel.WaitForSingleObject.restype=wt.DWORD;kernel.CloseHandle.argtypes=[wt.HANDLE];kernel.CloseHandle.restype=wt.BOOL
   handle=kernel.OpenProcess(0x00100000,False,pid);assert handle
   report('waiting-for-existing-sequential-queue',dependencyPid=pid)
   print('Waiting for the current serial queue; no duplicate production',flush=True)
   while kernel.WaitForSingleObject(handle,0)==258:e.authorized();time.sleep(15)
 for ident in ['M13','M14']:
  ep=Episode(ident)
  try:
   ep.authorized();plan=read(ep.H/'reconstruction-plan.json');preflight=read(ep.H/'reconstruction-preflight.json')
   assert preflight['directInspection']=='passed-still-preflight-only'
   assert preflight['sourceSha256']==sha(B/'polygon-scenes.py')
   assert plan['timelineSha256']==sha(ep.P/'production/timeline.json')
   env=dict(os.environ,PYTHONUTF8='1',POLISH_SLUG=ep.slug,MATH_RENDER_TIMING=str(ep.P/'production/timeline.json'),OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1')
   files=[B/'polygon-scenes.py',R/'manim/projects/game-math-part2-full-series/geometry_polygons.py',R/'manim/projects/game-math-part2-full-series/lesson.py',ep.P/'production/timeline.json',ep.P/'production/lesson.json']
   provenance={rel(p):sha(p) for p in files};signature=hashlib.sha256(json.dumps(provenance,sort_keys=True).encode()).hexdigest()
   target=ep.H/'explanation-restoration.json';record=read(target) if target.exists() else {'scenes':{}}
   for slot in ep.T['scenes']:
    if slot['classification']!='explanation':continue
    ep.authorized();sid=slot['id'];dst=ep.O/f'manim/videos/polygon-scenes/1080p60/Polish{sid}.mp4'
    old=record['scenes'].get(sid,{})
    if dst.exists() and old.get('signature')==signature and old.get('sha256')==sha(dst):continue
    report('rendering-original-clock',episode=ident,scene=sid)
    ep.run([R/'manim/.venv/Scripts/python.exe','-m','manim','--resolution','1920,1080','--fps','60','--disable_caching','--media_dir',ep.O/'manim',B/'polygon-scenes.py','Polish'+sid],f'manim-{sid}.log',env=env)
    assert all(sha(R/p)==h for p,h in provenance.items()),'Source changed during render'
    v=video(dst);assert (v['width'],v['height'],v['r_frame_rate'])==(1920,1080,'60/1')
    assert abs(int(v['nb_frames'])-slot['frames'])<=4
    record['scenes'][sid]={'signature':signature,'path':rel(dst),'sha256':sha(dst),'originalSceneSeconds':slot['seconds'],'restorationType':'original-program' if sid.isdigit() else 'baseline-referenced-missing-code-reconstruction','visualQa':'pending-moving-output-review'}
    record['sourceCode']=provenance;save(target,record);print(ident,sid,'source restored; moving QA pending',flush=True)
   report('normalizing-original-frame-counts',episode=ident)
   ep.run([sys.executable,'-X','utf8',B/'normalize-explanations.py',ident],'normalize-polygons.log')
   blockers=read(B/'source-blockers.json')
   if blockers.get(ident,{}).get('type')=='missing-original-addition-module':
    resolved=blockers.pop(ident);save(ep.H/'resolved-code-restoration-blocker.json',{'previous':resolved,'resolution':'Original numeric program reused; missing supplementary visuals reconstructed from viewed baseline and exact retained cues','sourceSha256':sha(B/'polygon-scenes.py'),'movingReview':'pending'})
    save(B/'source-blockers.json',blockers)
   results[ident]={'status':'explanations-restored-normalized-await-moving-visual-review'}
  except Exception as error:results[ident]={'status':'needs-repair','error':str(error)[-2500:]};print(ident,'restoration issue:',str(error)[-500:],flush=True)
  report('episode-restoration-finished',episode=ident)
 e.run([sys.executable,'-X','utf8',B/'progress.py'],'polygon-progress.log');report('source-restoration-finished-annotation-and-final-review-pending')
except Exception as error:report('failed',error=str(error)[-2500:]);raise
finally:
 if handle:kernel.CloseHandle(handle)
 if lock.exists() and lock.read_text()==str(os.getpid()):lock.unlink()
