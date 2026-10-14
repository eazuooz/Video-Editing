import {Circle,Node,Txt} from '@motion-canvas/2d';
import {all,createSignal,linear} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {depthSpace} from '../../game-lighting-history-shared/depth-space';

// Independent16-address/5-required-page teaching example. No game measurements,
// UE defaults or triangle-ray renderer are claimed by these small diagrams.
export function vsmModel(){
 const node=new Node({}),mode=createSignal(0),progress=createSignal(0);
 const text=(t:string|(()=>string),x:number,y:number,size=29,color:string=P.ink)=>new Txt({text:t,x,y,fontSize:size,fontFamily:P.font,fill:color,textAlign:'center'});
 const layer=(i:number)=>{const n=new Node({opacity:()=>Math.round(mode())===i?1:0});node.add(n);return n;};
 const needed=[1,2,5,6,10],nextNeeded=[2,3,6,7,11];
 const coords=(i:number):[number,number]=>[-180+(i%4)*120,-180+Math.floor(i/4)*120];
 function grid(n:Node,origin:[number,number],fill:(i:number)=>string,alpha:(i:number)=>number=()=>1,scale=.85){
  const s=depthSpace(()=>20,origin,scale);
  for(let i=0;i<16;i++){const[x,y]=coords(i),p=new Node({opacity:()=>alpha(i)});p.add(s.box(x,y,0,108,108,18,fill(i)));p.add(s.label(String(i),x,y,44,24));n.add(p);}
  return s;
 }
 const count=()=>Math.min(5,Math.floor(progress()*5.999));

 const a=layer(0),s=depthSpace(()=>20,[0,145],1);
 a.add(s.box(0,0,0,650,340,16,P.surfaceTop));
 a.add(s.box(-115,0,16,80,80,155,P.orange));
 a.add(s.box(195,70,16,60,60,30,P.teal));
 a.add(s.box(-330,-90,16,55,55,70,P.yellow));
 a.add(s.path(()=>[[-330,-90,100],[-115,0,150]],P.yellow,progress));
 a.add(s.path(()=>[[195,70,60],[-115,0,150]],P.teal,progress));
 a.add(text('광원 시점: 가장 가까운 깊이',-390,-195,29,P.yellow));
 a.add(text('화면 표면 → 광원 공간 → 깊이 비교',350,-150,28,P.teal));
 a.add(text(()=>progress()<.5?'저장 깊이 d = 4':'표면 깊이 z = 7 > d = 4 → 가림',0,300,32,P.yellow));
 a.add(text('독립 깊이 값 예 · 투영/바이어스 규칙은 실제 엔진 자원에서 확인',0,350,23,P.muted));

 const b=layer(1);
 grid(b,[-410,110],()=>P.surfaceTop,()=>1,.8);
 grid(b,[410,110],i=>needed.includes(i)?P.teal:P.surfaceTop,i=>needed.includes(i)?1:.22,.8);
 b.add(text('전체 영역을 세밀하게 저장',-410,-200,30,P.orange));
 b.add(text('지금 보이는 표면이 참조하는 영역',410,-200,28,P.teal));
 const near=depthSpace(()=>20,[410,110],.8);
 b.add(near.box(()=>-240+progress()*100,265,20,65,50,40,P.green));
 b.add(near.path(()=>[[-240,265,75],[-60,-60,50]],P.green,progress));
 b.add(text('넓은 주소 범위 ≠ 모든 곳에 같은 실제 작업',0,300,30,P.yellow));
 b.add(text('가까운 작은 그림자도 높은 표본 밀도가 필요할 수 있음',0,350,25,P.muted));

 function mapping(n:Node,numeric:boolean){
  const vs=grid(n,[-430,100],i=>needed.includes(i)?P.teal:P.surfaceTop,i=>needed.includes(i)?1:.3,.82),ps=depthSpace(()=>20,[430,100],.95);
  for(let j=0;j<5;j++){
   const y=-220+j*110,x=20;
   n.add(new Node({opacity:()=>j<count()?1:.16,children:[ps.box(x,y,0,165,90,32,P.orange),ps.label(`P${j}`,x,y,57,27)]}));
   const[vx,vy]=coords(needed[j]);
   // Both endpoint projections are converted to the common screen plane.
   const start=vs.point(vx,vy,38),end=ps.point(x,y,45),linkSpace=depthSpace(()=>0,[0,0],1);
   n.add(linkSpace.path(()=>[[start[0],start[1]/.48,0],[end[0],end[1]/.48,0]],P.teal,()=>Math.max(0,Math.min(1,progress()*5-j))));
  }
  n.add(text('가상 주소: 논리적 범위',-430,-210,31,P.teal));n.add(text('물리 페이지: 실제 저장',430,-210,31,P.orange));
  n.add(text(numeric?()=>`가상16칸 · 현재 필요5칸 · 배정 ${count()}개`:'필요 주소 찾기 → 페이지 배정 → 그 부분의 깊이 그리기',0,300,numeric?33:27,P.yellow));
  n.add(text('16과5는 설명용 숫자 · 실제 해상도/페이지 수/비용 측정값 아님',0,350,24,P.muted));
 }
 mapping(layer(2),false);mapping(layer(3),true);

 const e=layer(4),s5=grid(e,[0,105],()=>P.surfaceTop,()=>.35,1);
 for(let i=0;i<16;i++){
  const[x,y]=coords(i),old=needed.includes(i),fresh=nextNeeded.includes(i)&&!old,reused=old&&nextNeeded.includes(i);
  e.add(new Node({opacity:()=>progress()<.35?(old?1:0):(nextNeeded.includes(i)?1:old?.22:0),children:[s5.box(x,y,19,108,108,20,old?P.green:P.orange)]}));
  if(reused||fresh)e.add(new Node({opacity:()=>progress()>.7&&progress()<.93?1:0,children:[s5.box(x,y,40,108,108,9,P.red)]}));
 }
 e.add(s5.box(()=>-280+Math.min(progress()/.35,1)*200,270,20,55,45,40,P.teal));
 e.add(s5.path(()=>[[-280,270,70],[-80,270,70]],P.teal,()=>Math.min(progress()/.35,1)));
 e.add(text(()=>progress()<.35?'카메라 이동: 새 주소를 참조':progress()<.7?'현재5개: 재사용2 + 새 페이지3':progress()<.93?'광원 변경: 그 광원의 캐시 무효화':'변경된 깊이를 다시 그려 갱신',0,-200,32,P.yellow));
 e.add(text('초록 재사용 · 주황 새로 그리기 · 빨강 무효화',0,300,29,P.ink));
 e.add(text('보이지 않는 기존 페이지의 보존/퇴거는 별도 예산 · 물체 변경은 겹치는 영역을 무효화',0,350,23,P.muted));

 const f=layer(5),sm=depthSpace(()=>20,[0,120],1);
 f.add(sm.box(0,0,0,650,350,16,P.surfaceTop));
 f.add(sm.box(0,-90,18,160,70,135,P.orange));
 f.add(sm.box(-250,190,18,65,60,28,P.teal));
 for(let i=0;i<5;i++){
  const x=-160+i*80;f.add(sm.path(()=>[[-250,190,55],[x,-240,240]],i<3?P.red:P.teal,progress));
  f.add(new Circle({position:sm.point(-250+(x+250)*.53,190+(-240-190)*.53,55+(240-55)*.53),size:15,fill:i<3?P.red:P.teal,opacity:progress}));
 }
 f.add(text('SMRT: 광원 방향 표본 → 그림자 맵 깊이 검사',0,-200,32,P.yellow));
 f.add(text('깊이 자료로 가려짐을 어림 · 장면 삼각형 전체 교차와 구별',0,300,28,P.teal));
 f.add(text('5개의 선은 독립 표본 도식 · 실제 엔진의 표본 수/반그림자 계산을 재현한 것이 아님',0,350,23,P.muted));

 const g=layer(6);
 grid(g,[-410,110],i=>needed.includes(i)?P.green:P.surfaceTop,i=>needed.includes(i)?1:.2,.8);
 const gs=grid(g,[410,110],i=>needed.includes(i)?P.green:P.surfaceTop,i=>needed.includes(i)?1:.2,.8);
 const dirty=[1,5,10];for(let j=0;j<dirty.length;j++){const[x,y]=coords(dirty[j]);g.add(new Node({opacity:()=>Math.max(0,Math.min(1,progress()*3-j)),children:[gs.box(x,y,19,108,108,9,P.red)]}));}
 g.add(text('정적 조건: 이미 그린 깊이 재사용',-410,-200,28,P.green));g.add(text('변경 조건: 영향 영역 다시 그리기',410,-200,28,P.red));
 g.add(text(()=>`해상도 + 새 페이지 + 재사용 + 무효화 · 독립 예 ${Math.min(3,Math.floor(progress()*3.999))}개`,0,300,27,P.yellow));
 g.add(text('직접광의 그림자 질의 · 간접광 전체를 계산하는 기능이 아님',0,350,25,P.muted));
 const controls={mode,progress},poses=Array.from({length:7},(_,i)=>[{mode:i,progress:0},{mode:i,progress:1}]).flat();
 return{node,controls,poses,reset(p:Record<string,number>){mode(p.mode);progress(p.progress);},*transition(p:Record<string,number>,seconds:number){yield*all(mode(p.mode,seconds,linear),progress(p.progress,seconds,linear));}};
}
