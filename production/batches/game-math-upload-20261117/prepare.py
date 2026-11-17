"""Prepare approved masters' publishing metadata and editable vector thumbnails."""
import json,pathlib,re,hashlib,html,datetime,subprocess,difflib
R=pathlib.Path('D:/Github/VideoEditing');H=pathlib.Path(__file__).resolve().parent
REV=R/'production/batches/game-math-remaining-20261104/revision-concept-examples-20261116'
def rd(p):return json.loads(pathlib.Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):pathlib.Path(p).parent.mkdir(parents=True,exist_ok=True);pathlib.Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
DATA=[
('같은 구인데 왜 다르게 빛날까? | 게임수학: 빛과 셰이딩','Why Does the Same Sphere Shine Differently? | Light and Shading', ['같은 구인데','왜 다르게','빛날까?'],'법선과 빛·시선 방향을 그림 위에서 함께 읽고, 반사 계산에서 셰이딩·광원의 모양·라이트맵까지 연결합니다. 자동차의 반사와 건물 표면 등 실제 게임 장면으로 배운 개념을 확인합니다.','Read the normal, light and view directions on the surface, then connect reflection, shading, light shapes and lightmaps. Inspect car reflections and illuminated game surfaces.',[0,8,16,24,39,48,56,72],['오늘의 질문','법선·반사·시선 방향','반짝임을 조절하는 값','환경광과 간접광','정점과 픽셀 셰이딩','광원의 거리와 크기','면광원과 빛의 범위','표면에 조명을 저장하기']),
('캐릭터의 팔은 어떻게 자연스럽게 구부러질까? | 스키닝·노멀 매핑','How Does a Game Character Bend? | Skinning and Normal Mapping',['팔은 어떻게','자연스럽게','구부러질까?'],'마리오의 몸 전체 이동과 관절의 굽힘을 나누어 보고, 본과 가중치로 정점을 움직이는 스키닝을 설명합니다. 둠 3의 금속 표면과 함께 접선 공간·노멀 매핑·UV의 관계도 연결합니다.','Separate whole-body movement from joint bending in Mario, and learn how bones and weights move vertices. Connect tangent space, normal maps and UVs to the metal surfaces in Doom 3.',[0,6,12,18,24,30,35],['오늘의 질문','본 번호와 가중치','정점과 본의 저장 구조','텍스처와 방향의 재사용','접선·비탄젠트·법선','UV가 겹칠 때의 처리','이번 편 정리']),
('게임의 3D 장면은 어떻게 한 프레임이 될까? | 렌더링 파이프라인','How Does a 3D Game Scene Become a Frame? | Rendering Pipeline',['3D 장면이','한 장의 화면이','되기까지'],'타운스케이퍼의 건축과 포털의 가려짐에서 출발해, 입력 데이터가 정점·래스터화·픽셀 처리와 셰이더를 거쳐 화면으로 이어지는 과정을 살펴봅니다. 계산 목적과 실제 게임 결과를 함께 연결합니다.','Follow a scene from input data through vertex processing, rasterization, pixels and shaders. Building edits in Townscaper and visibility in Portal connect the calculations to their visible results.',[0,8,11,22,33,44,55,66],['오늘의 질문','그릴 그림과 보여줄 그림','렌더링 입력과 상태','화면 밖 영역의 처리','셰이더 입출력','여러 광원의 계산','보이는 깊이 범위','표면 기저와 파이프라인 연결']),
('지금 이 순간의 속도는 어떻게 구할까? | 게임수학: 속도와 미분','How Do We Find Velocity Right Now? | Velocity and Derivatives',['지금 이 순간','속도는 어떻게','구할까?'],'마리오의 이동과 자동차 속도계를 보며 변위·거리·평균속도·순간 변화율을 구분합니다. 미분이 무엇을 구하는지 먼저 이해한 뒤 그래프의 기울기와 미분 규칙, 연쇄법칙으로 이어갑니다.','Use Mario movement and a racing speedometer to distinguish displacement, distance, average velocity and instantaneous rate. Connect graph slopes to derivatives and the chain rule.',[0,7,14,21,28,35,42,46],['오늘의 질문','시간에 따라 달라지는 양','변위와 실제 이동 거리','변화율의 뜻','위치 그래프에서 속도 읽기','미분 규칙 적용','여러 변화가 연결될 때','이번 편 정리']),
('속도가 계속 바뀌면 위치는 어떻게 구할까? | 가속도와 적분','How Do We Find Position When Velocity Changes? | Acceleration and Integration',['바뀌는 속도','이동 거리는','어떻게 구할까?'],'마리오카트의 출발과 자동차·마리오의 점프를 보며 가속도와 누적 이동을 연결합니다. 잘게 나누어 더한다는 적분의 뜻에서 시작해 원시함수·초기 조건·정적분으로 이어갑니다.','Connect acceleration and accumulated movement to kart starts, driving and jumps. Begin with adding small changes, then learn antiderivatives, initial conditions and definite integrals.',[0,6,12,18,24,30,36,38],['오늘의 질문','속도에서 위치로','낙하 시간 계산','점프의 수평·수직 성분','작은 이동을 더하기','미분을 거꾸로 읽기','정적분과 원시함수','이번 편 정리']),
('커브를 돌면 왜 가속도가 생길까? | 원운동과 각속도','Why Is Turning an Acceleration? | Circular Motion and Angular Velocity',['커브를 돌면','왜 가속도가','생길까?'],'카트가 코너를 돌고 왕눈의 판이 회전하는 장면으로 속력과 방향의 변화를 나누어 봅니다. 원운동·각속도·접선 속도·단위 변환을 계산 목적과 그림의 기호부터 연결합니다.','Distinguish changes in speed from changes in direction using kart cornering and rotating objects in Zelda. Connect circular motion, angular velocity, tangential velocity and units.',[0,6,12,18,24,30,36,39],['오늘의 질문','각도로 원의 위치 적기','외적과 회전 방향','단위와 차원 읽기','구간별 속도 변화','포물선의 정점과 사거리','회전과 계산의 연결','이번 편 정리']),
('바퀴는 왜 미끄러지지 않고 차를 밀어줄까? | 힘과 마찰','How Do Wheels Push a Car Forward? | Forces and Friction',['바퀴는 어떻게','차를 앞으로','밀어줄까?'],'뉴턴의 법칙에서 알짜힘·자유 물체도·작용과 반작용을 연결합니다. 대포의 반동, 왕눈의 낙하, 바위를 오르는 바퀴를 보며 중력과 정지·운동 마찰을 구분합니다.','Connect Newton’s laws to net force, free-body diagrams and action–reaction. Use cannon recoil, falling objects and climbing wheels to distinguish gravity, static friction and kinetic friction.',[0,5,10,15,20,25,30,31],['오늘의 질문','여러 힘의 합','어느 기준에서 볼까','물체를 하나의 계로 묶기','게임의 중력 설정','미끄러지기 전의 마찰','접촉 면적과 마찰','이번 편 정리']),
('게임 카메라는 어떻게 부드럽게 따라올까? | 용수철과 감쇠','How Does a Game Camera Follow Smoothly? | Springs and Damping',['부드러운 움직임','용수철 하나로','만들 수 있을까?'],'당겼다 놓는 멍멍이, 차체의 흔들림과 라이더를 따라가는 카메라를 연결합니다. 되돌리는 힘과 속도를 줄이는 힘을 나누고, 초기 조건·감쇠비·목표 추종을 차근차근 살펴봅니다.','Connect a pulled-and-released Chomp, vehicle suspension and a following camera. Separate restoring force from damping, then examine initial conditions, damping ratio and target following.',[0,4,8,12,16,20,24],['오늘의 질문','가속도에서 시간 함수로','초기 속도와 위상','감쇠비와 흔들림','움직이는 목표 따라가기','제작자가 조절할 값','이번 편 정리']),
('충돌한 물체는 왜 다른 방향으로 튕길까? | 운동량과 충격량','Why Does an Object Bounce After a Collision? | Momentum and Impulse',['부딪힌 뒤','움직임은 왜','달라질까?'],'자동차 충돌과 멍멍이의 바위 파괴를 보며 충격량·운동량·충돌 판정과 반응을 구분합니다. 계의 경계·질량중심·반발계수를 식의 목적과 실제 움직임에 연결합니다.','Use vehicle impacts and Chomp collisions to distinguish impulse, momentum, hit detection and response. Connect system boundaries, center of mass and restitution to visible motion.',[0,6,12,18,24,30,36,37],['오늘의 질문','서로 주고받는 운동량','계의 질량중심','닿았는지 찾는 일과 반응','법선 방향과 반발','반발계수를 바꾸면','충돌 전후의 속도 변화','이번 편 정리']),
('같은 힘인데 왜 어떤 물체는 더 잘 돌까? | 강체와 관성','Why Do Some Objects Rotate More Easily? | Rigid Bodies and Inertia',['같은 힘인데','왜 더 쉽게','돌아갈까?'],'대포의 반동과 차량의 충돌·서스펜션을 보며 질량중심 이동과 회전을 나누어 봅니다. 토크·관성모멘트·관성 텐서·구속 조건을 작은 모형과 실제 게임 움직임으로 연결합니다.','Separate center-of-mass movement from rotation using cannon recoil, vehicle impacts and suspension. Connect torque, moment of inertia, inertia tensors and constraints to small models and real gameplay.',[0,10,20,30,40,50,60],['오늘의 질문','질량 배치와 관성모멘트','접촉점의 충격량','물리 처리의 순서','각속도와 회전 행렬','힘과 변형의 관계','이번 편 정리']),
('열차가 휘어진 선로를 따라가게 하려면? | 매개 곡선과 에르미트','How Do We Move a Train Along a Curve? | Parametric and Hermite Curves',['휘어진 길을','따라가는 위치','어떻게 구할까?'],'선로의 모양과 열차가 지나가는 속도를 나누어 생각합니다. 매개변수·다항식·보간 조건에서 출발해 끝점과 접선으로 에르미트 곡선을 만드는 과정을 연결합니다.','Separate a railway’s shape from a train’s speed along it. Build from parameters, polynomials and interpolation conditions to Hermite curves defined by endpoints and tangents.',[0,6,12,18,24,30,36],['오늘의 질문','곡선을 행렬로 묶기','위치와 진행 방향','시각 사이를 보간하기','다항식 조건과 유일성','에르미트 기저','더 많은 끝점 조건']),
('손잡이를 움직이면 곡선은 어떻게 바뀔까? | 베지에 곡선과 분할','How Do Handles Change a Curve? | Bezier Curves and Subdivision',['손잡이 하나로','곡선 전체가','바뀌는 이유'],'마리오 메이커의 경로 편집과 카트의 코너링을 보며 제어점·접선·곡률을 구분합니다. 반복 보간으로 베지에 곡선을 만들고 모양을 보존하며 일부 구간을 나누는 방법으로 이어갑니다.','Use track editing and kart cornering to distinguish control points, tangents and curvature. Build Bezier curves through repeated interpolation and subdivide them while preserving shape.',[0,5,10,15,20,25,29],['오늘의 질문','반복 보간과 다항식','손잡이와 곡선의 변화','제어점의 영향 범위','끝점의 속도와 고차 변화','드 카스텔조 분할','이번 편 정리']),
('이어 붙인 길이 왜 꺾여 보일까? | 스플라인과 연속성','Why Does a Joined Path Have a Kink? | Splines and Continuity',['이어진 길인데','왜 여기서','꺾여 보일까?'],'선로와 트랙을 이어 붙이는 장면으로 위치가 이어지는 것과 방향·속도까지 매끄러운 것을 구분합니다. 기하·매개 연속성, TCB 접선, 끝점 조건과 국소 편집을 연결합니다.','Use joined railways and tracks to distinguish connected positions from smooth directions and speeds. Connect geometric and parametric continuity, TCB tangents, endpoints and local editing.',[0,7,14,21,28,35,42],['오늘의 질문','들어오고 나가는 접선','기하 연속성','장력·연속성·편향','시간과 구간을 연결하기','제어점 배치의 함정','이번 편 정리'])
]
EN_CHAPTERS=[
['The question','Normal, reflected light and view','Controlling highlights','Ambient and indirect light','Vertex and pixel shading','Light distance and size','Area lights and light footprints','Storing light on surfaces'],
['The question','Bone indices and weights','Storing vertices and bones','Reusing textures and directions','Tangent, bitangent and normal','Handling degenerate UVs','Recap'],
['The question','Drawing and presenting frames','Rendering inputs and state','Regions outside the screen','Shader inputs and outputs','Combining multiple lights','Visible depth range','Surface bases and the pipeline'],
['The question','Quantities changing over time','Displacement versus traveled distance','Meaning of a rate of change','Reading velocity from a position graph','Differentiation rules','Connecting changes','Recap'],
['The question','From velocity to position','Finding a fall time','Horizontal and vertical jump motion','Adding small movements','Reading differentiation backward','Definite integrals and antiderivatives','Recap'],
['The question','Circle positions from angles','Cross products and rotation direction','Units and dimensions','Piecewise velocity changes','Projectile apex and range','Connecting motion and calculations','Recap'],
['The question','Net force','Choosing a reference frame','Choosing a system boundary','Gravity settings in games','Friction before sliding','Contact area and friction','Recap'],
['The question','From acceleration to a time function','Initial velocity and phase','Damping ratio and oscillation','Following a moving target','Parameters for creators','Recap'],
['The question','Exchanging momentum','Center of mass of a system','Detection versus response','Normals and restitution','Changing restitution','Velocity before and after impact','Recap'],
['The question','Mass distribution and inertia','Impulse at a contact point','Physics update order','Angular velocity and rotation matrices','Force and deformation','Recap'],
['The question','Writing a curve as a matrix','Position and travel direction','Interpolating between times','Polynomial constraints and uniqueness','The Hermite basis','Additional endpoint constraints'],
['The question','Repeated interpolation and polynomials','Handles and curve shape','The influence of control points','Endpoint velocity and higher derivatives','De Casteljau subdivision','Recap'],
['The question','Incoming and outgoing tangents','Geometric continuity','Tension, continuity and bias','Connecting time and curve segments','Control-point pitfalls','Recap']]
def norm(s):return re.sub('[^가-힣a-z0-9]','',s.lower())
def srt(p):
 out=[]
 for block in pathlib.Path(p).read_text(encoding='utf-8-sig').replace('\r','').strip().split('\n\n'):
  ls=block.splitlines()
  if len(ls)>2 and ' --> ' in ls[1]:
   h,m,s=map(float,ls[1].split(' --> ')[0].replace(',','.').split(':'));out.append((h*3600+m*60+s,' '.join(ls[2:])))
 return out
def stamp(t):t=int(t);return f'{t//60:02}:{t%60:02}'
def diagram(i):
 pre='<g stroke="#191b19" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round">'
 colors=['#eec85f','#64a7a5','#c93632']
 if i==0:b='<circle cx="965" cy="333" r="150" fill="url(#sphere)" stroke="none"/><circle cx="1120" cy="485" r="99" fill="url(#sphere2)" stroke="none"/>'
 elif i==1:b='<path d="M860 220L1010 335L1090 490" stroke="#65a8a6" stroke-width="68"/><path d="M860 220L1010 335L1090 490" stroke="#191b19" stroke-width="9"/>'+''.join(f'<circle cx="{x}" cy="{y}" r="19" fill="#ffcd41"/>' for x,y in [(860,220),(1010,335),(1090,490)])
 elif i==2:b='<path d="M795 250L940 170L940 390Z" fill="#eac764"/><path d="M975 310H1030"/><path d="M1010 290L1030 310L1010 330"/>'+''.join(f'<rect x="{1050+x*38}" y="{230+y*38}" width="34" height="34" fill="{colors[(x+y)%3]}" stroke-width="2"/>' for x in range(4) for y in range(5))
 elif i in (3,4):b='<path d="M790 470H1190M790 470V200"/><path d="M805 450Q920 450 980 340T1160 220" stroke="#64a7a5" stroke-width="11"/>'+('<path d="M805 470V450Q920 450 980 340T1160 220V470Z" fill="#ffcf4188" stroke="none"/>' if i==4 else '<path d="M920 420L1090 240" stroke="#c93632" stroke-width="10"/>')+'<circle cx="995" cy="328" r="18" fill="#ffcf41"/>'
 elif i==5:b='<circle cx="980" cy="340" r="153" stroke="#64a7a5" stroke-width="11"/><path d="M980 340H1133M1133 340V170M1113 193L1133 170L1153 193"/><circle cx="1133" cy="340" r="20" fill="#ffcf41"/><circle cx="980" cy="340" r="8" fill="#191b19"/>'
 elif i==6:b='<path d="M785 480H1190"/><rect x="940" y="285" width="172" height="172" rx="12" fill="#e8bf60"/><path d="M790 365H930M905 340L930 365L905 390" stroke="#c93632" stroke-width="15"/><path d="M1030 270V180M1010 204L1030 180L1050 204" stroke="#65a8a6" stroke-width="11"/>'
 elif i==7:b='<path d="M785 270V470M785 370H815L832 325L857 415L882 325L907 415L932 325L957 415L974 370H1000"/><rect x="1000" y="296" width="155" height="155" rx="14" fill="#e9c25d"/><path d="M940 240H1140M1110 218L1140 240L1110 262" stroke="#c93632"/>'
 elif i==8:b='<circle cx="905" cy="350" r="88" fill="#e8c563"/><circle cx="1110" cy="350" r="88" fill="#66aaa6"/><path d="M790 220H940M910 195L940 220L910 245" stroke="#c93632" stroke-width="11"/><path d="M1010 435L990 472L1030 460L1020 500" stroke="#c93632"/>'
 elif i==9:b='<path d="M845 355H1150M998 205V505" stroke="#8d9696"/>'+''.join(f'<circle cx="{x}" cy="{y}" r="33" fill="{colors[k%3]}"/>' for k,(x,y) in enumerate([(850,355),(1145,355),(998,210),(998,500)]))+'<path d="M1060 220Q1180 300 1110 430M1100 405L1110 430L1140 425" stroke="#c93632" stroke-width="11"/>'
 else:
  b='<path d="M790 455C860 150 1050 170 1185 395" stroke="#65a8a6" stroke-width="11"/>'
  if i==10:b+='<path d="M795 465C860 160 1050 180 1180 405" stroke="#eac764" stroke-width="3"/><path d="M792 445C860 140 1050 160 1188 385" stroke="#eac764" stroke-width="3"/>'
  if i==11:b+='<path d="M790 455L860 150L1050 170L1185 395" stroke="#aaafaf" stroke-width="4"/>'+''.join(f'<circle cx="{x}" cy="{y}" r="16" fill="#e8c563" stroke-width="4"/>' for x,y in [(790,455),(860,150),(1050,170),(1185,395)])
  if i==12:b='<path d="M790 430L985 260L1190 430" stroke="#c93632" stroke-width="10"/><path d="M790 480Q985 310 1190 480" stroke="#65a8a6" stroke-width="10"/>'
 return pre+b+'</g>'
def thumbnail(e,data,i,folder):
 # The original diagram + corner mascot was rejected by the user on 2026-11-17.
 # Reuse only the individually generated, visually reviewed illustrated asset.
 asset=H/'thumbnail-revision-v2'/e['id']/'thumbnail.png'
 if not asset.is_file():raise RuntimeError('Missing reviewed cat-led illustration: '+e['id'])
 return asset

def main():
 if (H.parent/'longform-daily-schedule-20261117/final-verification.json').exists():raise RuntimeError('Publishing preparation is frozen after saved reservations. Current dates: longform-daily-schedule-20261117/summary.json')
 batch=rd(H/'batch.json');delivery=rd(REV/'delivery.json');inventory={e['id']:e for e in rd(REV.parent/'revision-teaching-sync-20261115/inventory.json')['episodes']};sources=rd(REV/'sources.json');rights=rd(REV/'source-rights.json')['sources'];footer=(R/'shared/publishing/youtube-channel-description.ko.txt').read_text(encoding='utf8').split('📚 수업 노트')[0].strip();defaults=rd(R/'shared/publishing/youtube-defaults.json');review=[]
 for i,(e,data,row) in enumerate(zip(delivery['episodes'],DATA,batch['rows'])):
  folder=H/e['id'];folder.mkdir(exist_ok=True);thumbnail(e,data,i,folder)
  cues=srt(e['files']['ko']['path']);buf='';starts=[]
  for t,text in cues:starts.extend([t]*len(norm(text)));buf+=norm(text)
  scenes={s['scene']:s for s in inventory[e['id']]['scenes']};chapters=[]
  for sid,title in zip(data[5],data[6]):
   s=scenes[f'{sid:03}'];prefix=norm(s['speech'])[:24];at=0 if sid==0 else buf.find(prefix)
   if at<0:
    speech=norm(s['speech']);matches=[(buf.find(speech[a:a+16]),speech[a:a+16]) for a in range(0,len(speech)-16,4) if buf.find(speech[a:a+16])>=0]
    if matches:at,prefix=matches[0]
    else:
     match=difflib.SequenceMatcher(None,speech,buf,autojunk=False).find_longest_match(0,len(speech),0,len(buf));assert match.size>=12,(e['id'],sid,'no reliable spoken anchor');at=match.b;prefix=speech[match.a:match.a+match.size]
   assert at>=0,(e['id'],sid,'chapter speech not found');t=0 if sid==0 else starts[at]
   if not chapters or t-chapters[-1]['start']>=10:chapters.append(dict(scene=f'{sid:03}',start=t,title=title,titleEn=EN_CHAPTERS[i][data[5].index(sid)],matchedCaptionPhrase=prefix,matchedSpeech=s['speech'][:90]))
  selected={s['originalGame']['sourceId'] for s in inventory[e['id']]['scenes'] if s.get('originalGame')}
  if e['id']=='M27':selected.add('_wH_-1saHnw') # Actual Mario explanatory cutout.
  selected.update(sources[s['source']]['id'] if 'id' in sources[s['source']] else sources[s['source']].get('sourceId','') for s in e['inserts'])
  # Source IDs in the current catalog are recorded in the URL / filename map.
  selected.update(re.search(r'[?&]v=([^&]+)',r['url']).group(1) for r in rights if any(q['episode']==e['id'] for q in r['ranges']))
  foot=rd(R/'projects'/e['slug']/'planning/footage-audit.json')['sources'];credit=[];seen=set()
  for src in foot:
   sid=src['id']
   if sid not in selected:continue
   basis=src.get('recordingPermission',{}).get('basis','');current=next((r for r in rights if re.search(r'[?&]v=([^&]+)',r['url']).group(1)==sid),None)
   if current:cc='Creative Commons Attribution' in (current.get('license') or '')
   else:
    metadata=R/(src.get('recordingPermission',{}).get('metadata') or src.get('recordingPermission',{}).get('evidence') or '')
    cc=metadata.is_file() and 'Creative Commons Attribution' in rd(metadata).get('license','')
   name=src.get('title',src['game']) if cc else src['game']
   credit.append(f"{name} — {src['uploader']} | {src['recordingUrl']}"+(' | CC BY; edited/annotated. https://creativecommons.org/licenses/by/3.0/' if cc else ' | Recorder permits reuse; edited educational excerpt.'));seen.add(sid)
  for src in rights:
   sid=re.search(r'[?&]v=([^&]+)',src['url']).group(1)
   if sid not in selected or sid in seen:continue
   cc='Creative Commons' in (src.get('license') or '');name=src.get('title',src['game']) if cc else src['game']
   credit.append(f"{name} — {src['uploader']} | {src['url']}"+(' | CC BY; edited/annotated. https://creativecommons.org/licenses/by/3.0/' if cc else ' | Recorder permits reuse; edited educational excerpt.'));seen.add(sid)
  if e['id'] in ('M27','M28'):credit.append('BeamNG vehicle illustration — BeamNG Drive Crashes | https://www.youtube.com/watch?v=cKarsLzGuFE | CC BY; cropped/annotated. https://creativecommons.org/licenses/by/3.0/')
  credit += ['3D Math Primer — Fletcher Dunn & Ian Parberry | https://gamemath.com/book/','Unity | https://unity.com/ · Qwen3-TTS | https://github.com/QwenLM/Qwen3-TTS · FFmpeg | https://ffmpeg.org/']
  if e['id']=='M21':credit+=['Analog Memory environment — EmaceArt | https://emaceart.itch.io/1990s-retro-game-environments-classic-mid-poly-rooms']
  ko=data[3]+'\n\n'+ '\n'.join(stamp(c['start'])+' '+c['title'] for c in chapters)+'\n\n'+footer+'\n\n출처·자료·제작 도구\n'+'\n'.join(credit)
  # English chapters share measured timings and retain exact technical topic labels.
  en=data[4]+'\n\n'+ '\n'.join(stamp(c['start'])+' '+c['titleEn'] for c in chapters)+'\n\nYamYamCoding · Game programming and graphics\nProgramming coaching: '+defaults['coaching']['url']+'\nDiscord: https://discord.gg/wZuqe7fqkR\nMembership: '+defaults['membershipUrl']+'\n\nSources and credits\n'+'\n'.join(credit)
  assert len(ko)<=5000 and len(en)<=5000,(e['id'],len(ko),len(en));assert not any(x in ko for x in ['원영상','사쿠라이','여기에-GitHub'])
  for lang,text in [('ko',ko),('en',en)]: (folder/f'description.{lang}.txt').write_text(text+'\n',encoding='utf8')
  (folder/'pinned-comment.ko.txt').write_text(data[3]+'\n\n프로그래밍 코칭: '+defaults['coaching']['url']+'\n',encoding='utf8')
  schedule=datetime.datetime(2027,1,17,8,tzinfo=datetime.timezone(datetime.timedelta(hours=9)))+datetime.timedelta(days=i)
  row.update(titleKo=data[0],titleEn=data[1],descriptionKo=ko,descriptionEn=en,chapters=chapters,scheduleKst=schedule.isoformat(),thumbnail=str(H/'thumbnail-revision-v2'/e['id']/'thumbnail.png'),descriptionFiles={l:str(folder/f'description.{l}.txt') for l in ('ko','en')},sourceCredits=credit,playlistId=batch['playlistId'],humanContinuousListeningClaimed=False)
  save(folder/'package.json',row);review.append(dict(id=e['id'],title=data[0],chapters=chapters,descriptionChars=dict(ko=len(ko),en=len(en)),sourceIds=sorted(selected)))
 save(H/'batch.json',batch);save(H/'metadata-review.json',dict(status='prepared-for-content-and-render-review',rows=review));print('Prepared13 packages, all descriptions under5000 characters; exact spoken chapter anchors')
if __name__=='__main__':main()
