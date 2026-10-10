"""CPU drafts from independently visible color components and manual face seeds.

These are selected screen pixels, never game colliders or world measurements.
Hide uncertain observations. A draft still requires moving-pixel review.
"""
from pathlib import Path
import json,hashlib,subprocess,math,argparse
import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageFont
cv2.setNumThreads(2)
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
O=ROOT/'shared/output/game-math-part2-teaching-revision/lines-shape-drafts';O.mkdir(parents=True,exist_ok=True)
T=B/'lines-tracks';T.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',14)
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def box(points):
 lo,hi=points.min(0),points.max(0)
 return np.array([[lo[0],lo[1]],[hi[0],lo[1]],[hi[0],hi[1]],[lo[0],hi[1]]])
def circle(center,r):return np.array([center+r*np.array([math.cos(t),math.sin(t)]) for t in np.linspace(0,2*math.pi,33)[:-1]])
def resample(contour,n=48):
 p=contour.reshape(-1,2).astype(float);p=np.vstack([p,p[0]])
 lengths=np.linalg.norm(np.diff(p,axis=0),axis=1);cs=np.r_[0,np.cumsum(lengths)]
 if cs[-1]<30:return None
 samples=np.linspace(0,cs[-1],n,endpoint=False)
 return np.column_stack([np.interp(samples,cs,p[:,d]) for d in [0,1]])
jobs=[
 {'id':'10','file':'shared/output/game-math-lines-bounds/clips/10.mp4','start':0,'duration':48,'mode':'effect','windows':[[7,14]],'roi':[190,90,550,340]},
 {'id':'13','file':'shared/output/game-math-lines-bounds/clips/13.mp4','start':0,'duration':48,'mode':'blue','windows':[[0,15],[26,34]],'roi':[20,75,780,345]},
 {'id':'16','file':'shared/output/game-math-lines-bounds/clips/16.mp4','start':0,'duration':54,'mode':'blue','windows':[[0,3],[12,23],[27,38]],'roi':[20,75,780,345]},
 {'id':'LG06-blue','file':'shared/output/game-math-part2-full-series/sources/4s7nMfXt8uQ.mp4','start':731,'duration':8,'mode':'blue','windows':[[731,739]],'roi':[20,75,780,345]},
 {'id':'LG06-gray','file':'shared/output/game-math-part2-full-series/sources/4s7nMfXt8uQ.mp4','start':665,'duration':11,'mode':'gray','windows':[[665,667.15],[673,674.45]],'roi':[330,105,660,355]},
]
# Seed polygons are actual directly inspected corners. LK moves each vertex
# using local evidence with forward/backward error rejection; no world pose.
manual=[
 {'id':'LG04','file':'shared/output/game-math-part2-full-series/sources/4s7nMfXt8uQ.mp4','start':633,'duration':17,'roundComparison':True,'affineTracking':True,'seeds':[
  [633,633.75,(np.array([145,176])+np.column_stack([25*np.cos(np.linspace(0,2*math.pi,33)[:-1]),15*np.sin(np.linspace(0,2*math.pi,33)[:-1])])).tolist()],
  [634,634.75,(np.array([275,174])+np.column_stack([65*np.cos(np.linspace(0,2*math.pi,33)[:-1]),43*np.sin(np.linspace(0,2*math.pi,33)[:-1])])).tolist()],
  [635,635.6,(np.array([535,187])+np.column_stack([18*np.cos(np.linspace(0,2*math.pi,33)[:-1]),11*np.sin(np.linspace(0,2*math.pi,33)[:-1])])).tolist()],
  [639,640.1,(np.array([573,174])+np.column_stack([23*np.cos(np.linspace(0,2*math.pi,33)[:-1]),12*np.sin(np.linspace(0,2*math.pi,33)[:-1])])).tolist()],
  [641,641.8,(np.array([153,237])+np.column_stack([33*np.cos(np.linspace(0,2*math.pi,33)[:-1]),22*np.sin(np.linspace(0,2*math.pi,33)[:-1])])).tolist()],
  [642,643.2,(np.array([328,254])+np.column_stack([39*np.cos(np.linspace(0,2*math.pi,33)[:-1]),19*np.sin(np.linspace(0,2*math.pi,33)[:-1])])).tolist()],
  [648,648.45,(np.array([298,149])+np.column_stack([27*np.cos(np.linspace(0,2*math.pi,33)[:-1]),23*np.sin(np.linspace(0,2*math.pi,33)[:-1])])).tolist()],
  [649,649.8,(np.array([143,134])+np.column_stack([23*np.cos(np.linspace(0,2*math.pi,33)[:-1]),13*np.sin(np.linspace(0,2*math.pi,33)[:-1])])).tolist()]]},
 {'id':'LG05','file':'shared/output/game-math-part2-full-series/sources/portal2-steam-5787.mp4','start':48,'duration':40.5,'seeds':[
  [78,79.05,[[328,210],[466,210],[506,242],[297,243]]],
  [79.5,79.9,[[236,269],[353,257],[392,279],[294,305]]],
  [82,83,[[390,236],[449,233],[449,288],[393,295]]]]},
 {'id':'LG07-a','file':'shared/output/game-math-part2-full-series/sources/4s7nMfXt8uQ.mp4','start':560,'duration':11,'seeds':[
  [560,561,[[23,162],[554,153],[533,187],[25,233]]],
  [562,563.8,[[80,203],[496,174],[487,202],[78,264]]],
  [564,565.6,[[164,202],[481,190],[475,211],[163,240]]]],'affineTracking':True},
 {'id':'LG07-c','file':'shared/output/game-math-part2-full-series/sources/4s7nMfXt8uQ.mp4','start':719,'duration':12,'seeds':[
  [723,724.2,[[320,163],[508,164],[500,194],[327,195]]],
  [729,730.5,[[344,234],[573,214],[572,229],[345,248]]]],'affineTracking':True},
 {'id':'19','file':'shared/output/game-math-lines-bounds/clips/19.mp4','start':0,'duration':64,'seeds':[
  [0,2,[[362,217],[374,214],[379,349],[367,350]]],
  [12,13.2,[[410,166],[516,180],[516,212],[410,200]]],
  [36,37.2,[[221,278],[575,174],[575,205],[238,317]]]],'affineTracking':True},
 {'id':'21','file':'shared/output/game-math-lines-bounds/clips/21.mp4','start':0,'duration':56,'seeds':[
  [12,13.2,[[92,271],[424,235],[426,246],[93,281]]],
  [20,21.2,[[40,302],[330,254],[327,266],[43,316]]]],'affineTracking':True},
]
parser=argparse.ArgumentParser();parser.add_argument('--only',nargs='*');args=parser.parse_args()
records=[]
for job in jobs+manual:
 if args.only and job['id'] not in args.only:continue
 ident=job['id'];source=ROOT/job['file'];start=job['start'];duration=job['duration'];keys=[];pictures=[]
 decoder=subprocess.Popen(['ffmpeg','-v','error','-threads','1','-ss',str(start),'-i',str(source),'-t',str(duration),'-vf','scale=800:450,fps=30','-an','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
 out=O/(ident+'.mp4');encoder=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','800x450','-r','30','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','20','-threads','2','-movflags','+faststart',str(out)],stdin=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
 i=0;previous=None;points=None;features=None;seed_end=-1;object_id=None;previous_center=None
 while True:
  raw=decoder.stdout.read(800*450*3)
  if not raw:break
  assert len(raw)==800*450*3
  arr=np.frombuffer(raw,np.uint8).reshape(450,800,3);gray=cv2.cvtColor(arr,cv2.COLOR_RGB2GRAY);t=round(start+i/30,3);observed=None
  if 'seeds' in job:
   for seed_index,(seed_at,end,vertices) in enumerate(job['seeds']):
    if abs(t-seed_at)<.01:
     points=np.array(vertices,np.float32).reshape(-1,1,2);seed_end=end;object_id=f'{ident}-face-{seed_index}';previous=None
     region=np.zeros((450,800),np.uint8);cv2.fillPoly(region,[np.asarray(vertices,np.int32)],255)
     features=cv2.goodFeaturesToTrack(gray,200,.002,3,mask=region,blockSize=3)
   if points is not None and t<=seed_end:
    if previous is not None:
     required=3 if job.get('affineTracking') else 8
     if features is None or len(features)<required:points=None
     if points is not None:
      nxt,status,err=cv2.calcOpticalFlowPyrLK(previous,gray,features,None,winSize=(25,25),maxLevel=3,criteria=(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,30,.01))
      back,bst,be=cv2.calcOpticalFlowPyrLK(gray,previous,nxt,None,winSize=(25,25),maxLevel=3)
      good=(status.ravel()>0)&(bst.ravel()>0)&(err.ravel()<25)&(np.linalg.norm(back-features,axis=2).ravel()<1.3)
      if good.sum()<required:points=None
      else:
       if job.get('affineTracking'):
        matrix,inliers=cv2.estimateAffinePartial2D(features[good],nxt[good],method=cv2.RANSAC,ransacReprojThreshold=1.5)
        H=np.vstack([matrix,[0,0,1]]) if matrix is not None else None
       else:H,inliers=cv2.findHomography(features[good],nxt[good],cv2.RANSAC,2)
       if H is None or inliers.sum()<required:points=None
       else:
        moved=cv2.perspectiveTransform(points,H)
        before_area=abs(cv2.contourArea(points));after_area=abs(cv2.contourArea(moved))
        if before_area<5 or not .65<after_area/before_area<1.55 or np.max(np.linalg.norm(moved-points,axis=2))>95:points=None
        else:
         points=moved
         region=np.zeros((450,800),np.uint8);cv2.fillPoly(region,[moved.reshape(-1,2).astype(np.int32)],255)
         # Refresh only inside the newly observed face; retain no stale
         # feature after it disappears or a current frame rejects motion.
         features=cv2.goodFeaturesToTrack(gray,200,.002,3,mask=region,blockSize=3)
    if points is not None:
     contour=points.reshape(-1,2)
     if np.any(contour[:,0]<8) or np.any(contour[:,0]>792) or np.any(contour[:,1]<60) or np.any(contour[:,1]>355):points=None
     else:
      observed={'red':contour,'blue':box(contour),'object':object_id}
      if job.get('roundComparison'):
       center=contour.mean(0);radius=np.linalg.norm(contour-center,axis=1).max()+4;observed['teal']=circle(center,radius);observed.pop('blue')
   else:points=None
  elif any(a<=t<=z for a,z in job['windows']):
   r,g,b=np.moveaxis(arr.astype(np.int16),2,0);hsv=cv2.cvtColor(arr,cv2.COLOR_RGB2HSV)
   if job['mode']=='blue':mask=(b-r>20)&(g-r>8)&(b>55)&(g>38)&(hsv[:,:,1]>65)&(hsv[:,:,0]>80)&(hsv[:,:,0]<115)
   elif job['mode']=='effect':mask=(r>225)&(g>150)&(b<155)&(hsv[:,:,1]>100)
   else:mask=(hsv[:,:,1]<88)&(hsv[:,:,2]>105)&(hsv[:,:,2]<240)&(b-r>-45)&(b-r<80)
   x1,y1,x2,y2=job['roi'];clipped=np.zeros((450,800),np.uint8);clipped[y1:y2,x1:x2]=mask[y1:y2,x1:x2].astype(np.uint8)*255
   clipped=cv2.morphologyEx(clipped,cv2.MORPH_CLOSE,np.ones((7 if job['mode']=='blue' else 3,)*2,np.uint8))
   contours,_=cv2.findContours(clipped,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE);candidates=[]
   for contour in contours:
    area=cv2.contourArea(contour);x,y,w,h=cv2.boundingRect(contour)
    if area<(160 if job['mode']=='blue' else 500) or w<15 or h<15 or w>330 or h>245:continue
    if x<=x1+1 or y<=y1+1 or x+w>=x2-1 or y+h>=y2-1:continue
    center=np.array([x+w/2,y+h/2])
    score=area/(1+(np.linalg.norm(center-previous_center)/80 if previous_center is not None else 0))
    candidates.append((score,contour,center))
   if candidates:
    _,contour,center=max(candidates,key=lambda x:x[0]);red=resample(contour)
    if red is not None:
     if previous_center is None or np.linalg.norm(center-previous_center)>85:object_id=f'{ident}-component-{t}'
     previous_center=center;observed={'red':red,'blue':box(red),'object':object_id}
     if job.get('roundComparison'):
      (cx,cy),radius=cv2.minEnclosingCircle(contour);observed['teal']=circle(np.array([cx,cy]),radius+3)
      # Use the explained round comparison rather than an unspoken box here.
      observed.pop('blue')
   else:previous_center=None
  else:previous_center=None
  im=Image.fromarray(arr);draw=ImageDraw.Draw(im)
  if observed is not None:
   key={'t':t,'object':observed['object']}
   for color,hexcolor in [('red','#ef5350'),('blue','#42a5f5'),('teal','#26c6b8')]:
    if color not in observed:continue
    polygon=observed[color];key[color]=polygon.tolist();draw.line([tuple(p) for p in np.vstack([polygon,polygon[0]])],fill=hexcolor,width=3)
   keys.append(key)
  draw.text((18,22),f'{ident} source{t:.2f}s / selected screen pixels, draft only',font=font,fill='white',stroke_width=1,stroke_fill='black')
  encoder.stdin.write(im.tobytes())
  if i%30==0:pictures.append((t,im.copy()))
  previous=gray;i+=1
 decoder.stdout.close();assert decoder.wait()==0,decoder.stderr.read().decode()
 encoder.stdin.close();assert encoder.wait()==0,encoder.stderr.read().decode()
 for page in range((len(pictures)+7)//8):
  sheet=Image.new('RGB',(1600,1880),'white');draw=ImageDraw.Draw(sheet)
  for j,(t,im) in enumerate(pictures[page*8:page*8+8]):
   x=j%2*800;y=j//2*470;sheet.paste(im,(x,y+20));draw.text((x+5,y),f'{ident} source{t:.2f}s',font=font,fill='black')
  sheet.save(O/f'{ident}-sheet-{page+1:02}.jpg',quality=95)
 record={'id':ident,'sourceFile':job['file'],'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'sourceInterval':[start,start+duration],'coordinatePixels':[800,450],'samplingSeconds':1/30,'maxInterpolationGapSeconds':.05,'keyframes':keys,'manualHideIntervals':[],'closed':True,'method':'independent observed color component or manual visible corners with bidirectional LK residual rejection','selectionDefinition':'selected visible screen portion, not full hidden object or engine collision data','movingPixelApproval':False,'seedDefinition':job}
 write(T/(ident+'.json'),record);records.append({'id':ident,'sampled':i,'observations':len(keys),'debug':str(out.relative_to(ROOT))});print(json.dumps(records[-1]),flush=True)
write(B/'lines-shape-draft-progress.json',{'records':records,'approved':False})
buttons=''.join(f'<button data-src="{x["id"]}.mp4">{x["id"]}</button>' for x in records)
(O/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>범위 관측 초안</title><style>body{background:#222;color:white;font:16px sans-serif}video{width:min(100%,1100px);display:block}button{padding:8px;margin:4px}</style><h1>실제 보이는 부분의 윤곽·범위 초안</h1>'+buttons+'<video controls muted id="v"></video><script>const v=document.querySelector("video");for(const b of document.querySelectorAll("button"))b.onclick=()=>{v.src=b.dataset.src;v.playbackRate=1;v.play()}</script>',encoding='utf8')
