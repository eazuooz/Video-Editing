"""An original editable Pixelbolt pixel-grid prop; no image API or borrowed artwork."""
from pathlib import Path
import json,subprocess,hashlib
from PIL import Image,ImageDraw
H=Path(__file__).resolve().parent;P=H.parents[1];OUT=P/'production/local/room-v3/pixelbolt-ledger';OUT.mkdir(parents=True,exist_ok=True)
W,HGT=40,18;grid=[['.']*W for _ in range(HGT)]
def dot(x,y,col):
 if 0<=x<W and 0<=y<HGT:grid[y][x]=col
def line(x0,y0,x1,y1,col):
 dx=abs(x1-x0);sx=1 if x0<x1 else -1;dy=-abs(y1-y0);sy=1 if y0<y1 else -1;err=dx+dy
 while True:
  dot(x0,y0,col)
  if x0==x1 and y0==y1:break
  e=2*err
  if e>=dy:err+=dy;x0+=sx
  if e<=dx:err+=dx;y0+=sy
def poly(pts,col):
 for y in range(HGT):
  for x in range(W):
   inside=False;j=len(pts)-1
   for i in range(len(pts)):
    xi,yi=pts[i];xj,yj=pts[j]
    if (yi>y)!=(yj>y) and x<(xj-xi)*(y-yi)/(yj-yi)+xi:inside=not inside
    j=i
   if inside:dot(x,y,col)
 for i,(x,y) in enumerate(pts):line(x,y,*pts[(i+1)%len(pts)],col)
poly([(2,13),(19,16),(37,13),(38,16),(20,17),(3,16)],'s')
poly([(2,3),(15,1),(19,3),(22,3),(35,1),(38,3),(38,14),(21,16),(18,16),(1,14)],'c')
poly([(3,3),(15,2),(19,4),(19,14),(3,12)],'e');poly([(21,4),(34,2),(36,3),(37,12),(21,14)],'e')
poly([(4,3),(15,2),(18,4),(18,12),(4,11)],'p');poly([(22,4),(34,2),(35,3),(36,11),(22,12)],'p')
line(3,12,18,14,'t');line(22,14,37,12,'t');line(4,13,17,15,'b');line(23,15,37,13,'b')
line(19,4,19,14,'b');line(20,4,20,15,'d');line(21,4,21,14,'t');dot(20,3,'h');dot(20,16,'c')
line(5,3,14,2,'h');line(24,4,33,2,'h')
# Broken short marks resemble handwriting rather than unreadably tiny text.
for y in [5,7,9]:
 for a,b in [(5,8),(10,13),(15,16)]:line(a,y,b,y,'i')
for y in [5,7,9,11]:
 for a,b in [(24,26),(28,31),(33,34)]:
  if y==11 and a>28:continue
  line(a,y,b,y,'i')
dot(5,11,'a');dot(7,11,'a');dot(35,4,'a');dot(31,10,'a');dot(2,5,'a');dot(36,14,'a')
recipe={'version':1,'name':'open-ledger','width':W,'height':HGT,'palette':{'s':'#221b1550','c':'#5f3527','b':'#986846','d':'#4a3125','e':'#c4a16d','p':'#e5cf9d','h':'#f4e3bd','t':'#b78d5c','i':'#4c4035','a':'#b29363'},'symbols':{'ledger':[''.join(x) for x in grid]},'frames':[{'name':'open','duration':1000,'layers':[{'name':'ledger','ops':[{'op':'stamp','symbol':'ledger','x':0,'y':0}]}]}],'animations':{'idle':{'frames':['open'],'loop':True}}}
rp=Path(__file__).parent/'open-ledger.pixel.json';rp.write_text(json.dumps(recipe,ensure_ascii=False,indent=2),'utf8');tool=Path('C:/Users/1/Videos/YamyamCoding/ai-2d-tools/Pixelbolt/bin/pixelbolt.js');cmd=['node',str(tool),'render',str(rp),'--out',str(OUT)];subprocess.run(cmd,check=True)
png=OUT/'open-ledger.png';im=Image.open(png);preview=Image.new('RGB',(800,420),'#282522');large=im.resize((800,360),Image.Resampling.NEAREST);preview.paste(large,(0,30),large);ImageDraw.Draw(preview).text((12,10),'Actual Pixelbolt output / original40x18 / nearest20x preview',fill='white');preview.save(OUT/'preview.png')
record={'tool':'Pixelbolt0.13.0','actualExecution':True,'originalAuthoredGrid':True,'command':cmd,'sourceRecipe':str(rp),'output':str(png),'outputSHA256':hashlib.sha256(png.read_bytes()).hexdigest(),'nativeDimensions':[40,18],'colors':10,'alpha':'binary art + intentional translucent shadow, no smoothed edge','anchorRecommendation':'book centre at213,139; draw left193,top130 at1:1; coordinate subject to new desk plane QA','commercialLicenseBasis':'Own original pixel grid; Pixelbolt MIT renderer. No borrowed image or model generation.'}
(Path(__file__).parent/'open-ledger-execution.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),'utf8');print(str(png))
