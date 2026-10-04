import {Line, Node, Rect, Txt, View2D} from '@motion-canvas/2d';
import {all, createRef, easeInOutCubic, usePlayback} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';

type Point = [number, number];
const titles:Record<string,string> = {
  '01':'아직 없는 게임, 같은 행동을 떠올리게 하려면?',
  '03':'한 작품명에서 서로 다른 장면을 떠올린다',
  '05':'공간 → 행동 → 눈에 보이는 변화',
  '07':'관찰한 사실과 결정할 조건은 다른 칸에',
  '09':'목표 · 행동과 조건 · 연결의 세 문장',
  '11':'되말하기에서 빠진 조건을 찾는다',
  '13':'움직이는 대상 · 보인 변화 · 아직 정할 조건',
  '14':'보인 결과와 연결 조건을 다른 칸에',
};
const notes:Record<string,string> = {
  '01':'보이는 행동을 설명하고, 새 기획의 조건은 직접 결정합니다.',
  '03':'가상 청자의 설명 연습 · 실제 이용자 조사 결과가 아닙니다.',
  '05':'장르와 작품명 옆에, 핵심 행동을 직접 쓴 한 문장을 붙입니다.',
  '07':'제한 시간 · 재사용 비용은 우리의 설계 질문입니다.',
  '09':'우리의 설명 연습 · 개발사의 실제 기획서나 전체 목표가 아닙니다.',
  '11':'가상의 답변으로 확인 방법을 보여 줍니다.',
  '13':'새 기획을 쓰는 우리의 연습 · 실제 개발사 기획서가 아닙니다.',
  '14':'한 장면의 결과를 모든 상황의 규칙으로 약속하지 않습니다.',
};
const counts:Record<string,number> = {'01':4,'03':4,'05':3,'07':4,'09':4,'11':3,'13':1,'14':1};
function label(value:string,x:number,y:number,size=29,color:string=P.ink,weight=500){
  return <Txt text={value} x={x} y={y} fontFamily={P.font} fontSize={size} fill={color} fontWeight={weight} textAlign={'center'} lineHeight={size*1.35}/>;
}
// A visible top/right extrusion, offset hard shadow and independent movement
// make the relationship cards shallow planes rather than flat text slides.
function plane(x:number,y:number,w:number,h:number,title:string,detail='',color:string=P.blue){
  const l=-w/2,r=w/2,t=-h/2,b=h/2;
  return <Node x={x} y={y}>
    <Rect x={15} y={20} width={w} height={h} fill={'#e4e8eb'}/>
    <Line points={[[l,t],[l+12,t-10],[r+12,t-10],[r+12,b-10],[r,b],[l,b],[l,t]]} closed fill={'#d8e2ec'} stroke={P.line} lineWidth={1}/>
    <Rect width={w} height={h} fill={'white'} stroke={color} lineWidth={2}/>
    <Rect x={l+9} width={5} height={h-20} fill={color}/>
    {label(title,0,detail?-h*.19:0,30,color,700)}
    {detail?label(detail,0,h*.23,25,P.muted):null}
  </Node>;
}
function arrow(points:Point[],color:string=P.blue){
  return <Line points={points} stroke={color} lineWidth={4} endArrow arrowSize={15}/>;
}
function bracket(x:number,y:number,w:number,h:number,color:string=P.green){
  return <Rect x={x} y={y} width={w} height={h} stroke={color} lineWidth={4}/>;
}

export function* conceptDiagram(view:View2D,id:string,duration:number,paragraphEnds:number[],lookdev=false){
  if(!titles[id]||paragraphEnds.length!==counts[id]||duration<6||paragraphEnds.some((t,i)=>t<=(paragraphEnds[i-1]??0))||Math.abs(paragraphEnds[paragraphEnds.length-1]-duration)>1/60){
    throw Error(`Scene${id}: independent current paragraph timing required`);
  }
  const playback=usePlayback(),start=playback.frame;
  function* until(seconds:number){const end=start+Math.round(seconds*playback.fps);while(playback.frame<end)yield;}
  view.fill(P.background);
  const stages=Array.from({length:counts[id]},()=>createRef<Node>());
  const moving=createRef<Node>();
  view.add(<>
    <Txt x={-850} y={-470} offset={[-1,0]} text={`기획 전달  ·  ${id}${lookdev?'  ·  무음 구성 검토':''}`} fontFamily={P.font} fontSize={25} fill={P.muted}/>
    <Txt x={-850} y={-392} offset={[-1,0]} text={titles[id]} fontFamily={P.font} fontSize={48} fontWeight={700} fill={P.ink}/>
    <Txt x={-850} y={-313} offset={[-1,0]} text={notes[id]} fontFamily={P.font} fontSize={27} fill={P.muted}/>
    <Line points={[[-820,245],[-745,280],[835,280],[760,245]]} closed fill={'#f5f7f9'} stroke={P.line} lineWidth={1}/>
    {stages.map(ref=><Node ref={ref} opacity={0} y={15}/>)}
  </>);
  if(id==='01'){
    stages[0]().add(<>{plane(0,-146,1330,106,'같은 작품 이름 → 같은 머릿속 장면?')}{label('아직 없는 게임을 설명하는 질문',0,-30,29,P.muted)}</>);
    stages[1]().add(<>{plane(-545,90,435,115,'① 보이는 행동','파고 나와 공중으로')}{plane(0,90,435,115,'② 공간과 조건','그림면 · 책상 · 진입 지점')}{plane(545,90,435,115,'③ 세 문장으로','목표 · 행동과 조건 · 연결')}{arrow([[-302,90],[-241,90]])}{arrow([[241,90],[302,90]])}</>);
    stages[2]().add(<>{plane(0,231,1390,70,'시청 후: 세 문장을 적고, 되말하기에서 빠진 조건 찾기','',P.green)}</>);
    stages[3]().add(<>{bracket(-545,90,470,144)}{label('첫 사례: 노란 지형을 파고 나오는 움직임',0,312,28,P.green,700)}</>);
  }else if(id==='03'){
    stages[0]().add(<>{plane(0,-182,1180,96,'“익숙한 작품과 비슷한 게임입니다.”')}{label('비교가 가리키는 부분은 아직 말하지 않았다',0,-101,26,P.muted)}</>);
    stages[1]().add(<>{plane(-455,50,680,151,'가상 청자 A','장애물을 넘는 이동')}{plane(455,50,680,151,'가상 청자 B','적과 싸우는 장면',P.green)}{arrow([[-420,-124],[-455,-80],[-455,-37]])}{arrow([[420,-124],[455,-80],[455,-37]],P.green)}</>);
    stages[2]().add(<>{label('같은 이름을 들었다 ≠ 같은 행동을 떠올렸다',0,188,32,P.red,700)}</>);
    stages[3]().add(<Node ref={moving}>{plane(0,275,1480,77,'어떤 부분의 비교인가? → 새 기획의 행동과 조건을 이어서 설명','',P.blue)}</Node>);
  }else if(id==='05'){
    stages[0]().add(<>{plane(-570,-95,450,144,'공간','책상')}{plane(0,-95,450,144,'동사','진입 지점에 다가간다')}{plane(570,-95,450,144,'보이는 변화','인쇄면 안으로 들어간다')}{arrow([[-320,-95],[-250,-95]])}{arrow([[250,-95],[320,-95]])}</>);
    stages[1]().add(<>{plane(0,113,1530,115,'“재미있는 이동” 옆에 구체적인 행동 한 문장','어디서 무엇을 해서, 어떤 변화가 보이는가?',P.green)}{arrow([[0,-8],[0,42]],P.green)}</>);
    stages[2]().add(<>{label('작품명 · 장르 = 배경',-440,281,30,P.muted,600)}{label('핵심 행동 = 직접 쓴 문장',440,281,30,P.blue,700)}{bracket(440,281,710,70)}</>);
  }else if(id==='07'){
    stages[0]().add(<>{plane(-445,-60,700,242,'관찰한 사실','진입 지점에 다가가\n그림면 안으로 들어갔다')}{plane(445,-60,700,242,'새 기획에서 결정할 조건','진입 지점을 어떻게 알릴까?\n언제 다시 할 수 있을까?',P.green)}</>);
    stages[1]().add(<>{label('설계 질문',445,120,29,P.green,700)}{plane(445,188,700,80,'제한 시간? · 재사용 비용?','시연으로 확인한 규칙이 아니다',P.green)}</>);
    stages[2]().add(<>{arrow([[-30,-60],[30,-60]],P.red)}{label('기억으로 빈칸을 확정하지 않기',0,-237,30,P.red,700)}<Line points={[[-17,-87],[17,-33]]} stroke={P.red} lineWidth={6}/></>);
    stages[3]().add(<>{plane(-445,288,700,62,'확인한 조건은 설명','',P.blue)}{plane(445,288,700,62,'미정인 조건은 질문','',P.green)}</>);
  }else if(id==='09'){
    stages[0]().add(<>{plane(-555,-154,445,138,'① 목표','다음 발판에 도달한다')}{plane(0,-154,445,138,'② 행동과 조건','부드러운 지형에서 파고 이동')}{plane(555,-154,445,138,'③ 연결','나온 뒤 공중으로 다음 공간')}</>);
    stages[1]().add(<>{arrow([[-309,-154],[-250,-154]])}{arrow([[250,-154],[309,-154]])}{label('행동과 다음 행동이 어떻게 이어지는가?',0,-18,31,P.blue,700)}</>);
    stages[2]().add(<>{plane(-555,120,445,109,'도달하기')}{plane(0,120,445,109,'파고 이동하기')}{plane(555,120,445,109,'나와 이동하기')}{arrow([[-309,120],[-250,120]])}{arrow([[250,120],[309,120]])}{label('본 장면을 활용한 우리의 설명 연습',0,219,28,P.muted)}</>);
    stages[3]().add(<>{plane(0,280,1500,66,'자기 기획의 목표와 가능한 조건은 직접 정해 적습니다.','',P.green)}</>);
  }else if(id==='13'){
    stages[0]().add(<>
      {plane(-555,-97,440,142,'움직이는 대상','캐릭터 · 책 · 열쇠')}
      {plane(0,-97,440,142,'보인 변화','위치 · 기울기 · 이동 방향')}
      {plane(555,-97,440,142,'새 기획의 조건','직접 정하고 문장으로 적기',P.green)}
      {arrow([[-314,-97],[-246,-97]])}{arrow([[246,-97],[314,-97]],P.green)}
      {plane(0,170,1460,120,'작품명이 대신 채워 주던 조건은 무엇인가?','무엇이 움직이고, 어떤 변화가 생기는지 풀어 씁니다.',P.green)}
    </>);
  }else if(id==='14'){
    stages[0]().add(<>
      {plane(-435,-66,720,208,'이 장면에서 보인 결과','빨간 상자가 열림 · 카드 그림')}
      {plane(435,-66,720,208,'새 기획에서 정할 연결','언제 · 어떤 행동 뒤에 가능한가?',P.green)}
      {arrow([[-50,-66],[50,-66]],P.red)}
      {label('한 장면만으로 모든 상자의 규칙을 확정하지 않기',0,128,30,P.red,700)}
      {plane(0,255,1480,105,'청자가 자기 말로 나눠 설명할 수 있는가?','보인 결과와 아직 정할 조건을 구별해 빠진 질문을 찾습니다.',P.green)}
    </>);
  }else{
    stages[0]().add(<>{plane(-435,-161,720,135,'확인 질문','“처음 무엇을 할 건가요?”')}{plane(435,-161,720,135,'듣는 사람이 자기 말로','전달된 행동을 확인하기',P.green)}{arrow([[-51,-161],[51,-161]])}</>);
    stages[1]().add(<>{plane(-435,40,720,126,'가상의 답','“아무 벽에나 들어가요.”',P.red)}{plane(435,40,720,126,'빠진 조건 찾기','진입 지점을 말했는가?',P.green)}{arrow([[-51,40],[51,40]],P.red)}</>);
    stages[2]().add(<>{plane(-530,252,430,105,'목표와 동작','같게 이해했는가?')}{plane(0,252,430,105,'미정 조건','무엇이 남았는가?')}{plane(530,252,430,105,'필요한 문장만','보완하고 다시 확인',P.green)}{arrow([[-286,252],[-246,252]])}{arrow([[246,252],[286,252]],P.green)}</>);
  }
  for(let i=0;i<stages.length;i++){
    if(i)yield*until(paragraphEnds[i-1]);
    yield*all(stages[i]().opacity(1,.48),stages[i]().y(0,.48,easeInOutCubic));
    if(id==='03'&&i===3)yield* moving().x(12,.42,easeInOutCubic);
  }
  yield*until(duration);
}
