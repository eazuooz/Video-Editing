"""Continue the one already-running render into local encode/QA, never upload.

Usage: python production/ai-game-development-human-craft/finish-local.py --render-pid PID
This is a bounded foreground production job, not a recurring automation.
"""
from pathlib import Path
import argparse,ctypes,time,json,subprocess,datetime,sys,concurrent.futures
ROOT=Path(__file__).resolve().parents[2];SLUG='ai-game-development-human-craft';OUT=ROOT/'shared/output'/SLUG
p=argparse.ArgumentParser();p.add_argument('--render-pid',type=int,required=True);p.add_argument('--qa-only',action='store_true');args=p.parse_args()
kernel=ctypes.windll.kernel32;kernel.OpenProcess.restype=ctypes.c_void_p;kernel.WaitForSingleObject.argtypes=[ctypes.c_void_p,ctypes.c_ulong];kernel.CloseHandle.argtypes=[ctypes.c_void_p]
handle=kernel.OpenProcess(0x100000,False,args.render_pid)
status=OUT/'finish-local-status.json'
def record(stage,state):status.write_text(json.dumps({'stage':stage,'state':state,'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'selectedVideo':SLUG},indent=2)+'\n')
def selected():
 c=json.loads((ROOT/'shared/publishing/video-production-control.json').read_text(encoding='utf-8-sig'));assert c['selectedVideo']==SLUG and c['newProductionAuthorization']['fullProductionAuthorized']
try:
 selected();record('waiting-for-current-render','running');deadline=time.monotonic()+7200
 while handle and kernel.WaitForSingleObject(handle,0)==258:
  assert time.monotonic()<deadline,'Bounded render wait expired';time.sleep(5)
 if handle:kernel.CloseHandle(handle);handle=None
 for i in range(1,29):assert (OUT/'composite'/f'{i:02}'/'render.json').exists(),f'Render incomplete: {i:02}'
 py=str(ROOT/'qwen3-tts/.venv/Scripts/python.exe');base=f'production/{SLUG}/'
 steps=[('assemble',['python',base+'assemble-video.py']),('burn-captions',['node','motion-canvas/scripts/caption-ai-production.cjs','--burn']),('encoded-integrity',[py,base+'check-delivery.py']),('caption-pixels',[py,base+'check-caption-pixels.py']),('aligned-final-audio',[py,base+'inspect-audio.py']),('encoded-motion-evidence',['python',base+'extract-motion-review.py'])]
 def execute(stage,command):
  selected();record(stage,'running');print(stage,flush=True)
  with (OUT/(stage+'.log')).open('wb') as log:subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 if args.qa_only:
  # Existing finished clean/captioned files are immutable during these reads.
  # Full integrity, pixels and motion are independent; audio reuse needs the
  # completed integrity receipt and therefore runs afterwards.
  with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
   futures=[pool.submit(execute,*steps[i]) for i in [2,3,5]]
   for f in futures:f.result()
  execute(*steps[4])
 else:
  for stage,command in steps:execute(stage,command)
 record('await-direct-current-visual-review','technical-jobs-complete');print('Local jobs complete; direct visual review and delivery still required.',flush=True)
except Exception as e:
 record('failed',str(e));raise
finally:
 if handle:kernel.CloseHandle(handle)
