"""Narration-anchored, unique native-speed source cuts for the selected essay."""
from pathlib import Path
import json,hashlib,sys
from revision_paths import workroot
ROOT=Path(__file__).resolve().parents[2];SLUG='ai-game-development-human-craft'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
data=read(ROOT/f'motion-canvas/src/projects/{SLUG}/scene-data.json');scenes={s['id']:s for s in data['scenes']}
sources={
 'ue':('ue-map','Unreal Engine 5 · 실제 장면 제작','Ai Artistry Studio · 2024 · 타임랩스','편집기에서 오브젝트·재질을 선택하고 장면을 바꾸는 과정. AI 실행 증거가 아님.'),
 'godot':('godot-workflow','Godot · 실제 프로젝트 조작','Juan Linietsky · Godot Engine · 2019','독립 공개 시연의 편집기 조작만 사용. 참고 대본 제작자의 프로젝트가 아님.'),
 'krita':('krita-workflow','Krita · 사람이 직접 그리는 과정','David Revoy · 2022 · 제작 과정','드로잉·채색·구도 수정 동작. Thomas Brush나 Wild Ox의 작업으로 표시하지 않음.'),
 'ai':('unity-ai','Unity + Stable Diffusion · 별도 연동 사례','Dominic Branchaud · 2023 · Spark 화면 아님','서드파티 플러그인의 입력·생성·재질 적용. 현재 Unity 공식 AI/Spark의 기능 시연이 아님.'),
 'robot':('robot-stool','통나무를 의자로 가공하는 로봇','designboom · 7Xstool · 2013','별도 로봇 가공 실연. 원영상 제작자의 공장이나 일자리 감소의 측정 자료가 아님.'),
 'wood':('wood-carving','손으로 형태를 깎아 가는 과정','Ainembabazi leviticus · 2024','독립 목공 작업 기록. 수작업 자체가 품질을 보장한다는 근거로 사용하지 않음.'),
 'wood2':('wood-carving2','손으로 자르고 다듬는 작업','Ainembabazi leviticus · 2024','별도 수작업 과정. 산업 전체의 고용 상황을 입증하는 영상이 아님.'),
 'road':('historic-road','자동차와 마차가 함께 다니던 거리','Miles Brothers · Market Street · 1906','실제 역사 기록. 일부 교통은 연출되었으며 사고/법 제정의 인과 증거가 아님.'),
 'mix1':('mixandjam-movie001','잉크가 남는 동작부터 확인하기','Mix and Jam · Splatoon 방식 개발 실험','Nintendo 게임 본편 또는 AI가 만든 게임이 아님.'),
 'mix2':('mixandjam-movie002','이동과 색칠을 함께 확인하기','Mix and Jam · Splatoon 방식 개발 실험','이 화면으로 멀티플레이·제품 완성도를 입증하지 않음.'),
 'wow':('wow-nyhver-120-240','World of Warcraft Classic','Nyhver · 2020 녹화 · 일부 외형 변경','최신 버전/기본 외형/성능 측정으로 표시하지 않음.')}
rows=[]
def p(s,i):return scenes[s]['paragraphs'][i]['start']
def end(s):return scenes[s]['duration']
def add(s,a,b,key,source_in,action):
 a,b=round(a*60),round(b*60)
 assert 0<=a<b<=round(end(s)*60),(s,a,b,end(s))
 info=sources[key];name=info[0];source=ROOT/'shared/sources'/SLUG
 source=source/(name+'.mp4') if key in ('mix1','mix2','wow') else source/'actual-footage-v2'/(name+'.webm')
 rows.append({'id':f'{s}-{len([r for r in rows if r["scene"]==s])+1:02d}','scene':s,'startFrame':a,'endFrame':b,'source':key,'sourcePath':source.relative_to(ROOT).as_posix(),'sourceInSeconds':source_in,'sourceOutSeconds':source_in+(b-a)/60,'frames':b-a,'playbackRate':1,'loop':False,'classification':'independent-actual-footage','heading':info[1],'credit':info[2],'context':info[3],'beforeActionResult':action,'audio':'omitted; original narration/music not mixed into our narration','review':'selected-from-timestamped-source-survey; dense-motion-review-pending'})
add('01',2.3,13.3,'ai',28,'빈 생성 결과 → 입력 후 생성 → 고양이 이미지가 나타나는 작업의 시작')
add('01',13.3,p('01',2),'krita',60,'옅은 스케치 → 캐릭터 선을 그음 → 형태가 선명해짐')
add('02',0,p('02',2),'ue',120,'기본 바닥 → 사람/카메라 배치 → 장면 위치 확인')
add('02',p('02',3),p('02',5),'ue',365,'건물 블록 → 선택·이동 → 거리 형태 수정')
add('02',p('02',5),end('02'),'ue',1535,'단순 건물 → 창문과 입구 요소 배치 → 구체적인 외벽')
rows[-1]['heading']='3D 장면 제작 · 모델 수정과 엔진 적용'
rows[-1]['context']+=' Unreal Engine 5와 Maya 사이의 모델 편집 전환을 포함.'
add('03',0,p('03',1),'ue',390,'선택한 건물 → 크기/위치 조정 → 공간 변화')
add('03',p('03',3),end('03'),'ai',207,'Unity 장면 → 대상 선택 → 생성 컴포넌트 접근')
add('05',p('05',2),end('05'),'ue',627,'기본 도로 → 재질 적용 → 아스팔트/차선 확인')
add('06',0,p('06',2),'godot',1294,'텍스처 이미지 → 에디터 전환 → 표면 적용 상태 확인')
add('06',p('06',3),p('06',5),'godot',1340,'사진 질감 → 필터 조정 → 평면에서 재확인')
add('06',p('06',5),p('06',8),'godot',1360,'표면 재질 → 값을 바꾸고 시점 이동 → 반복/빛의 반응 확인')
add('06',p('06',8),end('06'),'krita',145,'실루엣 → 나무와 땅에 색을 쌓음 → 장면의 색 분리')
add('07',0,p('07',5),'robot',4,'통나무 고정 → 로봇 톱의 절단 → 잘린 면과 홈')
add('08',p('08',1),p('08',1)+29,'wood',.2,'거친 목재 → 손도구로 깎음 → 조각 형태와 나무 부스러기')
add('09',0,24,'krita',280,'채색된 장면 → 투시/색 조정 → 화면의 인상 변화')
add('10',p('10',4),p('10',4)+22,'ai',220,'그림 오브젝트 → 생성 입력 설정 → 요청 실행')
add('10',p('10',4)+22,end('10'),'ai',276.5,'생성 진행 → 새 이미지 도착 → Unity 표면에 반영')
add('11',0,273/60,'krita',0,'같은 풍경 → 붓질로 형태와 색이 쌓임 → 제작 과정의 변화')
add('11',p('11',3),end('11'),'krita',70.2,'캐릭터 윤곽 → 선을 직접 수정 → 다음 채색 준비')
add('12',p('12',2),p('12',3),'godot',1006,'애니메이션 트랙 → 시점/시간 조작 → 효과 변화')
add('12',p('12',3),end('12'),'godot',889,'캐릭터 모델 → 편집기에서 애니메이션 확인 → 움직이는 결과')
add('13',p('13',1),p('13',1)+16,'wood2',.1,'목재 → 톱질과 손조각 → 세부 형태')
add('13',p('13',4),end('13'),'krita',169,'큰 색면 → 작은 붓질을 쌓음 → 형태와 재질 표현')
add('14',0,p('14',1),'ue',453,'에디터 장면 → 플레이 실행 → 캐릭터 이동')
add('14',p('14',4),end('14'),'godot',3335,'완성 중인 레벨 → 시점으로 돌아봄 → 공간과 분위기 확인')
add('15',0,p('15',4),'robot',74,'가공된 통나무 → 사람이 외피 분리 → 완성된 스툴 형태')
add('15',p('15',4),p('15',6),'ai',315,'기존 벽 재질 → AI 이미지 요청 → 새 표면을 기다리는 실제 작업')
add('16',0,p('16',2),'ue',462,'직접 만든 거리 → 캐릭터 이동 → 에디터에서 결과 검토')
add('16',p('16',5),p('16',5)+700/60,'mix1',0,'깨끗한 바닥 → 잉크 발사 → 색이 남음')
add('16',p('16',5)+700/60,p('16',5)+1258/60,'mix2',0,'바닥과 벽 → 이동하며 발사 → 칠해진 영역 변화')
add('18',p('18',4),end('18'),'godot',749,'실제 프로젝트 코드 → 함수/조건을 확인 → 캐릭터 동작 구현을 검토; 상점 코드 아님')
add('19',p('19',2),p('19',4),'godot',1014,'애니메이션 트랙 → 실행 시각 조작 → 결과 확인')
add('19',p('19',7),end('19'),'ue',1390,'선택한 재질 → 색/값 조정 → 도로에서 결과 확인')
add('20',0,p('20',4),'wow',91,'게임 세계 → 캐릭터 이동 → 경로와 장면 반응 관찰; 지연 측정 아님')
add('20',p('20',5),end('20'),'ue',480,'플레이 검토 뒤 → 에디터로 돌아감 → 공간 수정')
add('21',0,p('21',2),'ai',330,'기존 벽 → 새 생성 결과 적용 → 회색 벽 재질 확인; 2023년 사례')
add('22',0,end('22'),'wow',36,'세계의 지형과 캐릭터 → 실제 이동 → 과장된 형태와 색의 일관성')
add('23',p('23',2),end('23'),'godot',3500,'완성 중인 공간 → 시점/조명 확인 → 따뜻한/차가운 색의 관계')
add('24',p('24',2),end('24'),'krita',348,'장면 → 붓질로 형태/광원 표현 보강 → 작가가 선택한 인상')
add('25',0,p('25',2),'krita',196,'채색 장면 → 색/레이어를 수정 → 의도한 구도에 가까워짐')
add('25',p('25',2),p('25',3),'krita',235,'나무와 인물 → 화면 확대 → 작은 표현의 차이 확인')
add('25',p('25',3),p('25',4),'godot',779,'구현된 코드 → 조건과 움직임 로직 검토 → 수정할 위치 탐색')
add('25',p('25',4),p('25',5),'krita',380,'마무리 단계 → 레이어/색 조정 → 장면 분위기 확인')
add('25',p('25',6),end('25'),'krita',304,'그림의 전체 구성 → 변형 도구로 조정 → 표현을 받아들일지 판단')
add('26',0,p('26',1),'robot',41,'절단 중 → 가공이 끝나며 공구가 멈춤 → 사람이 다음 작업을 준비')
add('26',p('26',4),end('26'),'ue',1575,'건물 외벽 → 창/문 부품 조정 → 구체적인 입구 형태')
add('27',0,p('27',3),'road',12,'같은 거리 → 마차·전차·자동차가 함께 이동 → 서로의 경로가 만남')
add('27',p('27',5),end('27'),'ue',1630,'기본 건물 → 재질/입구 적용 → 작업 결과 확인')
add('28',0,p('28',2),'ue',1730,'선택한 외벽 → 입구 요소 배치 → 건물 표현 보강')
add('28',p('28',2),21.4,'godot',785,'코드 → 동작 조건 검토 → 이해를 바탕으로 판단')
add('28',21.4,p('28',3),'krita',386,'완성 직전 그림 → 세부 조정 → 창작자의 의도 확인')
add('28',p('28',3),p('28',4),'ue',1760,'완성 중인 거리 → 카메라 이동 → 배치 결과 확인')
for sid,s in scenes.items():
 cuts=sorted([r for r in rows if r['scene']==sid],key=lambda r:r['startFrame'])
 for x,y in zip(cuts,cuts[1:]):assert x['endFrame']<=y['startFrame'],(sid,x['id'],y['id'])
source_overlaps=[]
for key in sources:
 cuts=sorted([r for r in rows if r['source']==key],key=lambda r:r['sourceInSeconds'])
 for x,y in zip(cuts,cuts[1:]):
  if x['sourceOutSeconds']>y['sourceInSeconds']+.00001:source_overlaps.append({'source':key,'left':x['id'],'right':y['id'],'overlapSeconds':x['sourceOutSeconds']-y['sourceInSeconds']})
if '--draft' not in sys.argv:assert not source_overlaps,source_overlaps
body=sum(round(s['duration']*60) for s in scenes.values());actual=sum(r['frames'] for r in rows)
payload={'schemaVersion':1,'selectedVideo':SLUG,'bodyFrames':body,'actualFrames':actual,'explanationFrames':body-actual,'actualShare':actual/body,'targetActualFrames':round(body*.6),'pendingFramesToTarget':round(body*.6)-actual,'narrationSha256':hashlib.sha256((ROOT/f'projects/{SLUG}/script/narration.ko.json').read_bytes()).hexdigest(),'footageRoles':'independent actual development, craft/automation and gameplay; self-authored Unity and source screenshots remain explanation','sourceAudio':'omitted; narration and source music excluded','cuts':rows}
if '--draft' in sys.argv:payload.update(status='unresolved-timing-draft',sourceOverlaps=source_overlaps)
dest=workroot(ROOT)/'footage-draft.json' if '--draft' in sys.argv else ROOT/f'projects/{SLUG}/planning/actual-footage-plan.json'
dest.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in payload.items() if k not in ('cuts',)},ensure_ascii=False))
