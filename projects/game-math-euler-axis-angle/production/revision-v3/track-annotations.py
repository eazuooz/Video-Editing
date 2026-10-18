"""CPU-only source tracking with inspectable samples; no simulated game telemetry."""
from pathlib import Path
import json,sys,hashlib,math
R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';O=P/'production/local/revision-v3';sys.path.insert(0,str(O/'deps'))
import cv2
from PIL import Image,ImageDraw,ImageFont
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert read(R/'shared/publishing/video-production-control.json')['selectedVideo']==P.name
 planfile=P/'sources/annotation-plan-v3.json';plan=read(planfile);sources=read(P/'sources/cut-plan-v3.json')['sources'];out=O/'tracking';out.mkdir(exist_ok=True)
 requested=set(sys.argv[1:]);font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',23);results=[]
 for w in plan['windows']:
  if requested and w['id'] not in requested:continue
  signature=hashlib.sha256(json.dumps(w,sort_keys=True).encode()).hexdigest();receipt=out/(w['id']+'.json')
  if receipt.exists() and read(receipt).get('seedSha256')==signature:print('Reusing',w['id'],flush=True);continue
  cap=cv2.VideoCapture(str(R/sources[w['sourceId']]['file']));assert cap.isOpened();cv2.setNumThreads(2)
  start=round(w['sourceIn']*60);end=round(w['sourceOutExclusive']*60);cap.set(cv2.CAP_PROP_POS_FRAMES,start)
  ok,frame=cap.read();assert ok;tracker=cv2.TrackerCSRT_create();tracker.init(cv2.resize(frame,(960,540)),tuple(round(x/2) for x in w['bbox']))
  keys=[];images=[];box=w['bbox'];good=True
  for f in range(start,end):
   if f>start:ok,frame=cap.read()
   if not ok:break
   if (f-start)%6:continue
   if f>start:
    good,b=tracker.update(cv2.resize(frame,(960,540)));box=[2*x for x in b]
   x,y,width,height=box;visible=bool(good and 25<width<1500 and 25<height<900 and x>=0 and y>=0 and x+width<=1920 and y+height<=1080)
   keys.append(dict(sourceTime=f/60,visible=visible,bbox=[round(v,2) for v in box],center=[round(x+width/2,2),round(y+height/2,2)],ellipseRadius=[round(width*.58,2),round(height*.58,2)]))
   if (f-start)%30==0:
    im=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB));d=ImageDraw.Draw(im)
    if visible:d.rectangle([x,y,x+width,y+height],outline='#F4D557',width=10)
    d.rectangle([0,880,1920,1080],fill='#101010');im=im.resize((480,270));d=ImageDraw.Draw(im);d.rectangle([0,0,480,32],fill='black');d.text((5,2),f'{w["id"]} {f/60:.1f}s '+('' if visible else 'HIDDEN'),font=font,fill='yellow');images.append(im)
  cap.release();assert keys
  if keys[-1]['sourceTime']<(end-1)/60:keys.append({**keys[-1],'sourceTime':(end-1)/60})
  data=dict(id=w['id'],seedSha256=signature,sourceId=w['sourceId'],sourceIn=w['sourceIn'],sourceOutExclusive=w['sourceOutExclusive'],method='OpenCV4.12 CSRT actual CPU-decoded source,10Hz',keyframes=keys,failedSamples=sum(not k['visible'] for k in keys),pixelReview='pending; tracker success alone is not approval')
  receipt.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
  for i in range(0,len(images),16):
   board=Image.new('RGB',(1920,1080));chunk=images[i:i+16]
   for j,im in enumerate(chunk):board.paste(im,((j%4)*480,(j//4)*270))
   board.save(out/f'{w["id"]}-{i//16+1}.jpg',quality=90)
  print(w['id'],len(keys),'samples',data['failedSamples'],'hidden',flush=True)
if __name__=='__main__':main()
