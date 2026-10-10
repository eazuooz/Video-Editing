"""Local, reproducible source-pixel grids for editable observation anchors."""
from pathlib import Path
import json,subprocess
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
D=ROOT/'shared/output/game-math-part2-teaching-revision/lines-observation-frames';D.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',15)
SAM='shared/output/game-math-part2-full-series/sources/4s7nMfXt8uQ.mp4'
UNCLE='shared/output/game-math-part2-full-series/sources/SSekdYTL4Ck.mp4'
jobs=[
 ('portal-cube','shared/output/game-math-part2-full-series/sources/portal2-steam-5787.mp4',[70,72,74,75.5,76,76.5,77,77.5,78,78.5,79,79.5,80,80.5,81,81.5,82,83,84,85,86,87]),
 ('portal-laser','shared/output/game-math-part2-full-series/sources/yFRbGppLaUI.mp4',[40,42,44,46,48,50,52,54,72,74,76,78,80,82,84]),
 ('gray-turn',SAM,[665,666,667,668,669,670,671,672,673,674,675]),
 ('blue-head',SAM,[633,635,637,639,641,643,645,647,649,731,732,733,734,735,736,737,738]),
 ('house',SAM,[560,561,562,563,564,565,566,567,569,571,652,654,656,658,660,662,664,723,724,725,726,727,728,729,730]),
 ('posts',UNCLE,[1205,1209,1213,1217,1221,1225,1229,1233,1237,1241,1245,1249,1253,1257,1261,1265]),
]
base=json.loads((B/'baselines/game-math-lines-bounds/production/timeline.json').read_text(encoding='utf8'))
for s in base['scenes']:
 if s['id'] in ['02','05','08','10','13','16','21']:
  jobs.append((s['id'],f'shared/output/game-math-lines-bounds/clips/{s["id"]}.mp4',list(range(0,int(s['seconds']),4))))
for ident,relative,times in jobs:
 frames=[]
 for t in times:
  path=D/f'{ident}-{t:g}.png'
  if not path.exists():
   subprocess.run(['ffmpeg','-v','error','-y','-threads','1','-ss',str(t),'-i',str(ROOT/relative),'-frames:v','1','-vf','scale=800:450',str(path)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
  frames.append((t,Image.open(path).convert('RGB')))
 for page in range((len(frames)+7)//8):
  sheet=Image.new('RGB',(1600,1880),'white');draw=ImageDraw.Draw(sheet)
  for j,(time,frame) in enumerate(frames[page*8:page*8+8]):
   x=j%2*800;y=j//2*470;draw.text((x+5,y),f'{ident} · source {time:g}s · coordinates800×450',fill='black',font=font);sheet.paste(frame,(x,y+20))
  sheet.save(D/f'{ident}-sheet-{page+1:02}.jpg',quality=95)
 print(ident,len(frames),flush=True)
