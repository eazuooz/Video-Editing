"""Use exact frames from the final captioned master for the companion article."""
from pathlib import Path
import json,hashlib,subprocess
P=Path(__file__).resolve().parents[1];R=P.parents[1];L=P/'production/local/full-video-v2';O=L/'wiki';O.mkdir(exist_ok=True)
d=json.loads((P/'production/full-video-delivery.json').read_text('utf-8'));v=Path(d['outputs'][1]['path']);master=hashlib.file_digest(v.open('rb'),'sha256').hexdigest();assert master==d['outputs'][1]['sha256']
t={r['id']:r for r in json.loads((L/'timeline.json').read_text('utf-8'))['scenes']}
items=[('room','01',3,'완성한 방의 실제 실행 화면. 걷기·앉기·음악·기록을 하나의 공간에서 연결한다.'),('model','06',3,'같은 캐릭터의 실제 Tripo 작업 화면. 자체 입력 이미지를 모델로 바꾸고 형상을 확인한 단계다.'),('texture','10',6,'실제 캐릭터의 Base Color·Normal·Roughness·Metallic 맵. 겉모양의 색과 표면 데이터의 역할이 다르다.'),('states','15',7,'대기→걷기→정렬→앉기→생활→일어나기. 실제 동작을 연결하는 상태의 관계를 설명한 완성 영상 프레임이다.'),('sit','17',10,'초기 가구와 수정한 실제 앉기 장면. 낮은 등받이·모니터와 몸의 접촉을 함께 확인한다.'),('window','20',6,'실제 게임의 잎과 창문 풍경. 잎의 기준점은 고정하고 창문에는 자체 숲·달 파노라마를 사용했다.'),('web','26',7,'실제 브라우저로 실행한 방. 로딩과 시작, 생활 동작과 저장 UI를 연결한 결과다.')]
records=[]
for name,scene,offset,caption in items:
 second=t[scene]['start']+min(offset,t[scene]['duration']*.65);f=O/(name+'.jpg')
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(second),'-i',str(v),'-frames:v','1','-q:v','2',str(f)],check=True)
 records.append({'name':name,'scene':scene,'timestampSeconds':second,'masterPath':str(v),'masterSha256':master,'imagePath':str(f),'imageSha256':hashlib.file_digest(f.open('rb'),'sha256').hexdigest(),'caption':caption,'modification':'Exact final encoded frame extraction; no post-extraction annotations. Film itself contains authored captions/graphics.','documentRights':'Own room/graphics/generated design and paid Tripo model; rendered licensed KayKit CC0 and EmacEArt project animation. Not redistributing source assets. Own model is visible in Tripo UI.','rightsSources':['https://kaylousberg.itch.io/kaykit-character-animations','https://emaceart.itch.io/philipp-stylized-modular-low-poly-character','https://www.tripo3d.ai/terms'],'notionAttachmentId':None})
(P/'production/companion-frames.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n','utf-8');print('Extracted',len(records),'final-master wiki frames')
