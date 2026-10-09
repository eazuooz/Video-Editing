import {Line,Node,Txt,View2D} from '@motion-canvas/2d';
import {createSignal,linear} from '@motion-canvas/core';
import {PAPER as P} from '../../styles/research-paper';
import {heading} from '../../shared/depth-diagrams';

type V3=[number,number,number];
type Value=number|(()=>number);
export type Timing={durationSeconds:number;paragraphStarts:number[];measured:boolean;timeOffsetSeconds?:number;visibleStartSeconds?:number;animationStarts?:number[];};
const v=(x:Value)=>typeof x==='function'?x():x;
const smooth=(x:number)=>{const a=Math.min(1,Math.max(0,x));return a*a*(3-2*a);};
const alongRoute=(points:V3[],progress:number):[number,number]=>{const lengths=points.slice(1).map((a,i)=>Math.hypot(a[0]-points[i][0],a[1]-points[i][1]));let left=Math.max(0,Math.min(1,progress))*lengths.reduce((a,b)=>a+b,0);for(let i=0;i<lengths.length;i++){if(left<=lengths[i]||i===lengths.length-1){const f=left/lengths[i];return[points[i][0]+(points[i+1][0]-points[i][0])*f,points[i][1]+(points[i+1][1]-points[i][1])*f];}left-=lengths[i];}return[points[0][0],points[0][1]];};
const shade=(c:string,k:number)=>'#'+[1,3,5].map(i=>Math.round(parseInt(c.slice(i,i+2),16)*k).toString(16).padStart(2,'0')).join('');

/** XYZ geometry with camera yaw and depth-dependent perspective. These are
 * explanation props, never playable source footage or actual-game quota. */
function space(yaw:()=>number){
 const rotated=(x:Value,y:Value)=>{const a=yaw()*Math.PI/180;return [v(x)*Math.cos(a)-v(y)*Math.sin(a),v(x)*Math.sin(a)+v(y)*Math.cos(a)] as [number,number];};
 const point=(x:Value,y:Value,z:Value=0):[number,number]=>{
  const [X,Y]=rotated(x,y),q=1450/(1450-Y*.34);
  return [.77*q*X,92+.77*q*(Y*.47-v(z))];
 };
 const polygon=(pts:()=>V3[],color:string,stroke:string=P.line)=><Line points={()=>pts().map(p=>point(...p))} closed fill={color} stroke={stroke} lineWidth={1.5}/>;
 const box=(x:Value,y:Value,z:Value,w:number,d:number,h:Value,color:string)=>{
  const p=(a:number,b:number,c:Value):V3=>[v(x)+a,v(y)+b,v(z)+v(c)];
  return <Node>
   {polygon(()=>[p(-w/2,d/2,0),p(w/2,d/2,0),p(w/2,d/2,h),p(-w/2,d/2,h)],shade(color,.82))}
   {polygon(()=>[p(w/2,-d/2,0),p(w/2,d/2,0),p(w/2,d/2,h),p(w/2,-d/2,h)],shade(color,.7))}
   {polygon(()=>[p(-w/2,-d/2,h),p(w/2,-d/2,h),p(w/2,d/2,h),p(-w/2,d/2,h)],color)}
  </Node>;
 };
 const layer=(x:Value,y:Value,node:Node)=>{node.zIndex(()=>rotated(x,y)[1]);return node;};
 // Increasing camera-space-Y is nearer; its larger geometry occludes far props.
 const solid=(x:Value,y:Value,z:Value,w:number,d:number,h:Value,color:string)=>layer(x,y,new Node({children:box(x,y,z,w,d,h,color)}));
 // Diagram annotations occupy a separate baseline below the projected solids.
 // White identity marks stay on the projected actor/token faces.
 const label=(text:string,x:Value,y:Value,z:Value=0,size=30,color:string=P.ink)=><Txt text={text} position={()=>color===P.ink?[point(x,y,z)[0],335]:point(x,y,z)} fill={color} fontFamily={P.font} fontSize={size} fontWeight={600}/>;
 // Ground paths sit above the floor and below every solid: a route behind a
 // rock must not be painted across its front face. Elevated comparison arrows
 // retain their camera-space depth with the other projected props.
 const path=(pts:()=>V3[],color:string=P.blue,progress:Value=1,dash:number[]=[])=> <Line zIndex={()=>{const p=pts();return p.every(a=>a[2]<=60)?-4800:p.reduce((n,a)=>n+rotated(a[0],a[1])[1],0)/p.length;}} points={()=>pts().map(p=>point(...p))} stroke={color} lineWidth={5} endArrow arrowSize={17} end={()=>v(progress)} lineDash={dash}/>;
 const actor=(x:Value,y:Value,col:string,mark='●',z:Value=30)=>layer(x,y,new Node({children:[
   box(x,y,z,62,48,76,col),box(x,y,()=>v(z)+76,70,56,44,'#f0e7d7'),
   label(mark,x,()=>v(y)+26,()=>v(z)+43,29,'#ffffff')]}));
 const floor=(x:number,y=0,w=630,d=550,color='#e7edf1')=><Node zIndex={-5000}>{box(x,y,0,w,d,30,color)}</Node>;
 const ring=(x:Value,y:Value,r:Value,color='#d8e8d1')=><Node zIndex={-4900}>{polygon(()=>Array.from({length:48},(_,i)=>[v(x)+v(r)*Math.cos(i*Math.PI/24),v(y)+v(r)*Math.sin(i*Math.PI/24),31] as V3),color,P.green)}</Node>;
 return {point,polygon,box,solid,label,path,actor,floor,ring,layer};
}

const titles:Record<string,[string,string]>={
 '01-overview':['익숙한 장르에서 새 작품을 고를 이유','경기장 → 채굴 경로 → 함께 하는 플레이'],
 '02-familiar-action':['비슷한 행동은 출발점','같은 이동과 공격에 어떤 목적과 상황을 연결할까요?'],
 '03-patterns-not-ranking':['무기 패턴을 한 줄 순위로 줄이지 않기','다른 공간과 판단 · 실제 성능의 순위가 아닌 설명용 비교'],
 '04-mining-route':['이동에 채굴이라는 목적이 붙을 때','피하기 / 목적지에 접근하기 · 지형을 읽는 이유'],
 '05-route-under-pressure':['같은 화면에서 두 목적을 읽기','원하는 곳에 가는 방향과 위험에서 떨어지는 방향'],
 '06-follow-the-space':['바위와 적 사이에서 무엇을 보는가','현재 위치 · 다가오는 대상 · 통과할 틈'],
 '07-purpose-combination':['익숙한 행동 위에 관계를 쌓기','아래층 행동과 위층 목적·공간의 연결'],
 '08-world-and-route':['공간과 분위기도 플레이에 연결하기','색과 소재의 변화 / 공간을 읽으며 움직이는 관계'],
 '09-combination-in-motion':['목적지와 좁은 길을 연결해서 보기','목적지에 도착하기 전과 도착한 뒤'],
 '10-playing-together':['함께 한다는 또 하나의 매력','혼자 집중하기와 같은 공간을 함께 보기'],
 '11-several-appeals':['모두에게 더 좋은 게임 대신','여러 매력의 조합 · 게임의 수치나 인기 순위가 아닙니다'],
 '12-check-your-reason':['내 게임을 고를 이유 한 문장','익숙한 행동 × 상황 → 만들고 싶은 경험'],
 '13-conclusion':['익숙함에서 자기 경험으로','행동 하나와 그 행동을 다르게 느끼게 할 상황 하나'],
 '14-corridor-pursuit':['캐릭터와 추격자를 따로 따라가기','이동하는 대상 · 바위 경계 · 통과할 틈'],
 '15-corridor-to-open':['좁은 길 다음에는 무엇을 볼까요?','같은 이동과 달라지는 주변 공간'],
 '16-effects-and-position':['경로와 공격 방향을 따로 보기','캐릭터 위치와 주변 효과를 구별하는 설명용 공간'],
 '17-rock-and-route':['가는 동안 읽을 대상도 설계하기','목적지 + 주변 바위 + 접근하는 대상'],
 '18-target-and-effects':['대상과 효과는 서로 다른 관찰점','같은 색으로 묶지 않고 위치와 거리를 보기'],
 '19-visible-destination':['방향 표시와 도착할 공간','목표가 생겨도 주변 관계는 계속 바뀝니다'],
 '20-moving-relationships':['선을 보는 것과 대상을 보는 것','같은 색보다 모양 · 위치 · 방향의 관계'],
 '21-read-before-ranking':['한 줄 순위 대신 행동과 상황','이 조합이 새 작품을 고를 이유일까요?'],
 '23-mining-and-pursuit':['접근할 목적과 피할 대상','광물에 다가가기와 위험에서 떨어지기를 같은 공간에서 보기'],
 '24-destination-and-danger':['원 안에 들어가도 주변은 남는다','목적지 도착과 주변 대상 읽기는 이어지는 관찰입니다'],
 '25-gap-during-pursuit':['캐릭터와 지나갈 틈을 함께 보기','추격자의 위치 · 가리는 바위 · 통과할 공간'],
};

export function* similarExplanation(view:View2D,id:string,timing:Timing){
 if(!titles[id]||timing.durationSeconds<=0||timing.paragraphStarts.length<2)throw Error('Independent timing missing');
 const begin=timing.timeOffsetSeconds??0,end=begin+timing.durationSeconds;
 const t=createSignal(begin),u=(i:number,d=2.5)=>{const a=timing.animationStarts?.[i]??timing.paragraphStarts[i]??timing.paragraphStarts[timing.paragraphStarts.length-1];return smooth((t()-a)/Math.max(.3,Math.min(d,end-a-.1)));};
 const orbit=()=>Math.max(0,Math.min(t()-(timing.visibleStartSeconds??0),7))/7;
 const s=space(()=>15+9*smooth(orbit()));
 const world=new Node({scale:.90});view.fill(P.background);view.add(heading(id.slice(0,2),...titles[id],'비슷한 게임의 고유한 매력'));view.add(world);
 const note=(text:string,color:string=P.muted)=>view.add(<Txt text={text} x={0} y={342} fill={color} fontFamily={P.font} fontSize={28} fontWeight={600}/>);
 const token=(x:Value,y:Value,z:Value,col:string,mark:string)=>world.add(s.layer(x,y,new Node({children:[s.box(x,y,z,94,84,58,col),s.label(mark,x,()=>v(y)+45,()=>v(z)+27,32,'#ffffff')]})));
 const pillar=(x:number,y:number,w=100,d=100,h:Value=160,col='#bac7d1')=>world.add(s.solid(x,y,30,w,d,h,col));
 const flag=(x:number,y:number,base=30)=>{world.add(s.solid(x,y,base,10,10,140,'#818c95'));world.add(s.polygon(()=>[[x+6,y,base+140],[x+100,y,base+114],[x+6,y,base+83]],P.green,P.green));};
 const arena=(x:number,w=640,d=620,color='#e7edf1')=>world.add(s.floor(x,0,w,d,color));
 const walk=(x:Value,y:Value,col:string=P.blue,z:Value=30,mark='●')=>world.add(s.actor(x,y,col,mark,z));
 const arrow=(pts:()=>V3[],col:string=P.blue,p:Value=1,dash:number[]=[])=>world.add(s.path(pts,col,p,dash));

 if(id==='01-overview'){
  [-620,0,620].forEach((x,i)=>{arena(x,480,470);pillar(x,0,180,160,80,['#bdd1e6','#c8dcc0','#e8d3bc'][i]);world.add(s.label(['경기장','채굴 경로','함께 하기'][i],x,-175,30,34));});
  walk(-620,10,P.blue,110);pillar(0,100,120,95,160);flag(110,-85);walk(580,30,P.green,110);walk(715,115,P.red);
  arrow(()=>[[-390,0,120],[-215,0,120]],P.blue,()=>u(1));arrow(()=>[[240,0,120],[420,0,120]],P.green,()=>u(2));
  token(()=>-620+620*u(1)+620*u(2),()=>-60+60*Math.sin(Math.PI*u(1)),()=>145+65*u(0)+60*Math.sin(Math.PI*u(2)),P.blue,'?');
  note('익숙한 행동을 둘러싼 경험의 조합을 살펴봅니다');
 }else if(id==='02-familiar-action'){
  [-470,470].forEach(arenaX=>arena(arenaX));
  [-470,470].forEach((x,i)=>{const route:V3[]=[[x-180,90,35],[x+80,100,35],[x+210,-170,35]];walk(()=>alongRoute(route,u(i))[0],()=>alongRoute(route,u(i))[1]);arrow(()=>route,P.blue,()=>u(i));[[x-190,-190],[x+220,130],[x+70,-70]].forEach(([a,b])=>pillar(a,b,65,65,78,'#dfb3ab'));});
  flag(635,-160);world.add(s.label('같은 행동',-470,-270,35,35));world.add(s.label('다른 목적과 상황',470,-270,35,35));
  token(()=>-470+940*u(3),210,()=>60+100*Math.sin(Math.PI*u(3)),P.green,'?');note('공통 동작만으로 새 작품의 선택 이유가 완성되지는 않습니다');
 }else if(id==='03-patterns-not-ranking'){
  [-440,440].forEach(x=>arena(x,650,640));walk(-630,140);walk(430,60,P.green);
  pillar(-200,-180,80,80,100,'#dfb3ab');arrow(()=>[[-600,100,140],[-220,-130,140]],P.blue,()=>u(0));
  [[250,70],[650,70],[430,-160]].forEach(([x,y])=>pillar(x,y,75,75,()=>80+55*u(1),'#bdd5b6'));
  [0,1,2].forEach(i=>arrow(()=>[[430,60,110],[430+Math.cos(i*2.094)*200,60+Math.sin(i*2.094)*200,110]],P.green,()=>u(1)));
  world.add(s.label('먼 공간을 보기',-440,-275,35,34));world.add(s.label('가까운 위험을 관리',440,-275,35,34));
  note('강함의 순위가 아니라, 살펴볼 공간과 판단의 차이');
 }else if(id==='04-mining-route'){
  arena(0,1450,730);[-370,0,370].forEach((x,i)=>pillar(x,35,120,140,150+i*12));
  flag(530,-210);world.add(s.ring(520,-210,110));
  const route:V3[]=[[-590,150,34],[-200,160,34],[-200,-130,34],[510,-210,34]];walk(()=>alongRoute(route,u(1))[0],()=>alongRoute(route,u(1))[1]);
  arrow(()=>route,P.blue,()=>u(1));
  world.add(<Node opacity={()=>1-u(2)}>{s.solid(490,-210,30,70,70,95,'#c0dbb2')}</Node>);
  token(()=>490-180*u(2),()=>-210+70*u(2),()=>100+70*Math.sin(Math.PI*u(2)),P.green,'◆');
  note('이동의 목적을 목적지와 주변 공간의 관계로 설명하기');
 }else if(id==='05-route-under-pressure'){
  arena(0,1380,700);pillar(-160,20,170,200,190);pillar(210,65,140,170,150);flag(550,-230);
  const route:V3[]=[[-540,170,35],[-350,-150,35],[500,-220,35]];
  world.add(s.ring(-390,200,170,'#ead3cf'));walk(()=>alongRoute(route,u(2))[0],()=>alongRoute(route,u(2))[1]);
  walk(()=>-450+390*u(0),()=>270-110*u(0),P.red);
  arrow(()=>route,P.green,()=>u(2));
  arrow(()=>[[-500,230,38],[-180,270,38],[240,240,38]],P.blue,()=>u(2),[13,8]);
  world.add(s.label('목적지',530,-270,70,33));world.add(s.label('위험에서 떨어지는 방향',-360,265,90,30));note('도착하려는 방향과 피하려는 방향이 달라질 수 있습니다');
  token(()=>-370+870*u(3,5),()=>140-260*u(3,5),()=>70+90*Math.sin(Math.PI*u(3,5)),P.green,'?');
 }else if(id==='06-follow-the-space'){
  arena(0,1450,650);[[-360,80],[0,-60],[350,85]].forEach(([x,y])=>pillar(x,y,200,200,220));
  // Move around solid footprints rather than interpolating through a rock.
  const route:V3[]=[[-650,-200,35],[-360,-150,35],[-160,-130,35],[-160,220,35],[510,220,35],[570,-200,35]];
  walk(()=>alongRoute(route,u(1))[0],()=>alongRoute(route,u(1))[1]);
  const chasing:V3[]=[[-780,-200,35],...route];
  walk(()=>alongRoute(chasing,u(1)*.82)[0],()=>alongRoute(chasing,u(1)*.82)[1],P.red);
  arrow(()=>route,P.blue,()=>u(1));flag(585,-190);note('높은 앞쪽 바위가 뒤의 움직임을 가리고, 틈에서는 다시 드러납니다');
 }else if(id==='07-purpose-combination'){
  arena(0,1250,750);[-450,450].forEach(x=>pillar(x,80,65,65,280,'#b6c3cb'));
  world.add(<Node zIndex={-1000}>{s.box(0,50,260,1120,560,45,'#d2dfc9')}</Node>);
  walk(()=>-400+800*u(0),180);walk(()=>-320+640*u(1),-80,P.green,305);flag(405,-90,305);
  arrow(()=>[[-400,180,40],[350,180,40]],P.blue,()=>u(0));arrow(()=>[[-290,-80,308],[320,-80,308]],P.green,()=>u(1));
  arrow(()=>[[-320,180,130],[-320,50,285]],P.blue,()=>u(2));arrow(()=>[[320,180,130],[320,50,285]],P.green,()=>u(3));
  world.add(s.label('이동 · 공격',-340,330,35,34));world.add(s.label('목적 · 공간',340,-290,305,34));note('층을 늘리는 숫자보다, 행동이 필요한 이유를 연결하기');
 }else if(id==='08-world-and-route'){
  [-440,440].forEach((x,i)=>{arena(x,630,610,i===0?'#d6e4ef':'#efd9c2');pillar(x,-10,145,145,180,i===0?'#b9cbd9':'#d2aa86');const route:V3[]=[[x-240,150,35],[x+100,180,35],[x+240,-130,35]];walk(()=>alongRoute(route,u(2))[0],()=>alongRoute(route,u(2))[1]);flag(x+215,-130);});
  arrow(()=>[[-680,150,35],[-340,180,35],[-200,-130,35]],P.blue,()=>u(2));
  arrow(()=>[[200,150,35],[540,180,35],[660,-130,35]],P.green,()=>u(2));
  world.add(s.label('소재와 색',-440,-265,35,33));world.add(s.label('공간을 읽는 행동',440,-265,35,33));note('설명용 공간 비교 · 실제 용암 피해나 제작 의도를 나타내지 않습니다');
  token(()=>-440+880*u(3,5),245,()=>65+110*Math.sin(Math.PI*u(3,5)),P.green,'?');
 }else if(id==='09-combination-in-motion'){
  [-455,455].forEach(x=>{arena(x,635,630);pillar(x-80,90,150,130,180);flag(x+155,-150);world.add(s.ring(x+130,-140,125));});
  const route:V3[]=[[-720,190,38],[-720,-40,38],[-305,-150,38]];walk(()=>alongRoute(route,u(0))[0],()=>alongRoute(route,u(0))[1]);walk(570,-120,P.green);walk(()=>730-180*u(1),()=>180-220*u(1),P.red);
  arrow(()=>route,P.blue,()=>u(0));
  arrow(()=>[[600,-130,135],[670,60,135]],P.green,()=>u(3));world.add(s.label('도착하기 전',-455,-275,40,33));world.add(s.label('도착한 뒤',455,-275,40,33));
  note('목적지 표시와 함께, 그 주변에서 읽을 대상을 설계');
 }else if(id==='10-playing-together'){
  arena(-480,580,620);arena(430,760,680);walk(()=>-640+250*u(0),()=>-100+180*u(0));
  const colors=[P.blue,P.green,P.red];[[180,-80],[470,160],[650,-160]].forEach(([x,y],i)=>{walk(()=>x+90*Math.sin(u(1)*Math.PI+i),()=>y+70*u(1),colors[i]);arrow(()=>[[x,y,35],[x-150,y-95,35]],colors[i],()=>u(1));});
  pillar(430,-20,85,85,120,'#d3b8b3');world.add(s.label('혼자 집중',-480,-285,35,34));world.add(s.label('같은 공간을 함께 보기',430,-285,35,34));
  token(()=>-480+910*u(3),245,()=>70+90*Math.sin(Math.PI*u(3)),P.green,'?');note('함께 하기의 매력은 피해량의 크기와 다른 방향입니다');
 }else if(id==='11-several-appeals'){
  arena(0,1420,670);[-480,0,480].forEach((x,i)=>{pillar(x,0,245,200,()=>80+[75,125,55][i]*u(0),['#bdd1e6','#c8dcc0','#e8d3bc'][i]);world.add(s.label(['익숙한 전투','공간과 목적','함께 하는 경험'][i],x,-210,40,32));});
  token(()=>-480+480*u(1)+480*u(3),-10,()=>300+45*Math.sin(Math.PI*u(1)),P.blue,'★');
  arrow(()=>[[-340,30,255],[-145,30,255]],P.blue,()=>u(1));arrow(()=>[[145,30,255],[335,30,255]],P.green,()=>u(3));
  note('높이는 설명용 강조 · 게임 수치·매출·선호도를 측정한 그래프가 아닙니다');
 }else if(id==='12-check-your-reason'){
  [-610,0,610].forEach((x,i)=>{arena(x,475,520);pillar(x,0,190,170,100,['#bdd1e6','#c8dcc0','#e8d3bc'][i]);world.add(s.label(['행동','상황','경험'][i],x,-180,35,38));});
  walk(-610,0,P.blue,130);pillar(0,110,105,80,170);flag(100,-90);walk(610,50,P.green,130);
  arrow(()=>[[-375,0,160],[-220,0,160]],P.blue,()=>u(1));arrow(()=>[[245,0,160],[420,0,160]],P.green,()=>u(2));
  token(()=>-610+610*u(1)+610*u(2)-220*u(3,5),()=>190-150*u(3,5),()=>65+100*Math.sin(Math.PI*u(2))+110*Math.sin(Math.PI*u(3,5)),P.blue,'?');
  arrow(()=>[[610,50,190],[390,-150,190]],P.green,()=>u(3,5),[13,8]);note('어떤 행동을, 어떤 상황에서, 어떤 경험으로 연결할까요?');
 }else if(id==='13-conclusion'){
  arena(0,1420,660);[-450,0,450].forEach((x,i)=>pillar(x,0,195,170,115,['#bdd1e6','#c8dcc0','#e8d3bc'][i]));
  const x=()=>-450+450*u(1)+450*u(2);walk(x,55,P.blue,()=>145+70*Math.sin(Math.PI*u(1)));
  token(()=>-450+900*u(3,6),205,()=>70+110*Math.sin(Math.PI*u(3,6)),P.green,'?');
  flag(450,-145);arrow(()=>[[-290,0,150],[-130,0,150]],P.blue,()=>u(1));arrow(()=>[[145,0,150],[310,0,150]],P.green,()=>u(2));
  world.add(s.label('익숙한 행동',-450,-205,35,33));world.add(s.label('고유한 상황',0,-205,35,33));world.add(s.label('내 작품의 경험',450,-205,35,33));
  note('행동과 상황을 적고, 직접 구현하며 점검해 보세요');
 }else if(id==='14-corridor-pursuit'){
  arena(0,1430,660);[[-280,80],[30,-70],[350,85]].forEach(([x,y])=>pillar(x,y,180,190,210));
  const route:V3[]=[[-630,-200,35],[-280,-140,35],[-150,-160,35],[-150,225,35],[565,225,35]];
  walk(()=>alongRoute(route,u(0,5))[0],()=>alongRoute(route,u(0,5))[1]);
  const pursuit:V3[]=[[-780,-200,35],...route];
  walk(()=>alongRoute(pursuit,u(0,5)*.74)[0],()=>alongRoute(pursuit,u(0,5)*.74)[1],P.green);
  arrow(()=>route,P.blue,()=>u(0,5));arrow(()=>[[-150,225,40],[565,225,40]],P.green,()=>u(1));
  note('추격자와 통과할 공간을 함께 읽는 설명용 경로');
 }else if(id==='15-corridor-to-open'){
  arena(-480,570,600);arena(400,850,660);
  world.add(s.floor(-120,-150,320,220));
  [-670,-290].forEach(x=>pillar(x,0,130,340,205));
  const route:V3[]=[[-500,220,35],[-500,-150,35],[100,-150,35],[610,140,35]];
  walk(()=>alongRoute(route,u(0,6))[0],()=>alongRoute(route,u(0,6))[1]);arrow(()=>route,P.blue,()=>u(0,6));
  walk(()=>100+280*u(1),()=>240-150*u(1),P.green);
  world.add(s.label('좁은 틈',-480,-300,40,33));world.add(s.label('열린 공간',400,-300,40,33));
  note('공격의 우열보다, 이동하며 살펴볼 주변 공간을 비교');
 }else if(id==='16-effects-and-position'){
  arena(0,1380,670);pillar(-100,-50,180,220,200);
  const route:V3[]=[[-580,170,35],[-250,190,35],[400,170,35],[560,-210,35]];
  walk(()=>alongRoute(route,u(0,5))[0],()=>alongRoute(route,u(0,5))[1]);arrow(()=>route,P.blue,()=>u(0,5));
  [[-420,-170],[190,-130]].forEach(([x,y])=>{pillar(x,y,65,65,95,'#e8ba76');arrow(()=>[[x,y,135],[x+180,y-120,135]],'#ba741d',()=>u(1));});
  world.add(s.label('이동 경로',-370,200,40,33));world.add(s.label('효과의 방향',310,-200,135,33));
  note('파란 이동 경로와 주황 효과 방향을 분리한 설명');
 }else if(id==='17-rock-and-route'){
  arena(0,1420,710);pillar(-220,10,210,230,210);pillar(250,50,150,180,165);flag(550,-220);
  const route:V3[]=[[-590,175,35],[-390,-165,35],[490,-220,35]];
  walk(()=>alongRoute(route,u(0,5))[0],()=>alongRoute(route,u(0,5))[1]);arrow(()=>route,P.blue,()=>u(0,5));
  walk(()=>540-180*u(1),()=>240-100*u(1),P.red);arrow(()=>[[540,240,38],[360,140,38]],P.red,()=>u(1));
  note('목적지에 가는 길과, 그 길 주변의 대상을 연결');
 }else if(id==='18-target-and-effects'){
  arena(0,1350,650);pillar(40,-60,170,170,185);walk(()=>-500+180*u(0),()=>165-80*u(0));
  world.add(s.solid(()=>440-190*u(1),()=>80-140*u(1),30,135,110,150,P.green));
  // A visible bar identifies the illustrative target; it is not a weapon token.
  world.add(s.layer(()=>440-190*u(1),()=>80-140*u(1),new Line({
   points:()=>[s.point(370-190*u(1),80-140*u(1),225),s.point(510-190*u(1),80-140*u(1),225)],
   stroke:P.red,lineWidth:9,
  })));
  arrow(()=>[[-350,80,140],[-120,-180,140]],'#ba741d',()=>u(0));
  arrow(()=>[[-300,90,38],[250,-35,38]],P.blue,()=>u(1),[13,8]);
  world.add(s.label('공격 효과',-420,-220,140,32));world.add(s.label('체력 막대가 있는 대상',400,-170,225,30));
  note('효과와 대상의 위치를 나누어 보는 도식 · 피해량과 결과는 미표시');
 }else if(id==='19-visible-destination'){
  arena(0,1420,710);pillar(445,-140,230,220,260,'#d2c4ae');pillar(445,-140,140,140,()=>300+20*u(1),'#bdd1e6');
  const route:V3[]=[[-560,170,35],[-260,60,35],[265,-40,35]];
  walk(()=>alongRoute(route,u(0,5))[0],()=>alongRoute(route,u(0,5))[1]);arrow(()=>route,P.green,()=>u(0,5));
  walk(()=>-80+220*u(1),230,P.red);world.add(s.ring(380,-90,160));
  note('방향을 따라 접근하는 관계 · 탈출이나 승리 결과를 그리지 않습니다');
 }else if(id==='20-moving-relationships'){
  arena(0,1400,650);pillar(-90,-20,190,190,200);
  const route:V3[]=[[-600,180,35],[-300,200,35],[510,160,35]];
  walk(()=>alongRoute(route,u(0,5))[0],()=>alongRoute(route,u(0,5))[1]);arrow(()=>route,P.blue,()=>u(0,5));
  walk(()=>430-200*u(1),()=>-170+150*u(1),P.green);
  arrow(()=>[[-410,-220,35],[450,230,35]],P.green,()=>u(1));
  world.add(s.label('대상의 위치',420,-250,40,33));world.add(s.label('선의 방향',-430,-250,35,33));
  note('같은 초록색이어도 대상과 선은 서로 다른 관찰점');
 }else if(id==='21-read-before-ranking'){
  [-520,0,520].forEach((x,i)=>{arena(x,430,500);pillar(x,0,190,170,100,['#bdd1e6','#c8dcc0','#e8d3bc'][i]);
   world.add(s.label(['행동','상황','선택할 이유?'][i],x,-180,40,34));});
  walk(-520,0,P.blue,130);pillar(0,120,110,75,160);flag(100,-80);
  arrow(()=>[[-310,0,160],[-195,0,160]],P.blue,()=>u(0));arrow(()=>[[200,0,160],[315,0,160]],P.green,()=>u(1));
  token(()=>-520+1040*u(1,4),180,()=>80+150*Math.sin(Math.PI*u(1,4)),P.green,'?');
  note('실제 행동과 상황에서 출발해, 새로운 선택 이유를 질문');
 }else if(id==='23-mining-and-pursuit'){
  arena(0,1410,680);pillar(-120,70,180,170,185);pillar(270,-20,160,190,170);
  const route:V3[]=[[-580,-180,35],[-200,-175,35],[450,-150,35]];
  walk(()=>alongRoute(route,u(0,6))[0],()=>alongRoute(route,u(0,6))[1]);
  arrow(()=>route,P.blue,()=>u(0,6));
  world.add(<Node opacity={()=>1-u(0,6)}>{s.solid(485,-145,30,70,70,100,'#e5c676')}</Node>);
  token(()=>485-100*u(0,6),()=>-145+140*u(0,6),()=>85+75*Math.sin(Math.PI*u(0,6)),'#bf9127','◆');
  walk(()=>-630+370*u(1,5),()=>50-60*u(1,5),P.green);
  arrow(()=>[[-450,-170,40],[-320,-190,40],[250,-180,40]],P.green,()=>u(1,5));
  world.add(s.label('접근할 광물',475,-255,35,32));world.add(s.label('뒤따르는 대상',-440,230,35,32));
  note('같은 공간의 두 관계를 구분하는 설명용 도식');
 }else if(id==='24-destination-and-danger'){
  arena(0,1420,700);pillar(-180,65,190,210,195);pillar(220,155,155,155,165);
  world.add(s.ring(455,-150,155));flag(490,-185);
  const route:V3[]=[[-585,-170,35],[-350,-180,35],[420,-145,35]];
  walk(()=>alongRoute(route,u(0,6))[0],()=>alongRoute(route,u(0,6))[1]);arrow(()=>route,P.blue,()=>u(0,6));
  walk(()=>630-160*u(1,5),()=>160-180*u(1,5),P.red);
  walk(()=>120+190*u(1,5),()=>-250+65*u(1,5),P.green);
  arrow(()=>[[420,-145,145],[600,0,145]],P.green,()=>u(1,5));
  world.add(s.label('도착할 원',460,-320,40,33));world.add(s.label('주변 대상을 계속 보기',-330,230,40,32));
  note('원 안에 들어간 뒤에도 대상의 위치를 관찰 · 승리 결과는 미표시');
 }else if(id==='25-gap-during-pursuit'){
  arena(0,1440,700);pillar(-120,-30,235,190,235);pillar(205,185,195,195,200);
  const route:V3[]=[[-625,-180,35],[-340,-175,35],[-340,260,35],[570,270,35]];
  walk(()=>alongRoute(route,u(0,6))[0],()=>alongRoute(route,u(0,6))[1]);
  const pursuit:V3[]=[[-770,-190,35],...route];
  walk(()=>alongRoute(pursuit,u(0,6)*.75)[0],()=>alongRoute(pursuit,u(0,6)*.75)[1],P.green);
  arrow(()=>route,P.blue,()=>u(0,6));
  arrow(()=>[[-340,200,40],[70,270,40],[570,270,40]],P.green,()=>u(1,5));
  world.add(s.label('추격자',-535,-280,40,33));world.add(s.label('통과할 틈',175,315,40,33));
  note('앞쪽 바위는 뒤의 경로를 가리고, 틈에서는 움직임이 다시 드러납니다');
 }
 // Each yield advances one frame at the fixed 60 fps of this measured project.
 // Floating tween endpoints can add a frame to otherwise integral scene lengths.
 const measuredFrames=Math.round(timing.durationSeconds*60);
 for(let frame=0;frame<measuredFrames;frame++){
  t(begin+frame/60);
  yield;
 }
 t(end);
}
