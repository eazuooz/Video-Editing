import {Node,Rect,Txt,View2D} from '@motion-canvas/2d';
import {createSignal,linear} from '@motion-canvas/core';
import {depthSpace,heading,V3,Value,val} from '../../shared/depth-diagrams';
import {PAPER as P} from '../../styles/research-paper';

export type ParagraphTiming={durationSeconds:number;paragraphStarts:number[];measured:boolean};
const clamp=(x:number)=>Math.max(0,Math.min(1,x));
const smooth=(x:number)=>{const q=clamp(x);return q*q*(3-2*q);};
const headings:Record<string,[string,string]>={
 '01-overview':['고르고 시험하고 나답게 만들기','효과를 읽기 → 선택과 시험 → 외형 미리보기'],
 '02-visible-effects':['숫자를 행동의 결과로 연결하기','지나가는 경로와 영향을 받는 공간을 함께 보기'],
 '03-readable-outcome':['동작 · 범위 · 대상의 변화','선택 전에는 예상하고, 사용 후에는 확인하기'],
 '04-situations':['상황이 달라지면 선택도 달라집니다','설명용 가상 비교 · 실제 게임 능력의 수치나 우열을 뜻하지 않습니다'],
 '05-manageable-choice':['찾고 비교하는 부담 줄이기','역할별 묶음 · 구별되는 모양 · 현재 선택과 후보'],
 '06-quick-trial':['고른 다음 곧바로 시험하기','선택을 보존하며 짧게 시험하고 돌아오는 흐름'],
 '07-expression':['강해지는 선택과 나다운 표현','미리보기와 적용을 구분하고, 이전 모습을 보존하기'],
 '08-conclusion':['내 게임의 선택 하나를 점검하기','결과 · 상황 · 선택 · 시험과 복귀 · 나다운 표현'],
};
const notes:Record<string,string[]>={
 '01-overview':['고르는 시간도 게임의 재미가 될까요?','결과를 이해하고, 직접 시험하고, 나답게 표현','가우스·제이드 → 설정과 시험 → 외형 미리보기','먼저 가우스의 경로와 적의 반응부터'],
 '02-visible-effects':['경로를 따라 지나갈 때 무엇이 반응하는가?','직선 경로와 주변 범위가 다루는 공간','수치와 함께 닿는 공간을 보여주기','가장 큰 숫자보다 가능해지는 행동을 이해'],
 '03-readable-outcome':['행동이 시작된 곳과 영향을 받은 대상','한 숫자보다 동작과 결과의 연결','도구 → 범위 → 대상의 변화','설정의 성능 향상을 이 시연만으로 확정하지 않기'],
 '04-situations':['지나가는 경로 / 주변으로 퍼지는 범위','회전 효과와 가까운 대상의 위치 관계','모인 대상 / 멀리 떨어진 한 대상','강점이 드러나는 상황과 놓치는 부분'],
 '05-manageable-choice':['선택지가 많아지면 찾는 과정도 설계','역할별 묶음 · 모양으로 구분 · 가까이 비교','모든 목록보다 출발점과 바뀔 부분을 먼저','추천에서 다른 목적의 후보로 이동할 길'],
 '06-quick-trial':['거리 → 진행률 → 동료의 회복을 관찰','내가 하려던 일을 실제로 시험','긴 이동과 반복 화면이 실험을 방해하지 않게','선택을 잃지 않고 다시 고르기로 복귀'],
 '07-expression':['결과를 미리 보고 적용은 따로 결정','성능이 그대로여도 원하는 모습을 만드는 가치','미리본 상태와 확인한 상태를 구분','외형을 더 강한 능력의 증거로 설명하지 않기'],
 '08-conclusion':['완성된 조합과 고르는 과정의 즐거움','결과 · 상황 · 짧은 시험과 복귀를 점검','상상을 행동과 나다운 표현으로 연결','설명란에서 프로그래밍 코칭 안내 확인'],
};
// Required policy wording is deliberately retained, including the source's spacing.
const noticeLines=[
 'Portions of the content provided here, including trademarks and copyrights',
 'and any other intellectual property rights, are owned or held by Digital Extremes,',
 'Ltd.or its licensor(s)(“DEP”) and all rights in and to the same are reserved by DEP.',
 'This content is not official DEP content and is not endorsed or approved by DEP.',
];

/** Editable XYZ diagram authoring. Unmeasured lookdev timings must never reach final render. */
export function* customizationExplanation(view:View2D,id:string,timing:ParagraphTiming){
 if(!headings[id]||timing.paragraphStarts.length!==4||timing.durationSeconds<=0)throw Error('Invalid independent scene timing');
 const t=createSignal(0);
 const starts=timing.paragraphStarts;
 const u=(p:number,d=2.2)=>smooth((t()-starts[p])/d);
 const phase=()=>starts.reduce((p,s,i)=>t()>=s?i:p,0);
 const camera=()=>20+9*smooth(t()/Math.min(6,timing.durationSeconds));
 const overview=id==='01-overview';
 const s=depthSpace(camera,overview?[0,225]:[0,75],overview?.58:.72);
 const world=new Node({});view.fill(P.background);view.add(heading(id.slice(0,2),...headings[id],'플레이어 커스터마이징'));view.add(world);
 const text=(v:string,x:number,y:number,color:string=P.ink,size=30)=><Txt text={v} x={x} y={y} fill={color} fontFamily={P.font} fontSize={size} fontWeight={600}/>;
 const floor=(x:number,y=0,w=590,d=450)=> <Node zIndex={-1000}>{s.box(x,y,0,w,d,30,'#e7edf1')}</Node>;
 const layer=(x:Value,y:Value,children:Node)=>{children.zIndex(()=>s.point(x,y,0)[1]);return children;};
 const target=(x:Value,y:Value,p=2,col:string=P.green)=><Node zIndex={()=>s.point(x,y,0)[1]}>
  {s.box(x,y,30,74,74,90,'#d8dee5')}
  <Node opacity={()=>u(p)}>{s.box(x,y,()=>30+42*u(p),74,74,90,col)}</Node>
 </Node>;
 const token=(x:Value,y:Value,z:Value,col:string,symbol:string)=> <Node zIndex={()=>s.point(x,y,0)[1]}>
  {s.shadow(x,y,88,65)}{s.box(x,y,z,82,70,48,col)}{s.label(symbol,x,()=>val(y)+38,()=>val(z)+23,30,'#ffffff')}
 </Node>;
 const ring=(x:Value,y:Value,radius:Value,col='#dae8d8')=> <Node zIndex={-900}>
  {s.polygon(()=>Array.from({length:48},(_,i)=>[val(x)+Math.cos(i*Math.PI/24)*val(radius),val(y)+Math.sin(i*Math.PI/24)*val(radius),33] as V3),col,P.green)}
 </Node>;
 if(overview){
  view.add(<Rect x={0} y={-137} width={1720} height={200} fill={'#f4f6f7'} stroke={P.line} lineWidth={1.5}/>);
  view.add(<Txt text={noticeLines.join('\n')} x={0} y={-137} fontFamily={P.font} fontSize={31} lineHeight={41} fill={P.ink} textAlign={'center'}/>);
  [-600,0,600].forEach((x,i)=>{world.add(floor(x,0,450,330));world.add(s.box(x,0,30,160,135,68,['#c7d9eb','#cddfc7','#ead8c4'][i]));world.add(s.label(['예상','시험','표현'][i],x,-220,150,37));});
  world.add(s.path(()=>[[-460,0,111],[-180,0,111]],P.blue,()=>u(1)));
  world.add(s.path(()=>[[155,0,111],[445,0,111]],P.green,()=>u(2)));
  world.add(token(()=>-600+600*u(1)+600*u(2),0,()=>110+65*Math.sin(Math.PI*u(1))+65*Math.sin(Math.PI*u(2)),P.blue,'★'));
 }else if(id==='02-visible-effects'){
  world.add(floor(0,0,1700,640));
  world.add(s.path(()=>[[-750,-190,37],[-120,-190,37]],P.blue,()=>u(0)));
  const x=()=>-700+610*u(0);world.add(layer(x,-190,new Node({children:s.actor(x,-190,P.blue,'●',30)})));
  [[-420,-190],[-90,-190],[250,145],[520,145]].forEach(([a,b])=>world.add(target(a,b,b<0?0:2)));
  world.add(ring(430,145,()=>235*u(1)));
  world.add(layer(430,145,new Node({children:s.actor(430,145,P.green,'●',30)})));
  world.add(text('진행 경로',-520,-200,P.blue,34));world.add(text('주변 범위',475,-110,P.green,34));
  world.add(text('변화 뒤에 가능한 행동을 함께 보여주기',0,328,P.muted,29));
 }else if(id==='03-readable-outcome'){
  world.add(floor(0,0,1400,620));world.add(s.box(-520,0,30,185,165,84,'#c7d9eb'));
  world.add(token(-520,0,()=>114+80*u(0),P.blue,'★'));
  world.add(s.path(()=>[[-440,0,115],[-240,0,115],[50,0,35]],P.blue,()=>u(1)));
  world.add(ring(130,0,()=>260*u(1)));
  [[5,-155],[340,-55],[180,155]].forEach(([x,y])=>world.add(target(x,y,2)));
  world.add(<Node zIndex={()=>s.point(410,110,0)[1]}>{s.box(410,110,30,85,70,210,'#c6cdd3')}</Node>);
  // Depth order hides the far target behind the tall foreground pillar at this yaw.
  world.add(text('선택',-480,-210,P.blue,34));world.add(text('범위',90,-210,P.green,34));world.add(text('대상 변화',500,-155,P.green,34));
  world.add(text('설명용 순서 · 특정 설정의 성능을 증명하는 장면이 아닙니다',0,328,P.muted,28));
 }else if(id==='04-situations'){
  [-450,450].forEach(x=>world.add(floor(x,0,660,600)));
  [[-550,-90],[-420,0],[-310,90]].forEach(([x,y])=>world.add(target(x,y,2)));
  world.add(target(665,-100,3));world.add(ring(-440,0,()=>210*u(1)));
  world.add(token(-680,170,45,P.blue,'A'));
  world.add(s.path(()=>[[240,160,65],[590,-100,65]],P.blue,()=>u(2)));
  world.add(token(()=>-540+1040*u(2),()=>200-150*u(2),()=>45+80*Math.sin(Math.PI*u(2)),P.green,'B'));
  world.add(text('모여 있는 대상',-450,-190,P.green,33));world.add(text('멀리 떨어진 대상',470,-145,P.blue,33));
  world.add(text('가상의 두 도구 · 상황에 따라 얻는 것과 놓치는 것',0,328,P.muted,29));
 }else if(id==='05-manageable-choice'){
  world.add(floor(-435,0,670,650));world.add(floor(475,0,600,490));
  const palette=[P.blue,P.green,P.red];const symbols=['★','●','▲'];
  for(let row=0;row<3;row++)for(let col=0;col<3;col++){
   const x=-665+col*165,y=-165+row*165;
   world.add(token(()=>x+(row===1&&col===1?1095*u(1):0),()=>y+(row===1&&col===1?45*u(1):0),()=>30+(row===1&&col===1?90*u(1):0),palette[row],symbols[row]));
  }
  world.add(token(285,-80,100,P.blue,'★'));world.add(s.path(()=>[[-280,0,105],[90,0,105]],P.blue,()=>u(1)));
  world.add(s.box(360,45,30,170,190,90,'#d7e1eb'));world.add(s.box(595,45,30,170,190,90,'#d7e8d1'));
  world.add(text('역할별 묶음',-445,-210,P.ink,33));world.add(text('현재 선택 / 후보',470,-150,P.ink,33));
  world.add(s.path(()=>[[600,60,140],[750,110,140]],P.green,()=>u(3)));
  world.add(text('같은 색뿐 아니라 모양으로도 구별 · 다른 목적의 후보로 이동',0,328,P.muted,27));
 }else if(id==='06-quick-trial'){
  [-580,40,640].forEach((x,i)=>{world.add(floor(x,0,450,470));world.add(s.box(x,0,30,140,140,68,['#cbdced','#d0e0c9','#e2d4c4'][i]));});
  world.add(s.path(()=>[[-415,0,108],[-165,0,108]],P.blue,()=>u(0)));
  world.add(s.path(()=>[[210,0,108],[470,0,108]],P.green,()=>u(1)));
  world.add(s.path(()=>[[620,165,65],[290,300,65],[-200,300,65],[-590,165,65]],P.green,()=>u(3),[15,10]));
  const x=()=>-580+620*u(0)+600*u(1)-1220*u(3),y=()=>250*Math.sin(Math.PI*u(3));
  world.add(token(x,y,()=>115+80*Math.sin(Math.PI*u(0))+80*Math.sin(Math.PI*u(1)),P.blue,'★'));
  world.add(token(-580,-100,100,'#c3cbd4','●'));
  world.add(text('고르기',-580,-190,P.blue,34));world.add(text('짧은 시험',25,-170,P.green,34));world.add(text('결과 확인',635,-100,P.ink,34));
  world.add(text('기존 선택을 보존한 복귀 경로',0,328,P.green,29));
 }else if(id==='07-expression'){
  world.add(floor(0,0,1250,600));world.add(s.box(0,0,30,350,280,55,'#dce4eb'));
  world.add(layer(0,0,new Node({children:s.actor(0,0,'#aebbc7','●',85)})));
  // Physical shells arrive from separate depths; the back shell stays behind the actor.
  world.add(<Node zIndex={-100}>{s.box(()=>-340+290*u(0),()=>-130+45*u(0),85,110,130,150,'#bad2e8')}</Node>);
  world.add(<Node zIndex={100}>{s.box(()=>340-270*u(1),()=>180-90*u(1),85,110,110,105,'#e6c5c0')}</Node>);
  world.add(token(520,80,()=>40+95*u(2),P.green,'✓'));
  world.add(s.path(()=>[[475,60,145],[255,30,145]],P.green,()=>u(2)));
  world.add(token(-520,80,55,'#c3cbd4','●'));
  world.add(text('미리보기',-365,-210,P.blue,34));world.add(text('확인·적용',430,-100,P.green,34));
  world.add(text('원하는 모습의 가치 · 성능 향상을 뜻하지 않습니다',0,328,P.muted,29));
 }else{
  world.add(floor(0,0,1570,600));
  [-610,-305,0,305,610].forEach((x,i)=>{
   const p=Math.min(3,i),z=()=>30+80*u(p);
   world.add(s.box(x,0,30,230,200,30,'#dde5eb'));world.add(token(x,0,z,[P.blue,P.green,P.blue,P.green,P.red][i],['★','●','▲','↩','♥'][i]));
   world.add(s.label(['결과','상황','선택','시험·복귀','표현'][i],x,135,20,31));
   if(i<4)world.add(s.path(()=>[[x+118,0,80],[x+186,0,80]],P.green,()=>u(Math.min(3,i+1))));
  });
  world.add(text('내 게임의 선택 하나를 실제로 점검하기',0,-170,P.ink,34));
  world.add(text('프로그래밍 코칭 · 설명란 안내',0,328,P.blue,30));
 }
 // Clear of fixed caption center y430: content note remains at most y328.
 if(!overview)view.add(<Txt text={()=>notes[id][phase()]} y={-262} fill={P.blue} fontFamily={P.font} fontSize={28} fontWeight={600}/>);
 // Prevent floating-point accumulation from adding a frame at integer60fps boundaries.
 // The signal still reaches the full intended source time; only sub-microsecond wait changes.
 yield* t(timing.durationSeconds,Math.max(0,timing.durationSeconds-1e-7),linear);
}
