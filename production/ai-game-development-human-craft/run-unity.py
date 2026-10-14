"""Sequential editor captures after the current narration GPU lease releases."""
from pathlib import Path
import json,time,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[2];SLUG='ai-game-development-human-craft'
OUT=ROOT/'shared/output'/SLUG/'unity-production';REQ=ROOT/'unity/VideoEditing/Library/AiCraftProduction.request'
plan=json.loads((Path(__file__).parent/'capture-plan.json').read_text())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def selected():
 c=json.loads((ROOT/'shared/publishing/video-production-control.json').read_text(encoding='utf-8-sig'))
 assert c['selectedVideo']==SLUG and c['newProductionAuthorization']['fullProductionAuthorized']
status={'status':'waiting-for-narration-gpu-release','completed':[]}
def save():(OUT/'job-status.json').write_text(json.dumps(status,indent=2)+'\n')
selected();save()
while (ROOT/'shared/output/GPU_HANDOFF.json').exists():time.sleep(3)
assert json.loads((ROOT/'shared/output'/SLUG/'narration-job/status.json').read_text())['status']=='complete-pending-content-review','Finish/review narration job failure before rendering'
try:
 for s in plan['scenes']:
  selected();d=OUT/s['id'];d.mkdir(parents=True,exist_ok=True)
  sources=list((ROOT/'unity/VideoEditing/Assets/AiCraftProduction').glob('*.cs'))+list((ROOT/'unity/VideoEditing/Assets/Editor').glob('AiCraft*.cs'))+list((ROOT/'unity/VideoEditing/Assets/VideoScenes'/SLUG).glob(s['id']+'-*.unity'))
  stamp={'sourceHashes':{p.relative_to(ROOT).as_posix():digest(p) for p in sources},'frames':s['seconds']*60,'fps':60}
  receipt=d/'render-input.json';movie=d/'unity.mp4';result=d/'render-status.txt'
  if movie.exists():
   assert receipt.exists() and json.loads(receipt.read_text())==stamp and result.read_text()=='complete','Existing capture differs; preserve it and use an explicit revision'
  else:
   assert not REQ.exists(),'Editor already has a pending request'
   receipt.write_text(json.dumps(stamp,indent=2)+'\n');status.update(status='rendering',scene=s['id']);save()
   REQ.write_text(json.dumps({'command':'render','scene':s['id'],'frames':stamp['frames'],'fps':60}),encoding='utf-8')
   started=time.time()
   while not result.exists():
    if time.time()-started>1800:raise TimeoutError('Unity scene '+s['id'])
    time.sleep(2)
   assert result.read_text()=='complete',result.read_text()
  capture=json.loads((d/'render-capture.json').read_text());assert len(capture['timeline'])==stamp['frames']
  subprocess.run(['ffmpeg','-v','error','-i',str(movie),'-f','null','-'],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
  status['completed'].append(s['id']);save();print('Completed '+s['id'],flush=True)
 status.update(status='complete-pending-visual-review');save()
except BaseException as e:
 status.update(status='failed',error=str(e));save();raise
