"""Native800x700 semantic readouts; three speech-revealed states per paragraph."""
from pathlib import Path
import importlib.util,json,re
from functools import lru_cache
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).parent
def mod(name,file):
 sp=importlib.util.spec_from_file_location(name,H/file);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
c=mod('v8_common','common.py');b=mod('v8_board_specs','board-specs.py')
WHITE='#f5f5f5';GOLD='#e8cf83';MUTED='#b8b8b8';TEAL='#73c7c2';RED='#ef5a63';GREEN='#6cce8e';BLUE='#66b9ed'
FONT='C:/Windows/Fonts/NotoSansKR-VF.ttf';BOLD='C:/Windows/Fonts/malgunbd.ttf';MONO='C:/Windows/Fonts/consola.ttf'
MATH='C:/Windows/Fonts/segoeui.ttf'
@lru_cache(maxsize=32)
def font(size,bold=False,mono=False):
 f=ImageFont.truetype(MONO if mono else BOLD if bold else FONT,size)
 if not mono and not bold:f.set_variation_by_axes([500])
 return f
@lru_cache(maxsize=16)
def mathfont(size):return ImageFont.truetype(MATH,size)
def runs(value,size,bold=False,mono=False):
 for ch in value:
  f=mathfont(size) if ch in '−ᵀᵢⱼ⁻₁₂₃′θ' else font(size,bold,mono)
  yield ch,f
def width(value,size=48,bold=False,mono=False):return sum(f.getlength(ch) for ch,f in runs(value,size,bold,mono))
def text(d,xy,value,size=48,color=WHITE,bold=False,mono=False):
 w=width(value,size,bold,mono)
 assert w<=760,(value,w,size)
 x,y=xy
 for ch,f in runs(value,size,bold,mono):
  d.text((x,y+size),ch,font=f,fill=color,stroke_width=0,anchor='ls');x+=f.getlength(ch)
def matrix(d,kind,y=210,highlight=None):
 vals={'R':[['0','0','−1'],['0','1','0'],['1','0','0']], 'T':[['0','0','1'],['0','1','0'],['−1','0','0']], 'DCM':[['p·p′','p·q′','p·r′'],['q·p′','q·q′','q·r′'],['r·p′','r·q′','r·r′']]}[kind]
 colors=[RED,GREEN,BLUE]
 for i in range(3):
  for j in range(3):
   x=132+j*200;yy=y+i*92
   text(d,(x,yy),vals[i][j],52,colors[i],mono=True)
 d.line([(90,y+12),(70,y+12),(70,y+274),(90,y+274)],fill=WHITE,width=4)
 d.line([(690,y+12),(710,y+12),(710,y+274),(690,y+274)],fill=WHITE,width=4)
 if highlight is not None:d.rectangle((95,y+highlight*92+2,680,y+highlight*92+82),outline=GOLD,width=4)
def panel(title,rows,stage):
 im=Image.new('RGB',(800,700),'black');d=ImageDraw.Draw(im)
 text(d,(20,20),title,42,GOLD,True)
 d.line((20,92,780,92),fill='#343b40',width=2)
 special=any(x.startswith('matrix:') for x in rows)
 for i,row in enumerate(rows):
  if i>=stage:break
  y=150+i*132
  if row.startswith('matrix:'):
   matrix(d,row.split(':')[1],130 if i==0 else 200);continue
  if special and rows[0].startswith('matrix:'):y=470+(i-1)*90
  if special and i==2:y=560
  if row.startswith('code:'):
   code=row[5:];parts=re.split(r'([A-Za-z]+)(?=\()',code)
   x=20
   for part in parts:
    if not part:continue
    col=TEAL if '(' not in part and part.isalpha() else WHITE
    text(d,(x,y),part,42,col,mono=True);x+=width(part,42,mono=True)
   continue
  size=48
  # Explicit two-line reflow keeps full wording at48px; never auto-shrink.
  f=font(size)
  if width(row)>760:
   spaces=[m.start() for m in re.finditer(' ',row)];cuts=[k for k in spaces if width(row[:k])<=760 and width(row[k+1:])<=760]
   assert cuts,(title,row)
   k=min(cuts,key=lambda k:abs(width(row[:k])-width(row[k+1:])))
   text(d,(20,y),row[:k],size,TEAL if i==2 else WHITE);text(d,(20,y+60),row[k+1:],size,TEAL if i==2 else WHITE)
  else:text(d,(20,y),row,size,TEAL if i==2 else WHITE)
 return im
def main():
 c.authorized();out=c.O/'boards';out.mkdir(parents=True,exist_ok=True);script=c.read(c.S/'narration.ko.json');records=[]
 for s in script['scenes']:
  assert len(b.SPECS[s['id']])==len(s['paragraphs'])
  for i,((title,rows),p) in enumerate(zip(b.SPECS[s['id']],s['paragraphs']),1):
   states=[]
   for stage in range(1,4):
    file=out/f'{s["id"]}-L{i:02}-{stage}.png';panel(title,rows,stage).save(file);states.append(dict(stage=stage,file=c.rel(file),sha256=c.sha(file)))
   records.append(dict(scene=s['id'],line=i,title=title,rows=rows,states=states,sourceKind='independently authored mathematical readout',dimensions=[800,700]))
 c.save(c.H/'board-manifest.json',dict(renderer='Pillow native typography and tables; Manim finite cell animations bound separately',scriptSha256=c.sha(c.S/'narration.ko.json'),paragraphCount=76,records=records,pixelReview='pending'))
 thumbs=[]
 for r in records:
  im=Image.open(c.R/r['states'][-1]['file']);im.thumbnail((320,280));thumbs.append((r,im))
 for start in range(0,len(thumbs),12):
  sheet=Image.new('RGB',(1280,900),'#222222');d=ImageDraw.Draw(sheet)
  for j,(r,im) in enumerate(thumbs[start:start+12]):
   x=(j%4)*320;y=(j//4)*300;sheet.paste(im,(x,y+20));d.text((x+5,y),f'{r["scene"]}.L{r["line"]:02}',font=font(16),fill=WHITE)
  sheet.save(out/f'contact-{start//12:02}.jpg')
 print('Prepared228 native board states across76 paragraphs.')
if __name__=='__main__':main()
