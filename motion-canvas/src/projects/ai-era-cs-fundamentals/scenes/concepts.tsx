import {Circle, Line, Node, Rect, Txt} from '@motion-canvas/2d';
import {createSignal, tween} from '@motion-canvas/core';
import {PAPER} from '../../../styles/research-paper';
import {tetrisDiagram} from './tetris';
const FONT=PAPER.font, MONO=PAPER.mono;
const C={ink:PAPER.ink,muted:PAPER.muted,green:PAPER.blue,amber:PAPER.ink,red:PAPER.red,panel:PAPER.panel,line:PAPER.line};
const PHRASES = [
  ['오늘 계획은 한 문제','소식은 많고, 기준은 흔들리고','AI 켜요? 꺼요?','오늘 내가 끝낼 기능 하나'],
  ['가상의 회의실','가능성과 검증은 별개','일정부터 최적화?','배우는 일과 반복 작업을 나누기'],
  ['기대: 다섯 번 / 실제: 네 번','중단점으로 변수 추적','끝 조건을 다시 확인','같은 입력으로 다시 실행'],
  ['모든 과목을 한 번에?','들어온 순서대로 처리','이름으로 값을 찾기','내 기능의 질문 → 필요한 기초'],
  ['작은 메모장, 거대한 설계','이 기술을 왜 골랐나요?','요구사항에 맞게 줄이기','입력부터 결과까지 내 말로'],
  ['답을 알아보기 ≠ 직접 시작하기','작은 입력과 기대 출력','이미 본 이름을 기억','새 입력으로 답 없이 다시'],
  ['판과 블록을 데이터로','입력 → 후보 위치 검사 → 이동','가득 찬 줄 지우기','작은 게임도 끝까지 완성'],
  ['중앙에서는 잘 되는데','벽 옆에서 회전하면?','동시 줄 삭제·종료 뒤 입력','실패한 입력은 테스트로'],
  ['구독료가 먼저 출근합니다','API 사용량 요금 / 월 구독료 아님','단가보다 작업 전체 비용','조건이 달라져도 이어갈 수 있게'],
  ['화면은 되는데, 업무는 아직','어디까지 해야 완료인가요?','남은 작업을 구체적으로','테스트·리뷰 안에서 함께 확인'],
  ['출발점은 서로 다릅니다','빈 파일부터 기능 하나','준비한 도구로 로컬 실행','AI가 없어도 시작할 수 있게'],
  ['한 번의 실패가 전부는 아니죠','어제 못 고친 오류 하나','작게 시작 → 검증 → 완료','도구는 구독해도, 실력은 내 것'],
];
function label(text:string|(()=>string),x=0,y=0,size=36,color:string=C.ink,mono=false) {
  return <Txt text={text} x={x} y={y} fontFamily={mono?MONO:FONT} fontSize={size} fontWeight={500} fill={color} />;
}
function card(text:string|(()=>string),x:number,y:number,w=440,h=110,color:string=C.green) {
  return <Rect x={x} y={y} width={w} height={h} fill={C.panel} stroke={color} lineWidth={2} radius={0}>{label(text,0,0,32)}</Rect>;
}
function arrow(x:number,y:number,vertical=false) {return label(vertical?'↓':'→',x,y,45,C.green);}

// Original per-chapter examples. Retiming follows the approved full narration.
export function* explain(parent:Node,index:number,duration:number) {
  const p=createSignal(0); const beat=()=>Math.min(3,Math.floor(p()*4));
  const body=new Node({y:-15,scale:0.92}); parent.add(body);
  body.add(<Txt text={()=>PHRASES[index][beat()]} x={-940} y={-315} offset={[-1,0]} fontFamily={FONT} fontSize={32} fill={C.muted} />);
  if(index===0) {
    body.add(<>
      <Rect x={-500} y={20} width={510} height={400} radius={0} fill={C.panel}>
        {label('TODAY',0,-133,30,C.green,true)}{label('□ 코딩 테스트 1문제',0,-40,31)}{label('□ 포트폴리오 한 기능',0,38,31)}
        {label(()=>beat()===3?'✓ 작은 기능 완료':'아직 시작 전',0,137,32,C.amber)}
      </Rect>
      <Rect x={410} y={15} width={560} height={330} radius={0} fill={PAPER.panel} rotation={()=>beat()===1?Math.sin(p()*120)*2:0}>
        {label('AI NEWS',0,-105,28,C.muted,true)}
        {label(()=>['개발자, 끝났다고?','안 쓰면 뒤처진다?','쓰면 실력이 안 는다?','소식보다 작은 실천'][beat()],0,-5,34,C.amber)}
        {label('과장된 헤드라인 예시',0,105,23,C.muted)}
      </Rect>{arrow(-90,25)}
      {label('불안한 마음을 능력 부족으로 단정하지 않기',0,300,29,C.muted)}
    </>);
  } else if(index===1) {
    ['사장님','임원','팀장'].forEach((s,i)=>body.add(<Node x={(i-1)*530} y={-35}>
      <Circle y={-80} size={84} fill={[C.green,C.amber,PAPER.line][i]} />
      <Rect y={20} width={170} height={120} radius={0} fill={C.panel} />{label(s,0,26,30)}
      {card(['AI로 다 된다던데?','비용도 절반?','일정도 절반?'][i],0,170,470,105,i===2?C.red:C.line)}
    </Node>));
    body.add(<>{label('가상 인물·과장된 상황 · 실제 자료화면 출연자와 무관',0,-185,24,C.muted)}
      {label(()=>beat()<3?'시연 1회 성공  ≠  서비스에서 지속 검증':'학습: 직접 생각    /    익숙한 반복: 도구 활용',0,335,32,C.amber)}
    </>);
  } else if(index===2) {
    const fixed=()=>beat()===3;
    body.add(<>
      <Rect x={-425} y={0} width={760} height={320} radius={0} fill={C.panel}>
        {label(()=>`for i in range(${fixed()?5:4}):`,0,-90,39,C.ink,true)}{label('    print(i)',0,-8,39,C.ink,true)}
        {label(()=>fixed()?'0   1   2   3   4':'0   1   2   3',0,90,40,C.green,true)}
      </Rect>
      {label('실행 횟수',475,-140,34,C.muted)}{label(()=>fixed()?'5 / 5':'4 / 5',475,-28,90,C.amber,true)}
      {label(()=>fixed()?'PASS':'끝 값은 포함하지 않음',475,104,31,C.amber)}
      {label('기대값 작성 → 변수 추적 → 조건 수정 → 재검사',0,290,34,C.muted)}
    </>);
    [0,1,2,3,4].forEach(i=>body.add(<Circle x={-620+i*96} y={205} size={42} fill={()=>i<4||fixed()?C.green:C.panel} stroke={C.green} lineWidth={2} />));
  } else if(index===3) {
    body.add(<>
      {label('QUEUE / 먼저 온 요청부터',-450,-150,32,C.amber)}
      <Rect x={-440} width={750} height={160} radius={0} fill={C.panel} />
      {[0,1,2].map(i=><Rect x={()=>-650+i*195-(beat()>=2?100:0)} width={140} height={100} radius={0} opacity={()=>i===0&&beat()>=2?.25:1} fill={i===0?C.green:PAPER.blueLight}>{label(['A','B','C'][i],0,0,48,PAPER.ink,true)}</Rect>)}
      {label(()=>beat()<2?'A → B → C':'A 처리 완료 → B 차례',-440,145,30,C.muted)}
      {label('DICTIONARY / 이름으로 찾기',470,-150,32,C.amber)}
      {card('"민수"',470,-10,500,105)}{arrow(470,95,true)}{card('프로필 데이터',470,200,500,100,C.line)}
      {label('어떤 문제를 풀지 정한 뒤 자료구조 선택',0,335,31,C.muted)}
    </>);
  } else if(index===4) {
    body.add(<>
      {card('입력',-650,0,260)}{arrow(-445,0)}
      {card(()=>beat()<2?'서버 A / B / C':'단순한 처리',0,0,570,130,C.green)}
      {arrow(445,0)}{card('저장·결과',650,0,270)}
      <Node opacity={()=>beat()<2?1:.15}>
        {card('캐시',-245,-155,270,85,C.line)}{card('메시지 큐',245,-155,270,85,C.line)}{card('별도 서비스',0,165,370,85,C.line)}
      </Node>
      {label(()=>beat()<2?'메모장 만들려다 전산실?':'혼자 쓰는 메모장이라 구성과 배포를 단순화',0,320,34,C.amber)}
    </>);
  } else if(index===5) {
    body.add(<>
      {label('입력',-705,-150,29,C.muted)}{card('민수 · 지수 · 민수',-370,-150,620,100)}{arrow(35,-150)}{card('민수 · 지수',430,-150,600,100)}
      <Rect y={80} width={1490} height={255} radius={0} fill={C.panel}>
        {label(()=>['1. 원하는 결과를 먼저 적기','2. 이미 본 이름은 seen에 기억','3. 처음 본 이름만 result에 추가','4. 입력을 바꿔 혼자 다시 풀기'][beat()],0,-65,36,C.green)}
        {label('seen = set()     result = []',0,10,37,C.ink,true)}
        {label('if name not in seen:  →  기억 + 결과에 추가',0,87,32,C.amber)}
      </Rect>{label('처음 등장한 순서 유지 · 완성 답을 외우는 연습이 아님',0,325,29,C.muted)}
    </>);
  } else if(index===6 || index===7) {
    tetrisDiagram(body,p,index===7);
  } else if(index===8) {
    body.add(<>
      {label('2026-09-06 확인 · 기본 API 요금 · USD / 100만 토큰',0,-185,28,C.muted)}
      {card('GPT-6 Astra',-440,-70,710,110)}{card('Claude Fable 5.1',440,-70,710,110)}
      {label('입력 $10  /  출력 $50',-440,40,37,C.amber)}{label('입력 $10  /  출력 $50',440,40,37,C.amber)}
      {label('캐시·긴 입력·실행 모드 등 별도 조건 / 월 구독료와 다름',0,155,28,C.muted)}
      {card(()=>beat()<2?'사용량 × 단가':'사용량 · 재시도 · 캐시 → 작업 전체 비용',0,275,1480,100,C.line)}
      {label('출처: OpenAI 모델 문서 · Anthropic 공식 요금표 / 게시 전 재확인',0,390,23,C.muted)}
    </>);
  } else if(index===9) {
    body.add(<>
      {card(()=>beat()<2?'거의 다 됐습니다…':beat()===2?'정상 입력 완료 / 저장 실패 처리 남음':'실패 처리까지 확인 / 리뷰 요청',0,-135,1500,125,C.amber)}
      {label('완료 기준을 팀과 함께 확인',0,-25,27,C.muted)}
      {['정상 입력','실패 처리','저장 검증','연동·권한·리뷰'].map((s,i)=><Rect x={(i-1.5)*420} y={110} width={385} height={150} fill={C.panel} radius={0} stroke={()=>beat()>=i?C.green:C.line} lineWidth={3}>
        {label(()=>beat()>=i?'✓':'□',0,-35,40,C.green)}{label(s,0,35,28)}
      </Rect>)}
      {label('남은 것 · 확인한 것 · 도움 필요한 조건',0,305,35,C.amber)}
      {label('지연 원인은 요구사항·일정·협업 조건도 함께 확인',0,375,27,C.muted)}
    </>);
  } else if(index===10) {
    body.add(<>
      <Rect x={-390} y={30} width={870} height={380} radius={0} fill={C.panel}>
        {label('memo.py',0,-130,28,C.muted,true)}
        {label(()=>beat()===0?'# 빈 파일에서 기능 하나':`from pathlib import Path\nPath("memo.txt").write_text(\n    "today: one small task",\n    encoding="utf-8"\n)`,0,15,31,C.ink,true)}
      </Rect>{arrow(120,25)}{card('로컬 파일 저장',510,25,550,130)}
      {label('실행 환경·문서 미리 준비',490,-130,27,C.amber)}
      {label('외부 API·추가 다운로드는 별개',0,305,29,C.muted)}
      {label('시연 영상이 오프라인이라는 뜻은 아님 · 자체 로컬 코드 예시',0,378,24,C.muted)}
    </>);
  } else {
    body.add(<>
      {['작게 시작','직접 검증','끝내고 설명'].map((s,i)=><Node x={(i-1)*540}>
        <Circle y={-60} size={150} stroke={C.green} lineWidth={5} fill={()=>beat()>i?C.green:C.panel} />
        {label(()=>beat()>i?'✓':String(i+1),0,-60,65,C.ink,true)}{label(s,0,90,41)}
      </Node>)}{arrow(-270,-60)}{arrow(270,-60)}
      {label('AI가 있으면 더 빠르게. 없어도 멈추지 않게.',0,280,40,C.amber)}
      {label('기초와 도구 활용은 함께 가져갈 수 있습니다',0,368,29,C.muted)}
    </>);
  }
  const takeaways = [
    '불안한 소식보다, 오늘 내가 끝낼 기능 하나.',
    '가능성을 아는 것과 현장에서 검증하는 것은 다르다.',
    '기대 결과 → 원인 추적 → 수정 → 같은 입력으로 재검사.',
    '내 기능에서 나온 질문이 기초를 배울 출발점.',
    '기술 이름보다 선택한 이유를 설명하기.',
    '답을 알아보는 연습과 직접 시작하는 연습은 다르다.',
    '입력 · 충돌 · 고정 · 줄 삭제를 연결해야 게임이 된다.',
    '시연하고 싶은 장면 밖에서도 규칙은 지켜져야 한다.',
    '단가 하나가 아니라, 재시도까지 포함한 작업 전체 비용.',
    '화면 동작 ≠ 업무 완료. 완료 기준을 팀과 함께 확인.',
    '도구와 문서를 준비하고, 빈 파일부터 작은 기능 하나.',
    'AI가 있으면 더 빠르게. 없어도 멈추지 않게.',
  ];
  const takeaway = new Rect({y:425,width:1728,height:86,fill:PAPER.panel,stroke:PAPER.ink,lineWidth:1.5});
  takeaway.add(<Txt text={takeaways[index]} fontFamily={FONT} fontSize={30} fontWeight={600} fill={PAPER.ink} />);
  parent.add(takeaway);
  yield* tween(duration,v=>p(v)); body.remove(); takeaway.remove();
}
