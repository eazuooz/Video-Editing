import {Line,Node,Txt} from '@motion-canvas/2d';
import {all,createSignal,linear} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {depthSpace,V3} from '../../game-lighting-history-shared/depth-space';

// An original explanatory mesh, not a Nanite renderer or actual-footage quota.
// Uniform-grid simplification is illustrative. Nanite's cluster DAG, locked
// group boundaries, conservative errors and streaming are more involved.
export function naniteModelV2(){
 const node=new Node({}),mode=createSignal(0),progress=createSignal(0);
 const label=(text:string|(()=>string),x:number,y:number,size=28,color:string=P.ink)=>new Txt({text,x,y,fontFamily:P.font,fontSize:size,fill:color,textAlign:'center'});
 const height=(x:number,y:number)=>35+65*Math.exp(-(x*x+y*y)/40000)+24*Math.sin(x/80)*Math.cos(y/100);
 const mesh=(origin:[number,number],step:number,color:string,scale=.9)=>{
  const layer=new Node({}),s=depthSpace(()=>22,origin,scale);
  layer.add(s.box(0,0,-12,510,290,12,P.surfaceFront));
  for(let j=0;j<4;j+=step)for(let i=0;i<8;i+=step){
   const x=-240+i*60,y=-120+j*60,x2=x+step*60,y2=y+step*60;
   const a:V3=[x,y,height(x,y)],b:V3=[x2,y,height(x2,y)],c:V3=[x2,y2,height(x2,y2)],d:V3=[x,y2,height(x,y2)];
   layer.add(s.polygon(()=>[a,b,c],color));layer.add(s.polygon(()=>[a,c,d],color));
  }
  return{layer,s};
 };
 const layer=(i:number)=>{const n=new Node({opacity:()=>Math.round(mode())===i?1:0});node.add(n);return n;};
 const m0=layer(0),fine=mesh([-400,50],1,P.teal),coarse=mesh([410,50],2,P.orange);
 m0.add(fine.layer);m0.add(coarse.layer);coarse.layer.opacity(progress);
 m0.add(label('세밀한 원본 표현',-400,-205,32,P.teal));m0.add(label('지금 필요한 표현 선택',410,-205,32,P.orange));
 m0.add(new Line({points:[[-100,70],[100,70]],stroke:P.ink,lineWidth:4,endArrow:true,end:progress}));
 m0.add(label('2020 공개 → 2021 구조 발표 · 이후 기능과 구분',0,285,27,P.muted));

 const m1=layer(1),parts=mesh([-455,90],1,P.teal,.7),simple=mesh([455,90],2,P.orange,.7);
 m1.add(parts.layer);m1.add(simple.layer);simple.layer.opacity(progress);
 const group=depthSpace(()=>22,[0,50],.72);
 for(let i=0;i<4;i++)m1.add(group.box(-100+i*65,0,0,60,190,90,i<2?P.teal:P.orange));
 m1.add(label('클러스터',-455,-195,30));m1.add(label('그룹 경계 일관성',0,-195,30,P.yellow));m1.add(label('단순화 · 재분할',455,-195,30));
 m1.add(new Line({points:[[-230,25],[-165,25]],stroke:P.teal,lineWidth:4,endArrow:true,end:progress}));
 m1.add(new Line({points:[[165,25],[235,25]],stroke:P.orange,lineWidth:4,endArrow:true,end:progress}));
 m1.add(label('독립 격자 예 · 실제 계층 전체의 재현이 아님',0,300,25,P.muted));

 const m2=layer(2),near=mesh([-380,75],1,P.teal),far=mesh([460,75],2,P.orange,.55);
 m2.add(near.layer);m2.add(far.layer);
 const cs=depthSpace(()=>22,[-380,75],.9);
 m2.add(cs.box(()=>-260-progress()*250,200,0,60,50,40,P.green));
 m2.add(new Line({points:[[-280,245],[600,245]],stroke:P.muted,lineWidth:2,endArrow:true,end:progress}));
 m2.add(label('같은 세계 오차 · 화면 크기는 달라짐',0,-210,31,P.yellow));
 m2.add(label('가까운 표면',-380,290,29,P.teal));m2.add(label('먼 표면',460,290,29,P.orange));

 const m3=layer(3),es=depthSpace(()=>18,[-290,90],1);
 const distance=()=>2+progress()*2,error=()=>1000*.01/distance();
 m3.add(es.box(-130,0,0,130,150,150,P.teal));m3.add(es.box(150,0,0,130,150,()=>error()*30,P.orange));
 m3.add(label('eₚ ≈ f · eworld / d',300,-150,40,P.yellow));
 m3.add(label(()=>`f = 1000 px · eworld = 0.01 m\nd ≈ ${distance().toFixed(1)} m`,300,-55,29));
 m3.add(label(()=>`화면 오차 ≈ ${error().toFixed(2)} px`,300,100,38,P.orange));
 m3.add(label('거리 2배 → 투영 오차 ½',300,210,30,P.teal));
 m3.add(label('표시값 반올림 · 핀홀 근사 · 실제 Nanite 선택 규칙의 전부가 아님',0,310,25,P.muted));

 const m4=layer(4),s4=depthSpace(()=>20,[0,120],1.15);
 const edge=(side:number,consistent:boolean)=>{
  const z=()=>45+(side===1&&!consistent?55*(1-progress()):0);
  return s4.polygon(()=>side===0?[[-260,-130,45],[0,-130,45],[0,130,45],[-260,130,45]]:[[0,-130,z()],[260,-130,45],[260,130,45],[0,130,z()]],side===0?P.teal:P.orange);
 };
 m4.add(edge(0,true));m4.add(edge(1,false));
 m4.add(new Line({points:()=>[s4.point(0,-130,45),s4.point(0,130,45)],stroke:P.red,lineWidth:5}));
 m4.add(label('이웃의 서로 다른 표현 수준',0,-205,32,P.yellow));
 m4.add(label(()=>progress()<.98?'불일치한 경계 · 균열':'일관된 그룹 경계',0,270,34, P.ink));
 m4.add(label('경계를 맞춰 움직이는 독립 예 · 실제 그룹 빌드와 구분',0,318,24,P.muted));

 const m5=layer(5),s5=depthSpace(()=>20,[0,115],.95);
 for(let i=0;i<8;i++){
  const x=-420+i*120,chosen=i===2||i===3;
  const page=new Node({children:[s5.box(x,0,0,92,100,65,chosen?P.orange:P.surfaceTop),s5.label(String(i+1),x,0,85,30,chosen?P.orange:P.muted)]});m5.add(page);
  if(chosen)m5.add(new Node({opacity:progress,children:[s5.box(x,220,0,92,100,65,P.teal)]}));
 }
 m5.add(label('선택된 데이터',0,-195,32,P.orange));m5.add(label('메모리에 도착한 데이터',0,290,32,P.teal));
 m5.add(new Line({points:[[0,-20],[0,170]],stroke:P.ink,lineWidth:4,endArrow:true,end:progress}));
 m5.add(label('선택 ≠ 공급 완료 · 페이지/그룹의 의존성은 별도',0,335,23,P.muted));

 const m6=layer(6),geo=mesh([-420,110],1,P.teal,.8),lit=depthSpace(()=>22,[420,110],.85);
 m6.add(geo.layer);m6.add(label('Nanite · 기하',-420,-195,34,P.teal));
 m6.add(lit.box(0,0,0,420,250,20,P.surfaceTop));m6.add(lit.box(0,-100,20,420,20,170,P.surfaceFront));
 m6.add(lit.path(()=>[[-170,0,130],[0,-100,115],[130,20,22]],P.orange,progress));
 m6.add(label('Lumen · 빛',420,-195,34,P.orange));m6.add(label('무엇을 그릴까? ↔ 빛을 어떻게 갱신할까?',0,305,31,P.yellow));
 const controls={mode,progress},poses=Array.from({length:7},(_,i)=>[{mode:i,progress:0},{mode:i,progress:1}]).flat();
 return{node,controls,poses,reset(p:Record<string,number>){mode(p.mode);progress(p.progress);},*transition(p:Record<string,number>,seconds:number){yield*all(mode(p.mode,seconds,linear),progress(p.progress,seconds,linear));}};
}
