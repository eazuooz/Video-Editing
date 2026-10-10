import {Circle,Line,Node,Txt} from '@motion-canvas/2d';
import {all,createSignal,linear} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {depthSpace} from '../../game-lighting-history-shared/depth-space';

// Independent examples. Depth0 is near and1 is far unless explicitly reversed.
export function cullingModelV2(){
 const node=new Node({}),mode=createSignal(0),progress=createSignal(0);
 const text=(t:string|(()=>string),x:number,y:number,size=29,color:string=P.ink)=>new Txt({text:t,x,y,fontFamily:P.font,fontSize:size,fill:color,textAlign:'center'});
 const layer=(i:number)=>{const n=new Node({opacity:()=>Math.round(mode())===i?1:0});node.add(n);return n;};
 const s=depthSpace(()=>22,[0,120],.9);
 const floor=()=>s.box(0,40,0,1050,560,14,P.surfaceTop);
 const m0=layer(0);m0.add(floor());
 m0.add(s.polygon(()=>[[-45,-250,16],[-300,300,16],[300,300,16],[45,-250,16]],'#164f4e',P.teal));
 for(const [x,y,inside]of[[-120,40,1],[160,200,1],[430,30,0]]as const){
  const a=new Node({opacity:()=>inside?1:1-progress()*.85,children:[s.box(x,y,15,85,85,100,inside?P.teal:P.muted)]});m0.add(a);
 }
 m0.add(s.box(0,-220,15,65,45,42,P.orange));
 m0.add(text('시야 절두체: 공간 경계 검사',0,-195,34,P.teal));
 m0.add(text('회색: 시야 밖 · 청록: 시야 안 후보',0,310,30,P.yellow));
 m0.add(text('시야 안에 있어도 다른 물체에 가릴 수 있음',0,355,25,P.muted));

 const m1=layer(1);m1.add(floor());
 // Reveal the hidden candidate through an explicitly transparent wall, then make the wall opaque.
 m1.add(s.box(0,-100,14,105,95,90,P.orange));
 m1.add(new Node({opacity:()=>.22+.78*progress(),children:[s.box(0,160,14,480,25,300,P.surfaceFront)]}));
 m1.add(s.path(()=>[[0,290,70],[0,175,70]],P.teal,progress));
 m1.add(text('큰 벽 뒤: 시야 안의 가려진 후보',0,-195,33,P.orange));
 m1.add(text(()=>progress()<.5?'벽을 투명하게 표시 · 뒤 물체 위치':'불투명 벽 · 전체 경계 가림 → 제출 생략',0,310,30,P.yellow));
 m1.add(text('독립 가림 예 · 경계 상자는 깊이를 쓰는 벽이 아님',0,355,25,P.muted));

 const m2=layer(2),z=depthSpace(()=>22,[0,120],1);
 for(let j=0;j<4;j++)for(let i=0;i<4;i++){
  const x=-150+i*100,y=-150+j*100,hidden=i<2;
  m2.add(new Node({opacity:()=>hidden?1-progress()*.8:1,children:[z.box(x,y,0,92,92,14,hidden?P.red:P.teal)]}));
  m2.add(z.label(hidden?'×':'•',x,y,30,30,hidden?P.red:P.teal));
 }
 m2.add(text('가능한 경로: 깊이 검사 → 셰이딩',0,-195,34,P.teal));
 m2.add(text('가린 깊이0.3 < 뒤 표본0.8',0,295,31,P.yellow));
 m2.add(text('가려진8표본을 거절하는 독립 예 · 셰이더 조건에 따라 달라짐',0,350,25,P.muted));

 const m3=layer(3),h=depthSpace(()=>22,[-330,115],.9);
 const depths=[.2,.3,.4,.4,.3,.2,.4,.4,.5,.5,.8,.6,.5,.5,.7,.8];
 for(let j=0;j<4;j++)for(let i=0;i<4;i++){const d=depths[j*4+i];m3.add(h.box(-135+i*90,-135+j*90,0,84,84,16,P.surfaceTop));m3.add(h.label(d.toFixed(1),-135+i*90,-135+j*90,34,24));}
 const coarse=depthSpace(()=>22,[250,115],1.05),maxes=[.3,.4,.5,.8];
 for(let j=0;j<2;j++)for(let i=0;i<2;i++){const d=maxes[j*2+i];m3.add(new Node({opacity:progress,children:[coarse.box(-65+i*130,-65+j*130,0,120,120,24,P.teal),coarse.label(d.toFixed(1),-65+i*130,-65+j*130,44,30)]}));}
 m3.add(text('4×4 → 2×2 최대 깊이 요약',0,-195,34,P.teal));
 m3.add(text('near0 / far1 · 후보의 가장 가까운 깊이0.9 > 요약0.8',0,285,27,P.yellow));
 m3.add(text('전체 경계가 덮일 때 거절 · 빈 픽셀의far1은 거절을 막음',0,320,25,P.muted));
 m3.add(text('역깊이near1/far0: min 요약과 비교 방향을 함께 뒤집기',0,365,24,P.muted));

 const m4=layer(4);m4.add(floor());m4.add(s.box(0,-100,14,105,95,100,P.teal));
 m4.add(s.box(()=>-progress()*540,160,14,480,25,300,P.surfaceFront));
 m4.add(new Node({opacity:()=>progress()*.5,children:[s.box(0,160,14,480,25,300,P.red)]}));
 m4.add(text('문이 열림: 현재 가림과 과거 깊이가 달라짐',0,-195,32,P.orange));
 m4.add(text('빨강: 오래된 가림 정보 · 청록: 새로 보이는 물체',0,310,28,P.yellow));
 m4.add(text('과거 깊이만으로 새 물체를 버리지 않기 · 특정 엔진의 해결법 재현 아님',0,355,24,P.muted));

 const m5=layer(5),a=depthSpace(()=>22,[-410,100],.85),b=depthSpace(()=>22,[410,100],.85);
 for(const ss of[a,b])m5.add(ss.box(0,0,0,410,310,16,P.surfaceTop));
 m5.add(a.box(-80,0,16,120,100,110,P.teal));m5.add(a.box(100,50,16,100,100,70,P.muted));
 m5.add(a.path(()=>[[-230,-90,80],[-80,0,80]],P.orange,progress));
 m5.add(b.box(0,-65,16,95,95,70,P.orange));
 m5.add(new Node({opacity:()=>.22+.78*progress(),children:[b.box(0,100,16,300,25,200,P.surfaceFront)]}));
 m5.add(text('BVH: 레이 질의 후보',-410,-195,31,P.teal));m5.add(text('컬링: 렌더 제출 후보',410,-195,31,P.orange));
 m5.add(text('비슷한 절약 목적 · 서로 다른 질의와 실행 위치',0,315,31,P.yellow));
 m5.add(text('원리 비교 도식 · 실제 게임의 내부 작업량 측정이 아님',0,350,24,P.muted));
 const poses=Array.from({length:6},(_,i)=>[{mode:i,progress:0},{mode:i,progress:1}]).flat();
 return{node,poses,reset(p:Record<string,number>){mode(p.mode);progress(p.progress);},*transition(p:Record<string,number>,seconds:number){yield*all(mode(p.mode,seconds,linear),progress(p.progress,seconds,linear));}};
}
