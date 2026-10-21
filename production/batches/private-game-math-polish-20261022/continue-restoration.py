"""One finite sequential queue after current jobs; does not grant visual approval."""
import ctypes,ctypes.wintypes as wt,datetime,time,sys
from polish_common import *
dependencies={23732:'finish-M05-technical.py',42724:'restore-lessons.py M07 M08 M09 M10 M11 M12 M15 M16 M17 M18 M19 M20'}
e=Episode('M06');e.authorized();status=B/'remaining-restoration-job.json'
lock=e.O/'remaining-restoration.lock'
fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.write(fd,str(os.getpid()).encode());os.close(fd)
kernel=ctypes.WinDLL('kernel32',use_last_error=True)
kernel.OpenProcess.argtypes=[wt.DWORD,wt.BOOL,wt.DWORD];kernel.OpenProcess.restype=wt.HANDLE
kernel.WaitForSingleObject.argtypes=[wt.HANDLE,wt.DWORD];kernel.WaitForSingleObject.restype=wt.DWORD
kernel.CloseHandle.argtypes=[wt.HANDLE];kernel.CloseHandle.restype=wt.BOOL
handles=[];results={}
def record(stage,**extra):
 save(status,{'pid':os.getpid(),'updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stage':stage,'dependencies':dependencies,'results':results,'visualApprovalGranted':False,'platformMutation':False,'newTts':False,**extra})
def run(episode,script,args=None):
 episode.authorized();record('running',episode=episode.id,script=script)
 episode.run([sys.executable,'-X','utf8',B/script,*(args if args is not None else [episode.id])],f'queue-{script}.log')
 print(episode.id,script,'finished; direct visual review still pending',flush=True)
try:
 for pid,needle in dependencies.items():
  actual=subprocess.check_output(['powershell','-NoProfile','-Command',f"(Get-CimInstance Win32_Process -Filter 'ProcessId={pid}').CommandLine"],text=True).strip()
  if not actual:continue
  assert needle in actual,('Dependency PID belongs to another command',pid)
  handle=kernel.OpenProcess(0x00100000,False,pid)
  if handle:handles.append(handle)
 record('waiting-for-existing-render-and-M05-technical')
 print('Finite queue waiting for existing jobs; no duplicate render or process termination',flush=True)
 while any(kernel.WaitForSingleObject(h,0)==258 for h in handles):
  e.authorized();time.sleep(15)
 try:
  for script in ['prepare-ui-clearance.py','build-composition-polish.py','assemble.py','technical-qa.py']:
   run(e,script)
  results['M06-technical']={'status':'technical-complete-await-final-moving-visual-review'}
 except Exception as error:results['M06-technical']={'status':'needs-repair','error':str(error)[-2000:]}
 for ident in ['M07','M08','M09','M10','M11','M12','M15','M16','M17','M18','M19','M20']:
  episode=Episode(ident)
  try:
   run(episode,'normalize-explanations.py');results[ident+'-normalize']={'status':'restored-not-visual-approved'}
  except Exception as error:results[ident+'-normalize']={'status':'needs-repair','error':str(error)[-2000:]}
  record('normalization-progress')
 # These original sources have verified FHD files. Low-resolution cases stay
 # pending the existing user question; missing additions do not block cuts.
 for ident in ['M13','M14','M15','M16','M18','M19','M20']:
  episode=Episode(ident)
  try:
   run(episode,'restore-gameplay.py')
   results[ident+'-gameplay']=read(B/'gameplay-restoration-status.json')[ident]
  except Exception as error:results[ident+'-gameplay']={'status':'needs-repair','error':str(error)[-2000:]}
  record('gameplay-restoration-progress')
 run(e,'progress.py',[]);record('finite-restoration-queue-finished-review-and-polish-pending')
except Exception as error:
 record('failed',error=str(error)[-2500:]);raise
finally:
 for handle in handles:kernel.CloseHandle(handle)
 if lock.exists() and lock.read_text()==str(os.getpid()):lock.unlink()
