"""Prepared causal/geometry plan. No adoption, synthesis or baseline edits."""
from pathlib import Path
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def rel(p):return p.relative_to(ROOT).as_posix()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
target=R/'causal-flow-and-annotation-plan-v1.json';assert not target.exists()
base=read(R/'baseline-preservation-v1.json')
assert all(sha(ROOT/x['path'])==x['sha256'] for x in base['protectedFiles'])
native=read(R/'selected-native-direct-review-v1.json');assert native['all68BoardsDirectlyRead']
rows=[
 ('01','같은 방향을 보는데도 자세가 다른 이유','첫 관찰→세 축과 행렬→역변환·검사→두 문제를 약속한다.','4문장20.16초 기존 안내 유지. 예시/풀이/결론 약속과 대조.','이 차이를 실제 비행에서 먼저 찾아보자.'),
 ('02','위치·방향·자세를 무엇으로 구별할까','몸 중심의 이동과 몸통/팔의 화면상 기울기를 따로 관찰한다.','처음 보는 Superflight를 짧게 소개. 밝은 배경의 몸 형태를 먼저 보여주고 중심점/관찰선을 차례로 추적.53초 CRASHED 제외.','방향 화살표 하나로 이 기울기를 모두 정할 수 있을까?'),
 ('03','방향 하나로 자세를 정할 수 있을까','같은 forward를 유지해도 물체가 그 축 둘레로 돌아갈 수 있다.','실제 관찰에서 독립된 강체 모형으로 이동. 같은 forward와 다른 up를 투영된 면/가림으로 비교.','몸에 붙인 세 기준축을 함께 기록하자.'),
 ('04','세 축은 어떤 조건을 만족해야 할까','축 길이1·서로 수직·오른손 x×y=z가 자세의 기준이다.','직교/단위 뜻을 자의 길이와 직각으로 설명. x빨강/y초록/z파랑 역할을 고정하고 모형과 축을 함께 회전.','이 몸 기준과 화면의 위는 같은 것일까?'),
 ('05','몸·월드·카메라 기준은 어떻게 다른가','같은 물체도 기준틀에 따라 좌표와 화면상 모습이 달라진다.','몸 관찰선 빨강, 화면 위 금색, 추적 가능한 배경 모서리 청록. 다른 맵/비행 사이에는 개별 예시임을 안내. 가려진 몸은 추적선을 숨긴다.','세 축을 숫자로 옮기면 행렬이 된다.'),
 ('06','행렬의 숫자는 어디서 오는가','column-vector local→world R의 세 열은 로컬 축을 월드 좌표로 적은 값이다.','격자 위 두 자를 먼저 비교한 뒤 축끝좌표→세 열을 하나씩 채운다. 행/열 관례 전치와 좌표계 손잡이 변경을 분리.','작은90도 예제로 실제 계산해보자.'),
 ('07','벡터를 어떻게 회전시키는가','Rz90의 열을 사용하면 local(2,1,0)이 world(-1,2,0)이 된다.','(1,0,0),(0,1,0) 축의 도착점을 먼저 보여준 뒤2배·1배 합성. 결과 위치까지 이동시키고 숫자만 나열하지 않는다.','몸 기준 명령은 현재 자세를 거쳐 바깥 방향이 된다.'),
 ('08','로컬 방향을 월드에서 읽는다는 뜻','한 몸 기준 방향을 현재 자세에 따라 외부 기준에서 해석한다.','몸 관찰선과 배경 모서리를 표시하되 실제 게임 입력/월드축을 추정하지 않는다. 계산은 별도 명시한 개념 모형 값으로 연결.','반대로 월드 방향을 몸 기준에서 읽으려면?'),
 ('09','왜 순수 회전의 역변환은 전치일까','축 방향으로 성분을 읽는 내적/투영이 RT이고 동일 예제로 되돌아간다.','전치는 행과 열 자리바꿈, 내적은 축 방향 몫 읽기라는 선행 설명. world(-1,2,0)→local(2,1,0)을 축별로 계산. 점이면 원점부터 뺀다.','각 행/열 성분은 축 사이 관계를 담는다.'),
 ('10','방향 코사인은 무엇을 재는가','같은 기준 공간의 단위축 사이 내적은 각도의 코사인이다.','한 축을 투영해서 부호와 길이가 변하는 것을 보여준다. row=월드 성분, column=로컬 축인 자신의 관례 고정.','카메라나 부모가 추가되면 기준틀이 이어진다.'),
 ('11','카메라를 거쳐 보이는 자세를 연결하려면','입력 공간과 출력 공간이 맞는 변환을 순서대로 연결해야 한다.','비행의 몸/배경/화면 관찰과 세 기준틀 도식을 대응.364.983초 메뉴 제외. 개별 비행 구간을 한 연속 동작으로 주장하지 않는다.','자식→부모→월드 순서로 간단히 써보자.'),
 ('12','AB에서 어떤 변환이 먼저 작용하는가','B자식→부모 다음 A부모→월드, 열벡터 AB는 오른쪽 B부터 적용한다.','평면 카드 체인에 부모 몸체/장착 부품의 투영된 깊이·가림을 추가. 부품 한 점의 두 단계를 이동시킨다.','합성한 결과가 정말 순수 회전인지 검사하자.'),
 ('13','회전 행렬인지 무엇으로 확인하는가','RTR≈I와 detR≈+1을 함께 검사한다.','길이/수직/손잡이를 먼저 회수. 내적 결과3×3을 한 칸씩 검증하고 반사 det−1을 비교; 부동소수 허용오차 설명.','그런데 화면에서는 길이가 달라 보이지 않았나?'),
 ('14','화면상 크기 변화는 회전 오류인가','원근 투영된 픽셀 길이와 월드에서 보존되는 길이는 다르다.','화면상 몸 길이를 표시할 때 px/화면 관찰로 명시. 동일한 월드 강체를 두 카메라 거리에서 투영해 별도 비교.515–518/525–528/537–540 충돌·재시작 의심 구간 검사.','길이가 바뀌는 실제 스케일/반사를 분리하자.'),
 ('15','스케일과 반사는 회전과 어떻게 다른가','diag(2,1,1),diag(−1,1,1),diag(−1,−1,1)을 구별한다.','같은 투영 모형의 길이/손잡이/반바퀴 회전 결과를 순서 비교. 검사13의 기준을 그대로 적용.','작은 수치 오차가 쌓일 때에는 어떻게 복구할까?'),
 ('16','축이 살짝 틀어지면 어떻게 교정할까','Gram–Schmidt는 평행 성분 제거와 정규화로 직교축을 복구한다.','두 화살표 사이 평행 조각을 먼저 떼고 남은 수직 조각을 정규화. 거의0인 축/평행 입력은 가드. 의도적 스케일을 자동 회전으로 바꾸지 않는다.','화면만 보고 이 내부 조건을 알 수 있을까?'),
 ('17','부드러운 동작이면 수학 검사도 통과한 걸까','가시적 움직임과 내부 수치 검증은 다른 증거이다.','기체 관찰선을 보여주고 모형 축 검사와 나란히 연결. 실제 게임 버그/행렬값/입력을 영상에서 단정하지 않는다.','이 정보를 저장하는 다른 표현은 무엇이 있을까?'),
 ('18','왜 행렬은 숫자9개를 쓰는가','32bit float 성분 기준 행렬36B/Euler12B/quat16B이나 모두 자유도와 메모리를 구별한다.','green 메모리 막대가 Euler 라벨을 덮는659초 상태 수정. 막대·값을 독립 영역에 배치.9개 성분은 독립 자유도9개가 아님을 축 조건과 연결.','프로그램의 이름에는 입력/출력 기준을 어떻게 남길까?'),
 ('19','벡터/점을 코드에서 잘못 섞지 않으려면','localToWorld/worldToLocal, direction/point를 명확히 구별한다.','예제07/09 결과를 함수 출력 옆에 재사용. point는 원점 더하기/빼기, direction은 평행이동 제외. 메모리 row-major와 row-vector 관례 분리.','몸 기준과 화면 기준 입력 이름도 같은 원칙이다.'),
 ('20','같은 좌우라도 기준이 다르면 무엇이 달라지나','인터페이스에 좌표계 의미를 기록해야 오해를 줄인다.','금색 화면 기준과 빨간 몸 관찰선을 구별해 표시. 이 녹화의 실제 조작키/입력 매핑 증거로 사용하지 않는다.','시작/목표 자세 사이를 단순히 평균내면 어떨까?'),
 ('21','회전 행렬 원소를 평균내면 안전할까','I와 Rz180의 원소중간값 diag(0,0,1)은 축을 무너뜨린다.','13의 길이 검사에 다시 연결한 뒤 두 축이 줄어0이 되는 투영모형 애니메이션. 실패→적절한 회전 보간 필요를 설명.','작은 두 문제로 오늘 규칙을 직접 확인하자.'),
 ('22','순방향·역방향 계산을 스스로 할 수 있나','Q1 local(1,0,0)→world(0,1,0); Q2 world(4,5,0)−origin(3,3,0)=(1,2,0), RT→local(2,−1,0).','문제마다 기준틀과 원점을 먼저 표시. 결과를 순방향 다시 적용해 검증. 답/풀이/검산을 단계적으로 펼친다.','처음 비행을 이제 기준틀 언어로 다시 보자.'),
 ('23','처음 보던 비행에서 무엇을 읽을 수 있나','위치·몸 기울기·관찰 기준을 따로 설명할 수 있다.','첫 예시와 같은 질문을 회수하되 새 고유 프레임 사용. 엔진 자세/roll 수치/월드축 측정값 주장은 하지 않는다.','한 행렬로 자세를 나타냈으니 다음에는 표현과 순서를 비교하자.'),
 ('24','무엇을 배웠고 다음 질문은 무엇인가','세 축으로 자세 기록, 기준틀 명시, 회전 조건 검사라는 세 원칙을 회수한다.','안내의 세 약속 및 두 계산 결과를 회수. Euler/axis-angle 다음 편 연결은 이번 결론 이후에만.','원래 회원10초로 마무리한다.'),
]
bridges=[
 {'id':'bridge-game-intro','beforeScene':'02','classification':'actual','sourceDependent':True,
  'ko':'슈퍼플라이트는 장애물 사이를 날아가는 게임입니다. 지금은 점수보다 캐릭터를 보세요. 몸의 중심이 어디로 움직이는지, 몸통이 화면에서 어떻게 기울어지는지 따로 관찰하겠습니다.',
  'en':'Superflight is a game about flying between obstacles. For now, watch the character rather than the score. We will observe separately where its center moves and how its body tilts on the screen.'},
 {'id':'bridge-basis-columns','beforeScene':'06','classification':'explanation','sourceDependent':False,
  'ko':'몸에 붙인 자와 방에 고정한 자가 있다고 생각해 보세요. 같은 화살표도 어떤 자로 읽느냐에 따라 숫자가 달라집니다. 회전 행렬은 몸의 세 자가 방의 기준에서 어느 쪽을 향하는지 적어 둔 표입니다.',
  'en':'Imagine one set of rulers attached to the body and another fixed in a room. The same arrow receives different numbers depending on which rulers we use. A rotation matrix records where the three body rulers point when read in the room frame.'},
 {'id':'bridge-transpose-projection','beforeScene':'09','classification':'explanation','sourceDependent':False,
  'ko':'앞에서는 몸 기준의 숫자를 바깥 기준으로 옮겼습니다. 이번에는 바깥 화살표를 몸의 각 축에서 얼마나 차지하는지 읽습니다. 그 몫을 읽는 계산이 내적입니다. 전치는 이 계산에 필요한 행과 열의 자리를 서로 바꿉니다.',
  'en':'Previously, we converted body-frame numbers into an external frame. Now we read how much of an external arrow lies along each body axis. A dot product reads that component. Transposition exchanges rows and columns for this calculation.'},
 {'id':'bridge-pure-rotation-check','beforeScene':'13','classification':'explanation','sourceDependent':False,
  'ko':'축을 숫자로 적었다고 모두 회전 행렬은 아닙니다. 자가 늘어나거나 서로 비스듬해지면 물체도 찌그러집니다. 그래서 축 길이, 축 사이 직각, 오른손 방향을 순서대로 확인합니다. 곧 나올 식은 이 세 검사를 짧게 적은 것입니다.',
  'en':'Not every numerical set of axes is a rotation matrix. If the rulers stretch or become oblique, the object becomes distorted. We therefore check axis lengths, right angles and handedness. The next equations summarize those checks.'},
 {'id':'bridge-orthogonalize','beforeScene':'16','classification':'explanation','sourceDependent':False,
  'ko':'살짝 기울어진 두 번째 자에서 첫 번째 자와 나란한 조각을 빼면 수직인 부분만 남습니다. 남은 자의 길이를 다시 일로 맞춥니다. 이것이 다음 교정 계산의 핵심입니다. 다만 자가 사라지거나 처음부터 평행하면 별도 처리가 필요합니다.',
  'en':'Subtracting the part parallel to the first ruler leaves only the perpendicular part of a slightly skewed second ruler. We then restore its length to one. That is the idea behind the next correction. A vanished ruler or initially parallel input needs separate handling.'},
 {'id':'bridge-interpolation','beforeScene':'21','classification':'explanation','sourceDependent':False,
  'ko':'시작 자세와 목표 자세를 안다고 중간 자세가 자동으로 안전해지는 것은 아닙니다. 두 행렬의 숫자를 절반씩 섞어 보면, 앞서 지켜야 했던 축 길이가 사라질 수도 있습니다. 같은 길이 검사로 그 문제를 확인해 보겠습니다.',
  'en':'Knowing a starting and target orientation does not automatically give a valid intermediate orientation. Averaging the numbers of two matrices can destroy the axis lengths we checked earlier. We will use that same length check to see the problem.'},
]
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
plan={'preparedAt':stamp,'status':'prepared-source-adoption-and-measured-audio-pending',
 'baselineProtectedUnchanged':len(base['protectedFiles']),'originalScenarios':24,'originalKoEnLinesEach':140,
 'originalApprovedPcmRetained':24,'originalOverviewRetainedSeconds':20.16,
 'mathSource':'https://app.notion.com/p/3e10b1ffa61e81d289e1da0dd7584a13','readRelevantSections':['8.1','8.2.1','8.2.2 corrected DCM','8.2.3','8.2.4','8.2.5'],
 'referenceFlow':'For this mathematics lecture compare its actual mathematics source; Sakurai applies to design productions. Use observable question → worked explanation → verification → next question rather than imitate wording or reproduce lecture media.',
 'conventions':{'vector':'column','handedness':'right','matrix':'local-to-world R','columns':'local axes in world coordinates','inverse':'RT only for orthonormal pure rotation','pointInverse':'RT*(worldPoint-origin)'},
 'rows':[{'scene':s,'viewerQuestion':question,'claim':claim,'visibleTeaching':visible,'causalTransition':transition} for s,question,claim,visible,transition in rows],
 'preparedAdditionalBridges':bridges,'bridgeFullKoEnDirectComparisonApproved':False,'measuredBridgeDurations':None,
 'geometryContract':{'bodyGuide':'red visible body/arm observation line; not an engine axis or bone-matrix measurement',
  'externalGuide':'teal tracked visible structure edge; label as visible background reference, never infer world-up from a screen edge',
  'screenGuide':'gold screen-up fixed to the image, distinguished from body and world',
  'conceptModel':'explicitly labelled separate projected rigid-body model for actual3D x/y/z and numerical calculations',
  'trackedGuideVisibility':'hide on occlusion, low contrast, invalid tracking or map discontinuity; never bridge a cut with interpolated coordinates',
  'reveal':'one narrated relation at a time; existing source credit, score UI and caption center960,970 stay clear',
  'finalEachCueReviewRequired':True},
 'retainedContract':{'palette':'research-paper-white-v1 already-started lecture','actualShare':0.4,'explanationShare':0.6,'toleranceFrames':1,'noBgm':True,'noSourceAudio':True,'catFrames':120,'memberFrames':600},
 'timingPolicy':'Preserve useful original explanation/PCM. Additional actual = max(0,(2/3)*added explanation seconds - added actual seconds), measured after approved narration. Use unique reviewed action, never loops/slowdown/menus. Do not pad to20minutes.',
 'sourceHold':['scene02 menu53','scene11 menu364.983','scene14 suspected collision/reset intervals; native probes pending'],
 'gates':{'sourceAdoptionApproved':False,'dependentNewNarrationApproved':False,'newTtsStarted':False,'annotationRenderApproved':False,'currentMixedAsrApproved':False,'newFinalPixelApproved':False,'privateReplacementSaved':False,'actualNewVideoId':None}}
write(target,plan)
cp=read(R/'latest-checkpoint.json');cp.update({'causalFlowPreparedPlan':rel(target),'dependentNewScriptPrepared':False,'dependentNarrationApproved':False});write(R/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/unpublished-teaching-clarity-revision/queue.json';q=read(qp)
item=next(x for x in q['items'] if x['slug']=='game-math-orientation-matrices');item['causalFlowPreparedPlan']=rel(target)
ex=read(R/'repair-candidate-execution-v1.json')
q['execution'].update({'stage':'source-repair-probes-and-unused-actions-extracting','ownedJob':{'script':ex['commandLine'][-1],'sessionId':39906,'pid':ex['pid'],'createTime':ex['createTime'],'commandLine':ex['commandLine'],'cwd':ex['cwd'],'state':rel(R/'repair-candidate-execution-v1.json'),'cpuThreads':2,'gpuJobs':0},'next':'Read new repair probes and unused-action samples; preserve held-source gates until exact transitions and selection are reviewed.'})
q['updatedAt']=stamp;write(qp,q)
print(json.dumps({'preparedRows':len(rows),'preparedIndependentBridges':len(bridges),'baselineUnchanged':len(base['protectedFiles']),'dependentNarrationApproved':False}))
