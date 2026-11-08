"""Use actual UE frames and exact recorded rig tracks. No synthetic game measurements."""
from pathlib import Path
import sys,json,gzip,functools,math
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1];B=R/'production/batches/animation-18-20261031';N=B/'local/real-clips-v2'
sys.path.insert(0,str(N/'python-deps'))
import numpy as np
from scipy.spatial.transform import Rotation
BG='#080b09';WHITE='#f2f3ee';YELLOW='#f2d787';MUTED='#a5b2aa'
COLORS=['#77d7ca','#77d7ca','#ff8d85','#a4d987'];NAMES=['대기','준비','타격','후속 동작'];KEYFRAMES=[0,23,35,48]
@functools.lru_cache(None)
def font(size):return ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',size)
def text(d,xy,s,size=44,c=WHITE,anchor='lt'):d.text(xy,s,font=font(size),fill=c,anchor=anchor)
def arrow(d,a,b,c,w=6):
 a=np.array(a);b=np.array(b);v=b-a;n=np.linalg.norm(v)
 if n<2:return
 u=v/n;p=np.array([-u[1],u[0]]);d.line([tuple(a),tuple(b)],fill=c,width=w);d.polygon([tuple(b),tuple(b-u*18+p*9),tuple(b-u*18-p*9)],fill=c)
@functools.lru_cache(None)
def data(key):return json.loads((N/'studies'/f'A03-{key}.json').read_text('utf-8'))
@functools.lru_cache(maxsize=432)
def native(key,f):return Image.open(N/'study-frames'/f'A03-{key}'/f'{max(0,min(107,int(f))):06d}.png').convert('RGB')
@functools.lru_cache(None)
def rig(key):
 d=data(key);source=json.load(gzip.open(N/'source-motion/AS_Spear_Attack_02.json.gz','rt',encoding='utf-8'));names=d['boneNames'];parents={b['name']:b['parent'] for b in source['bones']};out=[];rot=Rotation.from_euler('z',d['yaw'],degrees=True)
 for f in range(d['frames']):
  pp={};qq={}
  for name in names:
   t=d['tracks'][name];p=np.array(t['p'][f]);q=Rotation.from_quat(t['q'][f]);parent=parents[name]
   if parent in pp:p=pp[parent]+qq[parent].apply(p);q=qq[parent]*q
   pp[name]=p;qq[name]=q
  out.append({name:rot.apply(pp[name]).tolist() for name in ['pelvis','spine_03','head','upperarm_r','lowerarm_r','hand_r','upperarm_l','lowerarm_l','hand_l','thigh_l','calf_l','foot_l','thigh_r','calf_r','foot_r']})
 return out
def project(p):return (960+p[0]*1920/550,540-(p[2]-140)*1920/550)
def phase(f):
 s=data('attack')['trace'][int(f)]['state'];return {'standby':0,'lead-in':1,'attack':2,'follow-through':3,'idle':3,'run':3}[s]
def crop_into(im,key,f,box,crop=(510,130,1390,1060)):
 x,y,w,h=box;src=native(key,f).crop(crop);scale=min(w/src.width,h/src.height);sz=(round(src.width*scale),round(src.height*scale));ox=x+(w-sz[0])//2;oy=y+(h-sz[1])//2;im.paste(src.resize(sz,Image.Resampling.LANCZOS),(ox,oy))
 return lambda p:(ox+(p[0]-crop[0])*scale,oy+(p[1]-crop[1])*scale)
def phase_strip(d,f,y=839,pass_index=None):
 idx=phase(f);w=440
 for i,label in enumerate(NAMES):
  x=60+i*450;c=COLORS[i] if i==idx else '#526057';d.rectangle((x,y,x+w,y+8),fill=c);text(d,(x+w/2,y+17),label,45,c,'mt')
 if pass_index:text(d,(1815,118),f'1× · {pass_index}/3',38,YELLOW,'rt')
def header(im,title,small='언리얼 · 클립 기반 시연'):
 d=ImageDraw.Draw(im);text(d,(60,44),title,62,YELLOW);text(d,(1855,56),small,30,MUTED,'rt');return d
def native_pass(f,pass_index=1,chapter=1):
 if chapter==5:return compare(f,14,pass_index=pass_index)
 im=Image.new('RGB',(1920,1080),BG);d=header(im,'전체 동작부터 보기');text(d,(60,120),'같은 공격을 기본 속도로 세 번 봅니다',39,MUTED)
 crop_into(im,'attack',f,(390,174,1140,630),(350,100,1570,1070));phase_strip(d,f,pass_index=pass_index)
 return im
def four_phases(f,pid,progress=0):
 im=Image.new('RGB',(1920,1080),BG);d=header(im,'Attack Phases (공격 동작의 단계)');text(d,(60,122),'같은 공격을 네 자세로 나누어 봅니다',40,MUTED)
 # Only the relevant panel moves; every other phase stays visible for comparison.
 active=phase(f);dframes=list(KEYFRAMES);dframes[active]=f
 descriptions=[['공격 전','기준 자세'],['팔·검을 올려','공격을 예고'],['검을 내려','힘을 전달'],['몸을 굽혀','힘을 정리']]
 for i,n in enumerate(dframes):
  x=50+i*465;w=425;c=COLORS[i];text(d,(x+w/2,205),NAMES[i],56,c,'mt');d.rectangle((x,267,x+w,275),fill=c)
  trans=crop_into(im,'attack',n,(x,291,w,480),(510,130,1390,1060))
  if i==active:
   for a,b in [('upperarm_r','lowerarm_r'),('lowerarm_r','hand_r')]:d.line([trans(project(rig('attack')[n][a])),trans(project(rig('attack')[n][b]))],fill=c,width=6)
   d.rectangle((x,285,x+w,776),outline=c,width=5)
  for j,line in enumerate(descriptions[i]):text(d,(x+w/2,799+j*49),line,40,c if i==active else WHITE,'mt')
 return im
def paint_guides(im,key,f,trans,chapter):
 d=ImageDraw.Draw(im);r=rig(key);now=r[f];c=COLORS[phase(min(f,107))]
 # A baseline skeleton is a transparent guide from the exact captured rest pose.
 layer=Image.new('RGBA',im.size);g=ImageDraw.Draw(layer);chains=[['pelvis','spine_03','head'],['upperarm_r','lowerarm_r','hand_r'],['thigh_r','calf_r','foot_r']]
 ghost=0 if chapter==2 else 35
 for chain in chains:g.line([trans(project(r[ghost][n])) for n in chain],fill=(52,100,155,110),width=9)
 im.paste(layer,(0,0),layer)
 d=ImageDraw.Draw(im)
 start=18 if chapter==2 else 30 if chapter==3 else 35
 pts=[trans(project(r[k]['hand_r'])) for k in range(start,f+1)]
 if len(pts)>1:d.line(pts,fill=c,width=7)
 for a,b in [('upperarm_r','lowerarm_r'),('lowerarm_r','hand_r')]:d.line([trans(project(now[a])),trans(project(now[b]))],fill=c,width=10)
 for name in ['upperarm_r','hand_r']:
  x,y=trans(project(now[name]));d.ellipse((x-10,y-10,x+10,y+10),fill=c,outline='#16261e',width=3)
 foot=min(['foot_l','foot_r'],key=lambda n:now[n][2]);x,y=trans(project(now[foot]));d.line([(x-35,y+5),(x+35,y+5)],fill='#349675',width=8)
 return d
@functools.lru_cache(maxsize=64)
def analysis(f,pid,chapter):
 if pid in [2,3,19,21]:return four_phases(f,pid)
 if 13<=pid<=18:return compare(f,pid)
 im=Image.new('RGB',(1920,1080),BG)
 title={1:'한 번의 공격 안에 있는 시간',2:'Anticipation (준비 동작)',3:'Impact (타격 자세)',4:'Follow-through (후속 동작)',6:'자세와 시간표를 함께 보기'}.get(chapter,'공격 동작 분석')
 d=header(im,title);text(d,(60,120),'느린 분석 · 같은 실제 클립',38,MUTED)
 trans=crop_into(im,'attack',f,(60,178,920,640));d=paint_guides(im,'attack',f,trans,chapter);idx=phase(f);c=COLORS[idx]
 text(d,(1070,200),NAMES[idx],70,c);d.line([(1070,289),(1810,289)],fill=c,width=7)
 labels={1:['기준 자세에서','준비 → 타격 → 후속'],2:['팔과 검이 올라갑니다','파란 선 = 대기 자세','밝은 선 = 현재 팔'],3:['검과 표적을 확인합니다','움직이는 몸과','판정 구간은 별개'],4:['타격 뒤에도 몸은 이어집니다','파란 선 = 타격 자세','발과 상체로 균형 정리'],6:['출발 자세와 공격 자세','판정 시작과 조작 복귀','각 기준을 따로 기록']}
 for j,line in enumerate(labels.get(chapter,labels[1])):text(d,(1070,335+j*73),line,46,WHITE if j==0 else MUTED)
 rec=data('attack')['trace'][f]
 if chapter==3:
  enabled=12<=rec['simulationFrame']<=18 and f>=18;frozen=bool(rec['freezeLeft'])
  text(d,(1070,598),'판정 '+('켜짐' if enabled else '꺼짐'),48,COLORS[2] if enabled else MUTED)
  text(d,(1070,665),'히트 스톱' if frozen else '명중 순간에만 잠깐 정지',42,YELLOW if frozen else MUTED)
  text(d,(1070,740),'판정·멈춤 = 자체 시연 규칙',32,MUTED)
 else:
  text(d,(1070,604),'선·점 = 실제 관절 위치',38,c);text(d,(1070,662),'아래 표시 = 디딤발 위치',38,'#a4d987')
 phase_strip(d,f)
 return im
def compare(f,pid,pass_index=None):
 im=Image.new('RGB',(1920,1080),BG);d=header(im,'Control Recovery (조작 복귀)');text(d,(60,120),'같은 입력 · 허용하는 시점만 다르게',40,MUTED)
 left='noinput' if pid==18 else 'cancel48';right='cancel36'
 for i,key in enumerate([left,right]):
  x=55+955*i;rec=data(key)['trace'][f];c=COLORS[3] if rec['transitionAccepted'] else COLORS[2]
  text(d,(x+430,197),'입력 없음' if key=='noinput' else ('끝까지 기다림 · 48f' if i==0 else '먼저 연결 · 36f'),46,YELLOW if i else WHITE,'mt')
  crop_into(im,key,f,(x+10,270,850,470),(510,130,1390,1060))
  text(d,(x+430,760),'달리기 연결' if rec['transitionAccepted'] else '공격 동작 유지',47,c,'mt')
  for a,z,col in [(0,36,'#5a7069'),(36,48,COLORS[3] if i else COLORS[2])]:d.rectangle((x+850*a/48,836,x+850*z/48-2,853),fill=col)
  px=x+850*min(48,rec['simulationFrame'])/48;d.polygon([(px,830),(px-12,809),(px+12,809)],fill=WHITE)
 text(d,(960,881),f'시연 기본 속도 · {pass_index}/3' if pass_index else '자체 설정: 60fps · 36f = 0.6초 · 48f = 0.8초',35,MUTED,'mt')
 return im
def frame(row,i):
 i+=row.get('sourceOffset',0)
 if row['mode']=='native':return native_pass(min(95,i),row['passIndex'],row['chapter'])
 pid=row['paragraph'];ch=row['chapter'];n=row.get('gridFrames',row['frames'])
 if 13<=pid<=18:f=round(18+min(77,78*i/max(1,n-1)))
 elif pid in [2,3,19,21]:f=min(68,round(0+68*i/max(1,n-1)))
 else:
  a,z={1:(0,65),2:(18,29),3:(30,40),4:(35,68),6:(23,65)}.get(ch,(0,65));f=min(z,a+int(i/4))
 return analysis(max(0,min(107,f)),pid,ch)
def verify_rig():
 # Check FK against independently recorded weapon start for every frame.
 d=data('attack');raw=json.load(gzip.open(N/'source-motion/AS_Spear_Attack_02.json.gz','rt',encoding='utf-8'));names=d['boneNames'];parents={b['name']:b['parent'] for b in raw['bones']};errs=[]
 for f in range(108):
  pp={};qq={}
  for name in names:
   t=d['tracks'][name];p=np.array(t['p'][f]);q=Rotation.from_quat(t['q'][f]);parent=parents[name]
   if parent in pp:p=pp[parent]+qq[parent].apply(p);q=qq[parent]*q
   pp[name]=p;qq[name]=q
  rot=Rotation.from_euler('z',d['yaw'],degrees=True);point=rot.apply(pp['hand_r']+qq['hand_r'].apply(d['weaponAxisInHand'])*6)
  errs.append(float(np.linalg.norm(point-np.array(d['trace'][f]['bladeStart']))))
 assert max(errs)<1e-5,max(errs)
 return {'frames':108,'maxWorldUnitDifference':max(errs),'method':'Exact FK and yaw reproduced independently recorded bladeStart; projected using recorded orthographic width and height.','editorialGuidesNotGameTelemetry':True}
if __name__=='__main__':
 out=P/'production/local/contrast-v5';out.mkdir(exist_ok=True)
 samples=[('native',native_pass(23)),('four-phase',four_phases(35,3)),('anticipation',analysis(26,4,2)),('impact',analysis(36,9,3)),('follow-through',analysis(48,10,4)),('cancel',compare(58,16))]
 for name,im in samples:
  im.save(out/(name+'.png'));im.resize((375,211),Image.Resampling.LANCZOS).save(out/(name+'-375.png'))
 (H/'joint-guide-proof.json').write_text(json.dumps(verify_rig(),indent=2),'utf-8');print('previews and exact rig projection proof ready')
