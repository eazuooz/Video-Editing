import {Circle,Line,Node,Txt} from '@motion-canvas/2d';
import {createSignal} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {depthSpace,V3} from '../../game-lighting-history-shared/depth-space';

export type Part1TransferRole='horizon-comparison-before'|'outer-comparison-before'|'cyber-comparison-before'|'fortnite-comparison-before'|'four-game-transfer-conclusion';
const clamp=(n:number)=>Math.max(0,Math.min(1,n));
const stage=(p:number,a:number,b:number)=>clamp((p-a)/(b-a));

// Spatial explanatory models, not simulations of the games' hidden renderers.
// The eventual scene clock must bind selected PCM and directly compared word times.
export function part1TransferModel(role:Part1TransferRole){
 const p=createSignal(0),yaw=createSignal(-14),world=depthSpace(()=>yaw(),[0,160],1),node=new Node({});
 const text=(s:string,x:number,y:number,size=30,color:string=P.ink)=><Txt text={s} x={x} y={y} fontFamily={P.font} fontSize={size} fill={color} fontWeight={600}/>;
 const note=new Txt({text:'설명용 자료 역할 · 실제 게임 화면은 다음 장면',x:0,y:335,fontSize:24,fill:P.muted,fontFamily:P.font,fontWeight:600});
 const plane=(x:number,y:number,name:string,color:string,width=270)=>{
  node.add(world.shadow(x,y,width,80));
  node.add(world.box(x,y,0,width,110,28,color));
  node.add(world.label(name,x,y,165,28,P.ink));
 };
 if(role==='horizon-comparison-before'){
  const shift=()=>70*stage(p(),.32,.9),centers=[-420,420];
  for(let i=0;i<2;i++){
   const x=centers[i];plane(x,0,i===0?'CNN · SR':'Transformer · SR',P.surfaceTop,410);
   // The same abstract surface detail moves in both conditions. No invented score.
   node.add(<Node opacity={()=>stage(p(),.08,.32)}>
    {world.box(()=>x+shift()-50,0,31,150,90,52,'#6d6855')}
    {world.path(()=>[[x+shift()-105,-31,86],[x+shift()-47,-31,86],[x+shift()-47,25,86]],P.orange)}
    {world.path(()=>[[x+shift()-10,25,86],[x+shift()+20,-8,86]],P.teal)}
   </Node>);
   node.add(world.path(()=>[[x+shift()-138,-54,92],[x+shift()+35,-54,92],[x+shift()+35,50,92],[x+shift()-138,50,92],[x+shift()-138,-54,92]],P.red,()=>stage(p(),.4,.72)));
  }
  node.add(text('호라이즌 · 같은 가방의 자수',0,-155,33,P.title));
  node.add(text('조건 표시 → 동일 대상 → 움직이는 경계',0,276,32));
 }else if(role==='outer-comparison-before'){
  const xs=[-620,-210,210,620];
  xs.forEach((x,i)=>{
   const generated=i===1||i===2;
   node.add(<Node opacity={()=>stage(p(),generated ? .35 : .04,generated ? .74 : .26)}>
    {world.box(x,0,0,230,105,generated?38:65,generated?'#81674e':P.surfaceTop)}
    {world.box(x,0,()=>generated?41:68,180,72,8,generated?'#c59b64':P.teal)}
    {world.label(generated?'생성된 표시':'실제 렌더링',x,0,115,27)}
   </Node>);
  });
  node.add(world.path(()=>[[-760,0,-15],[780,0,-15]],P.teal,()=>stage(p(),.08,.82)));
  node.add(text('보여 줄 화면의 순서',0,-160,34,P.title));
  node.add(<Node opacity={()=>stage(p(),.58,.9)}>
   {text('게임 상태 갱신',-510,265,31)}
   <Line points={[[-235,265],[530,265]]} stroke={P.line} lineWidth={3}/>
   <Circle x={-130} y={265} size={18} fill={P.orange}/>
   <Circle x={430} y={265} size={18} fill={P.orange}/>
   {text('별도의 작업',620,265,29,P.title)}
  </Node>);
 }else if(role==='cyber-comparison-before'){
  plane(-520,0,'빛 입력',P.surfaceSide,360);plane(520,0,'표시할 표면',P.surfaceTop,360);
  const sampleColors=[P.orange,P.teal,P.muted,P.orange,P.teal];
  for(let i=0;i<5;i++){
   node.add(<Node opacity={()=>stage(p(),.02+i*.035,.24+i*.035)}>
    {world.box(-620+i*48,(i%2)*30-15,32,20,20,22,sampleColors[i])}
   </Node>);
  }
  node.add(world.box(0,0,0,250,130,105,'#374649'));
  node.add(world.label('복원',0,0,160,34,P.title));
  node.add(world.path(()=>[[-320,0,55],[-145,0,55]],P.teal,()=>stage(p(),.22,.52)));
  node.add(world.path(()=>[[145,0,55],[320,0,55]],P.teal,()=>stage(p(),.5,.78)));
  node.add(<Node opacity={()=>stage(p(),.45,.83)}>
   {world.box(520,0,31,235,78,12,'#688b90')}
   {world.box(565,-10,43,62,34,10,'#d1a766')}
  </Node>);
  node.add(text('사이버펑크 · 빛 자료를 복원하는 역할',0,-155,34,P.title));
  node.add(text('표면 세부 / 표시 빈도 / 빛 복원의 입력을 구별',0,278,31));
 }else if(role==='fortnite-comparison-before'){
  plane(-520,0,'같은 게임 · 다른 재질 조건',P.surfaceTop,470);
  for(let i=0;i<3;i++){
   node.add(<Node opacity={()=>stage(p(),.02+i*.05,.25+i*.05)}>
    {world.box(-660+i*145,0,31,90,70,()=>55+i*8,'#52666b')}
    {world.box(-660+i*145,0,()=>89+i*8,62,47,8,i===1?P.orange:P.teal)}
   </Node>);
  }
  plane(505,0,'원본의 성능 자료',P.surfaceSide,440);
  // Qualitative graph: deliberately no invented FPS, milliseconds or bandwidth.
  const pts=():V3[]=>Array.from({length:12},(_,i)=>[330+i*31,0,45+Math.sin(i*.8)*17]);
  node.add(world.path(pts,P.teal,()=>stage(p(),.32,.77)));
  node.add(world.path(()=>[[-235,0,58],[235,0,58]],P.orange,()=>stage(p(),.45,.86)));
  node.add(text('포트나이트 · 장면과 진단 자료를 함께 기록',0,-155,34,P.title));
  node.add(text('대상 기기 → 장면 조건 → 실제로 읽은 자료',0,278,31));
 }else{
  const names=['표면 세부','표시 빈도','빛 복원','기기 예산'],games=['Horizon','The Outer Worlds 2','Cyberpunk 2077','Fortnite'];
  for(let i=0;i<4;i++){
   const x=-630+i*420;
   node.add(<Node opacity={()=>stage(p(),.02+i*.07,.2+i*.07)}>
    {world.box(x,-85,0,280,90,70,P.surfaceTop)}
    {world.box(x,-85,74,210,65,12,i===1?'#ac8152':'#619092')}
    {world.label(names[i],x,-85,133,28,P.ink)}
   </Node>);
   node.add(text(games[i],x,-175,25,P.muted));
  }
  for(let i=0;i<3;i++){
   const x=-480+i*480,label=['만드는 자료','저장할 내용','다시 읽는 조건'][i];
   node.add(<Node opacity={()=>stage(p(),.38+i*.09,.58+i*.09)}>
    {world.box(x,120,0,300,85,45,P.surfaceSide)}
    {world.label(label,x,120,90,30,P.title)}
   </Node>);
  }
  node.add(world.path(()=>[[-320,120,23],[-165,120,23]],P.teal,()=>stage(p(),.6,.75)));
  node.add(world.path(()=>[[165,120,23],[320,120,23]],P.teal,()=>stage(p(),.73,.88)));
  node.add(text('다른 결과 · 공통의 자료 흐름 질문',0,288,32,P.ink));
  note.text('설명용 자료 역할 · 각 게임의 조건과 결과는 따로 확인');
 }
 node.add(note);
 return {node,reset:(progress:number)=>{p(clamp(progress));yaw(-14+5*clamp(progress));}};
}
