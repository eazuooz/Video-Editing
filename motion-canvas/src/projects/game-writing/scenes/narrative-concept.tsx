import {Circle,Line,Node,Rect,Txt,View2D} from '@motion-canvas/2d';
import {all,createRef,easeInOutCubic,waitFor} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';

const concepts=[
 {title:'장면 순서와 현재 상태는 다릅니다',sub:'두 번째 방문이라고 단서를 읽었다고 가정하지 않기',labels:['장면 1 → 장면 2','단서를 읽었는가?','이 답이 지금 참인가?'],details:['정해 놓은 순서','소유 · 정보 · 동행','대사의 성립 조건'],summary:'문장을 고르기 전에 필요한 사실을 확인합니다.'},
 {title:'누가 알고 있는 사실인가요?',sub:'세계의 사실 · 플레이어의 정보 · 상대에게 전한 정보',labels:['세계','플레이어','문지기'],details:['문이 잠겨 있다','게시판을 읽었다','규칙을 전해 들었다'],summary:'읽기와 전달은 서로 다른 사건입니다.'},
 {title:'얻었던 물건, 지금도 꺼낼 수 있나요?',sub:'과거 획득 기록과 현재 소유자를 따로 관리',labels:['플레이어','동료','보관함'],details:['지금 보여 줄 수 있다','함께 있는가?','다시 가져올 수 있다'],summary:'현재 소유와 접근 가능성이 대사를 결정합니다.'},
 {title:'같은 곳에 도착해도 선택은 남습니다',sub:'합류 조건은 공통으로, 결과 기록은 각 경로대로',labels:['먹이를 준다','우회한다','물러나게 한다'],details:['식량 −1 · 이동 1분','식량 유지 · 이동 3분','식량 유지 · 이동 1분'],summary:'합류는 플레이어가 한 행동을 지우는 작업이 아닙니다.'},
 {title:'놓친 필수 사실을 다시 얻을 수 있게',sub:'진행에 필요한 사실과 더 알고 싶은 배경을 구분',labels:['필수 사실','재확인 경로','선택 배경'],details:['증표가 필요하다','문지기 · 게시판','항구가 닫힌 역사'],summary:'모르는 플레이어에게 필요한 근거를 남깁니다.'},
 {title:'플레이 가능한 대본의 여섯 가지 확인',sub:'예쁜 문장과 실제 플레이 조건을 함께 검토',labels:['순서 · 정보','소유 · 합류','필수 사실 · 실행'],details:['누가 무엇을 아는가?','무엇이 실제로 남는가?','다른 경로에서도 참인가?'],summary:'이 대사가 참이려면 무엇이 먼저 일어나야 할까요?'},
];
const colors=[P.blue,P.green,'#9b7742'];
function depthCard(label:string,detail:string,x:number,y:number,color:string,ref:any){
 return <Node ref={ref} x={x} y={y} opacity={0}>
  <Rect x={18} y={22} width={438} height={226} fill={'#dce3e8'} rotation={-2}/>
  <Rect width={438} height={226} fill={P.background} stroke={color} lineWidth={3} rotation={-2}/>
  <Rect x={-195} y={-3} width={8} height={174} fill={color} rotation={-2}/>
  <Txt text={label} y={-43} fontFamily={P.font} fontSize={34} fontWeight={700} fill={P.ink}/>
  <Txt text={detail} y={32} width={375} textWrap fontFamily={P.font} fontSize={26} fill={P.muted} textAlign={'center'}/>
 </Node>;
}
export function* narrativeConcept(view:View2D,index:number,duration:number){
 const c=concepts[index],cards=[createRef<Node>(),createRef<Node>(),createRef<Node>()],token=createRef<Circle>(),tokenText=createRef<Txt>(),bridge=createRef<Line>(),footer=createRef<Node>();
 view.fill(P.background);
 view.add(<>
  <Txt text={`${index+1} / 6 · 게임 시나리오의 조건`} x={-850} y={-474} offset={[-1,0]} fontFamily={P.font} fontSize={25} fill={P.muted}/>
  <Txt text={c.title} x={-850} y={-394} offset={[-1,0]} width={1700} fontFamily={P.font} fontSize={50} fontWeight={700} fill={P.ink}/>
  <Txt text={c.sub} x={-850} y={-318} offset={[-1,0]} fontFamily={P.font} fontSize={30} fill={P.muted}/>
  {index!==3&&<Line ref={bridge} points={index===4?[[-585,132],[0,188],[-585,150]]:[[-585,132],[0,188],[585,132]]} stroke={P.line} lineWidth={6} endArrow arrowSize={18} end={0}/>}
  {c.labels.map((label,i)=>depthCard(label,c.details[i],[-585,0,585][i],[-70,10,-70][i],colors[i],cards[i]))}
  {index!==3&&<Circle ref={token} x={-585} y={144} size={70} fill={P.blue} opacity={0} shadowColor={'#abc4d7'} shadowOffset={[9,12]} shadowBlur={0}/>}
  {index!==3&&<Txt ref={tokenText} text={index===2?'증표':index===1?'정보':'조건'} x={-585} y={144} fontFamily={P.font} fontSize={23} fontWeight={700} fill={'#ffffff'} opacity={0}/>}
  {index===2&&<Txt text={'과거 기록: 증표를 획득함 ✓'} x={-790} y={175} offset={[-1,0]} fontFamily={P.font} fontSize={26} fill={P.green}/>}
  <Node ref={footer} y={index===3?280:260} opacity={0}>
    <Rect x={12} y={14} width={1620} height={90} fill={'#dbe6df'}/>
    <Rect width={1620} height={90} fill={P.background} stroke={P.green} lineWidth={2}/>
    <Txt text={c.summary} width={1510} textWrap textAlign={'center'} fontFamily={P.font} fontSize={32} fontWeight={600} fill={P.ink}/>
  </Node>
 </>);
 if(index===3){
  const branches=[createRef<Line>(),createRef<Line>(),createRef<Line>()],results=[createRef<Node>(),createRef<Node>(),createRef<Node>()];
  view.add(<>
   {[0,1,2].map(i=><Line ref={branches[i]} points={[[[-585,0,585][i],[-35,-5,-35][i]],[[ -90,0,90][i],190]]} stroke={colors[i]} lineWidth={5} endArrow arrowSize={15} end={0}/>)}
   <Rect y={190} width={430} height={56} fill={P.background} stroke={P.green} lineWidth={2}/>
   <Txt text={'항구 도착 · 결과 유지'} y={190} fontFamily={P.font} fontSize={28} fill={P.ink}/>
   {['식량 0','3분','1분'].map((s,i)=><Node ref={results[i]} x={[-585,0,585][i]} y={145} opacity={0}><Rect width={130} height={47} fill={colors[i]} radius={3}/><Txt text={s} fontFamily={P.font} fontSize={24} fill={'#fff'}/></Node>)}
  </>);
  yield* all(...cards.map((r,i)=>all(r().opacity(1,.55+i*.08),r().y([-155,-125,-155][i],.65,easeInOutCubic))));
  yield* waitFor(Math.max(.25,(duration-4)*.33));
  yield* all(...branches.map(r=>r().end(1,.65)),...results.map(r=>r().opacity(1,.4)));
  yield* all(...results.map((r,i)=>all(r().x([-220,0,220][i],1,easeInOutCubic),r().y(120,1))));
  yield* waitFor(Math.max(.25,(duration-4)*.33));
  yield* footer().opacity(1,.45);
  yield* waitFor(Math.max(0,duration-(.71+.65+1+.45+Math.max(.25,(duration-4)*.33)*2)));
  return;
 }
 const unit=Math.max(.3,(duration-4)/6);
 yield* all(...cards.map((r,i)=>all(r().opacity(1,.55+i*.08),r().y([-95,-15,-95][i],.65,easeInOutCubic))),bridge().end(1,.9));
 yield* waitFor(unit);
 yield* all(token().opacity(1,.35),tokenText().opacity(1,.35));
 yield* all(token().x(0,.85,easeInOutCubic),token().y(188,.85),tokenText().x(0,.85),tokenText().y(188,.85),cards[1]().scale(1.045,.65));
 yield* waitFor(unit);
 const endpoint=index===4?-585:585;
 yield* all(token().x(endpoint,.85,easeInOutCubic),token().y(index===4?150:144,.85),tokenText().x(endpoint,.85),tokenText().y(index===4?150:144,.85),cards[1]().scale(1,.65),cards[index===4?0:2]().scale(1.045,.65));
 yield* waitFor(unit);
 yield* all(cards[2]().scale(1,.45),footer().opacity(1,.45));
 yield* waitFor(Math.max(0,duration-(.9+.35+.85+.85+.45+unit*3)));
}
