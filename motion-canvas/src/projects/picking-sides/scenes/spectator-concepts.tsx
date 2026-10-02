import {Circle,Line,Node,Rect,Txt,View2D} from '@motion-canvas/2d';
import {all,createRef,easeInOutCubic,waitFor} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';

const C={blue:P.blue,green:P.green,gold:'#aa7b28',red:P.red};
const titles=[
 ['대상 · 이유 · 상황을 나누세요','알아보는 것과 신경 쓰는 것은 다른 문제입니다'],
 ['세 단서가 같은 참가자를 가리키게','색 · 외형 · 이름이 움직임 속에서도 이어져야 합니다'],
 ['응원할 이유는 보상과 다릅니다','외형, 행동 방식, 익숙한 사람도 출발점이 됩니다'],
 ['지금 중요한 관계를 보여주세요','대상 → 장애물 → 목표를 실제 행동과 연결합니다'],
 ['선택을 강요하지 않는 관전 화면','그냥 보기와 나중에 바꾸기도 남겨 두세요'],
 ['관전 화면을 점검하는 네 질문','누구 · 왜 · 지금 · 실제 결과를 한 흐름으로'],
];
const summaries=[
 '큰 이름표 하나로 세 문제를 모두 해결할 수는 없습니다.',
 '정보를 더하기 전에, 같은 대상을 가리키는지 확인하세요.',
 '소개한 차이를 다음 행동에서 직접 볼 수 있어야 합니다.',
 '필요한 정보는 달라져도, 경기의 사실은 바뀌지 않습니다.',
 '화면 점검의 통과와 사람의 재미 평가는 구분합니다.',
 '좋아 보이는 표시보다, 놓치지 않고 읽히는 행동이 먼저입니다.',
];
function label(text:string,x:number,y:number,size=30,color:string=P.ink,weight=500){return <Txt text={text} x={x} y={y} fontFamily={P.font} fontSize={size} fill={color} fontWeight={weight} textAlign={'center'}/>;}
function card(x:number,y:number,w:number,h:number,title:string,detail:string,color:string=P.blue,rows?:[number,number]){return <Node x={x} y={y}>
 <Rect x={14} y={17} width={w} height={h} fill={'#dbe3e5'} rotation={-1}/>
 <Rect width={w} height={h} fill={'white'} stroke={color} lineWidth={2} rotation={-1}/>
 <Rect x={-w/2+13} width={7} height={h-26} fill={color}/>
 {label(title,0,rows?.[0]??-h*.18,32,color,700)}{label(detail,0,rows?.[1]??h*.19,25,P.muted)}
 </Node>;}
function avatar(x:number,y:number,color:string,symbol:string,name:string){return <Node x={x} y={y}>
 <Circle x={11} y={42} width={110} height={25} fill={'#a7b9ae55'}/>
 <Rect y={10} width={75} height={82} radius={14} fill={color}/><Circle y={-44} size={53} fill={'#eee7d6'} stroke={color} lineWidth={3}/>
 {label(symbol,0,6,39,'white',700)}{label(name,0,-105,27,color,700)}
 </Node>;}
function arrow(points:any,color:string=P.line,ref?:any){return <Line ref={ref} points={points} stroke={color} lineWidth={5} endArrow arrowSize={15} end={ref?0:1}/>;}

export function* spectatorConcept(view:View2D,index:number,duration:number){
 if(index<0||index>5||duration<4)throw Error('Reviewed explanation duration required');
 const stage=createRef<Node>(),focus=createRef<Node>(),summary=createRef<Node>();
 const rays=[createRef<Line>(),createRef<Line>(),createRef<Line>()];
 const a=createRef<Node>(),b=createRef<Node>(),c=createRef<Node>(),cover=createRef<Rect>();
 view.fill(P.background);
 view.add(<>
  <Txt text={`${index+1} / 6  ·  관전과 응원 대상`} x={-850} y={-470} offset={[-1,0]} fontFamily={P.font} fontSize={25} fill={P.muted}/>
  <Txt text={titles[index][0]} x={-850} y={-391} offset={[-1,0]} fontFamily={P.font} fontSize={50} fontWeight={700} fill={P.ink}/>
  <Txt text={titles[index][1]} x={-850} y={-315} offset={[-1,0]} fontFamily={P.font} fontSize={29} fill={P.muted}/>
  <Node ref={stage} opacity={0} y={24}/>
  <Node ref={focus} opacity={0}/>
  <Node ref={summary} y={288} opacity={0}>
   <Rect x={11} y={12} width={1630} height={75} fill={'#dae6df'}/>
   <Rect width={1630} height={75} fill={'white'} stroke={P.green} lineWidth={2}/>
   {label(summaries[index],0,0,30,P.ink,600)}
  </Node>
 </>);
 if(index===0){
  stage().add(<>
   <Node ref={a}>{card(-570,-35,455,285,'대상','누구인지 찾을 수 있는가',C.blue,[-115,114])}{avatar(-570,-18,C.blue,'★','')}</Node>
   <Node ref={b}>{card(0,-35,455,285,'이유','왜 계속 보고 싶은가',C.gold,[-115,114])}{label('?',0,-15,64,C.gold,700)}</Node>
   <Node ref={c}>{card(570,-35,455,285,'상황','지금 무엇이 중요한가',C.green,[-115,114])}{label('! →',570,-15,54,C.green,700)}</Node>
   {arrow([[-335,18],[-235,18]],C.blue,rays[0])}{arrow([[235,18],[335,18]],C.green,rays[1])}
  </>);
  focus().add(<>{label('친구를 응원하지만, 화면에서 못 찾는다면?',0,162,31,C.red,600)}</>);
 }else if(index===1){
  stage().add(<>
   {card(-465,-33,690,330,'단서가 충돌','카드의 별 ≠ 몸체의 달',C.red,[-141,141])}
   {card(465,-33,690,330,'단서가 일치','카드의 별 = 몸체의 별',C.green,[-141,141])}
   <Node ref={a}>{avatar(-465,-1,C.blue,'●','★  별')}</Node>
   <Node ref={b}>{avatar(465,-1,C.blue,'★','★  별')}</Node>
   <Rect ref={cover} x={465} y={-10} width={130} height={132} fill={'#dfe7df'} opacity={0}/>
  </>);
  focus().add(<>{label('잠깐 가려졌다가 나와도 같은 참가자',465,190,28,C.green,600)}{label('크게 붙여도 모순은 남습니다',-465,190,27,C.red)}</>);
 }else if(index===2){
  stage().add(<>
   <Node ref={a}>{card(-565,-115,440,154,'좋아하는 외형','익숙한 색 · 실루엣',C.blue)}</Node>
   <Node ref={b}>{card(0,-115,440,154,'보고 싶은 행동','빠른 시도 · 차분한 진행',C.gold)}</Node>
   <Node ref={c}>{card(565,-115,440,154,'알고 있는 사람','친구 · 친숙한 참가자',C.green)}</Node>
   {arrow([[-565,-24],[-110,135]],C.blue,rays[0])}{arrow([[0,-24],[0,135]],C.gold,rays[1])}{arrow([[565,-24],[110,135]],C.green,rays[2])}
   {label('다음 행동을 기다릴 이유',0,188,36,P.ink,700)}
  </>);
  focus().add(<>{label('선택 = 관심의 보장?',0,82,28,C.red,600)}</>);
 }else if(index===3){
  stage().add(<>
   <Rect x={0} y={35} width={1560} height={200} fill={'#e9eeea'} skewX={-19} rotation={-3}/>
   <Rect x={16} y={110} width={1558} height={31} fill={'#ccd8d0'} skewX={-19} rotation={-3}/>
   <Node ref={a}>{avatar(-590,-25,C.blue,'★','대상')}</Node>
   <Node ref={b} x={0} y={-20}><Rect x={15} y={17} size={100} fill={'#9c7958'} rotation={-5}/><Rect size={100} fill={'#d6ad76'} rotation={-5}/>{label('장애물',0,-105,29,C.gold,700)}</Node>
   <Node ref={c} x={590} y={-20}><Line points={[[0,70],[0,-82],[91,-58],[0,-31]]} stroke={C.green} lineWidth={8}/>{label('목표',0,-105,29,C.green,700)}</Node>
   {arrow([[-450,-12],[-125,-12]],C.blue,rays[0])}{arrow([[125,-12],[435,-12]],C.green,rays[1])}
  </>);
  focus().add(<Rect x={-320} y={-55} width={830} height={274} stroke={C.blue} lineWidth={4} radius={4}/>);
 }else if(index===4){
  stage().add(<>
   <Node ref={a}>{card(-590,-118,390,149,'그냥 보기','선택 없이 시작',C.blue)}</Node>
   <Node ref={b}>{card(0,-118,390,149,'한 명 고르기','짧은 정보로 선택',C.gold)}</Node>
   <Node ref={c}>{card(590,-118,390,149,'나중에 바꾸기','행동을 본 뒤 전환',C.green)}</Node>
   {arrow([[-590,-30],[-590,13],[-170,13]],C.blue,rays[0])}{arrow([[0,-30],[0,35]],C.gold,rays[1])}{arrow([[590,-30],[590,13],[170,13]],C.green,rays[2])}
   {card(-410,152,650,122,'화면 · 입력 점검','같은 대상을 찾을 수 있는가?',C.blue)}
   {card(410,152,650,122,'실제 관전자 반응','계속 보고 싶은가?',C.green)}
  </>);
  focus().add(<>{label('다른 질문  ≠  같은 증거',0,30,29,C.red,600)}</>);
 }else{
  stage().add(<>
   <Node ref={a}>{card(-420,-149,720,160,'01  누구를 보는가','외형 · 표식 · 같은 이름',C.blue)}{card(420,-149,720,160,'02  왜 골랐는가','짧은 소개 · 실제 행동',C.gold)}</Node>
   <Node ref={b}>{card(-420,92,720,160,'03  지금 중요한 것은','장애물 · 방향 · 목표',C.green)}{card(420,92,720,160,'04  실제로 어떻게 끝났는가','행동과 일치하는 결과',C.blue)}</Node>
   <Node ref={c}/>{arrow([[-420,-59],[-420,-5]],C.green,rays[0])}{arrow([[420,-59],[420,-5]],C.blue,rays[1])}
  </>);
  focus().add(<>{label('사람에게 보여주고, 반응을 들어보기',0,218,29,C.green,600)}</>);
 }
 // Proportional timing is used only for lookdev until measured paragraph timing is installed.
 const unit=(duration-3.2)/4;
 yield* all(stage().opacity(1,.6),stage().y(0,.6,easeInOutCubic));
 yield* waitFor(unit);
 if(index===1){
  yield* all(cover().opacity(1,.3),b().x(75,.3));
  yield* all(b().x(-75,.6,easeInOutCubic),cover().opacity(0,.6));
 }else if(index===3){
  yield* all(rays[0]().end(1,.45),rays[1]().end(1,.45),a().x(140,.45,easeInOutCubic));
  yield* all(focus().opacity(1,.45),focus().x(320,.45));
 }else{
  const n=index===2||index===4?3:2;
  yield* all(...rays.slice(0,n).map(r=>r().end(1,.9)),a().scale(1.035,.9));
 }
 yield* waitFor(unit);
 yield* all(focus().opacity(1,.45),index===1?b().x(0,.45):a().scale(1,.45));
 yield* waitFor(unit);
 yield* summary().opacity(1,.45);
 yield* waitFor(unit+0.8);
}
