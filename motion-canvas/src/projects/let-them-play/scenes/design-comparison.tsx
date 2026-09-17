import {Circle,Line,Node,Rect,Txt,View2D} from '@motion-canvas/2d';
import {createSignal,tween} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';
import plan from '../../../../../projects/let-them-play/planning/scenes.json';
import {SEGMENT_SECONDS} from '../timing';
const ramp=(t:number,a:number,b:number)=>{const x=Math.max(0,Math.min(1,(t-a)/(b-a)));return x*x*(3-2*x)};
const lerp=(a:number,b:number,t:number)=>a+(b-a)*t;
function block(parent:Node,x:number,y:number,w:number,h:number,color:string=P.blue){
 const n=new Node({x,y});parent.add(n);
 n.add(<>
  <Line points={[[w/2,0],[w/2+22,-18],[w/2+22,-h-18],[w/2,-h]]} closed fill={'#647a97'}/>
  <Line points={[[-w/2,-h],[w/2,-h],[w/2+22,-h-18],[-w/2+22,-h-18]]} closed fill={'#b8c9df'}/>
  <Rect y={-h/2} width={w} height={h} fill={color}/>
 </>);return n;
}
function floor(n:Node){
 n.add(<>
  <Line points={[[-380,112],[330,112],[396,57],[-314,57]]} closed fill={P.panel} stroke={P.line} lineWidth={2}/>
  <Line points={[[-380,112],[330,112],[330,138],[-380,138]]} closed fill={'#d9dfe7'}/>
  <Line points={[[330,112],[396,57],[396,83],[330,138]]} closed fill={'#b7c3d2'}/>
 </>);
 for(let i=0;i<7;i++)n.add(<Line points={[[-350+i*98,112],[-284+i*98,57]]} stroke={'#dce2ea'} lineWidth={1}/>);
}
function hero(n:Node){
 const actor=block(n,-250,110,45,60);
 actor.add(<><Circle x={-9} y={-42} size={6} fill={P.background}/><Circle x={9} y={-42} size={6} fill={P.background}/><Line points={[[-7,-24],[7,-24]]} stroke={P.background} lineWidth={2}/></>);return actor;
}
function portal(n:Node,x:number){
 const gate=new Node({x});n.add(gate);block(gate,-46,110,16,154,'#8493a7');block(gate,46,110,16,154,'#8493a7');block(gate,0,-40,108,17,'#8493a7');
 return gate;
}
const brief=[
 ['설명을 먼저','장면을 먼저'],['목표가 프레임 밖','관계가 한눈에'],['모두 같은 강조','첫 대상에 강조'],['동시에 여러 행동','먼저 하나의 행동'],['결과가 시야 밖','행동과 결과 함께'],['원인 단서 없음','위험과 상태 연결'],['처음에 모두 안내','필요한 순간 안내'],['도착에서 끊김','다음 관심사 연결'],
];

/** A fictional design comparison, not a reconstruction of Zelda or a user study. */
export function* designComparison(area:Node,index:number,duration=SEGMENT_SECONDS){
 const s=plan.scenes[index],t=createSignal(0);
 area.opacity(()=>ramp(t(),0,.045)*(1-ramp(t(),.97,1)));
 area.add(<Line points={[[0,-270],[0,285]]} stroke={P.line} lineWidth={2}/>);
 for(let side=0;side<2;side++){
  const b=side===1,panel=new Node({x:b?435:-435});area.add(panel);
  panel.add(<>
   <Txt y={-245} text={(b?'B · ':'A · ')+brief[index][side]} fontFamily={P.font} fontSize={33} fontWeight={600} fill={b?P.blue:P.ink}/>
   <Txt y={-195} text={'가상 시작 장면'} fontFamily={P.font} fontSize={23} fill={P.muted}/>
  </>);
  const frame=new Rect({width:780,height:340,clip:true,stroke:P.line,lineWidth:2});panel.add(frame);
  const world=new Node({});frame.add(world);floor(world);
  let gateX=230;
  if(index===1&&!b)world.x(205); // same world, different camera crop
  if(index===4&&!b)gateX=500;
  const gate=portal(world,gateX);
  let actor:Node;
  // Subject and nearby targets share the same geometry within each A/B pair.
  if(index===2||index===3){
   for(let j=0;j<3;j++){
    const prop=block(world,-120+j*120,80,43,45,b&&index===2?'#b6c0ce':P.blue);
    if(index===2&&b)prop.opacity(()=>lerp(1,.48,ramp(t(),.2,.5)));
    if(index===3){
     const hint=new Node({x:-105+j*120,y:-70});world.add(hint);
     hint.add(<><Rect width={104} height={43} fill={P.background} stroke={P.line} lineWidth={1}/><Txt text={['살펴보기','줍기','사용하기'][j]} fontFamily={P.font} fontSize={19} fill={P.ink}/></>);
     hint.opacity(()=>b?(j===0?1-ramp(t(),.49,.55):j===1?ramp(t(),.53,.6)*(1-ramp(t(),.78,.84)):ramp(t(),.82,.88)):1);
    }
   }
  }
  actor=hero(world);
  actor.x(()=>lerp(-270,index===7?80:index===3?-100:180,ramp(t(),.18,.78)));
  if(index===1)actor.x(-250);
  if(index===2)actor.x(()=>lerp(-270,-180,ramp(t(),.58,.82)));
  if(index===0){
   actor.x(()=>lerp(-270,110,ramp(t(),.63,.9)));
   const cards=['세계의 배경','조작 방법','여행의 목표'];
   const overlay=new Node({});frame.add(overlay);
   if(!b)cards.forEach((text,j)=>overlay.add(<Rect y={-100+j*75} width={520} height={63} fill={P.background} stroke={P.line} lineWidth={2}><Txt text={text} fontFamily={P.font} fontSize={25} fill={P.ink}/></Rect>));
   overlay.opacity(()=>1-ramp(t(),.48,.62));
   if(b)world.add(<Txt x={220} y={-90} text={'가보고 싶은 곳'} fontFamily={P.font} fontSize={23} fill={P.blue}/>);
  }
  if(index===1){
   block(world,-65,110,70,12,P.yellow);
   world.add(<Line points={[[-205,125],[-65,125],[195,125]]} stroke={P.blue} lineWidth={3} endArrow end={()=>ramp(t(),.3,.7)}/>);
  }
  if(index===2){
   const ring=new Rect({x:gateX+8,y:15,width:145,height:203,stroke:P.blue,lineWidth:3});world.add(ring);
   ring.opacity(()=>b?ramp(t(),.4,.65):0);
   if(!b)for(const x of [-105,15,135])world.add(<Circle x={x} y={-10} size={75} stroke={P.blue} lineWidth={2} opacity={()=>ramp(t(),.4,.65)}/>);
  }
  if(index===4){
   actor.x(()=>t()<.55?lerp(-270,-100,ramp(t(),.14,.38)):lerp(-100,280,ramp(t(),.65,.92)));
   block(world,-100,110,80,10,P.yellow);
   gate.add(<Rect y={110} offset={[0,1]} width={74} height={()=>145*(1-ramp(t(),.45,.61))} fill={P.blue}/>);
   panel.add(<Txt y={209} text={()=>t()<.42?'스위치에 접근':t()<.64?(b?'문이 열리는 결과 확인':'문 반응은 프레임 밖'):'다음 행동의 근거는?'} fontFamily={P.font} fontSize={26} fill={P.ink}/>);
   if(!b)frame.add(<Txt x={300} y={-108} text={'문 →'} fontFamily={P.font} fontSize={24} fill={P.muted}/>);
  }
  if(index===5){
   gate.opacity(.25);
   const zone=new Line({points:[[-40,112],[275,112],[335,57],[20,57]],closed:true,fill:b?P.blueLight:P.panel});world.add(zone);actor.moveToTop();
   actor.x(()=>t()<.62?lerp(-270,45,ramp(t(),.17,.55)):lerp(45,-150,ramp(t(),.72,.92)));
   frame.add(<>
    <Rect x={-240} y={-100} width={175} height={20} fill={P.panel}/>
    <Rect x={-327} y={-100} offset={[-1,0]} width={()=>175-65*ramp(t(),.48,.62)} height={20} fill={P.blue}/>
    <Txt x={-240} y={-137} text={'상태'} fontFamily={P.font} fontSize={20} fill={P.muted}/>
   </>);
   if(b)frame.add(<>
    <Txt x={110} y={-95} text={'위험 구역'} fontFamily={P.font} fontSize={25} fill={P.blue}/>
    <Line points={[[110,-70],[110,45]]} stroke={P.blue} lineWidth={2} endArrow/>
    <Txt x={100} y={-130} text={()=>t()>.48?'원인 → 상태 변화':'진입 전 단서'} fontFamily={P.font} fontSize={22} fill={P.ink}/>
   </>);
  }
  if(index===6){
   const cards=['움직여 살펴보기','가까운 대상 조사','문 너머로 이동'];
   cards.forEach((text,j)=>{
    const card=new Rect({x:0,y:-117+j*65,width:550,height:55,fill:P.background,stroke:P.line,lineWidth:2});frame.add(card);
    card.add(<Txt text={text} fontFamily={P.font} fontSize={24} fill={P.ink}/>);
    card.opacity(()=>b?(j===0?1-ramp(t(),.27,.33):j===1?ramp(t(),.34,.4)*(1-ramp(t(),.59,.65)):ramp(t(),.66,.72)):1-ramp(t(),.68,.77));
   });
  }
  if(index===7){
   gate.x(100);actor.x(()=>lerp(-270,100,ramp(t(),.15,.57)));
   world.add(<Txt x={105} y={-100} text={()=>t()>.58?'첫 목표 도착':'첫 목표'} fontFamily={P.font} fontSize={23} fill={P.ink}/>);
   const next=block(world,295,76,36,85,P.blue);next.opacity(()=>b?ramp(t(),.63,.75):0);
   if(b)world.add(<><Line points={[[135,130],[290,102]]} stroke={P.blue} lineWidth={3} endArrow end={()=>ramp(t(),.7,.86)}/><Txt x={282} y={-85} text={'다음 관심사'} opacity={()=>ramp(t(),.73,.83)} fontFamily={P.font} fontSize={22} fill={P.blue}/></>);
  }
  if(index!==4)panel.add(<Txt y={223} width={730} textWrap textAlign={'center'} text={b?s.designComparison.after:s.designComparison.before} fontFamily={P.font} fontSize={26} lineHeight={37} fill={P.ink}/>);
 }
 yield* tween(duration,tick=>t(tick));
}

export function* comparisonScene(view:View2D,index:number){
 const s=plan.scenes[index];view.fill(P.background);
 view.add(<>
  <Txt x={-864} y={-477} offset={[-1,0]} text={'GAME DESIGN · 첫 플레이 장면의 설계'} fontFamily={P.font} fontSize={24} fill={P.muted}/>
  <Txt x={840} y={-477} offset={[1,0]} text={s.id+' / 08'} fontFamily={P.font} fontSize={24} fill={P.muted}/>
  <Txt x={-864} y={-394} offset={[-1,0]} text={s.title} fontFamily={P.font} fontSize={48} fill={P.ink}/>
  <Rect y={405} width={1728} height={90} fill={P.panel}><Txt text={s.key} fontFamily={P.font} fontSize={32} fill={P.ink}/></Rect>
  <Txt y={492} text={'2.5D 설계 비교 모음 · 무음 검토본 · 야숨 실제 영상/내레이션/BGM 미포함'} fontFamily={P.font} fontSize={22} fill={P.muted}/>
 </>);
 const area=new Node({});view.add(area);
 yield* designComparison(area,index,SEGMENT_SECONDS);
}
