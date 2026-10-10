import {Circle,Line,Node,Txt} from '@motion-canvas/2d';
import {all,createSignal,linear} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {depthSpace,V3} from '../../game-lighting-history-shared/depth-space';
import {wallBlocks} from './ddgi-math-v1';
import {replacementProbability,streamCandidate} from './restir-math-v1';
export function restirModel(){
 const node=new Node({}),mode=createSignal(0),progress=createSignal(0);
 const text=(t:string|(()=>string),x:number,y:number,size=29,c:string=P.ink)=>new Txt({text:t,x,y,fontSize:size,fontFamily:P.font,fill:c,textAlign:'center'});
 const active=(n:number)=>()=>Math.abs(mode()-n)<.1?1:0;
 const add=(...ns:Node[])=>ns.forEach(n=>node.add(n));
 const streamed=()=>{let r={sample:null,weightSum:0,candidates:0} as {sample:string|null,weightSum:number,candidates:number};const n=Math.floor(progress()*4+1e-6);for(let i=0;i<n;i++)r=streamCandidate(r,`L${i+1}`,[1,3,1,1][i],.5);return r;};
 const base=new Node({opacity:()=>mode()<2?1:0}),s=depthSpace(()=>26,[-70,60],1);
 base.add(s.box(-350,0,0,440,290,15,P.surfaceTop));
 for(let i=0;i<4;i++){
  const x=-500+i*100,y=-75+(i%2)*70;
  base.add(s.box(x,y,18,42,42,52,i===0?P.teal:P.orange));
  base.add(s.label(`L${i+1}`,x,y,105,27,i===0?P.teal:P.orange));
  base.add(s.path(()=>[[x,y,65],[70,35,100]],i===0?P.teal:P.orange,()=>progress(),[9,6]));
 }
 // Open projected reservoir walls, then selected token: explicit occlusion.
 base.add(s.box(70,35,70,160,145,12,P.surfaceTop));
 base.add(s.box(70,-35,80,160,10,110,P.surfaceFront));
 base.add(s.box(145,35,80,10,145,110,P.surfaceFront));
 const tokenA=s.box(70,35,95,44,44,45,P.teal),tokenB=s.box(70,35,95,44,44,45,P.orange);
 tokenA.opacity(()=>mode()===1&&streamed().sample==='L1'?1:0);tokenB.opacity(()=>mode()===0||streamed().sample==='L2'?1:0);base.add([tokenA,tokenB]);
 base.add(s.label('선택 후보 하나',70,35,225,31,P.yellow));
 const summary=text(()=>`선택 ${streamed().sample??'없음'} · M=${streamed().candidates} · W=${streamed().weightSum}`,270,285,27,P.teal);summary.opacity(()=>mode()===1?1:0);base.add(summary);
 base.add(text('후보 집합 → 가중 선택',-440,245,31,P.orange));
 base.add(text('선택 후보 + 요약',260,245,31,P.teal));
 base.add(text('2020 직접광 · 후속 GI/PT는 별도 변형',0,325,27,P.muted));
 add(base);
 const probability=new Node({opacity:active(2)}),r=depthSpace(()=>22,[0,75],1);
 probability.add(r.box(-390,0,0,135,140,70,P.teal));probability.add(r.box(-170,0,0,135,140,210,P.orange));
 probability.add([text('이전 w=1',-385,230,31,P.teal),text('새 w=3',-170,230,31,P.orange)]);
 probability.add(text('누적 W: 1 → 4',180,-165,34,P.yellow));
 probability.add(text(()=>`P(새 후보) = 3 / (1+3) = ${replacementProbability(1,3)}`,180,-100,31,P.orange));
 const trials=[.125,.375,.625,.875];
 for(let i=0;i<4;i++){
  const chosen=streamCandidate({sample:'A',weightSum:1,candidates:1},'B',3,trials[i]).sample;
  const x=40+i*110;
  probability.add(r.box(x,10,0,76,76,()=>40+progress()*35,chosen==='B'?P.orange:P.teal));
  probability.add(text(`${chosen}\nu=${trials[i]}`,x,220,25,chosen==='B'?P.orange:P.teal));
 }
 probability.add(text('등간격 u 네 값으로 본 확률 예 · 실제 난수 실행 통계 아님',30,310,24,P.muted));add(probability);
 const correction=new Node({opacity:active(3)}),c=depthSpace(()=>25,[0,75],1);
 for(const[x,t,color]of[[-420,'후보 분포 q',P.teal],[0,'목표 기여',P.orange],[420,'대표 후보 수 M',P.green]] as[number,string,string][]){
  correction.add(c.box(x,0,0,210,160,100,color));correction.add(text(t,x,225,32,color));
 }
 correction.add(text('선택 확률 ≠ 완성 조명 추정',0,-150,39,P.yellow));
 // Separate estimator inputs enter the comparison in sequence. This shows
 // their distinct roles without inventing an incomplete ReSTIR estimator.
 correction.add(c.path(()=>[[-300,0,130],[-120,0,130]],P.teal,()=>Math.min(1,progress()*2)));
 correction.add(c.path(()=>[[120,0,130],[300,0,130]],P.orange,()=>Math.max(0,progress()*2-1)));
 correction.add(text(()=>progress()<.5?'후보 분포를 반영':'대표 후보 수까지 반영',0,-95,30,P.muted));
 correction.add(text('최종 추정의 정규화·가시성·재사용 보정은 별도로 필요',0,315,28,P.muted));add(correction);
 const reuse=new Node({opacity:active(4)}),u=depthSpace(()=>25,[0,110],1);
 reuse.add(u.box(-360,120,0,360,200,15,P.surfaceTop));
 reuse.add(u.box(330,-80,150,360,200,15,P.surfaceTop));
 for(let i=0;i<3;i++){reuse.add(u.box(-490+i*130,120,20,65,65,40,i===1?P.teal:P.orange));reuse.add(u.box(200+i*130,-80,170,65,65,40,P.green));}
 reuse.add(u.path(()=>[[-490,120,65],[-360,120,65]],P.orange,()=>progress()));
 reuse.add(u.path(()=>[[330,-80,210],[-360,120,65]],P.green,()=>progress(),[8,6]));
 reuse.add([text('현재 표면 + 이웃',-400,270,31,P.teal),text('이전 프레임 후보',420,220,31,P.green)]);
 reuse.add(text('법선 · 위치 · 가시성의 유효성 다시 판단',0,310,29,P.yellow));add(reuse);
 const door=new Node({opacity:active(5)}),d=depthSpace(()=>28,[0,40],1);
 const q:V3=[-180,90,20],light:V3=[180,-70,120],doorY=()=>280*(1-progress());
 door.add(d.box(0,0,-15,600,380,15,P.surfaceTop));
 door.add(d.box(...light,45,45,40,P.orange));
 door.add(d.path(()=>[light,q],P.orange,1,[8,6]));
 door.add(d.box(0,doorY,0,24,300,160,P.surfaceFront));
 door.add(d.box(...q,70,70,30,P.teal));
 door.add(text('재사용한 후보',-400,-150,32,P.green));
 door.add(text(()=>wallBlocks(q,light,doorY())?'현재 가시성: 가려짐':'현재 가시성: 통과',390,225,34,P.orange));
 // Color is fixed by role; the geometric intersection controls the decision.
 door.add(text('이전 밝기를 그대로 복사하지 않기',0,310,30,P.yellow));add(door);
 const pipeline=new Node({opacity:active(6)}),f=depthSpace(()=>20,[0,65],1);
 const stages=['후보','선택','가시성','조명','필터'];
 for(let i=0;i<5;i++){const x=-580+i*290,color=i<2?P.orange:i===4?P.teal:P.green;pipeline.add(f.box(x,0,i===4?45:0,150,150,100,color));pipeline.add(text(stages[i],x,235,34,color));if(i<4)pipeline.add(f.path(()=>[[x+85,0,65],[x+200,0,65]],P.line,()=>progress()));}
 pipeline.add(text('표본 선택과 영상 필터링은 서로 다른 역할',0,310,30,P.yellow));add(pipeline);
 add(text('원리 비교용 입체 도식 · 실제 게임 성능/완전한 ReSTIR 추정기 아님',0,352,24,P.muted));
 const controls={mode,progress},poses=Array.from({length:7},(_,i)=>[{mode:i===0?0:i===1?1:i,progress:0},{mode:i===0?0:i===1?1:i,progress:1}]).flat();
 return{node,controls,poses,reset(p:Record<string,number>){mode(p.mode??0);progress(p.progress??0);},*transition(p:Record<string,number>,seconds:number){yield*all(mode(p.mode??0,seconds,linear),progress(p.progress??0,seconds,linear));}};
}
