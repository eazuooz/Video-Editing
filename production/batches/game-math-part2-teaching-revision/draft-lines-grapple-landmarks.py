"""Observed bright-connection endpoint candidates on CPU, never world values.

Reject clipped/short/ambiguous light components. Every 0.1-second observation
is independent; gaps must hide annotations, not extrapolate through a camera
cut or disappearance. Debug moving pixels require direct review and correction.
"""
from pathlib import Path
import json,subprocess,hashlib
import numpy as np
from scipy import ndimage
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
D=ROOT/'shared/output/game-math-part2-teaching-revision/lines-grapple-drafts';D.mkdir(parents=True,exist_ok=True)
T=B/'lines-tracks';T.mkdir(exist_ok=True)
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
base=read(B/'baselines/game-math-lines-bounds/production/timeline.json')
new=read(B/'lines-game-insertions.json')['scenes'];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',14)
jobs=[]
for s in base['scenes']:
 if s['id'] in ['02','05','08']:jobs.append((s['id'],f'shared/output/game-math-lines-bounds/clips/{s["id"]}.mp4',0,s['seconds']))
for s in new:
 if s['id'] in ['LG02','LG03']:
  for j,(a,z) in enumerate(s['intervals'],1):jobs.append((f'{s["id"]}-{j}',f'shared/output/game-math-part2-full-series/sources/{s["sourceId"]}.mp4',a,z-a))
records=[]
for ident,relative,start,duration in jobs:
 source=ROOT/relative;out=D/(ident+'.mp4');keys=[];frames=[];hidden=[];held=[]
 cmd=['ffmpeg','-v','error','-threads','1','-ss',str(start),'-i',str(source),'-t',str(duration),'-vf','scale=800:450,fps=10','-an','-pix_fmt','rgb24','-f','rawvideo','pipe:1']
 decoder=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
 encoder=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','800x450','-r','10','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','20','-threads','2','-movflags','+faststart',str(out)],stdin=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
 i=0
 while True:
  raw=decoder.stdout.read(800*450*3)
  if not raw:break
  assert len(raw)==800*450*3
  arr=np.frombuffer(raw,dtype=np.uint8).reshape(450,800,3);r,g,b=np.moveaxis(arr.astype(np.int16),2,0)
  cuff=(b-r>40)&(b-g>18)&(b>170)&(g>90)
  cuff[:175]=False;cuff[415:]=False;cuff[:,:425]=False;cuff[:,780:]=False
  cuff_components,cuff_n=ndimage.label(cuff);cuff_sizes=np.bincount(cuff_components.ravel());cuff_sizes[0]=0;references=[]
  for index in np.argsort(cuff_sizes)[-5:]:
   if not 18<=cuff_sizes[index]<=6000:continue
   yy,xx=np.where(cuff_components==index)
   if not 10<=xx.max()-xx.min()<=135 or not 8<=yy.max()-yy.min()<=100:continue
   center=np.array([xx.mean(),yy.mean()]);references.append(center)
  cuff_reference=min(references,key=lambda p:np.linalg.norm(p-[630,330])) if references else None
  # The retained teal-daylight recording has green approximately equal to
  # blue in the actual connection; the earlier blue-only draft missed it.
  # Long-span and visible hand-side checks reject isolated cuff/rune glows.
  mask=(r>65)&(g>160)&(b>185)&(b-r>28)&(g-r>18)&(b-g>-30)
  mask[:20]=False;mask[420:]=False;mask[:,:10]=False;mask[:,790:]=False
  components,n=ndimage.label(mask);sizes=np.bincount(components.ravel());sizes[0]=0
  candidate=None;quality=None
  for index in np.argsort(sizes)[-5:][::-1]:
   if sizes[index]<100:continue
   y,x=np.where(components==index);coords=np.column_stack([x,y]);mean=coords.mean(0);centered=coords-mean
   eigen,vec=np.linalg.eigh(centered.T@centered/len(coords));axis=vec[:,-1];project=centered@axis
   # Observed occupied pixels, not extrapolated PCA endpoints.
   low=coords[project<=np.quantile(project,.025)].mean(0);high=coords[project>=np.quantile(project,.975)].mean(0)
   span=np.linalg.norm(high-low);elongation=float(eigen[-1]/max(eigen[0],1))
   if span<140 or elongation<3.8 or min(x)<14 or max(x)>785 or min(y)<24 or max(y)>415:continue
   # Camera can aim downward: the lower endpoint then belongs to the rock.
   # Select the endpoint beside the independently visible blue cuff instead.
   verified_palm_only=(ident=='05' and any(a<=start+i/10<=z for a,z in [(10.7,12.2),(31.6,32.6),(33.9,34.4)]))
   if cuff_reference is None and not verified_palm_only:continue
   if verified_palm_only:
    # Directly viewed source12/32/34: palm faces the camera; the back-side
    # cuff is unseen. In these bounded intervals the right beam end is hand.
    hand,attachment=(low,high) if low[0]>high[0] else (high,low)
   else:
    hand,attachment=(low,high) if np.linalg.norm(low-cuff_reference)<np.linalg.norm(high-cuff_reference) else (high,low)
    if np.linalg.norm(hand-cuff_reference)>120 or np.linalg.norm(attachment-cuff_reference)<65:continue
   if hand[0]<425 or hand[1]<185:continue
   candidate=(hand,attachment);quality={'pixels':int(sizes[index]),'spanPixels':float(span),'elongation':elongation};break
  local=i/10;time=start+local;im=Image.fromarray(arr);draw=ImageDraw.Draw(im)
  if candidate is not None:
   hand,attachment=candidate;keys.append({'t':round(time,3),'left':hand.tolist(),'right':attachment.tolist(),'quality':quality})
   draw.line([tuple(hand),tuple(attachment)],fill='#ef5350',width=3)
   for p,c in [(hand,'#ffe082'),(attachment,'#42a5f5')]:draw.ellipse((p[0]-5,p[1]-5,p[0]+5,p[1]+5),outline=c,width=2)
   draw.text((20,45),'DRAFT: visible endpoints only / not measured world line',font=font,fill='white',stroke_width=1,stroke_fill='black')
  else:hidden.append(round(time,3))
  draw.text((20,23),f'{ident} source {time:.2f}s / draft, no pixel approval',font=font,fill='white',stroke_width=1,stroke_fill='black')
  encoder.stdin.write(im.tobytes())
  if i%20==0:frames.append((time,im.copy()))
  i+=1
 decoder.stdout.close();assert decoder.wait()==0,decoder.stderr.read().decode()
 encoder.stdin.close();assert encoder.wait()==0,encoder.stderr.read().decode()
 for page in range((len(frames)+7)//8):
  sheet=Image.new('RGB',(1600,1880),'white');draw=ImageDraw.Draw(sheet)
  for j,(time,im) in enumerate(frames[page*8:page*8+8]):
   x=j%2*800;y=j//2*470;sheet.paste(im,(x,y+20));draw.text((x+5,y),f'{ident} source{time:.2f}s',font=font,fill='black')
  sheet.save(D/f'{ident}-sheet-{page+1:02}.jpg',quality=95)
 record={'id':ident,'sourceFile':relative,'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'sourceInterval':[start,start+duration],'coordinatePixels':[800,450],'samplingSeconds':.1,'maxInterpolationGapSeconds':.15,'keyframes':keys,'undetectedObservations':hidden,'manualHideIntervals':[],'measurement':'observed bright beam component endpoints; projected only; physical/world/engine method unverified','detector':'candidate only; not accepted until direct moving pixels corrected','movingPixelApproval':False}
 write(T/(ident+'.json'),record);records.append({'id':ident,'sampled':i,'candidates':len(keys),'landmarks':str((T/(ident+'.json')).relative_to(ROOT)),'debug':str(out.relative_to(ROOT))})
 print(json.dumps(records[-1]),flush=True)
write(B/'lines-grapple-draft-progress.json',{'records':records,'approved':False})
buttons=''.join(f'<button data-src="{x["id"]}.mp4">{x["id"]}</button>' for x in records)
(D/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>연결선 관측 초안</title><style>body{background:#222;color:white;font:16px sans-serif}video{width:min(100%,1100px);display:block}button{padding:8px;margin:4px}</style><h1>실제 빛줄기 끝점 관측 초안 · 정상 속도 검수 필요</h1>'+buttons+'<video controls muted id="v"></video><script>const v=document.querySelector("video");for(const b of document.querySelectorAll("button"))b.onclick=()=>{v.src=b.dataset.src;v.playbackRate=1;v.play()}</script>',encoding='utf8')
