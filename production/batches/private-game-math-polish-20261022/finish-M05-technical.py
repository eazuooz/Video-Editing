"""Finite dependency queue. Wait for existing renders; never terminate them."""
import ctypes,ctypes.wintypes as wt,sys,time,datetime
from polish_common import *
e=Episode('M05');e.authorized();status=e.H/'technical-finish-job.json'
dependencies={29516:'restore-quaternion-gameplay.py M06',42724:'restore-lessons.py M07 M08 M09 M10 M11 M12 M15 M16 M17 M18 M19 M20'}
kernel=ctypes.WinDLL('kernel32',use_last_error=True)
kernel.OpenProcess.argtypes=[wt.DWORD,wt.BOOL,wt.DWORD];kernel.OpenProcess.restype=wt.HANDLE
kernel.WaitForSingleObject.argtypes=[wt.HANDLE,wt.DWORD];kernel.WaitForSingleObject.restype=wt.DWORD
kernel.CloseHandle.argtypes=[wt.HANDLE];kernel.CloseHandle.restype=wt.BOOL
handles=[]
lock=e.O/'technical-finish.lock'
fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.write(fd,str(os.getpid()).encode());os.close(fd)
def record(stage,**extra):
 save(status,{'pid':os.getpid(),'updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stage':stage,'dependencies':dependencies,'newTts':False,'platformMutation':False,'humanReview':'pending',**extra})
try:
 for pid,needle in dependencies.items():
  cmd=f"(Get-CimInstance Win32_Process -Filter 'ProcessId={pid}').CommandLine"
  actual=subprocess.check_output(['powershell','-NoProfile','-Command',cmd],text=True).strip()
  if not actual:continue
  assert needle in actual,('PID now identifies another process; do not wait on it',pid)
  handle=kernel.OpenProcess(0x00100000,False,pid)
  if handle:handles.append(handle)
 record('waiting-for-existing-render-jobs')
 print('M05 final technical job waits for existing M06/lesson render processes; no process stopped',flush=True)
 while any(kernel.WaitForSingleObject(h,0)==258 for h in handles):
  e.authorized();time.sleep(15)
 for script in ['prepare-ui-clearance.py','build-composition-polish.py','assemble.py','technical-qa.py','progress.py']:
  e.authorized();record('running-'+script)
  args=[sys.executable,str(B/script)]+([] if script=='progress.py' else ['M05'])
  e.run(args,'technical-finish-'+script+'.log')
 record('technical-complete-await-direct-final-visual-review')
 print('M05 complete pair and technical QA generated; direct final moving pixel review still pending',flush=True)
except Exception as error:
 record('failed',error=str(error)[-2500:]);raise
finally:
 for h in handles:kernel.CloseHandle(h)
 # Only this invocation's exact small lock file is removed; no media touched.
 if lock.exists() and lock.read_text()==str(os.getpid()):lock.unlink()
