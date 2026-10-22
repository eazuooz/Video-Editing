"""Generate bounded source-inspection sheets; never records visual approval."""
import sys,subprocess,math
from PIL import Image,ImageDraw
from polish_common import *
catalog=read(B/'fhd-candidate-acquisition.json')
for ident in sys.argv[1:]:
 rec=catalog[ident];assert rec['verifiedFhd'];src=R/rec['path'];assert sha(src)==rec['sha256']
 out=src.parent/(ident+'-fine-review');out.mkdir(exist_ok=True)
 points=list(range(0,int(rec['duration']),5));samples=[]
 for t in points:
  p=out/f'{t:04}.jpg'
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-ss',str(t),'-i',str(src),'-frames:v','1','-vf','scale=480:270','-y',str(p)],check=True,capture_output=True)
  samples.append({'seconds':t,'image':rel(p),'sha256':sha(p)})
 for start in range(0,len(samples),12):
  sheet=Image.new('RGB',(1440,1184),'#121212');draw=ImageDraw.Draw(sheet)
  for i,s in enumerate(samples[start:start+12]):
   x=i%3*480;y=i//3*296;sheet.paste(Image.open(R/s['image']),(x,y+26));draw.text((x+8,y+5),str(s['seconds'])+'s',fill='white')
  sheet.save(out/f'sheet-{start//12+1:02}.jpg')
 save(B/(ident+'-candidate-samples.json'),{'status':'await-direct-inspection','source':rec['path'],'sourceSha256':rec['sha256'],'intervalSeconds':5,'samples':samples,'sheets':math.ceil(len(samples)/12),'fullMasterApproval':False})
 print(ident,len(samples),'source samples generated; no approval',flush=True)
