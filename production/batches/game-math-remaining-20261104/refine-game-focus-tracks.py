"""Additive repairs selected by actual source/temporal inspection; QA remains pending."""
from pathlib import Path
import copy,json,math,sys
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
sys.path.insert(0,str(R/'projects/game-math-euler-axis-angle/production/local/revision-v3/deps'))
import cv2
from PIL import Image,ImageDraw,ImageFont
cv2.setNumThreads(2)
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
old=B/'local/annotation-tracking-v1';out=B/'local/annotation-tracking-v2';out.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def trim(d,end):
 d['end']=min(end,d['end']);d['keyframes']=[k for k in d['keyframes'] if k['time']<=d['end']];d['end']=d['keyframes'][-1]['time'];return d
def manual(d,keys,hidden=()):
 fps=d['fps'];d['start']=round(keys[0][0]*fps)/fps;d['end']=round(keys[-1][0]*fps)/fps;d['keyframes']=[]
 for frame in range(round(d['start']*fps),round(d['end']*fps)+1):
  t=frame/fps;j=next((i for i in range(1,len(keys)) if keys[i][0]>=t),len(keys)-1);ta,a=keys[j-1];tb,b=keys[j];u=max(0,min(1,(t-ta)/(tb-ta)))
  box=[round(x+(y-x)*u,2) for x,y in zip(a,b)]
  d['keyframes'].append(dict(time=t,bbox=box,visible=not any(lo<=t<=hi for lo,hi in hidden)))
 d['method']='Manually inspected screen-space extent, linearly interpolated at native fps; editorial guide, not game measurement'
 return d
records=[]
for source in sorted(old.glob('M*.json')):
 d=read(source);sid=d['id'];target=out/(sid+'.json');assert not target.exists(),'Preserve existing revision'
 d['priorTrack']=source.relative_to(R).as_posix();d['visualQa']='pending-after-repair';d['repair']='Original native-fps track retained after temporal sample inspection'
 if sid=='M25-000':
  manual(d,[(59.683,[650,480,640,520]),(60.433,[660,480,640,540]),(60.933,[680,450,610,580]),(61.683,[740,455,515,585]),(62.433,[750,465,500,590]),(63.183,[760,440,510,600]),(63.683,[750,420,510,550]),(63.933,[700,300,590,510]),(64.467,[650,450,620,550])]);d['repair']='Replaced repeated boundary-hide flicker by inspected car extents through the full takeoff/landing'
 elif sid=='M25-021':
  manual(d,[(213.95,[430,380,470,570]),(214.45,[430,380,470,570]),(214.7,[400,285,550,520]),(214.95,[470,70,480,700]),(215.2,[480,400,460,520]),(215.45,[460,350,470,580]),(215.7,[430,380,470,560]),(216.2,[420,380,480,560]),(216.45,[400,280,560,550]),(216.7,[430,65,520,710]),(216.95,[430,350,480,590]),(217.3,[430,340,490,600])]);d['repair']='Automatic track drifted below the skier during front flips; manually keyed observed whole-body extents'
 elif sid=='M26-011':d['label']='회전해 세운 돛';d['repair']='Label names the observed upright result; native earlier turn remains in the source cut'
 elif sid=='M27-000':d['label']='바퀴의 접촉 상태';d['repair']='Names contact state including loss of ground support, not continuous contact'
 elif sid=='M28-000':trim(d,10.45);d['repair']='Cleared before small wheel target became ambiguous in the later bounce'
 elif sid=='M29-000':
  post=copy.deepcopy(d);post['id']=sid+'-after';post['label']='충돌 후 변형된 차체'
  manual(post,[(32.2,[580,420,590,420]),(32.45,[810,300,520,400]),(32.7,[1030,310,520,430]),(32.95,[1160,300,500,440]),(33.2,[1160,310,560,350]),(33.45,[1260,355,455,360])]);post['repair']='New post-cut manual extent follows recognizable main body; detached debris is not represented as the body';records.append(post)
  trim(d,31.2);d['label']='충돌 전의 차체';d['repair']='Clear before the actual source camera cut; separate post-impact guide rather than carrying tracking across the cut'
 elif sid=='M29-018':
  manual(d,[(1446.467,[630,280,640,730]),(1446.967,[610,280,650,730]),(1447.467,[620,280,660,730]),(1447.967,[640,280,650,730]),(1448.25,[640,280,650,730])]);d['label']='충돌 전의 발사 준비';d['repair']='Stable observed body extent removes edge-hide flicker; clear before release and dust occlusion'
 elif sid=='M31-000':trim(d,709.05);d['repair']='Clear before subsequent camera viewpoint change'
 elif sid=='M31-012':trim(d,95.05);d['label']='이동 경로의 출발점';d['repair']='Observed launch-star target; no claim that the user edits the trajectory. Clear before top-edge clipping'
 elif sid=='M31-027':
  manual(d,[(271.438,[810,360,350,230]),(273.73,[810,360,350,230])],[(272.56,273.27)]);d['label']='선로 끝을 지정하는 조준점';d['repair']='Rejected terrain-drifting tracker. Mark observed center cursor/endpoint region; hide while no valid rail hologram is visible'
 records.append(d)
for d in records:
 sid=d['id'];images=[];cap=cv2.VideoCapture(str(R/d['sourceFile']));assert cap.isOpened();fps=d['fps']
 samplekeys=d['keyframes'][::max(1,round(fps/8))] # repairs checked more densely than initial candidates
 if samplekeys[-1]!=d['keyframes'][-1]:samplekeys.append(d['keyframes'][-1])
 for k in samplekeys:
  cap.set(cv2.CAP_PROP_POS_FRAMES,round(k['time']*fps));ok,f=cap.read();assert ok
  im=Image.fromarray(cv2.cvtColor(f,cv2.COLOR_BGR2RGB));dr=ImageDraw.Draw(im)
  if k['visible']:
   x,y,w,h=k['bbox'];dr.ellipse((x,y,x+w,y+h),outline='#101010',width=18);dr.ellipse((x+4,y+4,x+w-4,y+h-4),outline='#73C7C2',width=10)
  im=im.resize((480,270));dr=ImageDraw.Draw(im);dr.rectangle((0,0,480,22),fill='black');dr.text((4,1),f'{sid} {k["time"]:.3f} '+('' if k['visible'] else 'HIDDEN'),font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',13),fill='white');images.append(im)
 cap.release();d['sheets']=[]
 for n in range(0,len(images),16):
  tiles=images[n:n+16];board=Image.new('RGB',(1920,math.ceil(len(tiles)/4)*270))
  for j,im in enumerate(tiles):board.paste(im,((j%4)*480,(j//4)*270))
  path=out/f'{sid}-{n//16+1:02}.jpg';board.save(path,quality=96);d['sheets'].append(path.relative_to(R).as_posix())
 d['failedSamples']=sum(not k['visible'] for k in d['keyframes']);d['sampleFrames']=len(images);save(out/(sid+'.json'),d);print(sid,len(images),flush=True)
save(out/'manifest.json',dict(status='refined-candidates-awaiting-actual-inspection',records=[dict(id=d['id'],file=(out/(d['id']+'.json')).relative_to(R).as_posix(),sheets=d['sheets']) for d in records]))
