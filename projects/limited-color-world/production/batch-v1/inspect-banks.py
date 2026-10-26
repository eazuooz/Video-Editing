from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw
root=Path('D:/Github/VideoEditing')
sets=[('limited-color-world','puyo-intro-ot4gqysX29c.mp4','puyo-bank-review',[390,410,430,450,470,490,510,1050,1080,1110,1140,1170,1200,1230,1260,1290]),('computer-controlled-players','smash-cpu-I3LV8o_xhR8-section.mp4','cpu-bank-review',list(range(0,360,15))),('computer-controlled-players','dicey-reunion-fVsWXAAccVg.mp4','dicey-bank-review',list(range(0,36,2))),('computer-controlled-players','smash-samus-I9tcvSeemVo.mp4','samus-bank-review',list(range(0,24,2)))]
for slug,fn,name,times in sets:
 out=root/'projects'/slug/'production/local/batch-v1/sources'/name;out.mkdir(exist_ok=True)
 cells=[]
 for t in times:
  p=out/f'{t:07.2f}.jpg'
  if not p.exists():subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-ss',str(t),'-i',str(out.parent/fn),'-frames:v','1','-q:v','3',str(p)],check=True)
  im=Image.open(p);im.thumbnail((384,216));cell=Image.new('RGB',(384,242),(20,20,20));cell.paste(im,(0,26));ImageDraw.Draw(cell).text((8,5),f'{name}  local {t}s',fill='white');cells.append(cell)
 cols=4;board=Image.new('RGB',(cols*384,((len(cells)+cols-1)//cols)*242))
 for n,c in enumerate(cells):board.paste(c,((n%cols)*384,(n//cols)*242))
 board.save(out.parent/(name+'.jpg'),quality=90)
 print(out.parent/(name+'.jpg'))
