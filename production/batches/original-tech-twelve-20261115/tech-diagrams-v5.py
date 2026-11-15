"""Source-bounded contact conditions, with no invented game measurements."""
from pathlib import Path
import importlib.util
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('source_ordered_diagrams_v4',HERE/'tech-diagrams-v4.py');v4=importlib.util.module_from_spec(s);s.loader.exec_module(v4)
base,lines,arrow,C=v4.base,v4.lines,v4.arrow,v4.C
def kart_conditions(seconds):
 im,d=base('충돌에도 조건이 있습니다','Mario Kart 8 · 스핀 터보의 해설용 도식')
 for y,title,body,color in [(320,'반중력 구간','일반 주행과 구별합니다.','relation'),(520,'정해진 접촉 대상','다른 카트와 일부 대상입니다.','title'),(720,'회전과 가속','모든 벽과 장식물이 해당하지 않습니다.','changed')]:
  d.rounded_rectangle((70,y-70,914,y+85),radius=16,fill=C['panel'],outline=C[color],width=4);lines(d,title,(492,y-24),39,color);lines(d,body,(492,y+42),31,'ink')
 arrow(d,(492,410),(492,430),C['relation'],5);arrow(d,(492,610),(492,630),C['relation'],5);lines(d,'원래 게임의 입력·속도 수치를 측정한 화면은 아닙니다.',(492,930),27,'muted')
 return im,dict(kind='authored conditional contact diagram',gameTelemetryMeasured=False,allContactsAreBoosts=False)
def control_bonds(seconds):
 im,d=base('조각과 연결을 함께 준비합니다','Control · 제작 단계의 해설용 도식')
 for i in range(4):
  x=150+i*225;d.rounded_rectangle((x-75,365,x+75,540),radius=12,fill=C['panel'],outline=C['title'],width=5);lines(d,'조각 '+str(i+1),(x,445),33)
  if i<3:arrow(d,(x+80,445),(x+140,445),C['relation'],6)
 lines(d,'어디를 잇고 얼마나 버티게 할지 정합니다.',(492,635),36,'relation');lines(d,'충격 → 연결 변화 → 떨어질 조각과 남을 조각',(492,755),33,'changed');lines(d,'원래 엔진의 연결 강도나 물리 수치를 나타내지 않는 도식',(492,930),26,'muted')
 return im,dict(kind='authored piece connection preparation diagram',originalStrengthValuesMeasured=False,originalPhysicsExecuted=False)
DIAGRAMS=dict(v4.DIAGRAMS,**{'kart-conditions':kart_conditions,'control-bonds':control_bonds})
def render(key,seconds):
 im,e=DIAGRAMS[key](seconds);return im,dict(**e,diagramKey=key,localModelSeconds=seconds,notSpeechTimestamp=True,finalFilm=False)
