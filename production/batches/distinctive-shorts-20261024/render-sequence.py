"""One Motion Canvas exporter per server. Verify actual files, not UI status alone."""
from pathlib import Path
import json,time,subprocess,os
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
JOBS=[('shorts-titanfall-time-shift','distinctive-v3-full'),('shorts-ghost-leaf-updraft','distinctive-v2-full'),('shorts-gears-inertialization','distinctive-v1-full'),('shorts-portal-recursion','distinctive-v1-full'),('shorts-superliminal-perspective','distinctive-v1-full')]
lock=B/'local/motion-export.lock'
with lock.open('x') as f:f.write(str(os.getpid()))
try:
 for slug,mode in JOBS:
  p=R/'projects'/slug;deadline=time.monotonic()+3600
  while True:
   timingPath=p/'production/visual-timing.json'
   if timingPath.exists():
    timing=json.loads(timingPath.read_text(encoding='utf8'));capture=p/('production/local/capture-'+timing['captureMode']+'/success.json')
    if capture.exists() and json.loads(capture.read_text())['frames']==timing['frames']:break
   assert time.monotonic()<deadline,'Native-render wait expired';time.sleep(10)
  print('MOTION_START',slug,mode,flush=True)
  with (p/f'production/local/render-{mode}.log').open('w',encoding='utf8') as log:subprocess.run(['node',str(p/'production/render-visual.cjs'),mode],cwd=R,stdout=log,stderr=subprocess.STDOUT,check=True)
  file=R/f'shared/output/motion-canvas/{slug}-{mode}.mp4'
  probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,nb_frames,r_frame_rate','-of','json',str(file)]))['streams'][0]
  assert (probe['width'],probe['height'],probe['r_frame_rate'],int(probe['nb_frames']))==(1080,1920,'60/1',timing['frames'])
  (p/f'production/local/render-{mode}-verified.json').write_text(json.dumps(probe,indent=2)+'\n',encoding='utf8');print('MOTION_DONE',slug,flush=True)
finally:lock.unlink()
