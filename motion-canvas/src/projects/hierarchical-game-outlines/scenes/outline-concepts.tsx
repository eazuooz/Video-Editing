import {Line, Node, Rect, Txt, View2D} from '@motion-canvas/2d';
import {all, createRef, easeInOutCubic, waitFor} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';

const headings = [
  ['부모 항목은 읽는 질문', '설명용 기획 메모 · 개발사의 실제 기획서를 재현한 화면이 아닙니다'],
  ['형제 항목의 크기를 맞추기', '기능과 조절값을 섞지 않고, 포함 관계를 들여쓰기로 표시'],
  ['접기는 삭제가 아닙니다', '전체를 읽을 때 접고 · 필요한 규칙을 찾을 때 펼치기'],
  ['가지 이동 뒤에는 뜻도 확인하기', '설명용 비교 · 어울리지 않는 부모 아래로 이동한 예시'],
  ['포함 관계와 참고 관계를 구분', '우리의 구성 제안 · 게임의 전체 의존성 분석이 아닙니다'],
  ['읽는 사람이 필요한 조건을 찾는가', '전체 목표 → 구체적 확인 → 다시 전체 목표'],
];
const summaries = [
  '이 가지가 답할 질문을 먼저 정하고, 세부 내용을 그 아래에 놓습니다.',
  '같은 부모 아래에는 비슷한 크기의 질문을 나란히 놓습니다.',
  '접힌 제목만 읽어도 필요한 규칙의 위치를 예상할 수 있게.',
  '제목과 세부 내용은 함께 이동하고, 새 부모와 의미를 다시 대조합니다.',
  '공통 규칙은 한 곳에 두고, 다른 가지에서는 그 항목을 가리킵니다.',
  '정리한 문서와 검증한 설계를 구분하고, 미확인 질문도 남깁니다.',
];
function label(value:string,x:number,y:number,size=29,color:string=P.ink,weight=500) {
  return <Txt text={value} x={x} y={y} fontFamily={P.font} fontSize={size} fill={color} fontWeight={weight} textAlign={'center'}/>;
}
function tile(x:number,y:number,width:number,height:number,title:string,detail='',color:string=P.blue) {
  return <Node x={x} y={y}>
    <Rect x={11} y={13} width={width} height={height} rotation={-1} fill={'#dfe5e8'}/>
    <Rect width={width} height={height} rotation={-1} fill={'white'} stroke={color} lineWidth={2}/>
    <Rect x={-width/2+12} width={6} height={height-20} fill={color}/>
    {label(title,0,detail?-height*.2:0,31,color,700)}
    {detail?label(detail,0,height*.24,25,P.muted):null}
  </Node>;
}
function connector(points:[number,number][],color:string=P.blue,ref?:ReturnType<typeof createRef<Line>>) {
  return <Line ref={ref} points={points} stroke={color} lineWidth={4} endArrow arrowSize={14} end={ref?0:1}/>;
}

// Independent scene entrypoints call this concept with current measured ends.
// Silent8-second lookdev uses proportional ends and never approves final media.
export function* outlineConcept(view:View2D,index:number,duration:number,paragraphEnds?:number[]) {
  const ends=paragraphEnds??[duration*.25,duration*.5,duration*.75,duration];
  if(index<0||index>5||duration<7||ends.length!==4||Math.abs(ends[3]-duration)>1/60||ends.some((v,i)=>v<=(ends[i-1]??0)))throw Error('Four current paragraph ends required');
  const body=createRef<Node>(),focus=createRef<Node>(),summary=createRef<Node>();
  const detail=createRef<Node>(),branch=createRef<Node>(),folded=createRef<Node>();
  const arrows=[createRef<Line>(),createRef<Line>(),createRef<Line>()];
  view.fill(P.background);
  view.add(<>
    <Txt text={`${index+1} / 6  ·  게임 기획서의 읽는 순서`} x={-850} y={-470} offset={[-1,0]} fontFamily={P.font} fontSize={25} fill={P.muted}/>
    <Txt text={headings[index][0]} x={-850} y={-391} offset={[-1,0]} fontFamily={P.font} fontSize={50} fontWeight={700} fill={P.ink}/>
    <Txt text={headings[index][1]} x={-850} y={-315} offset={[-1,0]} fontFamily={P.font} fontSize={27} fill={P.muted}/>
    <Node ref={body} opacity={0} y={18}/>
    <Node ref={focus} opacity={0}/>
    <Node ref={summary} y={298} opacity={0}>
      <Rect x={11} y={12} width={1650} height={76} fill={'#dae6df'}/>
      <Rect width={1650} height={76} fill={'white'} stroke={P.green} lineWidth={2}/>
      {label(summaries[index],0,0,28,P.ink,600)}
    </Node>
  </>);
  if(index===0) {
    body().add(<>
      {label('섞인 목록',-560,-214,29,P.muted,700)}
      {tile(-560,-105,410,80,'놀이기구 배치')}
      {tile(-560,4,410,80,'높이 조절값','',P.green)}
      {tile(-560,113,410,80,'입구 연결')}
      <Node ref={branch} opacity={0}>
        {connector([[340,-135],[340,-75],[0,-75],[0,-42]],P.blue)}
        {connector([[340,-135],[340,-42]],P.blue)}
        {connector([[340,-135],[340,-75],[680,-75],[680,-42]],P.blue)}
        {connector([[340,44],[340,116]],P.green)}
        {tile(340,-188,820,100,'관람객이 놀이기구를 이용한다','이 가지가 답할 질문')}
        {tile(0,0,275,86,'배치')}{tile(340,0,275,86,'선로 설계')}{tile(680,0,275,86,'입구 연결')}
        {tile(340,160,350,86,'높이 · 곡선','',P.green)}
      </Node>
      {connector([[-310,4],[-190,4]],P.line,arrows[0])}
    </>);
    focus().add(<Rect x={340} y={160} width={372} height={104} stroke={P.green} lineWidth={4}/>);
  } else if(index===1) {
    body().add(<>
      {connector([[-170,127],[30,127],[30,199],[210,199]],P.line,arrows[1])}
      {tile(-520,-170,610,106,'크기가 다른 질문','기능 옆에 세부값을 올린 예시',P.red)}
      {tile(-520,-15,460,86,'놀이기구 배치')}
      <Node ref={detail} x={-520} y={127}>{tile(0,0,310,80,'높이 값','',P.green)}</Node>
      {label('같은 수준의 기능',390,-179,30,P.blue,700)}
      {tile(70,-15,268,86,'배치')}{tile(390,-15,268,86,'선로 설계')}{tile(710,-15,268,86,'입구 연결')}
      {connector([[390,28],[390,84]],P.green,arrows[0])}
    </>);
    focus().add(label('어느 기능의 세부 규칙인가?',390,231,27,P.green,600));
  } else if(index===2) {
    body().add(<>
      {tile(0,-185,1320,90,'관람객의 놀이기구 이용','')}
      {connector([[0,-140],[0,-105],[-550,-105],[-550,-62]],P.blue)}
      {connector([[0,-140],[0,-62]],P.blue)}
      {connector([[0,-140],[0,-105],[550,-105],[550,-62]],P.blue)}
      {tile(-550,-19,420,86,'배치')}{tile(0,-19,420,86,'선로 설계')}{tile(550,-19,420,86,'입구 연결')}
      <Node ref={detail}>
        {connector([[0,26],[0,71],[-170,71],[-170,110]],P.green)}
        {connector([[0,26],[0,71],[170,71],[170,110]],P.green)}
        {tile(-170,154,280,82,'높이','',P.green)}{tile(170,154,280,82,'곡선','',P.green)}
      </Node>
      <Node ref={folded} opacity={0}>{label('▶  세부 규칙은 보존',0,120,29,P.green,700)}</Node>
    </>);
    focus().add(label('접힌 제목으로 위치를 예상 → 필요한 가지 펼치기',0,231,27,P.green,600));
  } else if(index===3) {
    body().add(<>
      {connector([[-170,-11],[170,-11]],P.line,arrows[0])}
      {tile(-520,-178,620,100,'선로 설계','이 조절값을 설명하는 부모')}
      {tile(520,-178,620,100,'입구 연결','잘못 옮겨 본 위치',P.red)}
      <Node ref={branch} x={-520}>
        {connector([[0,-126],[0,-57]],P.blue)}
        {tile(0,-11,470,88,'곡선 조절')}
        <Node ref={detail}>
          {connector([[0,32],[0,90]],P.green)}
          {tile(0,138,485,86,'높이 · 연결 조건','',P.green)}
        </Node>
      </Node>
    </>);
    focus().add(<>
      <Rect x={520} y={36} width={532} height={300} stroke={P.red} lineWidth={4}/>
      {label('이 새 부모가 규칙의 질문에 답하는가?',0,231,27,P.red,600)}
    </>);
  } else if(index===4) {
    body().add(<>
      {connector([[0,-141],[0,-110],[-500,-110],[-500,-61]],P.blue)}
      {connector([[0,-141],[0,-110],[500,-110],[500,-61]],P.blue)}
      {tile(0,-187,1370,90,'놀이기구를 이용한다','')}
      {tile(-500,-12,590,98,'입구 연결')}{tile(500,-12,590,98,'장식 배치')}
      {connector([[-500,39],[-500,152],[-275,152]],P.green,arrows[0])}
      {connector([[500,39],[500,152],[275,152]],P.green,arrows[1])}
      {tile(0,152,510,108,'함께 참고할 조건','한 곳에 보관',P.green)}
      {label('세로 가지: 포함',-500,226,25,P.blue,600)}
      {label('옆 연결: 참고',500,226,25,P.green,600)}
    </>);
    focus().add(<Rect x={0} y={152} width={534} height={128} stroke={P.green} lineWidth={4}/>);
  } else {
    body().add(<>
      {connector([[-245,-181],[-35,-181],[-35,-76]],P.blue,arrows[0])}
      {connector([[240,-28],[570,-28],[570,96]],P.blue,arrows[1])}
      {connector([[570,191],[570,246],[-530,246],[-530,-129]],P.green,arrows[2])}
      {tile(-530,-181,565,100,'전체 목표','놀이기구를 이용한다')}
      {tile(-35,-28,525,100,'기능','선로 설계')}
      {tile(570,145,478,96,'확인할 조건','연결 조건은 확인했는가?',P.green)}
      {label('미확인 질문도 남기기',-390,72,28,P.red,600)}
    </>);
    focus().add(label('함께 구현하기 · 설명과 엔딩의 프로그래밍 과외 링크',0,221,25,P.green,600));
  }
  let elapsed=.55;
  yield* all(body().opacity(1,.55),body().y(0,.55,easeInOutCubic));
  yield* waitFor(Math.max(0,ends[0]-elapsed));elapsed=ends[0];
  if(index===0)yield* all(branch().opacity(1,.6),arrows[0]().end(1,.6));
  else if(index===1)yield* all(arrows[0]().end(1,.6),arrows[1]().end(1,.6));
  else if(index===2) {
    yield* all(detail().opacity(0,.45),detail().scale([1,.15],.45));
    yield* folded().opacity(1,.15);
  }
  else if(index===3)yield* all(branch().x(520,.6,easeInOutCubic),arrows[0]().end(1,.6));
  else yield* all(arrows[0]().end(1,.6),arrows[1]().end(1,.6));
  elapsed+=.6;yield* waitFor(Math.max(0,ends[1]-elapsed));elapsed=ends[1];
  if(index===1)yield* all(detail().position([390,142],.6,easeInOutCubic),focus().opacity(1,.6));
  else if(index===2) {
    yield* folded().opacity(0,.15);
    yield* all(detail().opacity(1,.45),detail().scale([1,1],.45),focus().opacity(1,.45));
  }
  else if(index===5)yield* all(arrows[2]().end(1,.6),focus().opacity(1,.6));
  else yield* focus().opacity(1,.6);
  elapsed+=.6;yield* waitFor(Math.max(0,ends[2]-elapsed));elapsed=ends[2];
  yield* summary().opacity(1,.45);elapsed+=.45;
  yield* waitFor(Math.max(0,duration-elapsed));
}
