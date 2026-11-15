import sys,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'production/batches/animation-18-20261031/research/A10/ocr-deps'))
import cv2,numpy as np
from prepare_sources import digest

def cut(key,file,box,height):
 im=cv2.imread(str(HERE/'local/sources'/file));x,y,w,h=box;pad=15
 crop=im[max(0,y-pad):y+h+pad,max(0,x-pad):x+w+pad].copy();mask=np.zeros(crop.shape[:2],np.uint8)
 cv2.grabCut(crop,mask,(pad,pad,w,h),np.zeros((1,65),np.float64),np.zeros((1,65),np.float64),7,cv2.GC_INIT_WITH_RECT)
 alpha=np.where((mask==1)|(mask==3),255,0).astype(np.uint8)
 # Remove disconnected dust/shadow fragments, retaining the connected subject.
 count,labels,stats,centroids=cv2.connectedComponentsWithStats(alpha)
 keep=1+np.argmax(stats[1:,4]);alpha=np.where(labels==keep,alpha,0).astype(np.uint8)
 if key=='beamng':
  blue,green,red=cv2.split(crop);grass=(green.astype(float)>red.astype(float)+5)&(green.astype(float)>blue.astype(float)+25)&(green>70);alpha[grass]=0
 rgba=Image.fromarray(cv2.cvtColor(np.dstack([crop,alpha]),cv2.COLOR_BGRA2RGBA));bounds=rgba.getbbox();rgba=rgba.crop(bounds)
 rgba.thumbnail((height*3,height),Image.Resampling.LANCZOS)
 out=HERE/'local/assets'/f'{key}.png';rgba.save(out)
 return dict(id=key,file=str(out),sourceFrame=file,sourceCrop=list(box),mask='GrabCut + largest connected subject',sha256=digest(out),dimensions=list(rgba.size),review='pending-encoded-picture-review')

def main():
 out=HERE/'local/assets';out.mkdir(exist_ok=True);rows=[]
 for args in [('mario','mario.png',(905,605,145,185),170),('kart','kart-sprite.png',(790,480,360,470),170),('forza','forza.png',(650,560,625,416),145),('beamng','beamng.png',(630,450,515,355),145)]:rows.append(cut(*args))
 # All actual-game stills retain their real background: no generated replacement.
 for key,box in [('doom',(935,380,425,370)),('town',(100,90,1550,910)),('portal',(620,290,680,580)),('windmill',(760,0,355,340)),('beamng',(450,330,1000,650)),('chomp',(420,230,1040,570)),('collision',(300,150,1400,850)),('train',(430,220,1490,760)),('maker',(500,100,1120,850)),('galaxy',(350,50,1300,900))]:
  im=Image.open(HERE/'local/sources'/f'{key}.png');x,y,w,h=box;im=im.crop((x,y,x+w,y+h));im.thumbnail((740,430),Image.Resampling.LANCZOS);p=out/f'{key}-context.png';im.save(p)
  rows.append(dict(id=key+'-context',file=str(p),sourceFrame=key+'.png',sourceCrop=list(box),sha256=digest(p),dimensions=list(im.size),review='pending-encoded-picture-review'))
 board=Image.new('RGB',(1500,900),'black');d=ImageDraw.Draw(board)
 for i,row in enumerate(rows):
  im=Image.open(row['file']).convert('RGBA');im.thumbnail((350,230));x=i%4*375;y=i//4*280;board.paste(im,(x,y),im if im.mode=='RGBA' else None);d.text((x,y+235),row['id'],fill='white')
 board.save(out/'contact.jpg',quality=95)
 (HERE/'assets.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
if __name__=='__main__':main()
