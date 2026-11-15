"""Topic-specific overview/recap, revealed at existing spoken caption boundaries."""
import sys,json,re,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from functools import lru_cache
from fontTools.ttLib import TTFont
from matplotlib.font_manager import findfont
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];PREV=HERE.parent/'revision-game-subjects-20261115'
sys.path.insert(0,str(PREV));import subject_revision as old
WHITE='#f4f2eb';GOLD='#e9ce83';TEAL='#73c7c2';MUTED='#a0a6a3'
# Exact phrase cues belong to approved speech, not estimated reading durations.
DATA={
'M21':('Lighting & Shading','빛과 셰이딩','게임은','오늘은','밝고 반짝이는 표면을 만드는 계산','반사 → 셰이딩 → 광원과 저장', ['빛의 반사','정점과 픽셀','광원 · Lightmap'], [('표면의 방향과','표면 방향·재질로 반사 계산','N · L · V · R을 같은 그림에서 읽기'),('계산하는 위치를','정점 또는 픽셀에서 셰이딩','계산 위치가 달라도 빛의 관계는 유지'),('Lightmap과','광원은 입력, Lightmap·Probe는 저장','실시간 계산과 미리 저장한 계산 구분')]),
'M22':('Skinning & Normal Mapping','스키닝과 노멀 매핑','컴퓨터는','오늘은','큰 자세와 작은 요철을 나누어 만들기','위치의 변형 / 표면 방향의 변환', ['본과 가중치','바인드 자세','노멀과 TBN'], [('스키닝은','Skinning · 본의 변환을 가중합','바인드 자세의 정점 → 움직인 정점'),('노멀 매핑은','Normal Mapping · 방향을 표면으로','텍스처의 노멀 → TBN 기저 → 조명'),('이제 캐릭터가','공통 핵심은 좌표계의 약속','위치와 방향을 올바른 공간으로 옮기기')]),
'M23':('Rendering Pipeline','렌더링 파이프라인','컴퓨터는','정점이','삼차원 장면을 화면의 픽셀로 바꾸기','정점 → 래스터화 → 픽셀과 깊이', ['좌표 변환','래스터화 · 깊이','셰이더 · 최종 색'], [('정점 셰이더가','Vertex Shader · 위치와 정보 준비','어느 공간의 값인지 먼저 확인'),('래스터화가','Rasterization · 삼각형 내부 채우기','정점 사이의 값을 픽셀로 전달'),('픽셀 셰이더와','Pixel Shader · 보이는 색 결정','텍스처·법선·깊이를 순서대로 점검')]),
'M24':('Velocity & Derivatives','속도와 미분','출발점과','오늘은','위치가 시간에 따라 바뀌는 정도 읽기','위치 기록 → 평균 속도 → 순간 속도', ['시간과 위치','접선 · 미분','이동 · 언덕의 변화율'], [('두 시점의','평균 속도는 두 시점 사이의 변화','위치 차이 ÷ 시간 차이'),('지금 이 순간의','순간 속도는 위치 그래프의 접선','미분은 그 기울기를 함수로 만드는 도구'),('단순한 이동에서는','관계가 겹치면 연쇄 법칙','길의 기울기 × 그 길을 가는 속도')]),
'M25':('Acceleration & Integration','가속도와 적분','이 사이에','오늘은','변화를 구하고, 변화를 쌓아 움직임 만들기','위치 ⇄ 속도 ⇄ 가속도', ['속도 변화 · 가속도','누적 · 적분','목표 점프 역설계'], [('위치를 미분하면','미분 · 위치 → 속도 → 가속도','시간에 따른 변화율을 차례로 구하기'),('반대로 가속도를','적분 · 가속도 → 속도 → 위치','출발값인 초기 속도·초기 위치도 필요'),('원하는 정점과','원하는 정점과 시간에서 거꾸로 설계','같은 관계를 이용해 점프의 입력값 찾기')]),
'M26':('Circular Motion','원운동','그렇다면','길을 원으로','빠르기가 같아도 방향이 바뀌면 가속도','접선의 v / 중심을 향하는 a', ['속도 벡터의 변화','속력 · 반지름','각속도 · 회전축'], [('이를 일정한','원운동의 가속도는 중심 방향','접선 방향의 속도 벡터가 계속 바뀜'),('각속도와','속력·반지름·각속도는 연결됨','삼차원에서는 회전축과 외적으로 표현'),('중요한 것은','공식보다 물체·기준·단위를 먼저','문제의 조건과 화면의 움직임 연결')]),
'M27':('Forces & Friction','힘과 마찰','이런 움직임은','먼저 뉴턴의','어떤 물체를 어느 방향으로 미는가','힘의 합 → 가속도 → 속도와 위치', ['뉴턴의 법칙','중력 · 접촉 · 마찰','점프 · 미끄러짐 설계'], [('누구에게 작용하는','물체를 정하고 힘을 방향까지 합산','중력 · 접촉력 · 마찰을 한 기준에서 읽기'),('질량으로 나누어','알짜힘을 질량으로 나누면 가속도','가속도에서 다음 속도·위치로 진행'),('현실의 법칙을','법칙을 알면 조절할 값을 고를 수 있음','게임의 점프와 미끄러짐에 적용')]),
'M28':('Springs & Damping','용수철과 감쇠','흔들리는 물체를','먼저 용수철이','돌아오는 힘에 흔들림을 줄이는 힘 더하기','복원력 + 감쇠력 → 부드러운 추종', ['늘어남 · 복원력','속도 · 감쇠력','카메라 · 메뉴 적용'], [('멀어질수록','복원력 · 멀어지면 되돌리는 힘','Spring · Fₛ = −kx'),('그리고 속도를','감쇠력 · 속도에 반대되는 힘','Damping · Fd = −cv'),('합쳐서 시간에','두 힘을 합쳐 시간에 따라 갱신','차체·카메라·메뉴의 반응을 설계')]),
'M29':('Momentum & Collisions','운동량과 충돌','충돌 전후의','힘이 만든','짧은 충돌 전후의 움직임 연결하기','충격량 → 운동량 변화 → 새 속도', ['힘과 충격량','운동량 · 질량중심','접촉 조건 · 충돌'], [('힘을 시간에 대해','Impulse · 힘을 시간에 대해 누적','충격량이 운동량을 바꿈'),('운동량 보존과','보존 법칙과 접촉 조건을 함께 사용','두 물체의 충돌 뒤 속도 결정'),('다음에는 물체를','이동을 알았다면 다음은 회전','비껴 미는 힘이 회전을 만드는 이유로 연결')]),
'M30':('Rigid Bodies & Inertia','강체와 관성','물체가 이동하는','힘을 가하는','같은 물체의 이동과 회전을 함께 계산','알짜힘 → 이동 / 토크 → 회전', ['힘의 위치 · 질량 분포','각운동량 · 토크','접촉 · 물리 시간 갱신'], [('알짜힘은','알짜힘은 질량중심의 움직임을 바꿈','이동에 작용하는 힘을 모으기'),('토크는','토크는 각운동량을 바꿈','가하는 위치와 질량 분포도 중요'),('접촉점에서는','접촉점에는 이동과 회전이 함께 나타남','제약을 맞추며 작은 시간씩 갱신')]),
'M31':('Parametric Curves & Hermite','매개 곡선과 에르미트','이런 길을','먼저 곡선의','길 위의 위치와 출발·도착 방향 정하기','p(t) → 지날 점 → 끝점과 접선', ['곡선의 표현','보간 · 지나갈 점','Hermite · 끝점 방향'], [('오늘의 핵심은','공식보다 어떤 입력을 정할지 먼저','위치·방향·변화량 중 필요한 조건 선택'),('지나야 할 점을','지나야 할 점을 정하면 보간 문제','Parameter t에서 위치 p(t)를 계산'),('출발과 도착의','끝점과 접선을 정하면 Hermite 표현','출발·도착 방향과 변화량을 직접 조절')]),
'M32':('Bézier & Subdivision','베지에와 분할','이렇게 곡선의','이번에는','제어점으로 곡선을 만들고 모양대로 나누기','제어점 → 반복 보간 → 분할', ['반복 보간','가중치 · 도함수','모양 보존 분할'], [('반복 보간으로','반복 보간으로 곡선 위 점 생성','제어점 사이를 같은 비율로 연결'),('그 계산을','가중치·도함수로 손잡이 역할 읽기','끝점과 접선이 모양을 조절'),('같은 중간점들을','중간점들을 모으면 모양 보존 분할','나누어도 원래 경로와 같은 곡선')]),
'M33':('Splines & Continuity','스플라인과 연속성','긴 경로를','오늘은','작은 곡선을 자연스럽게 이어 긴 길 만들기','곡선 조각 → 연결 조건 → 자동 접선', ['조각별 곡선','C⁰ · C¹ · C² 연속','자동 접선 · 경로 설계'], [('다루기 쉬운','다루기 쉬운 곡선 조각들을 연결','한 부분을 수정할 때의 영향 줄이기'),('위치와 방향과','위치·방향·변화량의 연결 조건 선택','모양뿐 아니라 움직임의 연속성도 확인'),('이 기준을 알고','조건을 알면 수동·자동 접선을 설계','왜 그 움직임이 나오는지 설명할 수 있음')])}
def norm(s):return re.sub(r'[^\w]','',s).lower()
def cue(s,phrase):
 rows=[c for c in s['captionEvidence'] if norm(phrase) in norm(c['text'])]
 assert len(rows)==1,(s['scene'],phrase,rows)
 return max(s['start'],rows[0]['start'])
def make_plan():
 prev=json.loads((PREV/'delivery.json').read_text(encoding='utf8'));rows=[]
 for delivered in prev['episodes']:
  eid=delivered['id'];e=old.EPISODES[eid];d=DATA[eid];first=e['scenes'][0];last=e['scenes'][-2] if eid=='M25' else e['scenes'][-1]
  start=cue(first,d[2]);road=cue(first,d[3]);recap=last['start']
  if eid=='M29':recap=cue(last,'오늘의 흐름을')
  if eid=='M31':recap=cue(last,'오늘의 핵심은')
  if eid=='M33':recap=cue(last,'긴 경로를 만들 때')
  q=ROOT/'projects'/e['slug']/'production/local'/e['baselineRevision']/'queue.json'
  hook=first.get('originalGame',{}).get('duration',first['end']-2)
  if q.exists():
   cuts=json.loads(q.read_text(encoding='utf8'))['cuts'];hook=next(c['frames']/60 for c in cuts if c['kind']=='actual-gameplay' and c['globalStartFrame']==0)
  rows.append(dict(id=eid,slug=e['slug'],frames=delivered['frames'],sources=delivered['files'],title=d[1],english=d[0],definition=d[4],relationship=d[5],steps=d[6],start=start,roadmap=road,end=first['end'],hookSeconds=hook,recapStart=recap,recapEnd=last['end'],recap=[dict(at=cue(last,p),title=t,meaning=m) for p,t,m in d[7]],humanReviewed=False))
 plan=dict(scope=list(DATA),userRequest='M21–M33 actual-facing / diagram direction audit; narrated overview and recap in every lesson, following animation playlist',noNewTts=True,voiceTempo=1,existingBodyPreserved=True,upload=False,platformChanges=False,episodes=rows)
 (HERE/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8');return plan
PRIMARY='C:/Windows/Fonts/malgun.ttf';FALLBACK=findfont('DejaVu Sans');CMAP=TTFont(PRIMARY).getBestCmap();FALLBACK_CMAP=TTFont(FALLBACK).getBestCmap()
@lru_cache(maxsize=64)
def font(size,fallback=False):return ImageFont.truetype(FALLBACK if fallback else PRIMARY,size)
def runs(s,size):
 result=[]
 for c in s:
  fallback=ord(c) not in CMAP
  assert not fallback or ord(c) in FALLBACK_CMAP or c.isspace(),('Missing visible glyph',c)
  if result and result[-1][0]==fallback:result[-1]=(fallback,result[-1][1]+c)
  else:result.append((fallback,c))
 return [(font(size,f),t) for f,t in result]
def length(s,size):return sum(f.getlength(t) for f,t in runs(s,size))
def draw_text(d,xy,s,size,color):
 x,y=xy;baseline=y+font(size).getmetrics()[0]
 for f,t in runs(s,size):d.text((x,baseline),t,font=f,fill=color,anchor='ls');x+=f.getlength(t)
def text(d,xy,s,size=44,color=WHITE,width=850):
 x,y=xy;f=font(size)
 for paragraph in s.split('\n'):
  line=''
  for w in paragraph.split():
   candidate=(line+' '+w).strip()
   if length(candidate,size)>width and line:draw_text(d,(x,y),line,size,color);y+=size+15;line=w
   else:line=candidate
  draw_text(d,(x,y),line,size,color);y+=size+15
 return y
def canvas(row,label):
 im=Image.new('RGBA',(1920,1080),'black');d=ImageDraw.Draw(im)
 text(d,(65,35),row['english'],48,GOLD,1780);text(d,(65,105),row['title']+' · '+label,40,WHITE,1780)
 d.line((65,177,1855,177),fill='#454b48',width=2);return im,d
def build(row):
 p=HERE/'local/work'/row['slug'];p.mkdir(parents=True,exist_ok=True)
 im,d=canvas(row,'이번에 배울 내용')
 text(d,(70,235),row['definition'],45,WHITE,850)
 text(d,(70,460),'관계를 먼저 보고, 계산으로 연결합니다',32,MUTED)
 text(d,(70,535),row['relationship'],44,TEAL,850)
 text(d,(1030,245),'실제 사례 다시 보기 → 설명 모형',32,MUTED,820)
 # Main captions are redrawn over this canvas at their exact approved times.
 im.save(p/'overview.png')
 roadmap=Image.new('RGBA',(1920,1080));rd=ImageDraw.Draw(roadmap)
 for i,s in enumerate(row['steps']):
  x=75+i*615;rd.line((x,785,x+545,785),fill=TEAL,width=4);text(rd,(x,805),f'{i+1:02}  '+s,36,WHITE,550)
 roadmap.save(p/'roadmap.png')
 for n in range(4):
  im,d=canvas(row,'이번 편 정리')
  text(d,(1030,245),'같은 관계를 화면에서 다시 읽기',32,MUTED,820)
  if n==0:text(d,(70,275),'처음 보았던 장면을\n배운 관계로 다시 살펴봅니다',44,WHITE,880)
  for i,point in enumerate(row['recap'][:n]):
   y=245+i*205;d.line((75,y+10,75,y+132),fill=TEAL,width=5)
   ty=text(d,(100,y),point['title'],38,WHITE,835)
   text(d,(100,max(y+70,ty+3)),point['meaning'],32,TEAL,835)
  im.save(p/f'recap-{n}.png')
 return p
if __name__=='__main__':
 for row in make_plan()['episodes']:build(row)
