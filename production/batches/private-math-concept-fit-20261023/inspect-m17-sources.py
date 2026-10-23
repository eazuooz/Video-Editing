from common import *
from PIL import Image,ImageDraw,ImageFont
import math,html
authorized('M17');Q=R/'shared/output/private-math-concept-fit-20261023/candidates/m17';Q.mkdir(parents=True,exist_ok=True)
sources={'portal':'shared/output/game-math-part2-full-series/sources/yFRbGppLaUI.mp4','town':'shared/output/game-math-part2-full-series/sources/FRfnXAIbA-M.mp4','tiny':'shared/output/private-math-concept-fit-20261023/sources/tiny-glade-official/release-date-trailer.mp4'}
windows=[('pillar','portal',16,40,2),('cube','portal',40,75,2),('tiny','tiny',16.5,31,1),('town-build','town',274,315,3),('town-turn','town',505,548,3),('town-hide','town',626,665,3)]
rows=[];meta={};font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20)
for k,p in sources.items():
 m=probe(R/p);v=next(x for x in m['streams'] if x['codec_type']=='video');meta[k]=dict(path=p,sha256=sha(R/p),width=v['width'],height=v['height'],fps=v['r_frame_rate'],audio=[x['codec_name'] for x in m['streams'] if x['codec_type']=='audio'])
 assert v['height']>=1080 or k=='portal'
for name,k,a,b,step in windows:
 for i in range(math.floor((b-a)/step)+1):
  tm=a+i*step;p=Q/f'{name}-{tm:09.3f}.jpg'
  if not p.exists():subprocess.run(['ffmpeg','-v','error','-ss',str(tm),'-i',str(R/sources[k]),'-frames:v','1','-q:v','2','-y',str(p)],capture_output=True,check=True)
  rows.append(dict(window=name,source=k,time=tm,path=rel(p)))
sheets=[]
for start in range(0,len(rows),12):
 im=Image.new('RGB',(1920,1560),'#111');d=ImageDraw.Draw(im)
 for n,row in enumerate(rows[start:start+12]):
  x=n%3*640;y=n//3*390;im.paste(Image.open(R/row['path']).resize((640,360)),(x,y+30));d.text((x+4,y+4),row['window']+' '+str(row['time']),font=font,fill='white')
 p=Q/f'sheet-{start//12+1:02}.jpg';im.save(p,quality=91);sheets.append(rel(p))
save(Q/'inspection.json',dict(sources=meta,windows=windows,frames=rows,sheets=sheets,directReview='pending'))
print(len(rows),'frames',len(sheets),'sheets')
