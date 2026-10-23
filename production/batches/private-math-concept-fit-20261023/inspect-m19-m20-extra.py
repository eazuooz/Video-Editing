from common import *
from PIL import Image,ImageDraw,ImageFont
import html
Q=R/'shared/output/private-math-concept-fit-20261023/candidates/m19-m20/extra';Q.mkdir(exist_ok=True)
S=read(Q.parent/'inspection.json')['sources'];windows=[('19-hole-recap','big',666,670),('20-roof','tiny',41,47),('20-recap','tiny',52,56)]
rows=[]
for name,key,a,b in windows:
 for i in range(round((b-a)*2)+1):
  t=a+i*.5;p=Q/f'{name}-{t:.1f}.jpg'
  if not p.exists():run(['ffmpeg','-v','error','-ss',t,'-i',R/S[key]['path'],'-frames:v','1','-q:v','2','-y',p])
  rows.append(dict(name=name,time=t,path=rel(p)))
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20);sheets=[]
for at in range(0,len(rows),12):
 im=Image.new('RGB',(1920,1560),'#111');d=ImageDraw.Draw(im)
 for i,r in enumerate(rows[at:at+12]):
  x=i%3*640;y=i//3*390;im.paste(Image.open(R/r['path']).resize((640,360)),(x,y+30));d.text((x+4,y+4),r['name']+' '+str(r['time']),font=font,fill='white')
 p=Q/f'sheet-{at//12+1:02}.jpg';im.save(p,quality=92);sheets.append(rel(p))
save(Q/'inspection.json',dict(windows=windows,frames=rows,sheets=sheets,directReview='pending'))
page=(R/'output/m19-m20-source-review/index.html').read_text(encoding='utf8');a=page.index('<div>');b=page.index('</div>',a)
buttons=''.join(f'<button data-src="/{S[k]["path"]}" data-a="{u}" data-b="{v}">{name} {u}–{v}</button>' for name,k,u,v in windows)
(R/'output/m19-m20-source-review/extra.html').write_text(page[:a]+'<div>'+buttons+page[b:],encoding='utf8');print(len(rows),'extra inspected-source candidate frames')
