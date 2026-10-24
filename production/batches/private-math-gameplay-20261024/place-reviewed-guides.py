"""Coordinates chosen from the decoded source frames listed in review evidence."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
def rd(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def circle(x,y,r,label):return dict(kind='circle',xy=[x,y],radius=r,label=label)
def path(points,label):return dict(kind='path',points=points,label=label)
def arrow(a,b,label):return dict(kind='arrow',a=a,b=b,label=label)
guides={
 'M13':{
 '02':[path([[.31,.34],[.39,.39],[.44,.64],[.57,.66],[.65,.49]],'바깥 경계')],
 '11':[path([[.18,.68],[.22,.65],[.28,.69],[.33,.62],[.44,.66],[.47,.61]],'전체 영역의 홈')],
 'QG01':[path([[.42,.61],[.42,.84],[.65,.72],[.65,.49]],'변한 건물의 외곽')],
 'QG02':[circle(.438,.70,55,'빈 통로')],
 'QG03':[path([[.31,.76],[.43,.85],[.57,.85],[.67,.75]],'높아진 지면')]},
 'M15':{
 '02':[arrow([.76,.60],[.61,.62],'가까운 벽'),circle(.39,.69,63,'뒤쪽 물체')],
 '05-hole':[circle(.87,.24,80,'표면이 없는 구멍')],
 '05-glass':[path([[.26,.55],[.37,.84],[.66,.88],[.71,.56]],'반투명 표면')],
 '08-entry':[arrow([.73,.72],[.58,.51],'밝은 면'),arrow([.10,.72],[.18,.51],'어두운 면')],
 '08-preview':[path([[.27,.71],[.27,.12],[.55,.10],[.55,.71]],'설치된 문틀')],
 '11':[arrow([.17,.27],[.36,.40],'밝은 빨강'),arrow([.86,.27],[.72,.42],'어두운 빨강')],
 '14':[path([[.22,.64],[.32,.57],[.46,.57],[.55,.63]],'굴곡 있는 표면')],
 '17':[circle(.42,.12,90,'설치한 조명'),arrow([.75,.45],[.65,.62],'빛을 받는 벽')],
 '19':[path([[.25,.65],[.43,.60],[.49,.71]],'그늘 속 바닥')],
 '21':[circle(.37,.47,80,'같은 장면의 여러 표면')]},
 'M16':{
 '02':[path([[.5,.04],[.5,.87]],'두 관찰 화면')],
 '05':[circle(.51,.60,85,'편집한 건물')],
 '08':[path([[.45,.26],[.61,.29],[.64,.43],[.55,.49]],'같은 지붕')],
 '11':[circle(.21,.49,65,'왼쪽 캐릭터'),circle(.75,.57,65,'오른쪽 캐릭터')],
 '13':[circle(.25,.20,76,'앞 지붕 A'),circle(.64,.10,62,'뒤 지붕 B')],
 '16':[circle(.76,.50,85,'앞벽 A'),circle(.31,.24,65,'뒤 지붕 B')],
 '19':[path([[.16,.12],[.16,.78],[.83,.78],[.83,.15]],'넓어진 관찰 범위')],
 '21-view':[circle(.5,.39,100,'같은 건물')],
 '21-build':[path([[.49,.49],[.63,.50],[.69,.62],[.5,.65],[.46,.58],[.49,.49]],'추가된 발판')]},
 'M17':{
 '02':[path([[.08,.20],[.30,.17],[.30,.58],[.08,.63]],'고정 기둥')],
 '05':[circle(.40,.43,40,'기존 모서리 A')],
 '08':[circle(.54,.10,60,'기존 탑'),circle(.46,.44,60,'새 발판')],
 '11-carry':[circle(.50,.70,105,'옮기는 큐브')],
 '11-place':[circle(.50,.64,96,'내려놓은 큐브')],
 '14':[path([[.15,.70],[.32,.58],[.44,.61]],'앞 지붕')]},
 'M18':{
 '03':[path([[.37,.55],[.42,.62],[.56,.60]],'앞 구조의 경계')],
 '06':[path([[.36,.03],[.60,.03],[.58,.22],[.31,.27]],'지붕에 붙은 무늬')],
 '09-view':[path([[.30,.49],[.55,.52],[.55,.59]],'같은 테라스 모서리')],
 '09-build':[circle(.53,.56,96,'새 벽과 지붕')]},
 'M19':{
 '02':[path([[.60,.09],[.81,.12],[.87,.33],[.72,.32],[.60,.09]],'바뀐 지붕 윤곽')],
 '06':[path([[.65,.43],[.85,.46],[.85,.79],[.71,.75]],'부품의 테두리')],
 '07':[path([[.24,.34],[.49,.23],[.66,.34]],'면 사이의 경계')],
 '10':[circle(.50,.39,83,'평평한 면'),circle(.22,.47,63,'둥근 탑')],
 '11-front':[circle(.50,.36,65,'빈 구멍')],
 '11-depth':[path([[.23,.22],[.21,.45],[.26,.65],[.35,.80]],'구멍 안쪽의 두께')],
 '15':[circle(.49,.46,90,'남아 있는 구멍 윤곽')]},
 'M20':{
 '04':[path([[.37,.42],[.38,.56],[.46,.58],[.46,.44]],'색을 바꾼 부품')],
 '05':[circle(.555,.36,69,'벽의 색과 윤곽')],
 '08':[path([[.84,.23],[.95,.33],[.93,.48],[.77,.37],[.84,.23]],'같은 지붕의 무늬')],
 '09':[path([[.07,.32],[.23,.36],[.36,.31]],'바닥에 붙은 무늬')],
 '12':[path([[.36,.04],[.41,.16],[.35,.20],[.32,.17],[.36,.04]],'빛과 별개인 윤곽')]}}
for ep,items in guides.items():
 f=B/f'{ep.lower()}-gameplay-plan.json';p=rd(f)
 for s in p['patches']:
  key=s['key']
  if (ep,key)==('M15','17'):
   s['segments']=[dict(kind='motion',**{'in':764.5},seconds=12.5),dict(kind='still',**{'in':777},seconds=6)]
  if (ep,key)==('M17','11-place'):
   s['segments']=[dict(kind='motion',**{'in':54},seconds=2),dict(kind='still',**{'in':56},seconds=8)]
  if (ep,key)==('M19','11-depth'):
   s['segments']=[dict(kind='motion',**{'in':603.4},seconds=1.6),dict(kind='still',**{'in':605},seconds=9.8)]
  # Freeze before the next undo feature title and retain actual colour action.
  if (ep,key)==('M20','04'):
   s['segments']=[dict(kind='motion',**{'in':78.5},seconds=2.5),dict(kind='still',**{'in':81},seconds=13.3)]
   items[key]=[path([[.62,.59],[.62,.74],[.71,.80],[.71,.66]],'색을 바꾼 부품')]
  at=s['segments'][0]['seconds']+.15
  s['guides']=[dict(g,**{'from':at,'to':s['duration']-.15}) for g in items[key]]
  s['stillTargetReview']='Decoded exact selected result frame inspected; guides are editorial, visible only on the held frame.'
 p['sourceReview']=dict(evidence=f'shared/output/private-math-gameplay-20261024/end-frame-review/{ep}-0.jpg',nativeSpeed=1,limits='Diagrams illustrate principles; no claimed measurement of hidden engine data. Analytical stills are separately labelled and timed.')
 p['status']='targets-inspected-patch-review-pending';save(f,p)
# Reject source-cut contamination and align genuine hinge/deck/contact points.
for ep in ['m07','m09','m11']:
 f=B/f'{ep}-gameplay-plan.json';p=rd(f);p['patchSet']='target-fix-2'
 if ep=='m07':
  s=p['patches'][0];s['guides']=[dict(path([[.395,.33],[.418,.60]],'경첩 쪽'),**{'from':3,'to':15.1}),dict(circle(.34,.49,60,'움직인 문'),**{'from':3,'to':15.1})]
 if ep=='m09':
  for s in p['patches']:s['modelCrop']=[30,120,980,800]
  s=p['patches'][1];s['segments']=[dict(kind='motion',**{'in':71.5},seconds=3),dict(kind='still',**{'in':74.5},seconds=8.1)];s['title']='두 접점을 잇는 배선';s['meaning']='실제 배선의 두 접점 → 계산용 선분의 끝점';s['guides']=[dict(path([[.50,.09],[.57,.38]],'연결할 두 접점'),**{'from':3.2,'to':11.1})]
 if ep=='m11':
  s=p['patches'][0];s['segments']=[dict(kind='motion',**{'in':8},seconds=4),dict(kind='still',**{'in':12},seconds=7)];s['guides']=[dict(path([[.36,.52],[.61,.54]],'다리 윗면'),**{'from':4.2,'to':11})]
  s=p['patches'][1];s['guides']=[dict(path([[.36,.60],[.41,.64],[.45,.62]],'기울어진 다리 면'),**{'from':3.9,'to':12.5})]
 p['targetCorrection']='Exact-frame review rejected later source cuts and corrected object-relative targets before final assembly.';save(f,p)
