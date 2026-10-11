import {Circle,Line,Node,Txt} from '@motion-canvas/2d';
import {createSignal} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {depthSpace} from '../../game-lighting-history-shared/depth-space';

export type GuidedTeachingRole='appearance-prerequisite'|'appearance-to-controls';
const clamp=(n:number)=>Math.max(0,Math.min(1,n));
const phase=(p:number,a:number,b:number)=>clamp((p-a)/(b-a));

// These are labelled illustrative surfaces and data roles. They do not simulate
// a game's unobserved renderer or establish pixel-aligned OFF/ON ground truth.
// Word-aligned clocks must be supplied only after both ASR contexts are read.
export function guidedTeachingModel(role:GuidedTeachingRole){
 const progress=createSignal(0),yaw=createSignal(-13);
 const world=depthSpace(()=>yaw(),[0,180],1),node=new Node({});
 const text=(value:string,x:number,y:number,size=28,color:string=P.ink)=><Txt text={value} x={x} y={y} fill={color} fontFamily={P.font} fontSize={size} fontWeight={600}/>;
 const overlay=new Node({});node.add(overlay);
 if(role==='appearance-prerequisite'){
  const games=[{name:'Resident Evil',x:-610,color:'#52787a',scope:'어두운 옷'},
   {name:'Starfield',x:-210,color:'#b57d47',scope:'밝은 외투'},
   {name:'Hogwarts Legacy',x:210,color:'#786796',scope:'실내 · 지하'},
   {name:'NBA 2K27',x:610,color:'#649679',scope:'피부 · 유니폼'}];
  for(let i=0;i<games.length;i++){
   const g=games[i],show=()=>phase(progress(),.02+i*.04,.15+i*.04);
   node.add(<Node opacity={show}>
    {world.shadow(g.x,0,180,70)}
    {world.box(g.x,0,0,210,90,115,g.color)}
    {world.box(g.x,0,119,146,65,()=>8+14*phase(progress(),.32,.64),'#b7c4c6')}
    {world.label(g.scope,g.x,0,165,25,P.ink)}
    {world.path(()=>[[g.x-70,-120,190],[g.x-25,-22,133]],'#e27655',()=>phase(progress(),.34,.55))}
   </Node>);
   overlay.add(text(g.name,g.x,-185,27));
  }
  // Date labels sit above geometry, never on the projected comparison faces.
  overlay.add(<Node opacity={()=>phase(progress(),.12,.3)}>
   {text('2026.03 · 미리보기',-215,-115,29,P.title)}
   <Line points={[[-775,-81],[335,-81]]} stroke={P.line} lineWidth={2}/>
   {text('2026.09 · 출시 사례',610,-115,29,P.title)}
   <Line points={[[450,-81],[770,-81]]} stroke={P.line} lineWidth={2}/>
  </Node>);
  overlay.add(<Node opacity={()=>phase(progress(),.3,.5)}>
   {text('원본의 OFF / ON 표시부터 읽기',0,258,31,P.ink)}
  </Node>);
  overlay.add(<Node opacity={()=>phase(progress(),.65,.88)}>
   {text('같은 역할 · 서로 다른 표면 조건',0,297,29,P.title)}
   {text('설명용 표면 도식 · 게임 내부 계산의 측정값 아님',0,340,23,P.muted)}
  </Node>);
 }else{
  const x=[-560,0,560],labels=['조절하는 입력','표시되는 결과','프레임 자료 검사'];
  for(let i=0;i<3;i++){
   node.add(<Node opacity={()=>phase(progress(),i*.18,.14+i*.18)}>
    {world.shadow(x[i],0,260,85)}
    {world.box(x[i],0,0,280,115,85,i===1?'#587e85':'#59636b')}
    {world.box(x[i],0,89,210,85,12,i===1?'#8babb0':'#859095')}
    {world.label(i===0?'노출 · 초점':i===1?'표면 픽셀':'입력 → 출력',x[i],0,145,27,P.ink)}
   </Node>);
   overlay.add(text(labels[i],x[i],-175,30,i===1?P.title:P.ink));
  }
  node.add(world.path(()=>[[-400,0,58],[-175,0,58]],'#48c1c2',()=>phase(progress(),.22,.44)));
  node.add(world.path(()=>[[175,0,58],[400,0,58]],'#48c1c2',()=>phase(progress(),.57,.82)));
  // Parameter and result move separately: appearance changes do not imply that
  // a light, game physics, input latency or a material asset was edited.
  overlay.add(<Node opacity={()=>phase(progress(),.16,.38)}>
   <Circle x={()=>-600+80*phase(progress(),.26,.45)} y={-80} size={18} fill={'#e27655'}/>
   <Line points={[[-655,-80],[-475,-80]]} stroke={P.line} lineWidth={3}/>
   {text('설정',-560,-35,26,P.muted)}
  </Node>);
  overlay.add(<Node opacity={()=>phase(progress(),.37,.58)}>
   {text('조명 이동 없이도 화면 표현은 달라질 수 있다',0,247,31,P.ink)}
  </Node>);
  overlay.add(<Node opacity={()=>phase(progress(),.72,.92)}>
   {text('결과만 추측 → 실제 입력과 출력 확인',0,297,30,P.title)}
   {text('설명용 자료 흐름 · 특정 게임의 내부 구현 증거 아님',0,340,23,P.muted)}
  </Node>);
 }
 return {node,reset:(p:number)=>{progress(clamp(p));yaw(-13+4*clamp(p));}};
}
