from common import *
from PIL import Image,ImageDraw,ImageFont
Q=R/'shared/output/private-math-concept-fit-20261023/candidates/m19-m20';src=read(Q/'inspection.json')['sources'];src['launch']=dict(path='shared/output/private-math-concept-fit-20261023/sources/se2-official/launch.mp4');O=Q/'selected';O.mkdir(exist_ok=True)
windows=[('19-roof','tiny',34,39),('19-panel','launch',56,59),('19-shape','launch',46,53),('19-hole','big',600,607),('19-round','tiny',28,31),('20-paint','se2',76,85),('20-wall','tiny',30,35),('20-panels','se2',94,99)]
rows=[]
for sid,k,a,b in windows:
 for i in range(round((b-a)*2)+1):
  tm=a+i*.5;p=O/f'{sid}-{tm:08.3f}.jpg'
  if not p.exists():subprocess.run(['ffmpeg','-v','error','-ss',str(tm),'-i',str(R/src[k]['path']),'-frames:v','1','-q:v','2','-y',str(p)],capture_output=True,check=True)
  rows.append(dict(scene=sid,key=k,time=tm,path=rel(p)))
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20);sheets=[]
for at in range(0,len(rows),12):
 im=Image.new('RGB',(1920,1560),'#111');d=ImageDraw.Draw(im)
 for i,row in enumerate(rows[at:at+12]):
  x=i%3*640;y=i//3*390;im.paste(Image.open(R/row['path']).resize((640,360)),(x,y+30));d.text((x+4,y+4),row['scene']+' '+str(row['time']),font=font,fill='white')
 p=O/f'sheet-{at//12+1:02}.jpg';im.save(p,quality=92);sheets.append(rel(p))
save(O/'inspection.json',dict(windows=windows,frames=rows,sheets=sheets,directReview='pending'))
D=R/'output/m19-m20-source-review';D.mkdir(exist_ok=True)
buttons=''.join(f'<button data-src="/{src[k]["path"]}" data-a="{a}" data-b="{b}">{sid} {a}–{b}</button>' for sid,k,a,b in windows)
template=(R/'output/m16-source-review/index.html').read_text(encoding='utf8');a=template.index('<div>');b=template.index('</div>',a);template=template[:a]+'<div>'+buttons+template[b:];template=template.replace('M16','M19/M20');(D/'index.html').write_text(template,encoding='utf8');print(len(rows),'fine frames')
