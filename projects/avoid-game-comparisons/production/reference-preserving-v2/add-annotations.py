"""Editorial guides from inspected source frames; never invented measured data."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[4];V=R/'projects/avoid-game-comparisons/production/reference-preserving-v2';p=V/'edit-plan.json';plan=json.loads(p.read_text(encoding='utf8'))
marks=[]
def mark(source,a,b,label,color,keys,pos,shape='rectangle'):
 marks.append(dict(source=source,**{'from':a,'to':b},label=label,color=color,keyframes=keys,labelPosition=pos,shape=shape,meaning=label,origin='editorial guide from directly inspected decoded source coordinates',occlusionRule='Hide outside listed interval and at every source/camera cut; no detector confidence or invented game data'))
B='73c7c2';G='a4c6a0';Y='e8cf83';RED='ef8585'
marks.append({'source':'nes-gameplay-project','from':24.5,'to':28.5,'shape':'path','points':[[1100,490],[1450,490]],'label':'진행 방향','labelPosition':[1090,335],'color':B,'meaning':'실제 횡스크롤의 오른쪽 진행 방향','origin':'directional editorial guide; no measured velocity'})
mark('nes-gameplay-project',194,196.5,'구간의 목표: 깃대',G,[[194,1110,150,100,760],[194.5,1000,150,100,760],[195,925,150,100,760],[196,925,150,100,760],[196.5,925,150,100,760]],[1160,220])
mark('odyssey-switch2-360-440',15.5,16.8,'조종하는 개구리',B,[[15.5,895,600,160,180],[16,895,600,160,180],[16.8,895,560,160,210]],[1130,450],'circle')
mark('odyssey-switch2-360-440',16,22.5,'새 대상의 조작 안내',Y,[[16,700,815,540,155],[22.5,700,815,540,155]],[1060,590])
mark('odyssey-switch2-555-705',94.8,96.35,'당겼다가 놓기',B,[[94.8,750,410,400,440],[95,750,410,400,440],[95.5,780,440,380,425],[96,780,410,355,410],[96.35,780,440,355,360]],[1165,650],'circle')
mark('odyssey-switch2-555-705',95.5,96.4,'벽을 향해',G,[[95.5,790,2,320,410],[96,805,2,300,330],[96.4,805,2,300,330]],[1125,245])
mark('odyssey-switch2-555-705',98.65,101.1,'파워문이 드러남',G,[[98.65,875,270,175,260],[99,875,270,175,260],[101.1,875,270,175,260]],[1140,420],'circle')
mark('odyssey-switch2-705-820',74,77.6,'캡처한 대상의 행동',Y,[[74,590,870,740,145],[77.6,590,870,740,145]],[1055,635])
for c in plan['cuts']:
 c['marks']=[]
 if c['kind']!='independent-gameplay':continue
 start=c['sourceStart'];end=start+c['frames']/60
 for m in marks:
  if m['source']==c['source'] and m['from']<end and m['to']>start:
   c['marks'].append({k:v for k,v in m.items() if k!='source'})
plan['annotations']={'policy':'footage-focus-annotations-v1','sourceCoordinatesVerified':'Decoded source grids and contact sequences recorded in existing plan','finalMovingOutputReviewed':False,'marksUsed':sum(len(c['marks']) for c in plan['cuts']),'backgroundDuckingDoesNotChangeVoice':True}
p.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('Applied',plan['annotations']['marksUsed'],'purposeful source marks; final motion review pending')
