"""Retain the existing lesson; bind genuine game images to its objects and math.

All expensive jobs require --render. Preparation is never a delivery/QA pass.
"""
import sys,json,math,shutil,subprocess,uuid,os,time,html
from pathlib import Path
from PIL import Image
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OLD=HERE.parent/'revision-teaching-sync-20261115'
# Reuse the old renderer helpers without shadowing this revision's progress.py.
if str(OLD) not in sys.path:sys.path.append(str(OLD))
import render_revision as prior
from inventory import read,save,sha
from boards import Board,GOLD,TEAL,WHITE,MUTED,RED,cue
from motion_panels import line,dot,arrow
import motion_positions as motion
import resource_guard
FF=prior.FF;REV='game-subjects-v4'
DEST=Path(os.environ['LOCALAPPDATA'])/'YamyamCoding/VideoEditingOutputs/game-math-subjects-20261115-final'
WORK=Path(os.environ['LOCALAPPDATA'])/'YamyamCoding/VideoEditingWork/game-math-subjects-20261115-final'
EPISODES={e['id']:e for e in read(OLD/'inventory.json')['episodes']}
ASSETS={a['id']:a for a in read(HERE/'assets.json')}

# Contexts are mapped to the actual subject, not added as decorative thumbnails.
# (episode, scenes, asset, caption, semantic correspondence, viewport)
CONTEXTS=[
 ('M26',['017'],'windmill-context','Besiege · 회전하는 풍차','날개 끝 → 원 위의 점',[80,620,390,210]),
 ('M27',['001','003','023','024'],'beamng-context','BeamNG.drive · 차량과 지면','차량 → 물체 / 지면과의 접촉 → 마찰',[80,650,475,215]),
 ('M28',['002'],'chomp-context','Super Mario Odyssey · 멍멍이','당겨진 멍멍이 → 질량 / 되돌아감 → 복원 운동',[1180,550,620,300]),
 ('M29',['006','019','021','022'],'collision-context','Super Mario Odyssey · 충돌','게임의 물체 → 단순화한 두 충돌 물체',[1280,435,480,245]),
 ('M30',['017','057','058','059'],'beamng-context','BeamNG.drive · 차량','실제 차량 → 부품별 질량으로 단순화',[1180,470,620,230]),
 ('M31',['001','005','013','033','034'],'train-context','Satisfactory · 철도 경로','열차가 지나는 경로 → p(t) / 진행 방향 → 접선',[1110,535,700,320]),
 ('M32',['001','003','010','015','029'],'maker-context','Super Mario Maker 2 · 경로 편집','실제 경로의 예시 / Bézier 제어점은 해설 모형',[1190,500,570,310]),
 ('M33',['003','018','020','024','026','042'],'train-context','Satisfactory · 이어지는 선로','선로의 연결 → 곡선 조각의 연결',[1190,420,620,195])
]

def work(e):
 p=WORK/e['slug'];p.mkdir(parents=True,exist_ok=True);return p
def latest(e,kind='clean'):
 return ROOT/'output'/(e['slug']+'-teaching-sync-v2')/(e['slug']+'.'+kind+('.srt' if kind in ('ko','en') else '.mp4'))
def cuts(e):
 if e['id']=='M21':return []
 q=read(ROOT/'projects'/e['slug']/'production/local'/e['baselineRevision']/'queue.json')
 return [(2+c['globalStartFrame']/60,2+(c['globalStartFrame']+c['frames'])/60) for c in q['cuts'] if c['kind']=='actual-gameplay']
def blocked(t,intervals):return any(a<=t<b for a,b in intervals)
def lesson_phase(l,t):
 u=float(np.interp(t,l['stepSeconds'],l['stepPositions'])) if l.get('stepSeconds') else t/l['durationSeconds']
 n=len(l['steps']);i=min(n-1,int(u*n));return l['steps'][i],min(1,u*n-i)
def mechanics_at(l,t):
 s,u=lesson_phase(l,t);m=s['model'];t=m.get('timeStart',0)+(m.get('timeEnd',3)-m.get('timeStart',0))*u
 x,y=-4.7,.1;p=m.get('picture',0);scale=m.get('worldScale',1);value=velocity=None
 if p==4:
  g=2*m.get('jumpHeight',2)/m.get('apexSeconds',.4)**2;y+=(g*m.get('apexSeconds',.4)*t-g*t*t/2)*scale-.3
 elif p==10:
  acceleration=(m.get('forceX',6)-m.get('opposingForce',2))/m.get('mass',2)
  distance=m.get('initialVelocity',0)*t+.5*acceleration*t*t
  x+=distance*scale-2
 elif p==11:x+=(-1.3-.5*m.get('forceX',6)/m.get('mass',2)*t*t*scale)
 elif p==12:
  if not m.get('showObserverFrame'):x+=m.get('frameVelocity',0)*t*scale;y+=.5*m.get('frameAcceleration',0)*t*t*scale
 elif p==6:
  mass=m.get('mass',2);k=m.get('k',16);c=m.get('c',4);x0=m.get('x0',1);v0=m.get('v0',0);w=math.sqrt(k/mass);zeta=c/(2*mass*w)
  if zeta<1-1e-8:
   wd=w*math.sqrt(1-zeta*zeta);b=(v0+zeta*w*x0)/wd;inside=x0*math.cos(wd*t)+b*math.sin(wd*t);value=math.exp(-zeta*w*t)*inside;velocity=math.exp(-zeta*w*t)*(-x0*wd*math.sin(wd*t)+b*wd*math.cos(wd*t)-zeta*w*inside)
  elif zeta<=1+1e-8:
   b=v0+w*x0;value=(x0+b*t)*math.exp(-w*t);velocity=(b-w*(x0+b*t))*math.exp(-w*t)
  else:
   r1=-w*(zeta-math.sqrt(zeta*zeta-1));r2=-w*(zeta+math.sqrt(zeta*zeta-1));a=(v0-r2*x0)/(r1-r2);value=a*math.exp(r1*t)+(x0-a)*math.exp(r2*t);velocity=r1*a*math.exp(r1*t)+r2*(x0-a)*math.exp(r2*t)
  x+=value*scale
 else:raise ValueError(('Unported robot mechanics model',p))
 return dict(x=960+96*x,y=540-96*y,model=m,t=t,springX=value,springV=velocity)

def segment_ranges(e,s,exclusions):
 # Split at exact original gameplay boundaries. Added paired games are composited
 # later and hide these subject layers together with the prior native scene.
 a,z=s['start'],s['end'];edges=sorted(set([a,z]+[t for pair in exclusions for t in pair if a<t<z]));return [(x,y) for x,y in zip(edges,edges[1:]) if not blocked((x+y)/2,exclusions)]

def tracks(e):
 result=[];exclude=cuts(e)
 for s in e['scenes']:
  l=s.get('currentTeaching') or {};eid=e['id'];asset=None;mode=None
  if eid in ('M24','M25','M26') and motion.visible(l):
   mode='motion';asset='mario' if eid=='M24' else 'forza' if eid=='M26' else 'kart'
   if eid=='M24' and s['scene'] in ('010','015'):asset='forza'
   if eid=='M25' and l['motion']['parameters'].get('kind')==3:asset='mario'
  elif eid=='M22' and s['scene'] in ('001','002','003','008','009','013','014','035'):mode='portrait';asset='mario'
  elif eid=='M22' and s['scene'] in ('015','017','018','022','034'):
   mode='surface-code' if s['scene'] in ('017','034') else 'surface';asset='doom-context'
  elif eid=='M23' and s['scene'] not in ('000','016','018','021','037','041','053','054','055','056','057','062','063','064','065','066'):
   mode='pipeline' if s['scene'] in ('001','002','003','004','006','014','023','034','050','060','061') else 'pipeline-clear';asset='mario' if s['scene']=='050' else 'town-context'
  elif eid=='M27' and s['scene'] in ('009','011','014','021','022'):mode='mechanics-jump' if s['scene'] in ('021','022') else 'mechanics';asset='beamng' if s['scene']=='021' else 'mario'
  elif eid=='M28' and s['scene'] in ('010','024'):mode='mechanics';asset='beamng'
  if not mode:continue
  for a,z in segment_ranges(e,s,exclude):result.append(dict(scene=s['scene'],start=a,end=z,mode=mode,asset=asset,lesson=l))
 return result

def anchor(track,t,fitting=None):
 if track['mode']=='motion':return motion.at(track['lesson'],t-track.get('sceneStart',track['start']),fitting)
 if track['mode'].startswith('mechanics'):return mechanics_at(track['lesson'],t-track.get('sceneStart',track['start']))
 return dict(x=600 if track['mode']=='portrait' or track['mode'].startswith('surface') else 500,y=535)

def unitguide(m,e):
 return e['id'] in ('M25','M26') and m.get('showVelocity',True) and m.get('showAcceleration',False) and not m.get('scalarFunction')
def maxima(lesson):
 models=[lesson['motion']]+[s['motionOverride'] for s in lesson['steps'] if s.get('useMotionOverride')]
 result=[0.,0.]
 for m in models:
  for t in np.linspace(m.get('startTime',0),m.get('endTime',3),161):
   _,v,a,valid=motion.state(m['parameters'],float(t))
   if valid:result=[max(result[0],np.linalg.norm(v)),max(result[1],np.linalg.norm(a))]
 return result
def text_now(b,x,y,value,a,z,color,size=42):
 b.event(a,z,r'{\an7\pos('+f'{x:.2f},{y:.2f}'+r')\fs'+str(size)+r'\1c&H'+color+r'&\bord0\shad0}'+value,5)

def mechanics_guides(b,background,q,lesson,a,z):
 m=q['model'];kind=m['picture'];cx,cy=q['x'],q['y'];t=q['t']
 if kind in (4,10):line(background,[(124.8,592.8),(892.8,592.8)],a,z,MUTED,5)
 if kind==10:
  acceleration=(m.get('forceX',6)-m.get('opposingForce',2))/m.get('mass',2);velocity=m.get('initialVelocity',0)+acceleration*t
  items=[('가속도 a',acceleration*m.get('accelerationScale',.15)*96,(cx+80,cy-164),(650,cy-190),RED),('속도 v',velocity*m.get('velocityScale',.3)*96,(cx+80,cy-96),(650,cy-120),'A0C6A4'),('지면의 힘 F₁',m.get('forceX',6)*m.get('forceScale',.12)*96,(cx+80,cy+20),(650,cy-5),TEAL),('상자의 힘 F₂',-m.get('opposingForce',2)*m.get('forceScale',.12)*96,(cx-80,cy+20),(90,cy+100),GOLD)]
  for name,length,tail,label,color in items:
   tip=(tail[0]+length,tail[1]);line(b,[(cx,cy),tail],a,z,MUTED,2);arrow(b,tail,tip,a,z,color,6);line(b,[tip,(label[0]-10,label[1]+25)],a,z,MUTED,2);text_now(b,*label,name,a,z,color,38)
  dot(b,cx,cy,a,z,TEAL,8)
 elif kind==11:
  force=m.get('forceX',4);other=960+96*(-4.7+1.3+.5*force/m.get('secondaryMass',4)*t*t*m.get('worldScale',1));centre=(m.get('mass',2)*cx+m.get('secondaryMass',4)*other)/(m.get('mass',2)+m.get('secondaryMass',4))
  line(background,[(centre,348),(centre,732)],a,z,MUTED,2)
  tail=(cx-65,cy);tip=(tail[0]-force*m.get('forceScale',.12)*96,cy)
  line(b,[(cx,cy),tail],a,z,MUTED,2);arrow(b,tail,tip,a,z,TEAL,6);text_now(b,90,650,'상자가 미는 힘 F_A',a,z,TEAL,36);line(b,[tip,(270,640)],a,z,MUTED,2);text_now(b,max(90,cx-90),cy-150,'사람 · 마리오',a,z,WHITE,34)
 elif kind==12:
  scale=m.get('worldScale',1);shiftx=-m.get('frameVelocity',0)*t if m.get('showObserverFrame') else 0;shifty=-.5*m.get('frameAcceleration',0)*t*t if m.get('showObserverFrame') else 0
  ox=960+96*(-4.7+1.5+shiftx*scale);oy=540-96*(.1+(-.5*m.get('gravity',9.8)*t*t+shifty)*scale)
  line(background,[(cx-96,cy-182.4),(cx-96,cy+67.2),(cx+211.2,cy+67.2),(cx+211.2,cy-182.4)],a,z,MUTED,4)
  text_now(b,cx-75,cy-160,'관찰자 · 마리오',a,z,TEAL,34)
  line(b,[(ox-19,oy-19),(ox+19,oy-19),(ox+19,oy+19),(ox-19,oy+19),(ox-19,oy-19)],a,z,GOLD,5)
  text_now(b,min(760,ox+35),min(780,oy-55),'낙하 물체',a,z,GOLD,34)
  acceleration=-m.get('gravity',9.8)-(m.get('frameAcceleration',0) if m.get('showObserverFrame') else 0)
  if abs(acceleration)>1e-8:arrow(b,(ox,oy),(ox,oy-acceleration*m.get('accelerationScale',.15)*96),a,z,RED,6)
  text_now(b,90,830,'빨강: 상대가속도' if abs(acceleration)>1e-8 else '상대가속도 0 · 같은 기준에서 함께 낙하',a,z,RED if abs(acceleration)>1e-8 else GOLD,34)
 elif kind==4:
  models=[x['model'] for x in lesson['steps']];maxv=max(2*x.get('jumpHeight',2)/x.get('apexSeconds',.4) for x in models);maxa=max(2*x.get('jumpHeight',2)/x.get('apexSeconds',.4)**2 for x in models)
  g=2*m.get('jumpHeight',2)/m.get('apexSeconds',.4)**2;velocity=g*(m.get('apexSeconds',.4)-t)
  for tail,tip,color,label,pos in [((cx-90,cy),(cx-90,cy-velocity/maxv*150),TEAL,'v · 속도',(700,350)),((cx+100,cy),(cx+100,cy+g/maxa*140),RED,'a · 가속도',(700,700))]:
   line(b,[(cx,cy),tail],a,z,MUTED,2);arrow(b,tail,tip,a,z,color,6);line(b,[tip,(pos[0]-15,pos[1]+25)],a,z,MUTED,2);text_now(b,*pos,label,a,z,color,40)
  dot(b,cx,cy,a,z,TEAL,8);text_now(b,90,830,'화살표 축척은 이 장면 안에서 고정',a,z,MUTED,30)

def prepare(e,origin=0,end=None):
 p=work(e);ts=tracks(e);ss={s['scene']:s for s in e['scenes']}
 if end is None:end=e['scenes'][-1]['end']+10
 for t in ts:t['sceneStart']=ss[t['scene']]['start']
 board=Board();postboard=Board();contexts=[]
 groups={}
 for t in ts:
  if t['start']>=end or t['end']<=origin:continue
  groups.setdefault((t['asset'],t['mode']),[]).append(t)
 extra=[];parts=[];evidence=[]
 for j,((asset,mode),items) in enumerate(groups.items()):
  # Commands use absolute main-picture timestamps, including sample seeks.
  cmds=[];last=None;af=ASSETS[asset];iw,ih=af['dimensions'];pathboard=Board();pathruns=[]
  if mode=='portrait':height=290
  elif mode=='mechanics-jump':height=116
  elif mode.startswith('surface'):height=230
  elif mode.startswith('pipeline'):height=235
  else:height=170 if asset in ('mario','kart') else 140
  width=round(iw*height/ih);width+=width%2;height+=height%2
  eraser=(420,400) if mode=='portrait' or mode.startswith('surface') else (300,400) if mode.startswith('pipeline') else (150,154)
  for t in items:
   fit=motion.fit(t['lesson']) if mode=='motion' else None;a=max(origin,t['start']);z=min(end,t['end']);limits=maxima(t['lesson']) if mode=='motion' else None;run=None
   hide_subject=e['id']=='M24' and t['scene'] in ('021','023','030')
   label={'mario':'Super Mario Odyssey · 위치를 나타내는 게임 이미지','kart':'Mario Kart 8 Deluxe · 카트의 운동 모형','forza':'Forza Horizon 5 · 코너링을 단순화한 모형','beamng':'BeamNG.drive · 차량의 운동 모형','town-context':'Townscaper · 실제 게임 이미지','doom-context':'Doom 3 · 금속 벽의 표면'}[asset]
   if asset=='forza' and e['id']=='M24':label='Forza Horizon 5 · 차의 위치·속도를 단순화한 모형'
   if mode not in ('portrait','pipeline','pipeline-clear','surface','surface-code'):
    board.rectangle(1180,30,720,147,a,z)
    board.text(1200,44,'수학적 관계를 나타내는 해설 모형' if hide_subject else label,a,z,GOLD,34,width=685)
    board.text(1200,127,'조건을 고정한 원리 설명' if hide_subject else '게임 이미지 + 해설 모형',a,z,WHITE,32,width=680)
   elif mode=='portrait':
    board.rectangle(350,510,55,95,a,z)
    board.text(398,716,'실제 마리오의 팔 → 오른쪽 관절 모형',a,z,GOLD,32,width=600)
    dot(board,638,535,a,z,TEAL,10);line(board,[(638,535),(790,410)],a,z,TEAL,4);board.text(750,360,'팔꿈치',a,z,TEAL,40,width=200)
   elif mode.startswith('surface'):
    board.rectangle(350,510,55,95,a,z)
    postboard.rectangle(75,200,900,90,a,z)
    postboard.text(85,210,'Doom 3의 금속 표면 → 오른쪽 해설 모형',a,z,WHITE,36,width=890)
    if mode!='surface-code':board.text(398,716,'실제 게임 표면과 노멀 계산의 대응',a,z,GOLD,32,width=600)
    if mode=='surface-code':
     labels=['Linear data','Decode XYZ','Normalize','TBN → Lighting'] if t['scene']=='017' else ['UV · 접선 · 부호 검증','노멀 데이터 읽기','TBN으로 표면의 기저에 맞추기','빛과 내적해 표면 표현']
     for n0,label0 in enumerate(labels):board.text(90,310+n0*87,label0,a,z,TEAL if n0==3 else WHITE,36,width=580)
   elif mode.startswith('pipeline'):
    board.rectangle(75,200,900,90,a,z)
    board.text(85,210,'캐릭터의 정점과 표면 데이터를 연결합니다' if asset=='mario' else '같은 물체와 카메라에서 살펴봅니다',a,z,WHITE,36,width=890)
    if mode=='pipeline':board.text(360,715,'게임의 캐릭터 → 본·표면·픽셀' if asset=='mario' else '게임의 건물 → 정점·삼각형·픽셀',a,z,GOLD,30,width=620)
    if asset=='mario':
     stages=[('Skinning (스키닝)','본으로 정점의 위치를 움직임'),('Normal Mapping (노멀 매핑)','그 표면에서 작은 방향을 복원'),('Pixel Shading (픽셀 셰이딩)','빛과 재질로 최종 색을 계산')]
     for index,(name,meaning) in enumerate(stages):
      yy=300+index*145
      line(board,[(1010,yy),(1775,yy),(1775,yy+106),(1010,yy+106),(1010,yy)],a,z,MUTED,3)
      board.text(1030,yy+5,name,a,z,WHITE,44,width=730)
      board.text(1030,yy+57,meaning,a,z,TEAL,36,width=730)
      if index<2:arrow(board,(1390,yy+108),(1390,yy+140),a,z,TEAL,4)
     dot(board,531,535,a,z,TEAL,9)
     line(board,[(531,535),(900,535),(995,350)],a,z,TEAL,3)
   if mode=='mechanics-jump':
    board.text(90,205,'오른쪽 +x · 위쪽 +y · 시간 s · 거리 m',a,z,MUTED,30,width=930)
    board.text(90,250,'청록: 속도 v · 빨강: 가속도 a',a,z,MUTED,30,width=930)
   elif mode.startswith('mechanics') and t['lesson']['steps'][0]['model']['picture']==12:
    board.text(90,205,'오른쪽 +x · 위쪽 +y · 시간 s · 거리 m',a,z,MUTED,30,width=930)
    board.text(90,250,'청록: 관찰자 · 노랑: 물체 · 빨강: 상대가속도',a,z,MUTED,30,width=930)
   if e['id']=='M24' and t['scene']=='004':
    board.rectangle(80,470,930,70,a,z)
    board.text(90,480,'캐릭터 몸 가운데의 한 점을 추적합니다',a,z,WHITE,40,width=930)
   for k in range(round(a*60),round(z*60)):
    sec=k/60;q=anchor(t,sec,fit);cx,cy=q['x'],q['y']
    # A scalar plot intentionally hides its actor; retain that decision.
    if mode=='motion' and q['model'].get('scalarFunction'):cx=cy=-2000
    sx=round(cx-width*.5);sy=round(cy-height*.55)
    if mode.startswith('mechanics') and q['model']['picture']!=6:sy=round(cy+(33.6 if q['model']['picture']==4 else 62.4)-height)
    if mode=='surface-code':
     sx+=220;sy=295
    ex=round(cx-eraser[0]/2);ey=round(cy-eraser[1]/2);ew,eh=eraser
    if mode=='surface-code':ex,ey,ew,eh=75,300,780,435
    if hide_subject:ex,ey,ew,eh=75,535,925,260;sx=-2200
    spring=mode.startswith('mechanics') and q['model'].get('picture')==6
    if spring:ex,ey,ew,eh=80,335,920,350
    if mode.startswith('mechanics') and q['model']['picture'] in (4,10,12):ex,ey,ew,eh=80,300,920,625
    if mode=='mechanics-jump' or (mode.startswith('mechanics') and q['model']['picture']==12):ex,ey,ew,eh=70,195,930,730
    if mode.startswith('mechanics') and q['model']['picture']==11:ex,ey,ew,eh=80,330,480,385
    ug=mode=='motion' and unitguide(q['model'],e)
    if ug and cx>0:ex,ey,ew,eh=80,535,920,260
    if mode=='pipeline-clear':sx=-2200
    current=(ex,ey,sx,sy,ew,eh)
    if current!=last:
     cmds.append(f'{max(0,sec-.0001):.6f} drawbox@erase{j} x {ex},drawbox@erase{j} y {ey},drawbox@erase{j} w {ew},drawbox@erase{j} h {eh},overlay@subject{j} x {sx},overlay@subject{j} y {sy};');last=current
    signature=json.dumps(q.get('model',{}),sort_keys=True) if ug else None
    if signature!=(run[0] if run else None):
     if run:pathruns.append((run[1],sec,run[2],fit));run=None
     if signature:run=(signature,sec,q['model'])
    if k%3==0 and spring:
     hi=min(z,sec+.05);start=(220.8,530.4);stop=(cx-57.6,cy)
     points=[(start[0]+(stop[0]-start[0])*(.08+.84*i/80),start[1]-16.32*math.sin(i/80*math.pi*20)) for i in range(81)]
     line(pathboard,[start,*points,stop],sec,hi,WHITE,4);line(pathboard,[(start[0],492),(start[0],568)],sec,hi,WHITE,5)
     for force,tail_y,color,name in [(-q['model'].get('k',16)*q['springX'],410,TEAL,'복원력 Fₛ = −kx'),(-q['model'].get('c',4)*q['springV'],620,GOLD,'감쇠력 Fd = −cv')]:
      tail=(cx,tail_y);line(board,[(cx,cy),tail],sec,hi,MUTED,2);arrow(board,tail,(cx+force*q['model'].get('forceScale',.12)*96,tail_y),sec,hi,color,6)
      text_now(board,90,360 if tail_y==410 else 642,name,sec,hi,color,40)
    if k%3==0 and mode.startswith('mechanics') and q['model']['picture'] in (4,10,11,12):mechanics_guides(board,pathboard,q,t['lesson'],sec,min(z,sec+.05))
    # Editorial vectors are mathematically coupled to the same native point.
    if k%3==0 and mode=='motion' and cx>0 and not hide_subject:
     hi=min(z,sec+.05);dot(board,cx,cy,sec,hi,TEAL,8)
     m=q['model']
     for field,visible,scale,color in [('velocity','showVelocity','velocityArrowScale',TEAL),('acceleration','showAcceleration','accelerationArrowScale',RED)]:
      if m.get(visible,field=='velocity') and q['valid']:
       v=motion.raw(m,q[field])
       if ug:
        vel=field=='velocity';side=-1 if vel else 1
        if m.get('graphY'):tail=(cx+side*56,max(578,min(650,cy)))
        else:tail=(max(180,min(770,cx+32)),max(600,min(708,cy+side*33)))
        limit=limits[0 if vel else 1]
        if m.get('beatId') in ('M25-002','M25-012','M25-013'):limit=max(abs(m.get('velocityMin' if vel else 'accelerationMin',-1)),abs(m.get('velocityMax' if vel else 'accelerationMax',1)))
        extent=100 if m.get('graphY') else 134;tip=(tail[0]+v[0]*extent/max(limit,1e-8),tail[1]-v[1]*extent/max(limit,1e-8))
        line(board,[(cx,cy),tail],sec,hi,MUTED,2);arrow(board,tail,tip,sec,hi,color,5)
        tx=780;ty=535 if vel else 745
        line(board,[tip,(tx+20,ty+43 if vel else ty-2)],sec,hi,color,2);text_now(board,tx,ty,'v · 속도' if vel else 'a · 가속도',sec,hi,color,44)
       else:
        v*=m.get(scale,.3 if field=='velocity' else .15)*fit[0]
        arrow(board,(cx,cy),(cx+96*v[0],cy-96*v[1]),sec,hi,color,5)
   if run:pathruns.append((run[1],z,run[2],fit))
   # At a shared boundary the old layer leaves before the new layer enters.
   # Both commands precede the same 60fps frame by less than 0.0002s, avoiding
   # float rounding and equal-time ordering without changing lesson timing.
   cmds.append(f'{max(0,z-.0002):.6f} drawbox@erase{j} x -2200,overlay@subject{j} x -2200;');last=None
   evidence.append(dict(scene=t['scene'],start=a,end=z,asset=asset,mode=mode,representation='Game image on the unchanged analytic position; illustration, not game measurement'))
  for a,z,m,fit in pathruns:
   path=[]
   for t0 in np.linspace(m.get('startTime',0),m.get('endTime',3),161):
    pos=motion.state(m['parameters'],float(t0))[0];point=motion.world(m,pos)*fit[0]+fit[1];path.append((960+96*point[0],540-96*(point[1]-2)))
   line(pathboard,path,a,z,'444444',2)
  pathboard.write(p/f'paths-{j}.ass')
  cmd=p/f'commands-{j}.txt';cmd.write_text('\n'.join(cmds)+'\n',encoding='utf8')
  extra.append(dict(asset=asset,mode=mode,file=af['file'],width=width,height=height,commands=cmd.name,eraser=eraser,j=j))
 # Keep the source-to-model context only in inspected blank areas. Math overlays
 # remain above it, and original game motion is never replaced by a still.
 for eid,sids,asset,title,meaning,viewport in CONTEXTS:
  if eid!=e['id']:continue
  for sid in sids:
   s=ss[sid];a=max(origin,s['start']);z=min(end,s['end'])
   if z<=a:continue
   # Original game prefaces come first; the same source subject remains when
   # the subsequent authored explanation begins.
   for ca,cz in segment_ranges(e,s,cuts(e)):
    ca=max(a,ca);cz=min(z,cz)
    if cz<=ca:continue
    x,y,w,h=viewport;af=ASSETS[asset];scale=min(w/af['dimensions'][0],h/af['dimensions'][1]);aw=round(af['dimensions'][0]*scale)//2*2;ah=round(af['dimensions'][1]*scale)//2*2
    contexts.append(dict(scene=sid,start=ca,end=cz,asset=asset,x=x,y=y,width=aw,height=ah))
    postboard.rectangle(x-5,y-52,aw+10,52,ca,cz)
    postboard.rectangle(x-5,y+ah,aw+10,66,ca,cz)
    postboard.text(x,y-50,title,ca,cz,GOLD,32,width=w)
    short={'M26':'날개 끝 → 원 위의 점','M27':'차량·지면 → 물체·마찰','M28':'실제 움직임 → 스프링·감쇠','M29':'게임 물체 → 충돌 모형','M30':'차량 → 부품별 질량','M31':'선로 → p(t) / 진행 방향 → 접선','M32':'경로 예시 · Bézier 원리 모형','M33':'이어지는 선로 → 곡선의 연결'}[eid]
    postboard.text(x,y+ah+5,short,ca,cz,TEAL,36,width=w)
    # Visible object-to-model link; fixed, labeled editorial guide, no fake data.
    if eid=='M26':
     hx,hy=x+aw*.423,y+ah*.324
     line(postboard,[(hx+12*math.cos(i*math.tau/32),hy+12*math.sin(i*math.tau/32)) for i in range(33)],ca,cz,GOLD,4)
     postboard.text(x+aw+12,y+30,'축',ca,cz,GOLD,40)
    evidence.append(dict(scene=sid,start=ca,end=cz,asset=asset,representation=meaning))
 # The full previously corrected jump construction now carries actual Mario.
 if e['id']=='M33':
  s=ss['029'];a,z=s['start'],s['end'];launch=cue(s,'원점에서 출발해');second=cue(s,'이 초에는 앞쪽으로');land=cue(s,'최고 높이를 h');recap=cue(s,'그래서 일 초에는');last=cue(s,'이 초에는 높이 영')
  groups2=[];cmds=[];af=ASSETS['mario'];height=130;width=round(af['dimensions'][0]*height/af['dimensions'][1])//2*2
  for k in range(round(max(a,origin)*60),round(min(z,end)*60)):
   sec=k/60
   t=0 if sec<launch else (sec-launch)/(second-launch) if sec<second else 1+(sec-second)/(land-second) if sec<land else 2 if sec<recap else 1 if sec<last else 2
   x=185+325*t-width*.5;y=740-330*t*(2-t)-height*.55
   cmds.append(f'{max(0,sec-.0001):.6f} overlay@jump x {round(x)},overlay@jump y {round(y)};')
  if cmds:
   cmds.append(f'{max(0,min(z,end)-.0002):.6f} overlay@jump x -2200;');(p/'jump-commands.txt').write_text('\n'.join(cmds)+'\n',encoding='utf8')
   contexts.append(dict(asset='mario',jump=True,width=width,height=height,start=max(a,origin),end=min(z,end)))
   postboard.text(80,210,'마리오의 점프를 단순화한 경로',a,z,GOLD,34,width=850)
   postboard.rectangle(400,330,330,65,a,z)
   postboard.text(565,330,'정점 · t=1 s',a,z,WHITE,40)
   postboard.rectangle(655,775,290,55,a,z)
   postboard.text(625,805,'착지 · t=2 s',a,z,WHITE,38)
 board.write(p/'identity.ass')
 postboard.write(p/'context-labels.ass')
 save(p/'subject-plan.json',dict(episode=e['id'],evidence=evidence,assets=extra,contexts=contexts,origin=origin,end=end,status='prepared-not-reviewed'))
 return extra,contexts

def graph(e,origin,end):
 extra,contexts=prepare(e,origin,end);gameinputs,g,remix=prior.filters(e,origin,end)
 # Retain the already delivered mixed audio bit-for-bit. Only use prior video
 # filters; their audio remix graph must not be applied a second time.
 g=g.split(';\n[0:a]')[0]
 # Put annotations on the final 60fps grid before drawing. Otherwise an input
 # timestamp drift or gap can otherwise leave a previously composited old
 # subject at a cut when output timestamps are later snapped to60fps.
 inputs=list(gameinputs);n=1+sum(x=='-i' for x in inputs);chain=['[0:v]setsar=1,fps=60:start_time=0,setpts=PTS+'+str(origin)+'/TB[identity0]'];current='identity0';counter=0
 for item in extra:
  inputs+=['-i',item['file']];j=item['j'];w,h=item['eraser'];label=f'identity{counter+1}';counter+=1
  restore=item['mode']=='pipeline-clear'
  if restore:
   chain.append(f'[{current}]split=2[clearbase{j}][textbase{j}]');current=f'clearbase{j}'
   chain.append(f'[textbase{j}]crop=300:400:350:335,format=rgba,colorkey=black:0.32:0.04[preservedtext{j}]')
  chain.append(f'[{current}]sendcmd=f={item["commands"]},drawbox@erase{j}=x=-2200:y=-2200:w={w}:h={h}:color=black:t=fill,ass=paths-{j}.ass[{label}]');current=label
  chain.append(f'[{n}:v]scale={item["width"]}:{item["height"]},format=rgba[sprite{j}]')
  label=f'identity{counter+1}';counter+=1;chain.append(f'[{current}][sprite{j}]overlay@subject{j}=x=-2200:y=-2200:eof_action=repeat:repeatlast=1[{label}]');current=label;n+=1
  if restore:
   label=f'identity{counter+1}';counter+=1;chain.append(f'[{current}][preservedtext{j}]overlay=350:335:eof_action=pass:repeatlast=0[{label}]');current=label
 tailparts=[];post='post0'
 for i,item in enumerate(contexts):
  inputs+=['-i',ASSETS[item['asset']]['file']];chain.append(f'[{n}:v]scale={item["width"]}:{item["height"]},format=rgba[context{i}]');label=f'post{i+1}'
  if item.get('jump'):
   tailparts.append(f'[{post}]sendcmd=f=jump-commands.txt[jumpbase]');post='jumpbase';command='overlay@jump=x=-2200:y=-2200'
  else:command=f'overlay=x={item["x"]}:y={item["y"]}'
  tailparts.append(f'[{post}][context{i}]{command}:eof_action=repeat:repeatlast=1:enable=\'gte(t,{item["start"]})*lt(t,{item["end"]})\'[{label}]');post=label;n+=1
 chain.append(f'[{current}]ass=identity.ass[b0]')
 g=g.replace(f'[0:v]setsar=1,setpts=PTS+{origin}/TB[b0]',';\n'.join(chain))
 # Mario's jump belongs above the already typeset complete path (old math).
 # Its context overlay is currently before math; move it to after workings.
 tail=f'ass=workings.ass,setpts=PTS-{origin}/TB[vout]'
 # A clear backing belongs behind the photo, not on top of it. Apply only the
 # authored labels after the context pictures (the math remains untouched).
 replacement='ass=workings.ass[post0];'+';'.join(tailparts)+(';' if tailparts else '')+f'[{post}]ass=context-labels.ass,setpts=PTS-{origin}/TB[vout]'
 assert tail in g;g=g.replace(tail,replacement)
 return inputs,g

def authorized(e):
 c=read(ROOT/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104'];v=c['gameSubjectRevision20261115']
 assert c['productionAllowedNow'] and e['id'] in v['scope'] and not v['upload']

def video_output(label,ni,frames,codec,target):
 return ['-map',label,'-map',f'{ni}:a:0','-frames:v',frames,*codec,'-c:a','copy','-movflags','+faststart',target]

def dual_graph(g,origin=0):
 return g.replace('[vout]','[dualbase]')+';[dualbase]split=2[vout][captionbase];[captionbase]setpts=PTS+'+str(origin)+'/TB,ass=captions.ko.ass,setpts=PTS-STARTPTS[captionout]'

def preserve_audio(movie,audio,p,kind):
 if prior.packet_hash(movie,'a')==prior.packet_hash(audio,'a'):return
 dest=movie.parent;repaired=dest/(kind+'-audio-preserved.mp4')
 prior.command(['-i',movie,'-i',audio,'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',repaired],p,'restore-'+kind+'-audio')
 # This is a newly generated, not-yet-delivered partial-audio mux. Replace it
 # atomically only after proving the video packets are identical and the audio
 # equals the preserved source; do not double the scarce disk usage with an
 # unnecessary duplicate of those same video packets. Prior masters stay intact.
 assert movie.resolve().is_relative_to(DEST.resolve()) and repaired.resolve().is_relative_to(DEST.resolve())
 before=prior.packet_hash(movie,'v');after=prior.packet_hash(repaired,'v');expected=prior.packet_hash(audio,'a')
 assert before==after and prior.packet_hash(repaired,'a')==expected
 save(p/('restore-'+kind+'-packet-proof.json'),dict(videoPacketsBefore=before,videoPacketsAfter=after,audioSourcePackets=expected,newUnreviewedMuxOnly=True,originalMastersUntouched=True))
 os.replace(repaired,movie)

def video_guard():return resource_guard.wrapper(prior.guard(),HERE/'resource-concurrency-evidence.json')

def encode(e,sample=None):
 authorized(e);p=work(e);G=video_guard();reason=G.idle_reason()
 cpu=bool(reason and reason.startswith('Insufficient idle headroom:'))
 if reason and not cpu:raise RuntimeError(reason)
 codec=['-c:v','libx264','-preset','fast','-crf','18','-threads','2','-g','120','-pix_fmt','yuv420p','-video_track_timescale','90000'] if cpu else prior.encoder()
 save(p/'resource-choice.json',dict(backend='CPU libx264, two encode/filter threads' if cpu else 'NVENC',reason=reason or 'GPU guard passed',noTts=True,otherProcessesUntouched=True))
 ownership=str(uuid.uuid4())
 try:
  with G.LEASE.open('x',encoding='utf8') as f:json.dump(dict(id=ownership,owner=e['slug']+'-'+REV,pid=os.getpid(),createdAt=G.now()),f)
 except FileExistsError:raise RuntimeError('Shared lease was claimed before this encode; retry at the next safe boundary')
 try:
  source=Path(e['baselineOutputs']['clean']);audio=latest(e)
  meta=json.loads(subprocess.check_output([str(FF.with_name('ffprobe.exe')),'-v','error','-select_streams','v:0','-show_entries','stream=nb_frames','-of','json',str(audio)]))['streams'][0]
  if sample:
   s=next(s for s in e['scenes'] if s['scene']==sample);start=s['start'];frames=round((s['end']-start)*60);dest=p/'samples';dest.mkdir(exist_ok=True)
   number=1
   while (dest/f'{sample}-v{number}.mp4').exists():number+=1
   clean=dest/f'{sample}-v{number}.mp4'
  else:
   start=0;frames=int(meta['nb_frames']);dest=DEST/e['slug'];dest.mkdir(parents=True,exist_ok=True);clean=dest/(e['slug']+'.clean.mp4')
  end=start+frames/60;inputs,g=graph(e,start,end);prior.prepare_captions(e,p)
  shutil.copy2(ROOT/'projects'/e['slug']/'production/local/teaching-sync-v2/workings.ass',p/'workings.ass')
  ni=1+sum(x=='-i' for x in inputs)
  inputs+=['-ss',str(start),'-i',str(audio)]
  if sample:g=g.replace('[vout]','[unsub]')+f';[unsub]setpts=PTS+{start}/TB,ass=captions.ko.ass,setpts=PTS-STARTPTS[vout]'
  simultaneous=not sample and not cpu
  if simultaneous:g=dual_graph(g)
  (p/'filter.ffgraph').write_text(g,encoding='utf8')
  assert shutil.disk_usage(dest).free>2*audio.stat().st_size+1024**3
  save(p/'worker.json',dict(status='rendering-sample' if sample else 'rendering-clean-and-captioned' if simultaneous else 'rendering-clean',pid=os.getpid(),episode=e['id'],finalReviewReady=False))
  trim=['-t',frames/60] if sample else []
  cap=dest/(e['slug']+'.captioned.mp4')
  if simultaneous:
   prior.command(['-ss',start,'-reinit_filter','0','-i',source,*inputs,'-filter_complex_threads','2','-/filter_complex','filter.ffgraph',*video_output('[vout]',ni,frames,codec,clean),*video_output('[captionout]',ni,frames,codec,cap)],p,'clean-and-captioned')
  else:
   prior.command(['-ss',start,'-reinit_filter','0','-i',source,*inputs,'-filter_complex_threads','2','-/filter_complex','filter.ffgraph','-map','[vout]','-map',f'{ni}:a:0','-frames:v',frames,*trim,*codec,'-c:a','copy','-movflags','+faststart',clean],p,('sample-'+sample) if sample else 'clean')
  prior.check_stream(clean,frames)
  if sample:save(p/'worker.json',dict(status='sample-needs-actual-visual-review',episode=e['id'],sample=str(clean)));return clean
  preserve_audio(clean,audio,p,'clean')
  if not simultaneous:
   save(p/'worker.json',dict(status='rendering-captioned',pid=os.getpid(),episode=e['id'],finalReviewReady=False))
   prior.command(['-i',clean,'-vf','ass=captions.ko.ass','-map','0:v:0','-map','0:a:0',*codec,'-c:a','copy','-movflags','+faststart',cap],p,'captioned')
  prior.check_stream(cap,frames);preserve_audio(cap,audio,p,'captioned')
  files={'clean':clean,'captioned':cap}
  for lang in ('ko','en'):
   target=dest/(e['slug']+'.'+lang+'.srt');shutil.copy2(latest(e,lang),target);files[lang]=target
  save(p/'encoded.json',dict(episode=e['id'],revision=REV,frames=frames,duration=frames/60,files={k:dict(path=str(v),sha256=sha(v)) for k,v in files.items()},audioSource=str(audio),audioBitstreamUnchanged=prior.packet_hash(clean,'a')==prior.packet_hash(audio,'a')==prior.packet_hash(cap,'a'),captionedDirectFromComposite=simultaneous,status='encoded-needs-actual-QA',humanReviewed=False,finalReviewReady=False))
  save(p/'worker.json',dict(status='encoded-needs-actual-QA',episode=e['id'],finalReviewReady=False));return cap
 except BaseException as error:
  save(p/'worker.json',dict(status='failed',episode=e['id'],error=repr(error),finalReviewReady=False));raise
 finally:G.release_lease(ownership)

if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('episodes',nargs='+');ap.add_argument('--render',action='store_true');ap.add_argument('--sample');a=ap.parse_args()
 for eid in a.episodes:
  e=EPISODES[eid]
  print(encode(e,a.sample) if a.render else prepare(e),flush=True)
