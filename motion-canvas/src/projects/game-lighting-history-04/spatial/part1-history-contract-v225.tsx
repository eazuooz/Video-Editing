import {Node,Txt} from '@motion-canvas/2d';
import {createSignal} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {depthSpace,V3} from '../../game-lighting-history-shared/depth-space';

// A separate explanation for complete narration that outlasts a native demo.
// Its duration is explanation time. It never extends or loops actual footage.
export function part1HistoryContract(mode:'silhouette'|'thin-blade') {
 const p=createSignal(0),space=depthSpace(()=>-12+5*p(),[0,170],1),node=new Node({});
 const at=(a:number,b:number)=>Math.max(0,Math.min(1,(p()-a)/(b-a)));
 node.add(<Txt y={-265} text={mode==='silhouette'?'과거와 현재가 같은 표면일까?':'얇은 경계 · 새로 드러난 배경'} fontFamily={P.font} fontSize={46} fontWeight={700} fill={P.title}/>);
 const xs=[-470,470];
 xs.forEach((x,i)=>{
  node.add(space.shadow(x,0,600,150));
  node.add(space.box(x,0,0,570,230,28,P.surfaceSide));
  node.add(space.box(x,0,31,520,180,8,'#496166'));
  node.add(space.label(i===0?'과거 표면':'현재 표면',x,-105,210,34,P.ink));
  const move=()=>i===0?0:160*at(.15,.68),base=()=>x-70+move();
  if(mode==='silhouette'){
   node.add(space.box(base,0,45,125,120,115,'#b18e58'));
  } else {
   node.add(space.path(():V3[]=>[[base()-80,0,105],[base()+60,-65,105],[base()+105,10,105]],P.orange));
  }
  node.add(space.path(():V3[]=>[[x-125,-55,47],[x-35,-55,47],[x-35,55,47],[x-125,55,47],[x-125,-55,47]],P.red,()=>at(i?.45:.03,i?.85:.27)));
 });
 node.add(space.path(():V3[]=>[[-125,0,65],[135,0,65]],P.teal,()=>at(.3,.65)));
 node.add(<Txt y={267} text={'대응 위치를 찾기 → 같은 표면인지 확인'} fontFamily={P.font} fontSize={35} fill={P.ink}/>);
 node.add(<Txt y={332} text={'설명용 공간 모델 · 게임 내부 값이나 측정 결과 아님'} fontFamily={P.font} fontSize={24} fill={P.muted}/>);
 return {node,reset:(progress:number)=>p(Math.max(0,Math.min(1,progress)))};
}
