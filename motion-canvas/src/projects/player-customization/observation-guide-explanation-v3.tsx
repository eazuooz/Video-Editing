import {Node,Txt,View2D} from '@motion-canvas/2d';
import {createSignal,linear} from '@motion-canvas/core';
import {depthSpace,heading,Value,val,V3} from '../../shared/depth-diagrams';
import {PAPER as P} from '../../styles/research-paper';
export type GuideTiming={durationSeconds:number;paragraphStarts:number[];measured:boolean};
const smooth=(x:number)=>{const q=Math.max(0,Math.min(1,x));return q*q*(3-2*q);};
const titles:Record<string,string[]>={
 '09-path-and-projectile-guide':['지나가는 경로와 보내는 방향','어느 공간을 바꾸는 선택인지 보여주기'],
 '10-origin-effect-target-guide':['시작 · 펼쳐지는 공간 · 대상','보이는 동작을 순서대로 연결하기'],
 '11-jade-ground-and-height-guide':['지면과 높이의 차이','확인할 위치 관계를 미리보기와 시험에 남기기'],
 '12-nearby-space-guide':['움직이는 중심과 가까운 대상','주변 효과와 대상의 상대 위치를 함께 보기'],
 '13-doorway-comparison-guide':['대상의 배치부터 비교하기','카메라 중심과 캐릭터 앞은 다릅니다'],
 '14-purpose-before-options-guide':['목적을 정한 뒤 후보 찾기','행동의 질문 → 후보 → 그 목적의 시험'],
 '15-task-and-result-guide':['돕는 시험과 닿는 시험','목적마다 확인할 대상과 완료 결과가 다릅니다'],
 '16-action-versus-expression-guide':['플레이 방식과 원하는 모습','행동의 시험과 외형의 미리보기 구분'],
};
export function* observationGuideExplanation(view:View2D,id:string,timing:GuideTiming){
 if(!titles[id]||!timing.measured||timing.paragraphStarts.length!==4)throw Error('Measured independent guide timing required before rendering');
 const t=createSignal(0),u=(p:number)=>smooth((t()-timing.paragraphStarts[p])/2.6);
 const s=depthSpace(()=>22+9*smooth(t()/7),[0,80],.71),world=new Node({});
 view.fill(P.background);view.add(heading(id.slice(0,2),titles[id][0],titles[id][1],'플레이어 커스터마이징'));view.add(world);
 const floor=(x=0,w=1570,d=650)=><Node zIndex={-1000}>{s.box(x,0,0,w,d,30,'#e4ebf0')}</Node>;
 const actor=(x:Value,y:Value,z:Value,col:string)=> <Node zIndex={()=>s.point(x,y,0)[1]}>{s.actor(x,y,col,'●',z)}</Node>;
 const token=(x:Value,y:Value,z:Value,col:string,symbol:string)=> <Node zIndex={()=>s.point(x,y,0)[1]}>{s.shadow(x,y)}{s.box(x,y,z,82,70,50,col)}{s.label(symbol,x,()=>val(y)+36,()=>val(z)+25,29,'#fff')}</Node>;
 const target=(x:number,y:number,p=2)=> <Node zIndex={()=>s.point(x,y,0)[1]}>{s.box(x,y,30,90,90,110,'#c5ced8')}<Node opacity={()=>u(p)}>{s.box(x,y,()=>30+35*u(p),90,90,110,P.green)}</Node></Node>;
 const ring=(x:Value,y:Value,r:Value)=> <Node zIndex={-900}>{s.polygon(()=>Array.from({length:48},(_,i)=>[val(x)+Math.cos(i*Math.PI/24)*val(r),val(y)+Math.sin(i*Math.PI/24)*val(r),34] as V3),'#d6e6cf',P.green)}</Node>;
 const label=(txt:string,x:number,y:number,col:string=P.ink)=><Txt text={txt} x={x} y={y} fill={col} fontFamily={P.font} fontSize={31} fontWeight={600}/>;
 if(id==='09-path-and-projectile-guide'){
  world.add(floor());world.add(actor(()=>-660+500*u(0)+190*u(3),-170,30,P.blue));world.add(s.path(()=>[[-710,-170,35],[-100,-170,35]],P.blue,()=>u(0)));
  [-390,-100].forEach(x=>world.add(target(x,-170,0)));world.add(actor(-500,170,30,P.green));world.add(s.path(()=>[[-100,-170,35],[155,-170,35]],P.blue,()=>u(3)));
  world.add(token(()=>-430+990*u(2),170,130,P.green,'▲'));world.add(s.path(()=>[[-420,170,132],[610,170,132]],P.green,()=>u(2)));world.add(target(635,170,2));
  world.add(label('지나가는 경로',-470,-200,P.blue));world.add(label('보내는 방향',435,-95,P.green));
 }else if(id==='10-origin-effect-target-guide'){
  world.add(floor());world.add(actor(-540,0,()=>30+45*u(0),P.blue));world.add(s.box(-540,0,30,165,165,35,'#cddcea'));
  world.add(token(()=>-400+730*u(1),0,125,P.blue,'★'));world.add(s.path(()=>[[-430,0,126],[360,0,126]],P.blue,()=>u(1)));world.add(target(510,0,2));
  world.add(ring(-540,0,()=>245*u(2)));world.add(label('시작',-550,-165,P.blue));world.add(label('공간',0,-120));world.add(label('대상',520,-110,P.green));
  world.add(<Node opacity={()=>u(3)}>{token(()=>-425+890*u(3),-75,150,P.green,'●')}{s.path(()=>[[-420,-75,151],[470,-75,151]],P.green,()=>u(3))}</Node>);
 }else if(id==='11-jade-ground-and-height-guide'){
  world.add(floor());world.add(ring(-470,40,()=>240*u(0)));world.add(actor(-470,40,()=>30+255*u(1),P.blue));
  world.add(s.path(()=>[[-460,40,385],[280,-120,50]],P.blue,()=>u(1)));world.add(target(280,-120));world.add(target(475,105));
  world.add(s.box(545,145,30,65,65,200,'#c5ccd3'));world.add(label('높이 차이',-420,-190,P.blue));world.add(label('아래의 대상',440,-140,P.green));
  world.add(<Node opacity={()=>u(3)}>{token(-410,40,()=>55+250*u(3),P.green,'●')}{s.path(()=>[[-410,40,65],[-410,40,310]],P.green,()=>u(3))}</Node>);
 }else if(id==='12-nearby-space-guide'){
  world.add(floor());const x=()=>-430+560*u(1)+120*u(3),y=()=>-100+170*u(1)-130*u(3);
  world.add(ring(x,y,()=>260*u(0)));world.add(actor(x,y,30,P.blue));[[-250,-95],[260,120],[510,-180]].forEach(([a,b])=>world.add(target(a,b,1)));
  world.add(s.path(()=>[[-400,-90,70],[135,85,70]],P.blue,()=>u(1)));world.add(label('움직이는 중심',-420,-180,P.blue));world.add(label('가까운 대상',390,-150,P.green));
 }else if(id==='13-doorway-comparison-guide'){
  world.add(floor());world.add(actor(()=>-570+260*u(1),()=>180-360*u(1),30,P.blue));
  [[450,-170],[450,170]].forEach(([x,y])=>world.add(target(x,y,2)));
  world.add(s.box(610,-235,30,60,110,270,'#c8d2db'));world.add(s.box(610,235,30,60,110,270,'#c8d2db'));
  world.add(s.path(()=>[[-515,180,112],[450,170,112]],P.blue,()=>u(0)));world.add(s.path(()=>[[-245,-180,112],[450,-170,112]],P.green,()=>u(1)));
  world.add(label('다른 위치에서 겨냥',-400,-230,P.blue));world.add(label('대상 배치',470,-205,P.green));
  world.add(<Node opacity={()=>u(3)}>{actor(()=>-570+260*u(3),()=>180-360*u(3),30,P.green)}{s.path(()=>[[-570,180,45],[-310,-180,45]],P.green,()=>u(3))}</Node>);
 }else if(id==='14-purpose-before-options-guide'){
  [-550,40,630].forEach(x=>world.add(floor(x,465,460)));
  world.add(actor(-550,0,30,P.blue));world.add(s.path(()=>[[-385,0,110],[-120,0,110]],P.blue,()=>u(1)));
  [-70,90].forEach((x,i)=>{world.add(s.box(x,0,30,110,150,65,'#d2dfe8'));world.add(token(x,0,()=>95+70*u(1),i?P.green:P.blue,i?'●':'▲'));});
  world.add(s.path(()=>[[220,0,135],[450,0,135]],P.green,()=>u(2)));world.add(target(630,0,2));
  world.add(label('목적',-540,-170,P.blue));world.add(label('행동으로 후보 구분',45,-145));world.add(label('목적에 맞는 시험',605,-110,P.green));
  world.add(<Node opacity={()=>u(3)}>{token(()=>90+465*u(3),100,140,P.green,'●')}{s.path(()=>[[630,205,45],[40,205,45]],P.green,()=>u(3),[15,10])}</Node>);
 }else if(id==='15-task-and-result-guide'){
  world.add(floor(-440,665,610));world.add(floor(440,665,610));world.add(actor(()=>-665+335*u(0),-90,30,P.blue));
  world.add(actor(-330,80,()=>30+60*u(0),P.green));world.add(s.path(()=>[[-620,-90,90],[-330,80,90]],P.green,()=>u(0)));
  world.add(actor(205,140,30,P.blue));world.add(target(625,-100,1));world.add(token(()=>260+325*u(1),()=>115-185*u(1),125,P.blue,'▲'));
  world.add(label('도울 대상과 회복',-465,-180,P.green));world.add(label('겨냥할 대상과 닿는 공간',460,-140,P.blue));
  world.add(s.path(()=>[[-335,220,40],[-620,220,40]],P.green,()=>u(3),[15,10]));
 }else{
  world.add(floor(-455,650,580));world.add(floor(455,650,580));world.add(actor(()=>-660+400*u(0),0,30,P.blue));
  world.add(s.path(()=>[[-655,0,40],[-175,0,40]],P.blue,()=>u(0)));world.add(target(-130,0,1));
  world.add(actor(430,0,30,'#aebdc9'));world.add(token(()=>750-230*u(2),150,135,P.red,'♥'));
  world.add(s.box(()=>210+125*u(2),-100,110,100,110,150,'#c8ddeb'));world.add(token(705,0,()=>30+95*u(3),P.green,'✓'));world.add(s.path(()=>[[645,0,70],[500,0,70]],P.green,()=>u(3)));
  world.add(label('행동을 이해하는 시험',-420,-190,P.blue));world.add(label('원하는 모습의 미리보기',455,-145,P.red));
 }
 // Plain Korean labels are separate from depth-moving geometry and clear of bottom captions.
 view.add(<Txt text={'설명용 공간 도식 · 실제 장비 수치나 성능 순위를 나타내지 않습니다'} y={328} fontSize={28} fill={P.muted} fontFamily={P.font}/>);
 yield* t(timing.durationSeconds,Math.max(0,timing.durationSeconds-1e-7),linear);
}
