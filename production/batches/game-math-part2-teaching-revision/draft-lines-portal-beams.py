"""Detect only visible straight red beam fragments, not hidden world endpoints."""
from pathlib import Path
import json,hashlib,subprocess,math
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
cv2.setNumThreads(2)
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;T=B/'lines-tracks';O=ROOT/'shared/output/game-math-part2-teaching-revision/lines-portal-beam-drafts';O.mkdir(parents=True,exist_ok=True)
source=ROOT/'shared/output/game-math-part2-full-series/sources/yFRbGppLaUI.mp4';font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',14);records=[]
for ident,start,end in [('LG01-a',40,56.5),('LG01-b',72,98)]:
 keys=[];pictures=[];output=O/(ident+'.mp4')
 decoder=subprocess.Popen(['ffmpeg','-v','error','-threads','1','-ss',str(start),'-i',str(source),'-t',str(end-start),'-vf','scale=800:450,fps=10','-an','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
 encoder=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','800x450','-r','10','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','20','-threads','2',str(output)],stdin=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
 i=0;previous=None;object_id=None
 while True:
  raw=decoder.stdout.read(800*450*3)
  if not raw:break
  arr=np.frombuffer(raw,np.uint8).reshape(450,800,3);r,g,b=np.moveaxis(arr.astype(np.int16),2,0);t=round(start+i/10,3)
  mask=((r-g>45)&(r-b>30)&(r>170)).astype(np.uint8)*255;mask[:75]=0;mask[355:]=0;mask[:,:15]=0;mask[:,785:]=0
  mask=cv2.dilate(mask,np.ones((3,3),np.uint8));lines=cv2.HoughLinesP(mask,1,np.pi/180,threshold=50,minLineLength=95,maxLineGap=6);candidate=None
  if lines is not None:
   scored=[]
   for line in lines[:,0]:
    p,q=line[:2].astype(float),line[2:].astype(float);length=np.linalg.norm(q-p)
    points=np.array([p+(q-p)*u for u in np.linspace(0,1,100)]).astype(int)
    if min(points[:,1])<78 or max(points[:,1])>352:continue
    if (mask[points[:,1],points[:,0]]>0).mean()<.85:continue
    score=length/(1+(np.linalg.norm((p+q)/2-previous)/200 if previous is not None else 0));scored.append((score,p,q))
   if scored:_,p,q=max(scored,key=lambda a:a[0]);candidate=(p,q)
  im=Image.fromarray(arr);draw=ImageDraw.Draw(im)
  if candidate:
   p,q=candidate;center=(p+q)/2
   if previous is None or np.linalg.norm(center-previous)>95:object_id=f'{ident}-visible-fragment-{t}'
   keys.append({'t':t,'object':object_id,'red':[p.tolist(),q.tolist()]});previous=center
   draw.line([tuple(p),tuple(q)],fill='#ef5350',width=3)
  else:previous=None
  draw.text((18,25),f'{ident} source{t:.2f}s / visible ray fragment only / draft',font=font,fill='white',stroke_width=1,stroke_fill='black');encoder.stdin.write(im.tobytes())
  if i%10==0:pictures.append((t,im.copy()))
  i+=1
 decoder.stdout.close();assert decoder.wait()==0,decoder.stderr.read().decode();encoder.stdin.close();assert encoder.wait()==0,encoder.stderr.read().decode()
 for page in range((len(pictures)+7)//8):
  sheet=Image.new('RGB',(1600,1880),'white');draw=ImageDraw.Draw(sheet)
  for j,(t,im) in enumerate(pictures[page*8:page*8+8]):
   x=j%2*800;y=j//2*470;sheet.paste(im,(x,y+20));draw.text((x+5,y),f'{ident} source{t:.2f}s',font=font,fill='black')
  sheet.save(O/f'{ident}-sheet-{page+1:02}.jpg',quality=95)
 record={'id':ident,'sourceFile':source.relative_to(ROOT).as_posix(),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'sourceInterval':[start,end],'coordinatePixels':[800,450],'samplingSeconds':.1,'maxInterpolationGapSeconds':.15,'keyframes':keys,'manualHideIntervals':[],'closed':False,'measurement':'visible red ray fragment pixels only; source/target beyond fragment not inferred','movingPixelApproval':False}
 (T/(ident+'.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8');records.append({'id':ident,'sampled':i,'observations':len(keys),'debug':output.relative_to(ROOT).as_posix()});print(json.dumps(records[-1]),flush=True)
(B/'lines-portal-beam-draft-progress.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf8')
buttons=''.join(f'<button data-src="{x["id"]}.mp4">{x["id"]}</button>' for x in records)
(O/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>포털 빛줄기 초안</title><style>body{background:#222;color:white;font:16px sans-serif}video{width:min(100%,1100px);display:block}button{padding:8px;margin:4px}</style><h1>보이는 직선 빛줄기 관측 초안</h1>'+buttons+'<video controls muted id="v"></video><script>const v=document.querySelector("video");for(const b of document.querySelectorAll("button"))b.onclick=()=>{v.src=b.dataset.src;v.playbackRate=1;v.play()}</script>',encoding='utf8')
