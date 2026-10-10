"""Manual visible seeds; native-frame CPU tracking, conservative failure hides.

There is no color-based object selection and no engine/world inference. These
remain drafts until final narration, tracked render, captions and motion review.
"""
from pathlib import Path
import json,hashlib,math,argparse
import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
T=B/'planes-tracks';T.mkdir(exist_ok=True)
O=ROOT/'shared/output/game-math-part2-teaching-revision/planes-track-drafts';O.mkdir(parents=True,exist_ok=True)
cv2.setNumThreads(2);font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',14)
base='shared/output/game-math-planes-barycentric/clips/'
src='shared/output/game-math-part2-full-series/sources/'
def circle(x,y,r=4):return [[x+r*math.cos(t),y+r*math.sin(t)] for t in np.linspace(0,2*math.pi,17)[:-1]]
def job(ident,file,a,z,region,shapes,meaning,affine=False):
 return {'id':ident,'file':file,'start':a,'end':z,'region':region,'shapes':shapes,'meaning':meaning,'affine':affine}
jobs=[
 job('02',base+'02.mp4',10,10.8,[[12,194],[320,211],[320,250],[12,234]],{'red':[[12,216],[320,229]]},'Observed near-shore sand/water boundary; no infinite engine plane.'),
 job('05',base+'05.mp4',8,9.5,[[450,245],[615,245],[615,280],[450,280]],{'red':[[456,258],[610,258]],'blue':circle(530,258)},'Visible waterline with an explicitly selected surface reference, not screen-bottom world floor.',True),
 job('08',base+'08.mp4',32.3,32.45,[[324,304],[477,304],[480,350],[325,351]],{'red':[[400,311],[334,347]],'teal':[[400,311],[334,347],[477,347]]},'Visible triangular floor marking; its outline is not asserted to be an engine triangle.'),
 job('11',base+'11.mp4',16,17.2,[[350,232],[443,232],[440,253],[350,254]],{'red':[[350,232],[440,232]],'teal':[[350,232],[440,232],[438,252]]},'Visible wooden platform corners; projected comparison triangle only.',True),
 job('14',base+'14.mp4',12,12.6,[[329,179],[459,180],[460,198],[329,197]],{'red':[[330,191],[459,192]],'blue':circle(455,191,3)},'Visible finite platform front edge; dark/occluded vertices elsewhere rejected.',True),
 job('17',base+'17.mp4',18,18.8,[[296,245],[372,247],[407,267],[319,281]],{'red':[[298,246],[329,227],[372,250]]},'Visible terrain slope/boundary; not color-interpolation engine evidence.',True),
 job('19',base+'19.mp4',24,25.2,[[422,172],[568,171],[568,192],[422,193]],{'red':[[424,189],[566,186]]},'Visible lower/front finite platform boundary; potion-obscured top edges are not traced.',True),
 job('21',base+'21.mp4',47,47.25,[[433,218],[639,225],[637,255],[432,251]],{'red':[[433,218],[639,226]],'teal':[[433,218],[639,226],[635,252]]},'Visible wood platform front/top corner comparison; hide fast approach and weapon afterwards.'),
 job('PG01-gel',src+'portal2-steam-5791.mp4',32,33.5,[[235,100],[358,32],[361,181],[230,263]],{'red':[[225,270],[365,193]],'blue':circle(350,201,3)},'Observed unobscured far portion of the left floor/wall junction and a far reference on that boundary; adjacent coplanar wall features track the same seam; omit the nearer portion crossed by falling gel, no measured player height.'),
 job('PG01-cube',src+'portal2-steam-5788.mp4',21,21.35,[[381,105],[425,105],[425,137],[381,137]],{'blue':circle(402,121,10)},'Visible airborne cube in a new camera shot; no inferred trajectory, launch physics or world coordinates.',True),
 job('PG02-slope',src+'portal2-steam-5795.mp4',35,37,[[24,282],[139,171],[246,129],[280,133],[143,290],[28,352]],{'red':[[80,320],[256,130]]},'Observed exposed white ramp rim, a line rather than a collinear triangle; stop before orange gel crosses its far end; no vertical support or floating offset edge.'),
 job('PG03-panel',src+'portal2-steam-80739.mp4',18.5,18.92,[[236,259],[281,275],[425,269],[376,258]],{'red':[[234,261],[281,276],[425,270]],'teal':[[234,261],[281,276],[425,270]]},'Exposed front edge of left lifting panel; reset at every montage cut and hide robot feet.'),
 job('PG03-door',src+'portal2-steam-5786.mp4',79.5,81.5,[[300,145],[354,123],[354,302],[302,283]],{'red':[[366,108],[366,310]]},'Observed jamb anchored to the adjacent stationary wall while the door opens; not Newell implementation.'),
 job('PG04-floor',src+'portal2-steam-5790.mp4',25,26.5,[[98,345],[161,296],[222,295],[172,347]],{'red':[[124,349],[159,307]]},'Observed gold floor-tile boundary beside the standing turret; not a shadow, inferred step height or passage/collider boundary.'),
 job('PG04-wall',src+'portal2-steam-5790.mp4',50.5,50.85,[[413,197],[445,213],[445,308],[413,281]],{'red':[[414,198],[414,281]],'teal':[[414,198],[445,214],[445,307]]},'Visible wall tile region after debris; comparison triangle on observed corners only.'),
 job('PG06-tile',src+'portal2-steam-5790.mp4',80,80.8,[[118,340],[223,272],[369,272],[313,354]],{'red':[[269,251],[350,252]],'teal':[[269,251],[350,252],[335,272]],'blue':circle(319,263,3)},'Three observed far floor-grid intersections before the portal flash; short local affine comparison must be reviewed in every native frame; illustrative projected triangle, explicitly not real mesh connectivity.',True),
 job('PG06-turret',src+'portal2-steam-5790.mp4',65,66.5,[[384,235],[408,235],[408,261],[384,261]],{'blue':circle(395,248,11)},'Visible airborne turret under the device, distinct from floor; hide at loss of same-object evidence; no same-plane inference.',True),
 job('PG07-pad',src+'portal2-steam-5791.mp4',50,51.5,[[183,189],[313,167],[361,267],[164,311]],{'red':[[164,311],[361,267]],'teal':[[183,189],[313,167],[361,267]]},'Visible finite platform top in the clearer slower view; gel color illustrates location/value distinction, not barycentric gel mechanics.'),
 job('PG07-wall',src+'portal2-steam-5795.mp4',80,80.3,[[331,82],[385,108],[409,113],[412,223],[330,220]],{'red':[[331,83],[410,114],[410,222]]},'Visible blue-coated wall patch boundary before rapid bounce/turn; no calculated world normal.')
]
parser=argparse.ArgumentParser();parser.add_argument('--only',nargs='*');args=parser.parse_args();records=[]
for spec in jobs:
 if args.only and spec['id'] not in args.only:continue
 ident=spec['id'];file=ROOT/spec['file'];cap=cv2.VideoCapture(str(file));fps=cap.get(cv2.CAP_PROP_FPS)
 first=math.ceil(spec['start']*fps-1e-7);last=math.floor(spec['end']*fps+1e-7);cap.set(cv2.CAP_PROP_POS_FRAMES,first)
 points={k:np.array(v,np.float32).reshape(-1,1,2) for k,v in spec['shapes'].items()}
 region=np.array(spec['region'],np.float32).reshape(-1,1,2);features=None;previous=None;keys=[];pictures=[];rejected=[]
 required=3 if spec['affine'] else 8
 for index in range(first,last+1):
  ok,frame=cap.read();assert ok,(ident,index)
  frame=cv2.resize(frame,(800,450));gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY);t=index/fps;valid=True;failure={}
  if previous is not None:
   if features is None or len(features)<required:valid=False;failure={'features':0 if features is None else len(features),'required':required}
   else:
    moved,status,error=cv2.calcOpticalFlowPyrLK(previous,gray,features,None,winSize=(25,25),maxLevel=3)
    back,bst,_=cv2.calcOpticalFlowPyrLK(gray,previous,moved,None,winSize=(25,25),maxLevel=3)
    good=(status.ravel()>0)&(bst.ravel()>0)&(error.ravel()<23)&(np.linalg.norm(back-features,axis=2).ravel()<1.1)
    if good.sum()<required:valid=False;failure={'bidirectionalGood':int(good.sum()),'features':len(features),'required':required}
    else:
     if spec['affine']:
      mat,inliers=cv2.estimateAffinePartial2D(features[good],moved[good],method=cv2.RANSAC,ransacReprojThreshold=1.3)
      H=np.vstack([mat,[0,0,1]]) if mat is not None else None
     else:H,inliers=cv2.findHomography(features[good],moved[good],cv2.RANSAC,1.8)
     if H is None or inliers.sum()<required:valid=False;failure={'inliers':0 if inliers is None else int(inliers.sum()),'required':required}
     else:
      changed=cv2.perspectiveTransform(region,H);ratio=abs(cv2.contourArea(changed))/max(abs(cv2.contourArea(region)),1)
      if not .8<ratio<1.25 or np.max(np.linalg.norm(changed-region,axis=2))>35:valid=False;failure={'areaRatio':ratio,'maxMove':float(np.max(np.linalg.norm(changed-region,axis=2)))}
      else:region=changed;points={k:cv2.perspectiveTransform(p,H) for k,p in points.items()}
  if not valid:
   rejected.append({'sourceTime':t,'reason':'Native motion/forward-backward/homography evidence insufficient; hide instead of extrapolation.','diagnostics':failure});break
  mask=np.zeros((450,800),np.uint8);cv2.fillPoly(mask,[region.reshape(-1,2).astype(np.int32)],255)
  features=cv2.goodFeaturesToTrack(gray,150,.003,3,mask=mask,blockSize=3)
  shapes={k:p.reshape(-1,2) for k,p in points.items()}
  if ident in ['PG01-gel','PG02-slope','PG04-floor']:
   # Clip only the visible portion of the already tracked physical seam.
   # The nearer end leaves the caption-safe picture before the far end.
   if 'red' in shapes:
    visible,p0,p1=cv2.clipLine((3,45,794,310),tuple(np.rint(shapes['red'][0]).astype(int)),tuple(np.rint(shapes['red'][1]).astype(int)))
    if visible:shapes['red']=np.array([p0,p1],np.float32)
    else:shapes.pop('red')
   if 'blue' in shapes and np.any(shapes['blue'][:,1]>355):shapes.pop('blue')
   if not shapes:break
  if any(np.any(p[:,0]<3) or np.any(p[:,0]>797) or np.any(p[:,1]<45) or np.any(p[:,1]>355) for p in shapes.values()):
   rejected.append({'sourceTime':t,'reason':'Observed geometry leaves safe picture/caption region; hide.'});break
  row={'t':round(t,6),'nativeFrame':index,'object':ident+'-observed-patch',**{k:p.tolist() for k,p in shapes.items()}};keys.append(row)
  im=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB));draw=ImageDraw.Draw(im)
  for k,c in [('red','#ef5350'),('blue','#42a5f5'),('teal','#26c6b8')]:
   if k in shapes:
    p=shapes[k];draw.line([tuple(x) for x in np.vstack([p,p[0]])],fill=c,width=3)
  draw.text((10,45),f'{ident} native {t:.3f}s / draft observed screen geometry',font=font,fill='white',stroke_width=1,stroke_fill='black')
  pictures.append((t,im));previous=gray
 cap.release();pages=[]
 for page in range(math.ceil(len(pictures)/8)):
  sheet=Image.new('RGB',(1600,1880),'white');draw=ImageDraw.Draw(sheet)
  for cell,(t,im) in enumerate(pictures[page*8:page*8+8]):
   x=cell%2*800;y=cell//2*470;sheet.paste(im,(x,y+20));draw.text((x+5,y),f'{ident} native {t:.3f}s',font=font,fill='black')
  p=O/f'{ident}-fine-{page+1:02}.jpg';sheet.save(p,quality=95);pages.append(p.relative_to(ROOT).as_posix())
 record={'id':ident,'sourceFile':spec['file'],'sourceSha256':hashlib.sha256(file.read_bytes()).hexdigest(),'coordinatePixels':[800,450],'nativeFps':fps,'nativeFirstFrame':first,'sourceInterval':[spec['start'],spec['end']],'keyframes':keys,'maxInterpolationGapSeconds':1.1/fps,'manualHideIntervals':[],'closed':True,'seedDefinition':spec,'meaning':spec['meaning'],'trackingMethod':'Manually observed source seed, exact native frame indices, CPU bidirectional LK and robust planar homography/2D affine; stop at first rejection. No extrapolation.','rejected':rejected,'movingPixelApproval':False}
 (T/f'{ident}.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 records.append({'id':ident,'observedFrames':len(keys),'fps':fps,'pages':pages,'finalMovingPixelApproval':False});print(json.dumps(records[-1]),flush=True)
index_path=O/'index.json'
older=json.loads(index_path.read_text(encoding='utf8')).get('records',[]) if index_path.exists() else []
updated={r['id']:r for r in older}
updated.update({r['id']:r for r in records})
index_path.write_text(json.dumps({'records':list(updated.values()),'approval':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
