"""CPU optical-flow preview with editable seeds, explicit occlusion and screen-space math."""
from pathlib import Path
import json,sys,subprocess,math
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;O=ROOT/'shared/output/game-math-part2-teaching-revision'
sys.path.insert(0,str(O/'python-deps'))
import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageFont
cv2.setNumThreads(2)
data=json.loads((B/'body-annotation-keyframes.json').read_text(encoding='utf8'));start,end=data['interval'];fps=30
cmd=['ffmpeg','-hide_banner','-loglevel','error','-threads','2','-ss',str(start),'-i',str(ROOT/data['sourceFile']),'-t',str(end-start),'-vf',f'scale=800:450,fps={fps}','-an','-f','rawvideo','-pix_fmt','bgr24','pipe:1']
dec=subprocess.Popen(cmd,stdout=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW);frames=[]
while True:
 raw=dec.stdout.read(800*450*3)
 if len(raw)!=800*450*3:break
 frames.append(np.frombuffer(raw,np.uint8).reshape(450,800,3).copy())
assert dec.wait()==0 and len(frames)==(end-start)*fps
gray=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) for f in frames];knots=data['keyframes'];dense={};issues=[]
for a,b in zip(knots,knots[1:]):
 ia=round((a['t']-start)*fps);ib=min(len(frames)-1,round((b['t']-start)*fps))
 seed=np.array([a['lower'],a['upper']],dtype=np.float32).reshape(-1,1,2);current=seed.copy();forward={ia:seed[:,0].copy()}
 for i in range(ia+1,ib+1):
  p,ok,err=cv2.calcOpticalFlowPyrLK(gray[i-1],gray[i],current,None,winSize=(31,31),maxLevel=3)
  if not ok.all():issues.append({'frame':i,'reason':'forward optical flow confidence failed'})
  current=p;forward[i]=p[:,0].copy()
 current=np.array([b['lower'],b['upper']],dtype=np.float32).reshape(-1,1,2);backward={ib:current[:,0].copy()}
 for i in range(ib-1,ia-1,-1):
  p,ok,err=cv2.calcOpticalFlowPyrLK(gray[i+1],gray[i],current,None,winSize=(31,31),maxLevel=3)
  if not ok.all():issues.append({'frame':i,'reason':'backward optical flow confidence failed'})
  current=p;backward[i]=p[:,0].copy()
 for i in range(ia,ib+1):
  mix=(i-ia)/max(1,ib-ia);points=forward[i]*(1-mix)+backward[i]*mix
  divergence=float(np.linalg.norm(forward[i]-backward[i],axis=1).max())
  t=start+i/fps;hidden=any(a<=t<=b for a,b in data['hideIntervals']) or divergence>30
  dense[i]={'sourceTime':t,'lower':points[0].tolist(),'upper':points[1].tolist(),'hidden':bool(hidden),'trackingDisagreementPixels':divergence}
out=O/'source-review/torso-annotation-preview.mp4'
enc=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','2','-f','rawvideo','-pix_fmt','rgb24','-s','800x450','-r',str(fps),'-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','20','-threads','2',str(out)],stdin=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',17);small=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',13)
sheet=Image.new('RGB',(1600,4*245),'white');sd=ImageDraw.Draw(sheet)
for i,frame in enumerate(frames):
 t=i/fps;im=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB));draw=ImageDraw.Draw(im);r=dense[i]
 lower=np.array(r['lower']);upper=np.array(r['upper'])
 if not r['hidden']:
  p=tuple(lower);q=tuple(upper)
  if t>.5:draw.ellipse((p[0]-4,p[1]-4,p[0]+4,p[1]+4),fill=data['colors']['landmark'])
  if t>1.5:
   draw.line([p,q],fill=data['colors']['observedTorso'],width=4);v=upper-lower;v=v/max(np.linalg.norm(v),1);perp=np.array([-v[1],v[0]])
   draw.polygon([tuple(upper),tuple(upper-12*v+5*perp),tuple(upper-12*v-5*perp)],fill=data['colors']['observedTorso'])
   draw.text((q[0]+10,q[1]-22),'몸통 방향',fill=data['colors']['observedTorso'],font=font,stroke_width=1,stroke_fill='black')
  if t>4:
   for k in range(0,86,10):draw.line([(p[0],p[1]-k),(p[0],p[1]-k-5)],fill=data['colors']['screenReference'],width=3)
  if t>6:
   angle=math.atan2((upper-lower)[1],(upper-lower)[0]);delta=(angle+math.pi/2+math.pi)%(2*math.pi)-math.pi
   arc=[tuple(lower+30*np.array([math.cos(-math.pi/2+delta*j/20),math.sin(-math.pi/2+delta*j/20)])) for j in range(21)]
   draw.line(arc,fill=data['colors']['projectedAngle'],width=3)
 draw.rectangle((215,6,680,29),fill='#151515');draw.text((222,8),'화면상 방향 비교 · 움직이는 카메라 · 월드 각도 측정 아님',fill='white',font=small)
 # Reserved caption band stays clear; this is a silent authoring preview.
 enc.stdin.write(np.asarray(im).tobytes())
 if i in [15,90,180,210,240,270,300,330,360,390,420,449]:
  k=[15,90,180,210,240,270,300,330,360,390,420,449].index(i);thumb=im.resize((400,225));x=k%4*400;y=k//4*245;sheet.paste(thumb,(x,y));sd.text((x+5,y+228),f'{r["sourceTime"]:.2f}s / hidden={r["hidden"]}',fill='black')
enc.stdin.close();assert enc.wait()==0
sheet.save(O/'source-review/annotation-moving-pixels.jpg')
(O/'body-tracking-dense.json').write_text(json.dumps({'fps':fps,'frames':list(dense.values()),'confidenceIssues':issues,'actualMovingPixelReviewComplete':False},indent=2)+'\n',encoding='utf8')
print(json.dumps({'preview':str(out),'frames':len(frames),'hiddenFrames':sum(v['hidden'] for v in dense.values()),'confidenceIssues':len(issues),'motionReviewPending':True}))
