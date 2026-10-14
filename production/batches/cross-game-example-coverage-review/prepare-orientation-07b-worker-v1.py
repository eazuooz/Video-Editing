"""Prepare the single scene worker using the already verified native-PTS pipeline."""
from pathlib import Path
B=Path(__file__).resolve().parent
base=(B/'render-orientation-03b-tracked-v1.py').read_text('utf-8')
header=base[:base.index('def observed(')].replace('03b','07b')
main=base[base.index('def main():'):].replace('03b','07b').replace('1050','1630')
body=r'''
def observed(source,p):
 if any(a*60<=source<b*60 for a,b in p['hideSourceSeconds']):return None
 for a,b in zip(p['anchors'],p['anchors'][1:]):
  if a['sourceFrame']<=source<=b['sourceFrame']:
   if not a['visible'] or not b['visible'] or b['sourceFrame']-a['sourceFrame']>31:return None
   u=(source-a['sourceFrame'])/(b['sourceFrame']-a['sourceFrame'])
   return {k:[a[k][i]+u*(b[k][i]-a[k][i]) for i in (0,1)] for k in ('nose','tail','wingA','wingB')}
 return None
def gameplay(im,frame,source,seg,p):
 layer=Image.new('RGBA',im.size);d=ImageDraw.Draw(layer);sec=frame/60
 label(d,(1210,90),'Trailmakers · 組立飛行機' if False else 'Trailmakers · 조립 비행기','#ffffff',28)
 if seg['kind']=='takeoff':label(d,(1210,150),'활주로에서 떠나는 실제 행동','#ffe16b',28)
 elif seg['kind']=='next-view-return':label(d,(1210,150),'다음 시점 · 날개의 기울기 비교','#ffe16b',28)
 elif seg['kind'].startswith('related'):label(d,(1210,150),'다른 고유 구간 · 두 선을 함께 비교','#ffe16b',26)
 elif seg['kind'].startswith('camera'):label(d,(1210,150),'다른 카메라 시점 · 화면 관찰','#ffe16b',28)
 else:label(d,(1210,150),'앞과 날개 방향을 나누어 보기','#ffe16b',28)
 blue=sec>=8.76;red=sec>=16.7166666667
 if red:label(d,(1210,220),'빨강: 기체의 앞을 가리키는 선',RED,26)
 if blue:label(d,(1210,275),'파랑: 날개 양쪽을 잇는 선',BLUE,26)
 label(d,(1210,340),'화면 관찰용 · 월드축/회전각 측정 아님','#ffffff',24)
 obs=observed(source,p)
 if obs and blue:
  a,b=obs['wingA'],obs['wingB'];d.line((tuple(a),tuple(b)),fill='#111822',width=10);d.line((tuple(a),tuple(b)),fill=BLUE,width=6)
 if obs and red and math.dist(obs['tail'],obs['nose'])>=55:
  a,b=obs['tail'],obs['nose'];d.line((tuple(a),tuple(b)),fill='#111822',width=11);arrow(d,a,b,RED,6)
 assert layer.getbbox()[3]<900
 return Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB'),obs
def model(frame,p):
 im=Image.new('RGB',(1920,1080),'#fafbf9');d=ImageDraw.Draw(im);sec=frame/60;late=frame>=1891
 local=sec-(1891/60 if late else 742/60)
 theta=math.pi/2*min(1,max(0,(local-.3)/1.3)) if late else .32*math.sin(local*1.15)
 scale=240;center=(815,555)
 def rotate(v):
  x,y,z=v;c,s=math.cos(theta),math.sin(theta);return (c*x-s*y,s*x+c*y,z)
 def proj(v):
  x,y,z=rotate(v);return (center[0]+scale*(.79*x-.61*z),center[1]+scale*(.32*x-.80*y+.41*z))
 def depth(v):
  x,y,z=rotate(v);return .49*x+.57*y+.66*z
 for k in range(-4,5):
  for a,b in [((k/2,-.8,-2),(k/2,-.8,2)),((-2,-.8,k/2),(2,-.8,k/2))]:
   def floor(v):
    x,y,z=v;return (center[0]+scale*(.79*x-.61*z),center[1]+scale*(.32*x-.80*y+.41*z))
   d.line((floor(a),floor(b)),fill='#dce4df',width=2)
 faces=[]
 def box(x0,x1,y0,y1,z0,z1,top,side):
  v=[(x,y,z) for z in (z0,z1) for y in (y0,y1) for x in (x0,x1)]
  for ids,col in [([0,1,3,2],side),([4,6,7,5],side),([0,4,5,1],side),([2,3,7,6],top),([0,2,6,4],side),([1,5,7,3],side)]:
   vv=[v[i] for i in ids];faces.append((sum(depth(t) for t in vv)/4,vv,col))
 box(-.20,.20,-.22,.22,-1.2,1.5,'#e3c56a','#af8a35')
 box(-1.65,1.65,.25,.36,-.05,.40,'#b7cce5','#637d9d')
 box(-.75,.75,.18,.28,-1.22,-.9,'#9bb4d2','#566c88')
 box(-.06,.06,.28,.70,-1.2,-.8,'#c1d2e6','#637d9d')
 for _,vv,col in sorted(faces,key=lambda x:x[0]):d.polygon([proj(v) for v in vv],fill=col,outline=DARK,width=2)
 origin=(0,.43,.25)
 red=late or sec>=13.1;blue=late or sec>=14.2
 if red:arrow(d,proj(origin),proj((0,.43,1.9)),RED,8)
 if blue:d.line((proj((-1.8,.43,.25)),proj((1.8,.43,.25))),fill=BLUE,width=9)
 text(d,(85,80),'앞과 날개를 함께 읽는 자세',DARK,48)
 text(d,(85,155),'따로 정한 설명모형 · 실제 게임 내부 축의 측정이 아닙니다',DARK,30)
 if red:text(d,(1330,390),'앞 f · 붉은 방향',RED,34)
 if blue:text(d,(1330,465),'날개 양쪽 · 파란 방향',BLUE,34)
 if not late and sec>=15.72:text(d,(1270,570),'두 방향을 함께 비교',DARK,34)
 if late:
  text(d,(1130,570),'별도 수학 예: z축 +90°',DARK,34)
  text(d,(1160,645),'x → y,  y → −x,  z → z',DARK,30)
  text(d,(1150,715),'Rz = [[0,−1,0],[1,0,0],[0,0,1]]',DARK,28)
 text(d,(85,842),'게임의 회전각을 수치로 추정하지 않습니다. 카메라와 물체의 움직임을 구분하세요.','#64716a',26)
 return im
'''
target=B/'render-orientation-07b-tracked-v1.py';assert not target.exists();target.write_text(header+body+main,'utf-8')
compile(target.read_text('utf-8'),str(target),'exec')
rec=(B/'record-orientation-03b-worker-exit-v1.py').read_text('utf-8').replace('03b','07b');target=B/'record-orientation-07b-worker-exit-v1.py';assert not target.exists();target.write_text(rec,'utf-8');compile(rec,str(target),'exec')
print('Prepared one CPU2/GPU0 07b worker and actual-exit recorder; not executed.')
