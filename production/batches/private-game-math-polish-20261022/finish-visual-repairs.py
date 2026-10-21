"""Finite serial queue for inspected text repairs and observed overlays."""
import argparse,ctypes,ctypes.wintypes as wt,datetime,shutil,time,sys
from polish_common import *
parser=argparse.ArgumentParser();parser.add_argument('--episodes',nargs='+',choices=['M05','M06','M15','M16'],default=['M05','M15']);parser.add_argument('--after-pid',type=int)
options=parser.parse_args();ids=options.episodes
suffix='-'+'-'.join(ids) if options.after_pid else ''
status=B/f'visual-repair{suffix}-job.json';output=R/'shared/output/private-game-math-polish-20261022'
lock=output/f'visual-repair{suffix}-queue.lock';fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.write(fd,str(os.getpid()).encode());os.close(fd)
dependencies={options.after_pid:'finish-visual-repairs.py'} if options.after_pid else {85416:'continue-restoration.py',46192:'restore-polygons.py'}
kernel=ctypes.WinDLL('kernel32',use_last_error=True)
kernel.OpenProcess.argtypes=[wt.DWORD,wt.BOOL,wt.DWORD];kernel.OpenProcess.restype=wt.HANDLE
kernel.WaitForSingleObject.argtypes=[wt.HANDLE,wt.DWORD];kernel.WaitForSingleObject.restype=wt.DWORD
kernel.CloseHandle.argtypes=[wt.HANDLE];kernel.CloseHandle.restype=wt.BOOL
handles=[];results={}
def record(stage,**extra):
 save(status,{'pid':os.getpid(),'updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stage':stage,'dependencies':dependencies,'results':results,'newTts':False,'platformMutation':False,'visualApprovalGranted':False,**extra})
try:
 for ident in ids:Episode(ident).authorized()
 for pid,needle in dependencies.items():
  actual=subprocess.check_output(['powershell','-NoProfile','-Command',f"(Get-CimInstance Win32_Process -Filter 'ProcessId={pid}').CommandLine"],text=True).strip()
  if not actual:continue
  assert needle in actual,('PID now belongs to another process',pid)
  handle=kernel.OpenProcess(0x00100000,False,pid)
  if handle:handles.append(handle)
 record('waiting-for-existing-render-chain')
 while any(kernel.WaitForSingleObject(h,0)==258 for h in handles):
  for ident in ids:Episode(ident).authorized()
  time.sleep(15)
 for ident in ids:
  e=Episode(ident);e.authorized()
  if ident in ['M05','M06']:
   current=e.D/f'{e.slug}.captioned.mp4';digest=sha(current)
   assert digest==read(e.H/'supplement-spacing-preflight.json')['previousMasterSha256']
   archive=e.O/f'initial-encoded-{digest[:12]}';archive.mkdir(exist_ok=True)
   pixels=archive/'final-pixel-review'
   if not pixels.exists() and (e.O/'final-pixel-review').exists():shutil.copytree(e.O/'final-pixel-review',pixels)
   records=[]
   for src in [e.D/f'{e.slug}.{kind}' for kind in ['clean.mp4','captioned.mp4','ko.srt','en.srt']]+[e.H/f'{name}.json' for name in ['assembly','outputs','technical-qa','visual-review','final-pixel-samples']]:
    if not src.exists() and src.name=='final-pixel-samples.json':continue
    dst=archive/src.name
    if not dst.exists():shutil.copy2(src,dst)
    assert sha(src)==sha(dst);records.append({'path':rel(dst),'sha256':sha(dst)})
   save(e.H/'initial-encoded-preservation.json',{'captionedSha256':digest,'files':records,'pixelDirectory':rel(pixels) if pixels.exists() else None,'reason':'Preserve first encode and its failed spacing review before selective label repair'})
   tasks=[('assemble.py',[ident,'--supplement-spacing']),('technical-qa.py',[ident]),('review-final-pixels.py',[ident])]
  elif ident=='M16':
   tasks=[('render-camera-polish.py',[]),('prepare-observed-composition.py',[ident]),('apply-camera-composition.py',[]),('assemble.py',[ident]),('technical-qa.py',[ident]),('review-final-pixels.py',[ident])]
  else:
   tasks=[('prepare-observed-composition.py',['M15']),('assemble.py',['M15']),('technical-qa.py',['M15']),('review-final-pixels.py',['M15'])]
  for script,args in tasks:
   e.authorized();record('running',episode=ident,script=script)
   e.run([sys.executable,B/script,*args],'visual-repair-'+script+'.log')
  results[ident]='technical-complete-await-direct-final-visual-review'
  e.run([sys.executable,B/'progress.py'],'visual-repair-progress.log')
 record('technical-complete-await-direct-final-visual-review')
except Exception as error:
 record('failed',error=str(error)[-3000:]);raise
finally:
 for handle in handles:kernel.CloseHandle(handle)
 if lock.exists() and lock.read_text()==str(os.getpid()):lock.unlink()
