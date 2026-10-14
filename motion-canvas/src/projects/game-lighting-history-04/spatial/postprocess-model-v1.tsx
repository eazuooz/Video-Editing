import {Line,Node,Txt} from '@motion-canvas/2d';
import {all,createSignal,linear} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {depthSpace} from '../../game-lighting-history-shared/depth-space';

// Worked teaching examples, not UE's filmic curve or captured game buffers.
export function postprocessModel(){
 const node=new Node({}),mode=createSignal(0),p=createSignal(0);
 const layer=(i:number)=>{const n=new Node({opacity:()=>Math.round(mode())===i?1:0});node.add(n);return n;};
 const text=(t:string|(()=>string),x:number,y:number,size=30,c:string=P.ink)=>new Txt({text:t,x,y,fontSize:size,fontFamily:P.font,fill:c,textAlign:'center'});
 const note=(n:Node,t:string)=>n.add(text(t,0,350,23,P.muted));
 const a=layer(0),s=depthSpace(()=>16,[0,110],1),xs=[-540,0,540],values=[2,4,16];
 for(let i=0;i<3;i++){
  a.add(s.box(xs[i],40,0,300,230,20,P.surfaceTop));
  a.add(s.box(xs[i]-65,40,20,85,100,()=>values[i]*11*(1-p())+values[i]/(1+values[i])*160*p(),P.orange));
  a.add(text('HDR '+values[i],xs[i],-225,32,P.yellow));
  a.add(text(()=>p()<.05?'압축 전':('y = '+(values[i]/(1+values[i])).toFixed(3)),xs[i],275,31,P.ink));
 }
 a.add(text('수치 예: y = x / (1 + x)',0,-270,32,P.teal));
 note(a,'HDR 값을 표시 범위로 압축 · 독립 수치 예이며 UE의 ACES 곡선을 재현한 것이 아님');

 const b=layer(1),bs=depthSpace(()=>16,[0,115],1),input=[.25,1,4];
 for(const [base,kind] of [[-440,'노출 × 2'],[440,'톤 매핑 x/(1+x)']] as [number,string][]){
  b.add(bs.box(base,25,0,630,320,20,P.surfaceTop));b.add(text(kind,base,-235,34,P.yellow));
  for(let i=0;i<3;i++){
   const x=base+(i-1)*170,out=base<0?input[i]*2:input[i]/(1+input[i]);
   b.add(bs.box(x,25,20,70,110,()=>50*((1-p())*input[i]+p()*out),base<0?P.orange:P.teal));
   b.add(text(()=>((1-p())*input[i]+p()*out).toFixed(2),x,260,27));
  }
 }
 note(b,'왼쪽은 비례 · 오른쪽은 비선형 압축 · 비교할 때 노출·카메라·조명 조건을 통제');

 const c=layer(2),cs=depthSpace(()=>18,[0,90],1);
 c.add(text('화면의 블룸',-440,-230,33,P.yellow));c.add(text('표면 사이의 간접광',440,-230,33,P.teal));
 for(let j=0;j<3;j++)for(let i=0;i<3;i++){
  const k=i===1&&j===1?1:.1+.25*p();
  c.add(new Node({opacity:()=>i===1&&j===1?1:k,children:[cs.box(-440+(i-1)*115,(j-1)*110,0,105,100,20,P.yellow)]}));
 }
 c.add(cs.box(300,40,0,220,230,30,P.surfaceTop));c.add(cs.box(650,-100,0,200,35,220,P.teal));
 c.add(cs.box(200,-160,30,55,55,60,P.yellow));
 c.add(cs.path(()=>[[200,-160,90],[300,40,35],[650,-100,135]],P.orange,p));
 c.add(text('이웃 픽셀로 번짐 ≠ 다른 면에 빛이 도달',0,285,32));
 note(c,'블룸의 픽셀 분포와 빛의 경로를 구별 · 실제 셰이더 출력이 아닌 원리 설명');

 const d=layer(3),ds=depthSpace(()=>18,[0,130],.95);
 d.add(text('초점과 거리',-470,-235,34,P.yellow));d.add(text('노출 시간 동안의 이동',470,-235,34,P.yellow));
 for(let i=0;i<3;i++){
  d.add(ds.box(-470,-160+i*170,0,290,80,50,i===1?P.teal:P.surfaceTop));
  d.add(ds.label(['가까움','초점면','멀어짐'][i],-470,-160+i*170,105,27,i===1?P.teal:P.muted));
  if(i!==1)for(let k=-1;k<=1;k+=2)d.add(new Node({opacity:()=>.25*p(),children:[ds.box(-470+k*25,-160+i*170,20,290,80,40,P.muted)]}));
 }
 d.add(ds.box(470,20,0,620,250,20,P.surfaceTop));
 for(let i=0;i<5;i++)d.add(new Node({opacity:()=>i===4?1:.13*p(),children:[ds.box(()=>210+i*90+100*p(),20,20,70,90,80,P.orange)]}));
 d.add(text('켜고 끈 조건에서 작은 오류의 보임도 달라짐',0,285,31));
 note(d,'초점면과 잔상을 구별하는 원리도 · 실제 게임의 필터나 노출 시간 측정은 아님');

 const e=layer(4),es=depthSpace(()=>16,[0,115],1);
 const labels=['sRGB 입력','선형에서 계산','표시 변환'],cols=[P.surfaceTop,P.teal,P.orange];
 for(let i=0;i<3;i++){const x=(i-1)*540;e.add(es.box(x,0,0,350,270,65,cols[i]));e.add(text(labels[i],x,-230,32,P.yellow));}
 e.add(es.path(()=>[[-315,0,105],[-210,0,105]],P.yellow,p));e.add(es.path(()=>[[210,0,105],[315,0,105]],P.yellow,p));
 for(const[x,t]of[[-540,'0.500'],[0,'0.214 × 2 = 0.428'],[540,'≈ 0.686']]as[number,string][])e.add(text(t,x,260,29));
 note(e,'sRGB 구간별 함수로 계산 · 입력 디코드와 최종 인코드를 한 번씩 적용한 수치 예');

 const f=layer(5),fs=depthSpace(()=>14,[0,90],1),roles=['기하','가시성','조명','재질','복원','후처리'];
 for(let i=0;i<6;i++){const x=-650+i*260;f.add(fs.box(x,0,0,180,210,35+i*10,i%2?P.teal:P.surfaceTop));f.add(fs.label(roles[i],x,0,150,27));if(i<5)f.add(fs.path(()=>[[x+110,0,100],[x+150,0,100]],P.orange,p));}
 f.add(text('최종 픽셀은 여러 자료와 처리의 연결',0,285,33,P.yellow));
 note(f,'각 역할의 관계도 · 모든 엔진에 공통인 고정 패스 순서로 해석하지 않기');
 const poses=Array.from({length:6},(_,i)=>[{mode:i,progress:0},{mode:i,progress:1}]).flat();
 return{node,poses,reset(v:Record<string,number>){mode(v.mode);p(v.progress);},*transition(v:Record<string,number>,seconds:number){yield*all(mode(v.mode,seconds,linear),p(v.progress,seconds,linear));}};
}
