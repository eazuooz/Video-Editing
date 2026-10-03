"""Additional normal-speed source bank for post-narration cut fitting."""
import json, subprocess
from pathlib import Path
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'production/batches/sakurai-planning-game-design/preflight/proof-motion-sickness-games/game-research/PF5L_2g9UVQ.mp4'
OUT=Path(__file__).resolve().parent/'source-action-review/pws-reserves'
OUT.mkdir(parents=True,exist_ok=True)
TIMES=sorted(set(list(range(199,291,3))+list(range(310,339,2))+list(range(345,553,4))))
for t in TIMES:
 subprocess.run(['ffmpeg','-v','error','-threads','2','-ss',str(t),'-i',str(SOURCE),'-frames:v','1','-vf','scale=480:270','-q:v','2','-y',str(OUT/f'{t:04}.jpg')],check=True)
for page in range((len(TIMES)+11)//12):
 sheet=Image.new('RGB',(1440,1208),'white');d=ImageDraw.Draw(sheet)
 for j,t in enumerate(TIMES[page*12:(page+1)*12]):
  x,y=(j%3)*480,(j//3)*302;sheet.paste(Image.open(OUT/f'{t:04}.jpg'),(x,y));d.text((x+8,y+277),f'PWS {t}s',fill='black')
 sheet.save(OUT/f'contact-{page+1}.jpg',quality=93)
(OUT/'index.json').write_text(json.dumps({'sourceId':'PF5L_2g9UVQ','sampleSeconds':TIMES,'manualReview':'pending','finalCutApproval':False},indent=2)+'\n','utf-8')
print(len(TIMES),'reserve source frames ready',flush=True)
