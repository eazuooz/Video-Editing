"""Source-ordered authored illustrations; no original-game measurements."""
from pathlib import Path
import importlib.util,math,random
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('ot12_diagrams_v3',HERE/'tech-diagrams-v3.py');v3=importlib.util.module_from_spec(s);s.loader.exec_module(v3)
base,lines,arrow,dot,C=v3.base,v3.lines,v3.arrow,v3.dot,v3.C
def sand_flicker(seconds):
 im,d=base('작은 반짝임과 거슬리는 깜빡임','움직임의 차이를 보여 주는 해설용 예시')
 rng=random.Random(7123);points=[(rng.uniform(-160,160),rng.uniform(390,680),rng.random()*6.28)for i in range(36)]
 for k,cx in enumerate([250,734]):
  d.rectangle((cx-210,285,cx+210,760),fill='#493724');lines(d,'의도된 반짝임'if k==0 else'불안정한 깜빡임',(cx,330),34,'title')
  for i,(x,y,phase)in enumerate(points):
   amount=(.5+.5*math.sin(seconds*1.8+phase))if k==0 else(float((int(seconds*2)+i)%3==0));radius=1+amount*4;px=cx+x+12*math.sin(seconds*.7);d.ellipse((px-radius,y-radius,px+radius,y+radius),fill=(int(125+125*amount),int(105+124*amount),int(65+130*amount)))
 lines(d,'같은 작은 빛도 움직일 때 다르게 느껴집니다.',(492,839),33,'relation');lines(d,'표현 차이의 도식 · 게임 셰이더나 깜빡임 측정 결과 아님',(492,938),27,'muted')
 return im,dict(kind='authored sparkle-versus-flicker illustration',flashingWholeFrame=False,originalShaderExecuted=False,originalFlickerMeasured=False)
def returnal_bodies(seconds):
 im,d=base('몸체를 잇는 구상에서 입자 구조로','개발 과정의 관계를 설명하는 도식')
 for i in range(5):
  x=150+i*170;y=420+25*math.sin(seconds*.7+i*.6);d.rounded_rectangle((x-53,y-30,x+53,y+30),radius=8,fill=C['panel'],outline=C['title'],width=4)
  if i<4:arrow(d,(x+58,y),(x+110,y),C['muted'],4)
 lines(d,'처음 구상: 뼈대마다 물리 몸체',(492,300),36,'title')
 for i in range(5):
  x=150+i*170;y=695+25*math.sin(seconds*.7+i*.6);dot(d,(x,y),'relation',13)
  if i<4:arrow(d,(x+20,y),(x+145,695+25*math.sin(seconds*.7+(i+1)*.6)),C['relation'],5)
 lines(d,'발전시킨 구조: 부모와 자식 입자',(492,580),35,'relation');lines(d,'조절과 계산 비용의 어려움에서 다른 표현 방법으로',(492,850),32,'relation');lines(d,'원래 엔진의 실행이나 성능 비교가 아닌 개발 과정 설명',(492,938),27,'muted')
 return im,dict(kind='authored design-evolution diagram',rigidBodySimulationExecuted=False,originalGpuEffectsExecuted=False,performanceMeasured=False)
def doom_rewards(seconds):
 im,d=base('보상의 종류와 조건을 나눕니다','DOOM · 자원 흐름의 해설용 도식')
 for i,(title,action,reward,cost)in enumerate([('체력','다가가 마무리','회복 보상','체력 상황에 맞춰 조절'),('탄약','전기톱 사용','탄약 보상','연료를 써야 함')]):
  y=360+i*300;d.rounded_rectangle((75,y-70,909,y+130),radius=16,fill=C['panel'],outline=C['relation'],width=4);lines(d,title,(170,y),42,'title');lines(d,action,(438,y-23),34);lines(d,reward,(755,y-23),33,'changed');arrow(d,(565,y-20),(635,y-20),C['relation'],6);lines(d,cost,(595,y+71),33,'relation')
 lines(d,'같은 자원 보상 규칙을 그대로 복사하지 않습니다.',(492,850),32,'relation');lines(d,'원래 게임의 보상 수치나 입력 기록을 나타내지 않는 도식',(492,938),26,'muted')
 return im,dict(kind='authored reward-type and cost diagram',originalRewardNumbersMeasured=False,originalInputsMeasured=False)
DIAGRAMS=dict(v3.DIAGRAMS,**{'sand-flicker':sand_flicker,'returnal-bodies':returnal_bodies,'doom-rewards':doom_rewards})
def render(key,seconds):
 im,e=DIAGRAMS[key](seconds);return im,dict(**e,diagramKey=key,localModelSeconds=seconds,notSpeechTimestamp=True,finalFilm=False)
