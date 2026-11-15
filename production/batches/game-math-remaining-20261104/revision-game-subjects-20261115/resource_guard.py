"""This finite video revision may coexist with a verified Null-device CPU test.

All GPU leases, games, model jobs, media encodes, actual Unity/UE renders and
memory/utilization thresholds remain enforced. No other process is changed.
"""
import json,subprocess,time
from pathlib import Path
from types import SimpleNamespace
import psutil


def wrapper(base,receipt):
 def idle_reason(own=None):
  reason=base.idle_reason(own)
  if reason!='Other Unity batch job still running':return reason
  permitted=[]
  for process in psutil.process_iter(['pid','name','exe','cmdline']):
   info=process.info;name=(info['name'] or '').lower();exe=(info['exe'] or '').replace('\\','/').lower();args=info['cmdline'] or [];lower=[x.lower() for x in args]
   if '/steamapps/common/' in exe or name in ('overwatch.exe','d2r.exe'):return 'Game process still running'
   if name=='unity.exe' and '-batchmode' in lower:
    if '-name' in lower and lower[lower.index('-name')+1].startswith('assetimportworker'):continue
    method=args[lower.index('-executemethod')+1] if '-executemethod' in lower else None
    log=Path(args[lower.index('-logfile')+1]) if '-logfile' in lower else None
    text=log.read_text(encoding='utf8',errors='replace') if log and log.is_file() else ''
    if not ('-nographics' in lower and method=='LunaValidation.ContentMatrix' and 'Renderer: Null Device' in text):return 'Other Unity batch job still running'
    permitted.append(dict(pid=info['pid'],method=method,nographics=True,observedGraphics='Renderer: Null Device',processChanged=False))
   if name=='unrealeditor.exe' and any(x.startswith('-moviepipeline') or x=='-renderoffscreen' for x in lower):return 'Other Unreal render still running'
   if name.startswith('python') and any(k in ' '.join(lower) for k in ('--synthesize','render_narration','review-source-voice.py','faster_whisper','torchrun')):return 'Other model job still running'
   if name=='ffmpeg.exe':return 'Other media encode still running'
  try:
   if base.LEASE.exists() and json.loads(base.LEASE.read_text(encoding='utf8')).get('id')!=own:return 'Another scoped GPU job holds the lease'
  except (PermissionError,json.JSONDecodeError):return 'Shared lease is being updated; retry without changing ownership'
  samples=[]
  for _ in range(3):
   result=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True,creationflags=base.CREATE)
   free,use=map(int,result.splitlines()[0].split(','));samples.append([free,use]);time.sleep(.4)
  receipt.parent.mkdir(parents=True,exist_ok=True);receipt.write_text(json.dumps(dict(scope='Current M21–M33 local game-subject revision only',permittedConcurrentCpuValidation=permitted,gpuSamples=samples,otherProcessesUnchanged=True),ensure_ascii=False,indent=2),encoding='utf8')
  if any(free<8192 or use>35 for free,use in samples):return f'Insufficient idle headroom: {samples}'
  return None
 return SimpleNamespace(LEASE=base.LEASE,now=base.now,release_lease=base.release_lease,idle_reason=idle_reason)
