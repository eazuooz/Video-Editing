from common import *
from PIL import Image,ImageDraw,ImageFont
Q=R/'shared/output/private-math-concept-fit-20261023/candidates/m14';Q.mkdir(exist_ok=True)
sources={'tiny':'shared/output/private-math-concept-fit-20261023/sources/tiny-glade-official/release-date-trailer.mp4','shapeA':'shared/output/game-math-part2-teaching-revision/polygons-fresh-candidates/shapez2-257294952.mp4','shapeB':'shared/output/game-math-part2-teaching-revision/polygons-fresh-candidates/shapez2-257312662.mp4','dorf':'shared/output/game-math-part2-full-series/sources/dorfromantik-official/Dorfromantik_Explanation_Trailer.webm'}
windows=[('tiny',30.5,40,.5),('shapeA',0,4,.5),('shapeB',41.9,49,.5),('shapeB',27.9,32.3,.5),('dorf',90,103,.5),('dorf',115,123,.5),('dorf',173,184,1)]
rows=[];metadata={}
for key,start,end,step in windows:
 if key not in metadata:
  m=probe(R/sources[key]);v=next(s for s in m['streams'] if s['codec_type']=='video');metadata[key]=dict(path=sources[key],sha256=sha(R/sources[key]),width=v['width'],height=v['height'],fps=v['r_frame_rate'],audioStreams=[s['codec_name'] for s in m['streams'] if s['codec_type']=='audio'])
 t=start
 while t<end:
  p=Q/f'{key}-{t:07.2f}.jpg'
  if not p.exists():run(['ffmpeg','-v','error','-ss',t,'-i',R/sources[key],'-frames:v',1,'-vf','scale=640:360','-y',p])
  rows.append(dict(source=key,time=t,path=rel(p)));t=round(t+step,3)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20);sheets=[]
for at in range(0,len(rows),12):
 im=Image.new('RGB',(1920,1560),'#111');d=ImageDraw.Draw(im)
 for i,r in enumerate(rows[at:at+12]):
  x=i%3*640;y=i//3*390;im.paste(Image.open(R/r['path']),(x,y+30));d.text((x+5,y),f"{r['source']} {r['time']:.2f}s",font=font,fill='white')
 p=Q/f'sheet-{at//12+1:02}.jpg';im.save(p,quality=92);sheets.append(rel(p))
save(Q/'inspection.json',dict(sources=metadata,frames=rows,sheets=sheets,directReview='pending'));print(len(rows),'frames',len(sheets),'sheets')
