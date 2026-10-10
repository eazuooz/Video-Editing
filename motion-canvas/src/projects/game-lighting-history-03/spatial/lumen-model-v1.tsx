import {Circle,Line,Node,Txt} from '@motion-canvas/2d';
import {all,createSignal,linear} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {depthSpace} from '../../game-lighting-history-shared/depth-space';

// Original role diagram grounded in Epic's Surface Cache / tracing docs.
// Cards below are exploded capture representations, not scene collision walls.
export function lumenModel(){
 const node=new Node({}),mode=createSignal(0),progress=createSignal(0);
 const label=(text:string|(()=>string),x:number,y:number,size=28,color:string=P.ink)=>new Txt({text,x,y,fontFamily:P.font,fontSize:size,fill:color,textAlign:'center'});
 const layer=(i:number)=>{const n=new Node({opacity:()=>Math.round(mode())===i?1:0});node.add(n);return n;};
 const room=(origin:[number,number],scale=.95,illumination?:()=>number)=>{
  const s=depthSpace(()=>22,origin,scale),n=new Node({});
  n.add(s.box(0,0,0,400,270,15,P.surfaceTop));
  if(illumination)n.add(new Node({opacity:illumination,children:[s.polygon(()=>[[-195,-120,16],[185,-120,16],[185,120,16],[-195,120,16]],P.orange)]}));
  n.add(s.box(0,-125,15,400,20,185,P.surfaceFront));
  n.add(s.box(190,0,15,20,270,185,P.surfaceSide));n.add(s.box(-75,-30,15,90,90,60,P.teal));
  return{n,s};
 };
 const m0=layer(0),r0=room([-500,90],.85);m0.add(r0.n);
 const c0=depthSpace(()=>22,[40,75],.8);
 for(let i=0;i<3;i++)m0.add(c0.box(-110+i*115,0,20,90,190,8,P.orange));
 const q0=depthSpace(()=>22,[590,75],.8);m0.add(q0.box(0,0,0,250,190,65,P.teal));
 m0.add(label('장면 추적',-500,-180,32,P.teal));m0.add(label('표면 조명 저장',40,-180,32,P.orange));m0.add(label('최종 질의',590,-180,32));
 m0.add(new Line({points:[[-260,80],[-150,80]],stroke:P.teal,lineWidth:4,endArrow:true,end:progress}));
 m0.add(new Line({points:[[260,80],[405,80]],stroke:P.orange,lineWidth:4,endArrow:true,end:progress}));
 m0.add(label('추적 → 저장 → 읽기 · 역할을 분리한 도식',0,305,28,P.muted));

 const m1=layer(1),r1=room([280,120]);m1.add(r1.n);
 const ss=depthSpace(()=>22,[-480,30],.8);m1.add(ss.box(0,0,0,300,220,8,P.surfaceTop));
 m1.add(new Line({points:[[-560,-30],[-380,70]],stroke:P.teal,lineWidth:5,endArrow:true}));
 m1.add(new Circle({x:-380,y:70,size:24,fill:P.orange}));
 m1.add(new Line({points:[[-360,85],[0,130],r1.s.point(90,-120,100)],stroke:P.orange,lineWidth:5,endArrow:true,end:progress}));
 m1.add(label('이미 그린 화면',-480,-195,32,P.teal));m1.add(label('화면 밖 → 장면 표현',280,-195,32,P.orange));
 m1.add(label('화면에서 실패한 경로를 다른 표현으로 이어감',0,315,28));

 const m2=layer(2),software=room([-450,125],.9),hardware=room([450,125],.9);m2.add(software.n);m2.add(hardware.n);
 const points=[[-135,70,20],[-80,25,50],[0,-15,65],[70,-75,95]] as const;
 for(let i=0;i<points.length;i++)m2.add(new Circle({position:software.s.point(points[i][0],points[i][1],points[i][2]),size:()=>16+(i+1)*9*progress(),stroke:P.teal,lineWidth:2,fill:null}));
 m2.add(hardware.s.polygon(()=>[[-160,-125,40],[120,-125,40],[20,-125,170]],P.orange));
 m2.add(hardware.s.path(()=>[[-140,120,30],[15,-125,110]],P.orange,progress));
 m2.add(label('거리장 경로',-450,-195,34,P.teal));m2.add(label('삼각형 경로',450,-195,34,P.orange));
 m2.add(label('정확한 엔진 버전 · 모드 · 장면 표현을 함께 기록',0,320,29));

 const m3=layer(3),r3=room([-320,145]);m3.add(r3.n);
 const cards=depthSpace(()=>22,[420,90],.85);
 for(let i=0;i<3;i++)m3.add(new Node({opacity:progress,children:[cards.box(-130+i*125,0,40+i*35,100,190,8,i===1?P.orange:P.teal)]}));
 m3.add(new Line({points:[[-20,-25],[150,-25]],stroke:P.orange,lineWidth:4,endArrow:true,end:progress}));
 m3.add(label('실제 메시 표면',-320,-195,32));m3.add(label('방향별 캡처 카드',420,-195,32,P.orange));
 m3.add(label('카드: 표면 정보를 담는 캡처 위치 · 물리 벽과 구분',0,320,28));

 const m4=layer(4),r4=room([-430,170]);m4.add(r4.n);
 const cache=depthSpace(()=>22,[400,80],.85);
 m4.add(cache.box(0,0,0,340,200,8,P.orange));m4.add(cache.box(0,0,100,340,200,8,P.teal));
 const hit=r4.s.point(60,-125,120);
 m4.add(new Line({points:[r4.s.point(-120,120,25),hit],stroke:P.teal,lineWidth:5,endArrow:true,end:()=>Math.min(1,progress()*2)}));
 m4.add(new Line({points:[hit,cache.point(0,0,100)],stroke:P.orange,lineWidth:5,endArrow:true,end:()=>Math.max(0,progress()*2-1)}));
 m4.add(label('표면을 찾는 추적',-430,-185,31,P.teal));m4.add(label('저장된 조명을 읽음',400,-185,31,P.orange));
 m4.add(label('청록: 위치 찾기 · 주황: 캐시 조회',0,325,30));

 const m5=layer(5),r5a=room([-450,145]),r5b=room([450,145],.95,progress);m5.add(r5a.n);m5.add(r5b.n);
 m5.add(r5b.s.path(()=>[[-160,-120,150],[0,-120,115],[70,70,17]],P.orange,progress));
 m5.add(label('간접광 변화 전',-450,-195,31,P.muted));m5.add(label('간접광 변화 후',450,-195,31,P.orange));
 m5.add(label('공개 시연의 관찰 연결 도식 · 내부 패스 비용의 증명 아님',0,320,26));

 const m6=layer(6),r6=room([-360,130],1);m6.add(r6.n);const c6=depthSpace(()=>22,[460,100],.9);
 m6.add(c6.box(0,0,0,320,200,12,P.orange));m6.add(new Line({points:[[-60,40],[260,40]],stroke:P.teal,lineWidth:5,endArrow:true,end:progress}));
 m6.add(label('Nanite · 메시 캡처 지원',-360,-195,31,P.teal));m6.add(label('Lumen · 조명 갱신',460,-195,31,P.orange));
 m6.add(label('지원 관계 ≠ 기능의 동일성 · Nanite 없이도 Lumen 경로 존재',0,325,27));
 const controls={mode,progress},poses=Array.from({length:7},(_,i)=>[{mode:i,progress:0},{mode:i,progress:1}]).flat();
 return{node,controls,poses,reset(p:Record<string,number>){mode(p.mode);progress(p.progress);},*transition(p:Record<string,number>,seconds:number){yield*all(mode(p.mode,seconds,linear),progress(p.progress,seconds,linear));}};
}
