const fs=require('fs'),path=require('path');
const W=__dirname,R=path.resolve(W,'../../../..');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8')),write=(p,v)=>fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n');
const rows=[
 [0,'취업이 어렵다. AI가 만드는 결과물만으로 신입의 가치를 설명할 수 있을까?','game',645,720,'캐릭터 이동 기능을 코드와 실행으로 연결','완성된 화면 뒤에 있는 구현 결정을 보세요.','질문 → 코드 생성 → 개발자의 판단'],
 [1,'공고가 있다는 사실과 신입이 취업하기 쉽다는 주장은 다르다.','game',720,790,'입력 처리와 이동 코드 작성','코드를 읽는 자격과 실제 구현 능력을 구분','공고 수 ≠ 신입 채용 가능성; 수치 임의 생성 금지'],
 [2,'설명할 수 있어도 빈 프로젝트에서는 막힐 수 있다.','tetris',100,145,'회전·이동·착지하는 블록','작동하는 게임을 처음부터 설계할 수 있나요?','읽기 / 작성의 차이; 개인 교육 경험 명시'],
 [3,'문법 지식과 스스로 문장을 만드는 숙련은 다르다.','manim',0,42,'Node와 next를 구성하고 포인터를 순회','노드 선언, 연결, 해제를 스스로 결정','영어 해석 / 회화, 코드 이해 / 구현 비교'],
 [4,'반복 경험은 테트리스 요구사항을 구조로 바꾸는 능력을 만든다.','tetris',145,220,'블록 회전·이동·라인 완성','입력 → 회전 → 충돌 → 고정 → 줄 제거','Board / Block / Collision / Rotation / Line Clear 분해'],
 [5,'AI로 결과를 얻는 과정에서 생각하는 훈련을 건너뛸 수 있다.','tetris',270,315,'다음 블록을 보고 배치하는 플레이','다음 블록 표시에도 상태 관리가 필요','요청 → 결과, 그 사이의 설계 질문'],
 [6,'요구사항 전달과 독립적인 분석·검증은 같은 AI 사용이 아니다.','profile',25,155,'게임 실행과 에디터 노드 설정 변경','코드를 받고 끝내는가, 실행 결과를 검증하는가','전달형 / 분석·설계·검증형 흐름 비교'],
 [7,'도구를 이용하여 독립적으로 문제를 해결하는지가 중요하다.','game',790,900,'함수 작성 후 플레이어 움직임 확인','코드 변경과 결과를 연결해 관찰','문제 분해 → 구현 → 실행 → 판단'],
 [8,'경력 개발자도 AI를 쓸 수 있다. 단순 구현 채용 유인은 약해질 수 있다.','game',900,1010,'기존 이동 로직을 수정하고 실행','프로젝트 구조를 아는 사람이 판단하는 부분','경력의 판단 + AI 속도; 경제적 결론은 추론 표시'],
 [9,'라이브 서비스는 출시 후에도 개발이 누적된다.','inventory',94,170,'아이템 데이터의 필드와 리소스 정의','아이템 하나의 속성이 여러 시스템으로 이어진다','출시 → 아이템 / 이벤트 / 버그 / 후속 업데이트'],
 [10,'아이템 잠금 하나도 판매·강화·저장·UI에 영향을 준다.','inventory',194,320,'희귀도 리소스와 생성 함수 수정','데이터와 UI의 연결을 보세요. 잠금 자체의 구현 증거는 아님','잠금 중심의 9개 의존 관계 + 6개월 뒤 예외 요구'],
 [11,'기존 코드에서 원인과 영향 범위를 찾는 능력이 필요하다.','save',69,115,'캐릭터·인벤토리·맵 정보를 저장하는 코드 작성','여러 상태가 하나의 저장 구조에 연결','Feature Creator → Problem Solver → System Maintainer'],
 [12,'같은 AI를 써도 진단·설계·검증 능력은 다르다.','inventory',320,420,'리소스를 조합하는 생성 로직','어떤 데이터를 만들고 연결하는지 읽어보세요.','신입 A / 신입 B 비교; 도구 의존 / 도구 활용'],
 [13,'신입이 경험을 쌓던 첫 계단이 줄면 시작 기준이 높아질 수 있다.','game',1010,1130,'이동 코드와 작은 동작을 단계별로 작성','작은 구현과 피드백이 경험을 만든다','구현 → 리뷰 → 디버깅 계단, 첫 계단 소실은 추론'],
 [14,'초반 학년에는 예제를 닫고 백지에서 구현하는 연습이 필요하다.','game',1130,1230,'에디터에서 코드를 추가하고 실행','강의가 대신 결정한 항목을 확인','따라 쓰기 → 정답 닫기 → 스스로 구현'],
 [15,'Linked List를 배운 뒤 Node부터 스스로 만들어보자.','manim',0,84,'Node 구성과 삽입의 포인터 갱신 순서','새 노드의 next를 먼저 연결','완성 코드 → 빈 함수 → 선언·연결'],
 [16,'테트리스 강의를 따라한 뒤 다시 빈 프로젝트에서 만들자.','tetris',440,505,'블록 회전·착지·줄 제거','규칙이 작동하려면 어떤 상태와 함수가 필요한가','구현 순서를 스스로 결정; 잘린 원문은 19장으로 연결'],
 [17,'코드를 읽는 훈련과 백지에서 생성하는 훈련을 구분하자.','game',1230,1330,'실제 강의의 에디터 입력과 실행','따라하기 이후의 독립 구현 단계','읽어서 이해 / 혼자 생성 비교'],
 [18,'학습 뒤 책과 예제를 닫고 Node부터 구현하자.','manim',84,168,'중간 노드 삭제 및 마지막 노드 처리','연결 변경 후 해제하고 head의 빈 상태를 확인','값 파랑 / 포인터 보라 / 추가 초록 / 삭제 빨강'],
 [19,'테트리스의 보드·회전·충돌 질문에 내가 답해야 한다.','tetris',505,570,'회전과 빈 공간을 고려하며 블록 배치','블록 데이터, 충돌 시점, 게임 루프를 떠올려보세요.','데이터 → 규칙 → 실행 순서'],
 [20,'Recognition과 Recall·Problem Solving은 다른 훈련이다.','game',1330,1440,'함수와 입력 동작을 구성하고 검증','누가 자료구조와 구현 순서를 결정하는가','보고 알아보기 / 기억·분해·설계·디버깅'],
 [21,'이해 후 자료를 닫고 다시 만들어보자.','tetris',645,700,'플레이하며 회전과 착지를 반복','완성된 동작에서 필요한 규칙을 다시 떠올리기','입력·이해 → 독립적인 출력'],
 [22,'막히고 디버깅하는 과정이 문제를 코드로 바꾸는 훈련이다.','game',1440,1560,'코드 변경과 실행 결과의 비교','예상한 움직임과 실제 움직임의 차이','가설 → 코드 변경 → 관찰 → 다시 판단'],
 [23,'기초 숙련을 만든 뒤 AI로 프로젝트 생산성을 높이자.','game',1560,1700,'플레이어 이동을 다듬고 실행','작은 함수들을 이해한 상태에서 확장','1·2학년 사고 훈련 → 숙련 후 AI 생산성'],
 [24,'도구를 쓰면서도 머릿속에 문제를 프로그램으로 바꾸는 능력이 있어야 한다.','game',1700,1900,'입력과 속도를 조정하여 동작을 완성','내가 설계한 변화와 실행 결과를 연결','배움 → 정답 닫기 → 구현 → AI로 가속'],
 [25,'공부 방향과 막힌 코드를 얌얌코딩 코칭에서 함께 살펴본다.','explanation',0,0,'공식 코칭 안내와 링크','직접 생각·설계·구현하는 공부 방향','코칭 URL + 설명란 + 종료화면 + 고정댓글']
];
const names={tetris:'lt1Lal2gh_E',inventory:'LD2CFMXoIXM',save:'wSq1QJ-g91M',profile:'lfuGLaZ3khs',game:'GwCiGixlqiU'};
const script=read(path.join(W,'narration.ko.json'));
const plan={revision:'original-restored-v2',createdBeforeTTS:true,createdAt:new Date().toISOString(),originalOrderUnchanged:true,target:{actualShare:.6,explanationShare:.4,excludes:['2-second cat intro','10-second membership ending'],toleranceFrames:1},chapters:rows.map(([chapter,claim,source,start,end,visibleAction,viewerFocus,diagramConnection])=>({chapter,claim,sceneIds:script.scenes.filter(s=>s.chapter===chapter).map(s=>s.id),source,sourceVideoId:names[source]||null,sourceInterval:[start,end],sourceIntervalStatus:source==='game'?'chapter-confirmed-download-pending-direct-visual-review':'broad-contact-reviewed-exact-cut-review-pending',classification:source==='manim'||source==='explanation'?'explanation':'actual',visibleAction,viewerFocus,diagramConnection,insertionPoint:'Within this chapter narration, preserving all original spoken words and order. Alternate explanation with action; final measured cuts may select smaller clean intervals from this source window.'})),guards:['No claim that illustrative GDQuest footage shows AI use or actual Korean employment.','Manim and all diagram-like workbench scenes count as explanation.','Source audio muted; original third-party music not reused.','No repeated source seconds or slowed/looped actual footage to fill quota.','Exact chosen source cuts require direct review before final render.'],rejectedCandidates:[{id:'rAUn1Lom6dw',reason:'No reusable video license verified; reference only'},{id:'8OK8_tHeCIA',reason:'Code license does not establish reusable video rights'},{id:'WahYlxs9Ns0',reason:'CC licensed but visual review shows generic stock and abstract code; not concept-matched development action'}],priorUseExclusions:{lt1Lal2gh_E:[[54,60.5],[84,90.5],[320,326.5]],GwCiGixlqiU:[[7472,7491.5]],lfuGLaZ3khs:[[186,205.5]]},captionPosition:[960,970],codePalette:{value:'#245CA8',pointer:'#7C3AAD',newNode:'#23875B',executingLine:'#BA750C',deletedNode:'#C34242'},reviewedBy:'Codex direct contact-sheet review; human full source listening/rights review pending'};
write(path.join(W,'concept-connections.json'),plan);
let manifest=read(path.join(W,'voice.manifest.json'));manifest.status='original-restoration-production';manifest.production={currentStage:'original-script-restored-source-planned-TTS-ready',ttsGenerated:false,rendered:false,collected:false,uploaded:false};manifest.approvals.fullNarration='pending-new56-scenes';manifest.approvals.render='pending';manifest.editing.exampleInterleaving.planningPath=path.relative(R,path.join(W,'concept-connections.json')).replaceAll('\\','/');write(path.join(W,'voice.manifest.json'),manifest);
console.log('26 original-order chapter/source connections recorded before TTS.');
