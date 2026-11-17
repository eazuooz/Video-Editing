"""Use exact frames from the final captioned master for the companion article."""
from pathlib import Path
import json,hashlib,subprocess
P=Path(__file__).resolve().parents[1];R=P.parents[1];L=P/'production/local/full-video-v5';O=L/'wiki';O.mkdir(exist_ok=True)
d=json.loads((P/'production/full-video-delivery.json').read_text('utf-8'));v=Path(d['outputs'][1]['path']);master=hashlib.file_digest(v.open('rb'),'sha256').hexdigest();assert master==d['outputs'][1]['sha256']
t={r['id']:r for r in json.loads((L/'timeline.json').read_text('utf-8'))['scenes']}
items=[
 ('room','01',4,'완성 게임. 입력 이미지와 모델, 코드가 조작 가능한 같은 방으로 이어진다.'),
 ('reference','04',4,'캐릭터 생성 입력. 손발이 보이는 전신 중립 자세와 고정할 디자인 조건을 함께 요청한다.'),
 ('prop','05',4,'헤드폰은 단독 이미지로 분리한다. 구조와 두께를 확인할 수 있는 입력을 만든다.'),
 ('model','06',4,'실제 Tripo의 자체 캐릭터 작업 화면. Image to 3D에 입력 그림을 넣고 생성 결과를 확인한다.'),
 ('retopo','08',4,'목표 10K와 실제 9,968개 사각형 면. 생성 원본과 게임용 메시를 구별한다.'),
 ('texture','10',6,'캐릭터의 실제 Base Color·Normal·Roughness·Metallic 맵과 역할.'),
 ('mcp','25',5,'Codex의 요청이 프로젝트 범위의 Unity CLI/MCP를 거쳐 Editor 작업과 실제 결과로 이어진다.'),
 ('states','15',7,'Walk → Align → Enter → Loop → Exit. 자세 사이의 중간 동작을 보존하는 상태 흐름.'),
 ('reading','18',7,'새 독서 시연. 책이 얼굴을 향하고 손목은 표지 바깥, 팔꿈치는 몸 밖에 놓이도록 함께 맞춘다.'),
 ('rain','29',6,'창문 영역 안의 비와 배경·유리·창틀 순서를 보여 주는 실제 게임 장면.'),
 ('cat','30',20,'CC0 수면 사진의 파생 입력 → Tripo H3.1 → 게임용 19,398삼각형 삼색고양이. 원본 메시의 몸통 호흡과 작은 꼬리 움직임을 더하고 얼굴은 고정한다.'),
 ('web','26',7,'새 WebGL 빌드를 실제 브라우저에서 실행한 화면. 저장·입력·소리의 검증도 게임 제작에 포함한다.')]
records=[]
for name,scene,offset,caption in items:
 second=t[scene]['start']+min(offset,t[scene]['duration']*.65);f=O/(name+'.jpg')
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(second),'-i',str(v),'-frames:v','1','-q:v','2',str(f)],check=True)
 records.append({'name':name,'scene':scene,'timestampSeconds':second,'masterPath':str(v),'masterSha256':master,'imagePath':str(f),'imageSha256':hashlib.file_digest(f.open('rb'),'sha256').hexdigest(),'caption':caption,'modification':'Exact final encoded frame extraction; no post-extraction annotations. Film itself contains authored captions/graphics.','documentRights':'Own room/graphics/generated design and paid Tripo model; rendered licensed KayKit CC0 and EmacEArt project animation. Not redistributing source assets. Own model is visible in Tripo UI.','rightsSources':['https://kaylousberg.itch.io/kaykit-character-animations','https://emaceart.itch.io/philipp-stylized-modular-low-poly-character','https://www.tripo3d.ai/terms','https://rg-poly.itch.io/vintage-retro-stylized-pack','https://commons.wikimedia.org/wiki/File:Calico_Cat_Asleep.jpg'],'notionAttachmentId':None})
(P/'production/companion-frames.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n','utf-8');print('Extracted',len(records),'final-master wiki frames')
