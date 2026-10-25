from pathlib import Path
import json,re
R=Path(__file__).resolve().parents[3]
B=Path(__file__).resolve().parent
state=json.loads((B/'checkpoint.json').read_text(encoding='utf-8'))
titles=[
('같은 방향인데 왜 기울기는 다를까? | 3D 회전 ① 방향과 회전 행렬','Same Direction, Different Tilt? | 3D Rotation 1: Orientation and Matrices'),
('회전 순서만 바꿨는데 왜 자세가 달라질까? | 3D 회전 ② 오일러 각과 축·각','Why Does Rotation Order Change the Result? | Euler Angles and Axis–Angle'),
('회전을 저장하는 데 숫자 네 개가 필요한 이유 | 쿼터니언 ①','Why Four Numbers for a Rotation? | Quaternions 1'),
('지금 자세에서 목표 자세까지, 어떻게 돌릴까? | 쿼터니언 ②','How Do We Rotate from Here to a Target? | Quaternions 2'),
('두 자세 사이를 자연스럽게 움직이려면? | 회전 보간 ①','How Do We Move Smoothly Between Orientations? | Rotation Interpolation 1'),
('각도와 쿼터니언과 행렬, 정말 같은 회전일까? | 회전 보간 ②','Angles, Quaternions and Matrices: The Same Rotation? | Rotation Interpolation 2'),
('두 점만 알면 연결선을 어떻게 만들까? | 직선과 경계 ①','How Do Two Points Define a Connection? | Lines and Bounds 1'),
('물체를 돌렸는데 충돌 상자는 왜 커질까? | 직선과 경계 ②','Why Can a Bounding Box Grow When an Object Rotates? | Lines and Bounds 2'),
('바닥까지 얼마나 남았을까? | 평면과 삼각형 ① 표면까지의 거리','How Far Is the Surface? | Planes and Triangles 1'),
('삼각형 안의 한 점에는 어떤 주소를 붙일까? | 평면과 삼각형 ②','How Do We Address a Point Inside a Triangle? | Planes and Triangles 2'),
('도형의 중심은 왜 하나가 아닐까? | 다각형 ① 중심과 경계','Why Does a Shape Have Different Centers? | Polygons 1'),
('삼각형으로 나눴는데 빈 공간이 사라진다면? | 다각형 ② 삼각형 분할','What If Triangulation Fills an Empty Space? | Polygons 2'),
('화면의 한 점은 왜 그 색과 밝기로 보일까? | 렌더링 ① 빛·재질·시선','Why Does a Pixel Have That Color and Brightness? | Rendering 1'),
('카메라를 앞으로 옮기는 것과 줌은 뭐가 다를까? | 렌더링 ②','Moving the Camera or Zooming: What Changes? | Rendering 2'),
('게임 속 3D 점은 어떻게 화면의 픽셀이 될까? | 렌더링 ③','How Does a 3D Point Become a Screen Pixel? | Rendering 3'),
('화면 좌표를 구했는데 깊이와 w는 왜 남을까? | 렌더링 ④','Why Keep Depth and w After Projection? | Rendering 4'),
('삼각형으로 만든 물체는 어떻게 매끈해 보일까? | 렌더링 ⑤ 메시·법선','How Can a Triangle Mesh Look Smooth? | Rendering 5: Meshes and Normals'),
('물체를 늘렸더니 빛과 무늬가 이상해진다면? | 렌더링 ⑥ 법선 변환과 UV','Why Do Lighting and Textures Change When We Scale an Object? | Rendering 6')]
extra={
 'totk':'The Legend of Zelda: Tears of the Kingdom — Nintendo. Recording: Royalty Free Game Clips; transformative reuse allowed by uploader.\nhttps://www.youtube.com/watch?v=YNQ20CKbY8U',
 'besiege':'Besiege — Spiderling Studios. Advanced Building footage; publisher permission and original links.\nhttps://www.youtube.com/watch?v=uWKEJ92486U\nhttp://multiverse.spiderlinggames.co.uk/',
 'bridge':'Poly Bridge 3 — Dry Cactus. Official release trailer.\nhttps://store.steampowered.com/app/1850160/Poly_Bridge_3/',
 'big':'Big Walk — NCR Gameplay recording.\nhttps://www.youtube.com/watch?v=wzQLP0Z3zII',
 'town':'Townscaper — independent gameplay recording.\nhttps://www.youtube.com/watch?v=FRfnXAIbA-M',
 'se2':'Space Engineers 2 — Keen Software House official press kit.\nhttps://mirror.keenswh.com/PressKits/SE2%20Press%20Kit.zip\nhttps://2.spaceengineersgame.com/eula/',
 'sub':'Subnautica 2 — NCR Gameplay recording.\nhttps://www.youtube.com/watch?v=dYyWmhVuc3w',
 'shapez':'shapez 2 — tobspr Games official Steam footage.\nhttps://store.steampowered.com/app/2162800/shapez_2/'
}
additions={'M07':['totk','besiege','bridge'],'M09':['bridge','besiege'],'M10':['big','besiege'],'M12':['town','se2'],'M19':['sub']}
for e,t in zip(state['entries'],titles):
 p=R/'projects'/e['slug']; e['titleKo'],e['titleEn']=t
 assert len(t[0])<=100 and len(t[1])<=100
 e['titleSelection']={'alternatives':[t[0],e['title']+' | 게임수학 Part 2'],'audience':'게임 프로그래밍 학습자','reason':'학습 본문의 실제 질문과 관찰 가능한 결과를 앞세우고 정확한 주제와 연속 순서를 유지'}
 for lang in ['ko','en']:
  old=p/'publishing/revisions/concept-fit-v2'/('upload-description.'+lang+'.txt')
  text=old.read_text(encoding='utf-8-sig')
  if e['id']=='M14':
   def shift(m):
    seconds=int(m[1])*60+int(m[2])+18
    return f'{seconds//60:02d}:{seconds%60:02d} '+m[3]
   text=re.sub(r'^(\d{2}):(\d{2}) (.+)$',shift,text,flags=re.M)
   heading='챕터' if lang=='ko' else 'Chapters'
   abstract='00:00 실제 게임에서 보는 분할의 목표' if lang=='ko' else '00:00 The goal of partitioning, shown in real games'
   text=text.replace(heading+'\n',heading+'\n'+abstract+'\n',1)
  for key in additions.get(e['id'],[]):
   block=extra[key]
   if block.splitlines()[1] not in text: text=text.rstrip()+'\n'+block+'\n'
  # These are reused code-based render/composite tools, not guessed game engines.
  text=text.rstrip()+'\n\n'+('강의 자료·제작 도구' if lang=='ko' else 'Lesson material and production tools')+'\n게임수학 Part 2 · 얌얌위키\nhttps://www.yamyamcoding.com/1ea0b1ff-a61e-803f-bd54-cac4f028f6b3\nMotion Canvas\nhttps://motioncanvas.io/\nFFmpeg\nhttps://ffmpeg.org/\n'
  assert len(text)<=5000,(e['id'],lang,len(text))
  dest=B/'packages'/e['id']/('description.'+lang+'.txt');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(text,encoding='utf-8')
  e['description'+lang.upper()]=str(dest)
 e['status']='upload-queued' if state['entries'].index(e)<15 else 'package-ready'
state['metadataBasis']='Preserve concept-fit descriptions/chapters matching unchanged body timeline; shift M14 by18.15s rounded down to chapter seconds. Add actual v4/v6 footage credits. Original body timings preserved in final QA.'
state['status']='uploading-and-configuring'
(B/'checkpoint.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Prepared18 KO/EN packages; all within platform length limits')
