"""Extract exact game evidence for the six native tool-summary slides."""
from pathlib import Path
import json, subprocess, hashlib, shutil
R=Path(__file__).resolve().parents[3];P=R/'projects/ai-games-showcase-2026'
O=P/'production/local/tool-slides';O.mkdir(parents=True,exist_ok=True)
plan=json.loads((P/'planning/production-plan.json').read_text(encoding='utf-8-sig'))
receipts=[]
for scene in plan['scenes']:
 card=scene.get('developmentSummary')
 if not card:continue
 source=R/card['frameSource'];output=O/card['frame']
 if source.suffix.lower()=='.png':shutil.copy2(source,output)
 else:subprocess.run(['ffmpeg','-v','error','-y','-ss',str(card['sourceTime']),'-i',str(source),'-frames:v','1','-vf','scale=1920:1080','-threads','2',str(output)],check=True)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','json',str(output)]))['streams'][0]
 assert probe=={'width':1920,'height':1080},probe
 receipts.append({'game':card['game'],'source':card['frameSource'],'sourceSecond':card['sourceTime'],'output':str(output.relative_to(R)).replace('\\','/'),'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'dimensions':probe})
(O/'frame-receipts.json').write_text(json.dumps(receipts,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'frames':len(receipts),'directory':str(O)}))
