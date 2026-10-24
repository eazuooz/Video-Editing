"""Finish specified successful composites; human review stays pending."""
import json,subprocess,time,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
for arg in sys.argv[1:]:
 slug,mode=arg.split(':');p=R/'projects'/slug;execution=p/f'production/local/motion-{mode}-execution.json';deadline=time.monotonic()+1800
 while not (p/f'production/local/render-{mode}-verified.json').exists():
  assert time.monotonic()<deadline,'Render wait expired';time.sleep(10)
 d=json.loads(execution.read_text(encoding='utf8'));assert d['done'] and d['result']==0 and not d['errors']
 print('ENCODE_START',slug,mode,flush=True)
 for command in ['pair','integrity','qa']:
  cmd=[sys.executable,'-X','utf8',str(p/'production/finish-video.py'),command]
  if command=='pair':cmd+=['--visual',str(R/f'shared/output/motion-canvas/{slug}-{mode}.mp4')]
  with (p/f'production/local/finish-{mode}-{command}.log').open('w',encoding='utf8') as log:subprocess.run(cmd,cwd=R,stdout=log,stderr=subprocess.STDOUT,check=True)
 subprocess.run([sys.executable,'-X','utf8',str(B/'package-reviews.py'),slug],check=True,cwd=R)
 print('ENCODE_DONE',slug,flush=True)
