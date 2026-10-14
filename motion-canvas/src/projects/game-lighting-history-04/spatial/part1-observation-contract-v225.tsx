import {Node,Txt} from '@motion-canvas/2d';
import {createSignal} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {depthSpace,V3} from '../../game-lighting-history-shared/depth-space';

export type Part1ObservationRole='shadow-address-update'|'missing-measurement'|'different-reconstruction-inputs';

// These are explicit explanations for complete PCM, never additional actual time.
// Bind progress to directly reviewed speech anchors in the eventual scene wrappers.
export function part1ObservationContract(role:Part1ObservationRole){
 const node=new Node({}),p=createSignal(0),world=depthSpace(()=>-13+5*p(),[0,160],1);
 const phase=(a:number,b:number)=>Math.max(0,Math.min(1,(p()-a)/(b-a)));
 const caption=(s:string,x:number,y:number,size=32,color:string=P.ink)=>
  <Txt text={s} x={x} y={y} fontFamily={P.font} fontSize={size} fill={color} fontWeight={600}/>;
 const slab=(x:number,y:number,name:string,color:string,width=360)=>{
  node.add(world.shadow(x,y,width,90));
  node.add(world.box(x,y,0,width,120,35,color));
  node.add(world.label(name,x,y,205,30,P.ink));
 };
 if(role==='shadow-address-update'){
  node.add(caption('주소를 찾는 일 · 내용을 갱신하는 일',0,-265,43,P.title));
  slab(-540,0,'화면에서 필요한 영역',P.surfaceTop,380);
  // Sixteen cells remain an expressly labelled toy example, not engine page count.
  for(let y=0;y<4;y++)for(let x=0;x<4;x++){
   const cx=300+x*90,cy=-125+y*82;
   node.add(world.box(cx,cy,0,74,62,20,P.surfaceSide));
   if(x===1&&y===2){
    node.add(world.box(cx,cy,23,66,54,8,P.orange));
    node.add(world.path(():V3[]=>[[cx-37,cy-31,39],[cx+37,cy-31,39],[cx+37,cy+31,39],[cx-37,cy+31,39],[cx-37,cy-31,39]],P.red,()=>phase(.42,.75)));
   }
  }
  node.add(world.path(():V3[]=>[[-325,0,70],[200,40,70],[355,40,45]],P.teal,()=>phase(.04,.32)));
  node.add(world.path(():V3[]=>[[570,-190,110],[430,-110,90],[390,40,45]],P.orange,()=>phase(.42,.82)));
  node.add(caption('청록: 필요한 주소 찾기',-390,275,31,P.teal));
  node.add(caption('주황: 바뀐 내용 갱신',420,275,31,P.orange));
  node.add(caption('설명용16칸 · 실제 재계산 여부는 별도 진단',0,333,24,P.muted));
 }else if(role==='missing-measurement'){
  node.add(caption('측정의 빈칸도 기록에 남긴다',0,-265,43,P.title));
  slab(-540,0,'',P.surfaceTop,390);
  slab(520,0,'도구가 준비되지 않은 대상',P.surfaceSide,430);
  node.add(world.box(-540,0,39,230,80,70,'#42696a'));
  node.add(world.label('비교 가능한 자료',-540,0,150,30,P.teal));
  // A hollow raised box represents unavailable data, never a zero cost score.
  node.add(world.path(():V3[]=>[[380,-45,135],[655,-45,135],[655,45,135],[380,45,135],[380,-45,135]],P.orange));
  node.add(world.path(():V3[]=>[[380,-45,40],[380,-45,135],[655,-45,135],[655,-45,40]],P.orange,()=>phase(.12,.42)));
  node.add(world.path(():V3[]=>[[380,45,40],[380,45,135],[655,45,135],[655,45,40]],P.orange,()=>phase(.12,.42)));
  node.add(world.label('확인 필요',520,0,270,31,P.title));
  node.add(world.path(():V3[]=>[[230,-70,50],[745,100,50]],P.red,()=>phase(.42,.75)));
  node.add(caption('대상 플랫폼 / 컴파일러 / 조건을 먼저 확인',0,275,32));
  node.add(caption('빈칸 ≠ 비용0 · 설명용 모형, 실제 수치 아님',0,333,24,P.muted));
 }else{
  node.add(caption('복원이라는 말 · 입력 자료는 서로 다르다',0,-265,41,P.title));
  slab(-550,0,'표면의 세부',P.surfaceTop,380);
  slab(540,0,'빛과 반사의 자료',P.surfaceSide,380);
  for(let i=0;i<5;i++){
   node.add(world.box(-690+i*66,0,39,22,60,14,i%2?P.orange:P.teal));
   node.add(world.box(420+i*55,(i%2)*45-25,39,20,20,35,i%2?P.orange:P.teal));
  }
  node.add(world.path(():V3[]=>[[-310,0,70],[-90,0,70]],P.teal,()=>phase(.05,.4)));
  node.add(world.path(():V3[]=>[[95,0,70],[305,0,70]],P.orange,()=>phase(.4,.8)));
  node.add(caption('원본 조건과 처리 단계를 함께 기록',0,275,32));
  node.add(caption('복원 역할의 비교 · 게임 내부 처리 순서의 단정 아님',0,333,24,P.muted));
 }
 return {node,reset:(progress:number)=>p(Math.max(0,Math.min(1,progress)))};
}
