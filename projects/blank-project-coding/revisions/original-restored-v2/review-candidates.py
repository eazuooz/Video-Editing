from pathlib import Path
import json,subprocess,math,concurrent.futures
from PIL import Image,ImageDraw,ImageFont
W=Path(__file__).resolve().parent;R=W.parents[3];O=W/'source-review';O.mkdir(exist_ok=True)
raw=R/'shared/assets/blank-project-coding/original-restored-v2/raw'
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
jobs={
 'tetris-dense':('tetris.mp4',0,[(100,220,2),(270,315,2),(440,570,2),(645,700,2)]),
 'game-movement':('game-movement.mp4',645,[(5,1325,20)]),
 'inventory-dense':('inventory.mp4',0,[(94,170,5),(194,420,5),(424,448,4),(520,582,4)]),
 'profile-dense':('profile.mp4',0,[(25,155,5),(159,185,3),(206,227,3)]),
 'save-dense':('save.mp4',0,[(23,46,3),(69,115,3)])
}
report=[]
for key,(file,offset,ranges) in jobs.items():
 times=[t for a,b,step in ranges for t in range(a,b,step)]
 def frame(t):
  dest=O/f'{key}-frame-{t:04}.jpg'
  if not dest.exists():subprocess.run(['ffmpeg','-y','-v','error','-threads','1','-ss',str(t),'-i',str(raw/file),'-frames:v','1','-vf','scale=480:270',str(dest)],check=True)
  im=Image.open(dest).convert('RGB');d=ImageDraw.Draw(im);d.rectangle((0,0,480,26),fill='#202733');d.text((6,2),f'{key} source {t+offset}s',font=font,fill='white');return im
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex: frames=list(ex.map(frame,times))
 contacts=[]
 for start in range(0,len(frames),16):
  chunk=frames[start:start+16];canvas=Image.new('RGB',(1920,math.ceil(len(chunk)/4)*270),'white')
  for j,im in enumerate(chunk):canvas.paste(im,((j%4)*480,(j//4)*270))
  name=f'{key}-review-{start//16+1}.jpg';canvas.save(O/name,quality=91);contacts.append(name)
 report.append({'key':key,'file':file,'sourceOffset':offset,'sourceSampleTimes':[t+offset for t in times],'contacts':contacts,'directReview':'pending'})
 print(key,len(frames),'frames',flush=True)
(O/'candidate-review.json').write_text(json.dumps(report,indent=2),encoding='utf8')
