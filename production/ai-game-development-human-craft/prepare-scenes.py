"""Generate editable, independently renderable Motion Canvas scenes.

Estimated timing is for layout preflight only; full render refuses it.
"""
from pathlib import Path
import json, math, re
ROOT=Path(__file__).resolve().parents[2]
SLUG='ai-game-development-human-craft'
P=ROOT/'motion-canvas/src/projects'/SLUG
P.mkdir(parents=True,exist_ok=True)
script=json.loads((ROOT/f'projects/{SLUG}/script/narration.ko.json').read_text(encoding='utf-8'))
manifest=json.loads((ROOT/f'projects/{SLUG}/project.json').read_text(encoding='utf-8'))
timingfile=ROOT/manifest['tts']['outputDir']/(manifest['tts']['filenameStem']+'.timing.json')
timing=json.loads(timingfile.read_text(encoding='utf-8')) if timingfile.exists() else None
captions=[]
if timing and timing.get('alignment'):
 captionfile=ROOT/manifest['tts']['outputDir']/(manifest['tts']['filenameStem']+'.srt')
 def seconds(t):
  h,m,s=t.replace(',','.').split(':');return int(h)*3600+int(m)*60+float(s)
 for block in re.split(r'\r?\n\s*\r?\n',captionfile.read_text(encoding='utf-8').strip()):
  lines=block.splitlines();a,b=lines[1].split(' --> ')
  captions.append({'id':int(lines[0]),'start':seconds(a),'end':seconds(b),'text':'\n'.join(lines[2:])})
# Short editorial beats. The complete narration remains the source of truth.
specs=[
 ('flow','실력은 어디에 쓰일까?','도구의 변화|자동화의 영향|상점으로 확인','오늘 살펴볼 순서'),
 ('unity','동작을 눈으로 연결한다','조건 확인|열쇠 찾기|문 열기','사람이 작업하기 쉬운 도구'),
 ('compare','사람과 AI가 작업을 읽는 방식','화면과 노드|기능 호출|결과 확인','서로 다른 접근을 연결한다'),
 ('source','도구를 연결하는 차세대 엔진','초기 공존|구조 성숙|단계적 전환','UE6 장기 계획 · 현재 기능과 구분'),
 ('source','작성 속도에서 완성 책임으로','AI 활용 확대|정확하게 구현|검증하고 완성','보도와 회사의 공식 발표를 구분'),
 ('unity','표면과 이미지를 연결하는 UV','같은 좌표|모델 표면|펼친 이미지','실제 메시 UV 샘플링 · 설명용 모델'),
 ('branch','효율의 증가, 서로 다른 결과','반복 작업|다른 역할|일자리 감소','생산성 향상과 고용 불안은 함께 존재'),
 ('unity','같은 기능에도 다른 가치가 있다','재료 선택|세부 표현|완성 품질','손으로 만들었다는 사실만으로 충분할까?'),
 ('unity','작동하는 기능에서 느껴지는 보상으로','수치 변경|캐릭터 반응|보상 전달','같은 구매 결과 · 다른 피드백'),
 ('source','아이디어를 시험하는 입구가 넓어진다','브라우저 제작|시작할 기회|제품 완성','Unity Spark · 출시 예정 / 대기자 등록'),
 ('timeline','만드는 과정도 창작의 일부다','직접 코딩|움직임 구현|그림 완성','결과와 함께 기억되는 창작 과정'),
 ('timeline','만들고, 작동하는 것을 확인하는 경험','BASIC·Flash|게임 모드|음악·영상|자동화','원리를 익히고 결과를 확인하는 경험'),
 ('branch','산업의 변화와 기술의 소멸은 다르다','산업의 비중|일하는 방식|기술과 표현','제작 방식이 바뀌어도 남는 판단'),
 ('unity','게임은 행동에 반응하는 경험이다','선택|실패|다시 도전','작은 팀이 연결하는 여러 기술'),
 ('flow','가능한 일과 책임 있게 할 일을 함께','작업 이용 조건|결과물 권리|사람에게 미치는 영향','자동화의 역사만으로 답이 정해지지 않는다'),
 ('footage','한 번의 시연에서 계속 쓰는 제품까지','이동·색칠|함께 플레이|제품의 완성도','Mix and Jam · 독립 개발 데모'),
 ('unity','돈과 아이템이 함께 맞아야 한다','정상 구매|골드 부족|가방 가득','실제 C# 구매 조건을 실행합니다'),
 ('unity','같은 요청과 두 번의 구매는 다르다','같은 ID 재전송|다른 ID 구매|저장·통신 확인','메모리 내 요청 처리 시연 · 네트워크 미구현'),
 ('cycle','통과했다면 무엇을 검사했는가?','요구사항|구현|테스트|결과 검토','빠진 조건은 자동으로 채워지지 않는다'),
 ('unity','답답한 느낌을 수정할 조건으로','같은 높이|같은 입력|18프레임 지연','60fps · 설명용 비교 · 실제 게임 측정값 아님'),
 ('horizon','현재의 기능과 미래의 전망','현재 가능 범위|조율·검증 발전|만들고 싶은 경험','앞으로의 발전 가능성 · 현재의 성능과 구분'),
 ('footage','오래 기억되는 세계의 선택','과장된 형태|그린 듯한 질감|색과 분위기','World of Warcraft Classic · Nyhver (2020)'),
 ('unity','사실성과 개성은 같은 기준이 아니다','따뜻한 방향|차가운 방향|경험에 맞는 선택','같은 모델·장소·카메라 · 조명만 변경'),
 ('timeline','작품에서 제작자의 감각으로','음악과 미술|반복되는 선택|다음 작품의 기대','Halo · The Elder Scrolls · 기억되는 음악과 미술'),
 ('unity','축적한 기술로 결과를 판단한다','빠진 조건 찾기|표현 다듬기|결과에 책임','검증과 연출에는 서로 다른 판단이 쓰인다'),
 ('unity','강한 공구를 언제 멈출 것인가','재료 이해|힘 조절|멈추는 시점','공구 사용의 개념 시연 · 토크 측정 아님'),
 ('road','새 도구와 함께 바뀌는 기준','사용법|사고와 책임|함께 지킬 규칙','도로의 비유에서 개발과 창작의 책임으로'),
 ('unity','배운 실력은 판단의 기준이 된다','이해|검증|표현','여러분은 어떤 판단에 자신의 지식을 쓰나요?'),
]
sources={'04':{'name':'Epic Games · The Road to UE6','date':'2026.06.22','url':'unrealengine.com/news/the-road-to-ue-6','statement':'Blueprint·Actor 유지 → 새로운 구조 성숙 → 전환 도구와 단계적 대체','note':'장기 계획입니다. 지금 즉시 폐지되는 것이 아닙니다.'},'05':{'name':'Bloomberg 보도','date':'2026.10.12','url':'bloomberg.com · Epic / Disney 프로젝트 보도','statement':'Disney 협업 일정 지연과 개발팀 AI 활용 확대를 보도','note':'보도 내용입니다. 에픽의 공식 공지와 구분합니다.'},'10':{'name':'Unity 공식 소개 · Unity Spark','date':'확인 2026.10.14','url':'unity.com/spark','statement':'경험이 없어도 브라우저에서 게임을 만들고 공유하는 방향','note':'공식 페이지: 출시 예정 · 대기자 등록'}}
data=[];origin=0
for i,(s,spec) in enumerate(zip(script['scenes'],specs)):
 entries=[e for e in timing['entries'] if str(e['scene_id'])==s['id']] if timing else []
 if timing:
  start=round(entries[0]['start']*30)/30
  nexts=timing['duration_seconds'] if i==27 else next(e['start'] for e in timing['entries'] if str(e['scene_id'])==script['scenes'][i+1]['id'])
  end=round(nexts*30)/30
  paragraphs=[{'start':max(0,e['start']-start),'end':e['end']-start,'text':e['text']} for e in entries]
 else:
  start=origin;local=0;paragraphs=[]
  for line in s['lines']:
   duration=max(2.0,len(line)/5.3)
   paragraphs.append({'start':local,'end':local+duration,'text':line});local+=duration
  end=start+math.ceil((local+.72)*60)/60
 origin=end
 mode,heading,labels,note=spec
 localcues=[dict(c,start=c['start']-start,end=c['end']-start) for c in captions if c['end']>start and c['start']<end]
 data.append({'id':s['id'],'title':s['title'],'start':start,'duration':end-start,'paragraphs':paragraphs,'captions':localcues,'mode':mode,'heading':heading,'labels':labels.split('|'),'note':note,'source':sources.get(s['id'])})
payload={'timingStatus':'measured-narration' if timing else 'estimated-layout-only','captionTimingStatus':'asr-aligned' if captions else 'pending','fps':60,'scenes':data}
if script.get('revision',0)>=4:
 # Inspect viewer-facing text only. Source/license history is deliberately
 # retained and must not be confused with narration or diagram copy.
 visible='\n'.join([t for s in script['scenes'] for t in s['lines']]+[s['note'] for s in data])
 assert not re.search(r'원\s*영상|원작자|제공된?\s*자막|Wild Ox Studios',visible),'Source-video framing returned to the current lesson'
(P/'scene-data.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for s in data:
 d=P/'scenes'/s['id'];d.mkdir(parents=True,exist_ok=True)
 (d/'scene.tsx').write_text("import {makeScene2D} from '@motion-canvas/2d';\nimport {lesson} from '../../scene-kit';\nexport default makeScene2D(function*(view){yield* lesson(view,"+str(int(s['id'])-1)+");});\n",encoding='utf-8')
 (d/'project.ts').write_text("import {makeProject} from '@motion-canvas/core';\nimport scene from './scene?scene';\nexport default makeProject({name:'ai-craft-scene-"+s['id']+"',scenes:[scene]});\n",encoding='utf-8')
imports='\n'.join(f"import s{s['id']} from './scenes/{s['id']}/scene?scene';" for s in data)
audio=(P/'assets/final-mix.wav').exists()
(P/'project.ts').write_text("import {makeProject} from '@motion-canvas/core';\nimport intro from './intro-scene?scene';\nimport members from './member-scene?scene';\n"+imports+("\nimport audio from './assets/final-mix.wav';" if audio else '')+"\nexport default makeProject({name:'ai-game-development-human-craft',"+('audio,' if audio else '')+"scenes:[intro,"+','.join('s'+s['id'] for s in data)+",members]});\n",encoding='utf-8')
print(json.dumps({'timing':payload['timingStatus'],'scenes':len(data),'paragraphs':sum(len(s['paragraphs']) for s in data),'duration':origin}))
