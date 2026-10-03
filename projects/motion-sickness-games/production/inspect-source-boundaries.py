"""One-second source action inspection, not final caption/cut approval."""
import json, subprocess
from pathlib import Path
from PIL import Image, ImageDraw
ROOT = Path(__file__).resolve().parents[3]
PROOF = ROOT / 'production/batches/sakurai-planning-game-design/preflight/proof-motion-sickness-games/game-research'
OUT = Path(__file__).resolve().parent / 'source-action-review'
OUT.mkdir(parents=True, exist_ok=True)
SETS = {
 '6slinvkF0Rs': list(range(16,43)) + list(range(46,54)),
 'PF5L_2g9UVQ': list(range(118,133)) + list(range(153,170)) + list(range(301,310)) + list(range(546,559))
}
for source_id, times in SETS.items():
 folder = OUT/source_id
 folder.mkdir(exist_ok=True)
 for t in times:
  subprocess.run(['ffmpeg','-v','error','-threads','2','-ss',str(t),'-i',str(PROOF/f'{source_id}.mp4'),'-frames:v','1','-vf','scale=480:270','-q:v','2','-y',str(folder/f'{t:04}.jpg')],check=True)
 for page in range((len(times)+11)//12):
  sheet=Image.new('RGB',(1440,1208),'white'); d=ImageDraw.Draw(sheet)
  for j,t in enumerate(times[page*12:(page+1)*12]):
   x,y=(j%3)*480,(j//3)*302
   sheet.paste(Image.open(folder/f'{t:04}.jpg'),(x,y))
   d.text((x+8,y+277),f'{source_id}  {t}s',fill='black')
  sheet.save(folder/f'contact-{page+1}.jpg',quality=93)
 (folder/'index.json').write_text(json.dumps({'sourceId':source_id,'sampleSeconds':times,'manualReview':'pending','finalCutApproval':False},indent=2)+'\n','utf-8')
 print(source_id,len(times),'source boundary frames ready',flush=True)
