from common import *
from PIL import Image,ImageDraw,ImageFont
import math
Q=R/'shared/output/private-math-concept-fit-20261023/candidates/m15-refined';Q.mkdir(parents=True,exist_ok=True)
windows=[('m14-square','shared/output/game-math-part2-teaching-revision/polygons-fresh-candidates/shapez2-257312662.mp4',38.5,44.5,.5),('m15-entry','shared/output/game-math-part2-full-series/sources/dYyWmhVuc3w.mp4',616,625,.5),('m15-shadow','shared/output/game-math-part2-full-series/sources/wzQLP0Z3zII.mp4',1944,1953,.5)]
rows=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20)
for name,path,a,b,step in windows:
 for i in range(math.floor((b-a)/step)+1):
  t=a+i*step;p=Q/f'{name}-{t:09.3f}.jpg'
  if not p.exists():subprocess.run(['ffmpeg','-v','error','-ss',str(t),'-i',str(R/path),'-frames:v','1','-q:v','2','-y',str(p)],capture_output=True,check=True)
  rows.append(dict(window=name,source=path,time=t,path=rel(p)))
sheets=[]
for start in range(0,len(rows),12):
 im=Image.new('RGB',(1920,1560),'#111');d=ImageDraw.Draw(im)
 for n,r in enumerate(rows[start:start+12]):
  l=n%3*640;t=n//3*390;im.paste(Image.open(R/r['path']).resize((640,360)),(l,t+30));d.text((l+4,t+4),r['window']+' '+str(r['time']),font=font,fill='white')
 p=Q/f'sheet-{start//12+1:02}.jpg';im.save(p,quality=91);sheets.append(rel(p))
save(Q/'inspection.json',dict(windows=windows,frames=rows,sheets=sheets,directReview='pending'))
print(len(rows),'frames',len(sheets),'sheets',flush=True)
