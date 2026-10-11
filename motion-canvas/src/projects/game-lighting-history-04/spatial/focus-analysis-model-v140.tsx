import {Circle,Line,Node,Txt} from '@motion-canvas/2d';
import {createSignal} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {depthSpace} from '../../game-lighting-history-shared/depth-space';

export type FocusAnalysisRole='focus-later-settings'|'focus-observation-protocol'|'focus-to-frame-inspection';
const clamp=(n:number)=>Math.max(0,Math.min(1,n));
const phase=(p:number,a:number,b:number)=>clamp((p-a)/(b-a));

// Analysis, never actual-footage quota. Preserve existing PCM and source stills.
// The clock wrapper must be authored from directly compared whole/context ASR.
export function focusAnalysisModel(role:FocusAnalysisRole){
 const progress=createSignal(0),yaw=createSignal(-15),world=depthSpace(()=>yaw(),[0,175],1);
 const node=new Node({}),overlay=new Node({zIndex:100});node.add(overlay);
 const text=(value:string,x:number,y:number,size=28,color:string=P.ink)=><Txt text={value} x={x} y={y} fill={color} fontFamily={P.font} fontSize={size} fontWeight={600}/>;
 overlay.add(text('관찰 순서 도식 · 게임 내부 수치의 측정값 아님',0,330,23,P.muted));
 if(role==='focus-later-settings'){
  const boxes=[{x:-480,y:165,h:110,label:'가까운 면',color:P.axisY},{x:0,y:0,h:125,label:'초점 기준',color:P.ink},{x:455,y:-170,h:135,label:'먼 면',color:P.axisZ}];
  node.add(world.box(0,0,-18,1340,515,18,'#263338'));
  // The near and far labels preserve the source legend: near green, far blue.
  for(let i=2;i>=0;i--){const b=boxes[i];node.add(<Node opacity={()=>phase(progress(),.03+i*.04,.19+i*.04)}>
   {world.shadow(b.x,b.y,220,115)}{world.box(b.x,b.y,0,190,155,b.h,'#8b979e')}
   {world.label(b.label,b.x,b.y,b.h+50,30,b.color)}
   {world.path(()=>[[b.x-90,b.y+105,b.h+40],[b.x-30,b.y+80,b.h*.6]],P.red,()=>phase(progress(),.25+i*.1,.39+i*.1))}
  </Node>);}
  node.add(<Node opacity={()=>phase(progress(),.52,.72)}>
   {world.polygon(()=>[[-220,-240,0],[220,-240,0],[220,-240,165],[-220,-240,165]],'#151a1d',P.ink)}
   {world.label('기준 위치',0,-240,210,28,P.title)}
  </Node>);
  overlay.add(<Node opacity={()=>phase(progress(),.75,.95)}>{text('전체 인상 → 바뀐 거리 영역',0,-255,35,P.title)}</Node>);
 }else if(role==='focus-observation-protocol'){
  const stages=[{x:-570,title:'① 입력 이름',sub:'무엇을 조절했나?',color:'#586c75'}, {x:0,title:'② 값의 변화',sub:'언제 달라졌나?',color:'#567f82'}, {x:570,title:'③ 영향받은 면',sub:'어디가 달라졌나?',color:'#819192'}];
  for(let i=0;i<3;i++){
   const s=stages[i];node.add(<Node opacity={()=>phase(progress(),i*.17,.15+i*.17)}>
    {world.shadow(s.x,0,290,110)}{world.box(s.x,0,0,285,170,120,s.color)}
    {world.box(s.x,0,124,220,135,16,'#acb9c0')}{world.label(s.sub,s.x,0,190,27,P.ink)}
   </Node>);overlay.add(text(s.title,s.x,-195,33,P.title));
  }
  node.add(world.path(()=>[[-390,0,70],[-185,0,70]],P.teal,()=>phase(progress(),.25,.4)));
  node.add(world.path(()=>[[185,0,70],[390,0,70]],P.teal,()=>phase(progress(),.43,.59)));
  overlay.add(<Node opacity={()=>phase(progress(),.22,.45)}><Line points={[[-95,-88],[95,-88]]} stroke={P.line} lineWidth={4}/><Circle x={()=>-90+180*phase(progress(),.25,.48)} y={-88} size={20} fill={P.orange}/></Node>);
  overlay.add(<Node opacity={()=>phase(progress(),.62,.83)}>{text('카메라 변화는 별도로 기록',0,255,31,P.ink)}{text('관찰 방법의 전이 ≠ 엔진 내부 순서의 동일성',0,300,29,P.title)}</Node>);
 }else{
  const stages=[{x:-550,title:'화면 변화',label:'노출 · 색 · 초점',c:'#809195'},{x:0,title:'남은 질문',label:'어떤 자료를 읽었나?',c:'#756955'},{x:550,title:'프레임 검사',label:'입력 → 명령 → 출력',c:'#4d7679'}];
  for(let i=0;i<3;i++){
   const s=stages[i];node.add(<Node opacity={()=>phase(progress(),.03+i*.19,.19+i*.19)}>
    {world.shadow(s.x,0,280,95)}{world.box(s.x,0,0,285,125,95,s.c)}
    {world.box(s.x,0,99,218,95,15,'#a0aeb3')}{world.label(s.label,s.x,0,167,26,P.ink)}
   </Node>);overlay.add(text(s.title,s.x,-185,32,P.title));
  }
  node.add(world.path(()=>[[-365,0,65],[-180,0,65]],P.teal,()=>phase(progress(),.26,.45)));
  node.add(world.path(()=>[[180,0,65],[365,0,65]],P.teal,()=>phase(progress(),.53,.73)));
  overlay.add(<Node opacity={()=>phase(progress(),.74,.95)}>{text('기능 이름 → 실제 자료 연결 확인',0,276,34,P.title)}</Node>);
 }
 return {node,reset:(p:number)=>{progress(clamp(p));yaw(-15+6*clamp(p));}};
}
