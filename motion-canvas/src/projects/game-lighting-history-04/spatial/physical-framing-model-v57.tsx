import {Circle,Node,Txt} from '@motion-canvas/2d';
import {all,createSignal,linear} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {depthSpace,V3} from '../../game-lighting-history-shared/depth-space';

// Projected boxes have distinct top/front/side faces. Arrows connect named
// responsibilities in depth. This is explanation, with no measured GPU costs.
// Only use after the five selected narration takes and exact word clocks are
// reviewed. Creation of this model does not approve its rendered motion.
export type FramingRole='part1-overview'|'part1-conclusion'|'part2-overview'|'part2-conclusion'|'part3-overview';
export function physicalFramingModel(role:FramingRole){
 const node=new Node({}),progress=createSignal(0),space=depthSpace(()=>16,[0,90],1);
 const phase=(a:number,b:number)=>()=>Math.max(0,Math.min(1,(progress()-a)/(b-a)));
 const txt=(t:string,x:number,y:number,size=30,color:string=P.ink)=>new Txt({text:t,x,y,fontSize:size,fontFamily:P.font,fill:color,textAlign:'center'});
 const box=(x:number,y:number,width:number,height:number,color:string,label:string,show:()=>number=()=>1)=>{
  const group=new Node({opacity:show});group.add(space.box(x,y,0,width,150,height,color));
  group.add(space.label(label,x,y,height+48,29,P.ink));node.add(group);
 };
 const path=(points:()=>V3[],color:string,a:number,b:number)=>node.add(space.path(points,color,phase(a,b)));
 if(role.startsWith('part1')){
  const conclusion=role.endsWith('conclusion');
  box(-480,0,300,35,P.teal,'필요한 그림자');
  box(0,0,300,35,P.orange,'유효한 과거 표본',phase(.22,.45));
  box(480,0,300,35,P.green,'기기의 저장 장소',phase(.48,.7));
  // Only the five declared cells gain physical depth; the remaining cells
  // stay outlined virtual addresses. No number is claimed about an engine.
  const local=depthSpace(()=>16,[-480,120],.72);
  for(let y=0;y<4;y++)for(let x=0;x<4;x++){
   const i=y*4+x,px=(x-1.5)*62,py=(y-1.5)*62;
   node.add(local.polygon(()=>[[px-26,py-26,0],[px+26,py-26,0],[px+26,py+26,0],[px-26,py+26,0]],P.panel));
   if([0,5,6,10,15].includes(i))node.add(new Node({opacity:phase(0,.22),children:[local.box(px,py,0,50,50,28,P.teal)]}));
  }
  for(let i=0;i<3;i++)node.add(new Circle({position:space.point(-80+i*80,10,72),size:18,fill:P.orange,opacity:phase(.22,.45)}));
  path(()=>[[-320,0,60],[-160,0,60]],P.teal,.22,.45);
  path(()=>[[160,0,60],[320,0,60]],P.orange,.48,.7);
  node.add(txt(conclusion?'필요한 정보와 남은 비용을 구별':'계산과 메모리를 어디에 쓸까?',0,-200,34,P.yellow));
  node.add(txt(conclusion?'다음 질문: 빛의 어떤 표본을 고를까?':'그림자 → 시간적 복원 → 모바일',0,285,31,P.ink));
  node.add(txt('16칸·5자리: 주소와 저장을 구별하는 독립 도식',0,337,23,P.muted));
 }
 if(role.startsWith('part2')){
  const conclusion=role.endsWith('conclusion');
  box(-550,-40,230,55,P.teal,'경로와 광원');
  box(0,-40,230,55,P.orange,'남은 표본 복원',conclusion?phase(.6,.88):phase(.3,.6));
  const layers=conclusion?phase(.3,.6):phase(.63,.88);
  box(550,-40,230,55,P.green,'얇고 겹친 표면',layers);
  // A visibility query terminates at the orange front layer; the teal rear
  // layer remains separately present, motivating the transparency question.
  node.add(new Node({opacity:layers,children:[space.box(560,-150,0,190,16,170,P.teal),space.box(560,90,0,190,16,170,P.orange)]}));
  path(()=>[[-620,210,25],[-550,-40,90],[-280,-130,90]],P.teal,0,.3);
  path(()=>[[-280,-130,90],[0,-40,90]],P.orange,.3,.6);
  path(()=>[[160,-40,90],[390,-40,90]],P.green,.63,.88);
  node.add(txt(conclusion?'가시성과 복원은 서로 다른 책임':'예산 안에서 어떤 표본을 고를까?',0,-205,34,P.yellow));
  node.add(txt(conclusion?'다음 질문: 최종 화면의 입력과 출력을 확인할까?':'Cyberpunk 경로 → Unreal 광원 → 겹친 층',0,285,30));
  node.add(txt('역할 연결 도식 · 게임의 비공개 구현이나 실측 표본 수가 아님',0,337,23,P.muted));
 }
 if(role==='part3-overview'){
  const xs=[-600,-200,200,600],labels=['재구성의 책임','노출과 초점','실제 프레임','입력 ↔ 출력'];
  xs.forEach((x,i)=>{box(x,0,260,40,i===0?P.teal:i===1?P.orange:P.surfaceTop,labels[i],i===0?()=>1:phase((i-1)*.25,i*.25));
   if(i<3)path(()=>[[x+145,0,70],[xs[i+1]-145,0,70]],P.teal,i*.25,(i+1)*.25);
  });
  node.add(txt('화면의 인상과 내부 계산을 구별',0,-205,34,P.yellow));
  node.add(txt('DLSS 역할 → 직접 설정 변경 → 자원 검사',0,285,31));
  node.add(txt('표시된 프레임 수 ≠ 게임의 시뮬레이션 횟수',0,337,25,P.orange));
 }
 return {node,reset(value:number){progress(value);},*transition(value:number,seconds:number){yield*all(progress(value,seconds,linear));}};
}
