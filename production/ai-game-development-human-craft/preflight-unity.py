from pathlib import Path
import time,json
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'shared/output/ai-game-development-human-craft/unity-production';REQ=ROOT/'unity/VideoEditing/Library/AiCraftProduction.request'
plan=json.loads((Path(__file__).parent/'capture-plan.json').read_text())
for s in plan['scenes']:
 if s['id'] not in ['02','09','17','18','20','23','25','28']:continue
 assert not REQ.exists(),'Pending editor request'
 status=OUT/s['id']/'preflight-status.txt';start=time.time()
 REQ.write_text(json.dumps({'command':'preflight','scene':s['id'],'frames':s['seconds']*60,'fps':60}),encoding='utf-8')
 while not status.exists() or status.stat().st_mtime<start:
  if time.time()-start>120:raise TimeoutError(s['id'])
  time.sleep(.5)
 assert status.read_text()=='complete',status.read_text()
 print('Preflight '+s['id'],flush=True)
