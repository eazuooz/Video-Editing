import {makeScene2D,Node,Rect,Circle,Line,Txt} from '@motion-canvas/2d';
import {createSignal,tween} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';
const clamp=(v:number)=>Math.max(0,Math.min(1,v));
const phase=(t:number,a:number,b:number)=>{const v=clamp((t-a)/(b-a));return v*v*(3-2*v);};
const mix=(a:number,b:number,t:number)=>a+(b-a)*t;
export default makeScene2D(function*(view){
 view.fill(P.background);const t=createSignal(0);
 const press=()=>phase(t(),0.35,0.4),open=()=>phase(t(),0.43,0.57);
 const x=()=>t()<0.5?mix(-270,-95,phase(t(),0.08,0.32)):mix(-95,275,phase(t(),0.6,0.91));
 const moving=()=>((t()>0.08&&t()<0.32)||(t()>0.6&&t()<0.91));
 const bounce=()=>moving()?-Math.abs(Math.sin(t()*Math.PI*36))*5:0;
 view.add(<>
  <Txt x={-864} y={-477} offset={[-1,0]} text={'VISUAL STUDY 01 · 같은 동작, 다른 공간감'} fontFamily={P.font} fontSize={24} fill={P.muted}/>
  <Txt x={-864} y={-398} offset={[-1,0]} text={'내 행동이 길을 연다'} fontFamily={P.font} fontSize={56} fontWeight={700} fill={P.ink}/>
  <Txt x={-864} y={-325} offset={[-1,0]} text={'스위치 → 반응 확인 → 열린 문 통과'} fontFamily={P.font} fontSize={30} fill={P.muted}/>
  <Line points={[[0,-225],[0,282]]} stroke={P.line} lineWidth={2}/>
 </>);
 for(const iso of [false,true]){
  const area=new Node({x:iso?435:-435,y:30});view.add(area);
  area.add(<>
   <Txt y={-255} text={iso?'B · 2.5D 입체 도형':'A · 2D 평면 도형'} fontFamily={P.font} fontSize={36} fontWeight={600} fill={iso?P.blue:P.ink}/>
   <Txt y={-202} text={iso?'바닥 · 두께 · 가림 관계':'동작과 결과를 간결하게'} fontFamily={P.font} fontSize={25} fill={P.muted}/>
  </>);
  if(iso){
   area.add(<>
    <Line points={[[-352,110],[290,110],[352,57],[-290,57]]} closed fill={P.panel} stroke={P.line} lineWidth={2}/>
    <Line points={[[-352,110],[290,110],[290,142],[-352,142]]} closed fill={'#d9dee5'}/>
    <Line points={[[290,110],[352,57],[352,89],[290,142]]} closed fill={'#bcc6d3'}/>
   </>);
   for(let k=0;k<7;k++)area.add(<Line points={[[-330+k*96,110],[-268+k*96,57]]} stroke={'#dfe4eb'} lineWidth={1}/>);
  }else area.add(<Rect y={113} width={700} height={6} fill={P.line}/>);
  // Switch pad. Both views show identical press and gate timing.
  area.add(<Rect x={-95} y={107} width={100} height={16} fill={P.muted}/>);
  if(iso)area.add(<Line points={()=>[[-145,96+press()*7],[-45,96+press()*7],[-17,75+press()*7],[-117,75+press()*7]]} closed fill={()=>press()>.6?P.yellow:P.blueLight} stroke={P.blue} lineWidth={2}/>);
  else area.add(<Rect x={-95} y={()=>98+press()*8} width={82} height={16} fill={()=>press()>.6?P.yellow:P.blueLight} stroke={P.blue} lineWidth={2}/>);
  // Illustrated signal highlights the causal link, not a real in-game wire.
  area.add(<Line points={[[-75,154],[115,154],[115,128]]} stroke={P.blue} lineWidth={3} end={()=>phase(t(),0.39,0.46)} endArrow/>);
  area.add(<Txt x={-70} y={199} text={()=>t()<0.35?'스위치':t()<0.57?'입력 → 문 반응':'반응을 확인하고 이동'} fontFamily={P.font} fontSize={26} fill={P.ink}/>);
  // Front plane of doorway, gate retracts into the floor so it never crosses labels.
  const gateHeight=()=>170*(1-open());
  area.add(<>
   <Rect x={142} y={18} width={18} height={184} fill={'#8794a5'}/>
   <Rect x={234} y={18} width={18} height={184} fill={'#8794a5'}/>
   <Rect x={188} y={-78} width={110} height={20} fill={'#8794a5'}/>
   <Rect x={188} y={110} offset={[0,1]} width={74} height={gateHeight} fill={P.blue}/>
  </>);
  if(iso)area.add(<>
   <Line points={[[133,-88],[243,-88],[267,-109],[157,-109]]} closed fill={'#b8c3d2'}/>
   <Line points={[[243,-88],[267,-109],[267,89],[243,110]]} closed fill={'#65768d'}/>
   <Line points={()=>[[151,110-gateHeight()],[225,110-gateHeight()],[241,96-gateHeight()],[167,96-gateHeight()]]} closed opacity={()=>1-open()} fill={'#7195c5'}/>
  </>);
  area.add(<Txt x={192} y={-143} text={()=>open()>.98?'OPEN':'LOCKED'} fontFamily={P.mono} fontSize={24} fill={()=>open()>.98?P.blue:P.muted}/>);
  area.add(<Circle x={293} y={97} size={22} fill={P.yellow} opacity={()=>phase(t(),0.6,0.68)}/>);
  const actor=new Node({x,y:()=>110+bounce()});area.add(actor);
  if(iso)actor.add(<>
   <Circle x={14} y={5} width={75} height={18} fill={'#bac4d1'} opacity={0.5}/>
   <Line points={[[25,-66],[46,-84],[46,-18],[25,0]]} closed fill={'#234572'}/>
   <Line points={[[-25,-66],[25,-66],[46,-84],[-4,-84]]} closed fill={'#7195c5'}/>
  </>);
  actor.add(<Rect x={0} y={-33} width={50} height={66} fill={P.blue}/>);
  actor.add(<>
   <Circle x={-10} y={-47} size={7} fill={P.background}/><Circle x={10} y={-47} size={7} fill={P.background}/>
   <Line points={[[-8,-29],[8,-29]]} stroke={P.background} lineWidth={3}/>
  </>);
 }
 view.add(<>
  <Rect y={401} width={1728} height={90} fill={P.panel}/>
  <Txt y={401} text={()=>t()<0.35?'① 눈에 띄는 목표':t()<0.6?'② 조작 직후, 알아볼 수 있는 반응':'③ 배운 행동으로 다음 공간까지'} fontFamily={P.font} fontSize={35} fill={P.ink}/>
  <Txt y={487} text={'Motion Canvas · 직접 만든 설명 애니메이션 · 무음 스타일 샘플 / 실제 게임·물리 엔진 아님'} fontFamily={P.font} fontSize={22} fill={P.muted}/>
 </>);
 yield* tween(12,v=>t(v));
});
