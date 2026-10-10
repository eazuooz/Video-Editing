import {Circle,Line,Node,Txt} from '@motion-canvas/2d';
import {all,createSignal,linear} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {depthSpace} from '../../game-lighting-history-shared/depth-space';

// Original, deliberately small cache examples. The numeric recurrence below
// is an educational low-pass filter, never a claimed Lumen implementation.
export function cacheModel(){
 const node=new Node({}),mode=createSignal(0),progress=createSignal(0);
 const label=(text:string|(()=>string),x:number,y:number,size=29,color:string=P.ink)=>new Txt({text,x,y,fontFamily:P.font,fontSize:size,fill:color,textAlign:'center'});
 const layer=(i:number)=>{const n=new Node({opacity:()=>Math.round(mode())===i?1:0});node.add(n);return n;};
 const room=(origin:[number,number],light:()=>number,scale=.9)=>{
  const s=depthSpace(()=>22,origin,scale),n=new Node({});
  n.add(s.box(0,0,0,370,250,15,P.surfaceTop));
  n.add(new Node({opacity:light,children:[s.polygon(()=>[[-180,-115,16],[180,-115,16],[180,115,16],[-180,115,16]],P.orange)]}));
  n.add(s.box(0,-115,15,370,20,180,P.surfaceFront));
  n.add(s.box(175,0,15,20,250,180,P.surfaceSide));
  n.add(s.box(-60,-20,15,85,85,65,P.teal));return{s,n};
 };
 const step=()=>Math.min(4,Math.floor(progress()*4.999)),value=()=>2**(-step());
 const m0=layer(0),direct=room([-430,120],()=>progress()<.12?1:0),cached=room([430,120],value);
 m0.add(direct.n);m0.add(cached.n);
 m0.add(label('직접광: 광원 변화',-430,-195,32,P.teal));m0.add(label('간접광 캐시: 갱신',430,-195,32,P.orange));
 m0.add(label(()=>`독립 예: α = ½ · 갱신 ${step()}회 · 값 ${value().toFixed(4)}`,0,290,31,P.yellow));
 m0.add(label('Cₖ = (1 − α) Cₖ₋₁ + α · 새 값(0) · 실제 엔진 상수 아님',0,340,25,P.muted));

 const m1=layer(1),s1=depthSpace(()=>20,[0,140],.9);
 const target=()=>progress()<.35?-210:210;
 m1.add(s1.box(0,0,0,920,260,15,P.surfaceTop));
 // A deliberately wrong history that remains at the old position.
 m1.add(new Node({opacity:()=>progress()>.35?.65:0,children:[s1.box(-210,0,15,100,100,80,P.red)]}));
 m1.add(s1.box(target,0,15,100,100,80,P.teal));
 m1.add(s1.path(()=>[[-210,0,120],[210,0,120]],P.teal,progress));
 m1.add(label('오래된 대응: 잔상',-430,-180,31,P.red));m1.add(label('현재 표면: 새 자료',430,-180,31,P.teal));
 m1.add(label('안정성 ↔ 변화 반응 · 이동 뒤 과거 값의 신뢰를 재검사',0,320,30,P.yellow));

 const m2=layer(2),s2=depthSpace(()=>22,[0,100],1.05);
 m2.add(s2.box(0,0,0,650,350,15,P.surfaceTop));
 for(let j=0;j<3;j++)for(let i=0;i<5;i++){
  const missing=i===3&&j===1;
  m2.add(s2.box(-240+i*120,-120+j*120,16,112,112,5,missing?'#dd609c':P.teal));
  if(missing)m2.add(new Node({opacity:progress,children:[s2.box(-240+i*120,-120+j*120,22,112,112,8,P.orange)]}));
 }
 m2.add(label('분홍: 커버리지 없음',-420,-200,31,'#dd609c'));
 m2.add(label('자료 표현을 고친 뒤 재확인',420,-200,31,P.orange));
 m2.add(label('밝기만 올려도 없던 표면 정보가 생기지는 않음',0,325,29,P.muted));

 const m3=layer(3),s3=depthSpace(()=>22,[-430,145],.9),s3b=depthSpace(()=>22,[430,145],.9);
 for(const s of[s3,s3b]){m3.add(s.box(0,0,0,350,270,15,P.surfaceTop));m3.add(s.box(0,0,15,12,270,180,P.surfaceFront));}
 m3.add(s3.path(()=>[[-140,100,50],[140,100,50]],P.red,progress));
 m3.add(s3b.path(()=>[[-140,100,50],[-8,100,50]],P.teal,progress));
 m3.add(new Circle({position:s3b.point(-8,100,50),size:20,fill:P.orange,opacity:progress}));
 m3.add(label('성긴 표현: 얇은 벽 누락 예',-430,-185,30,P.red));
 m3.add(label('벽을 담은 표현: 가림 검사',430,-185,30,P.teal));
 m3.add(label('표현 해상도 · 작은 발광체의 표본 예산을 따로 검사',0,325,29,P.yellow));

 const m4=layer(4),a=room([-430,145],()=>1-progress()),b=room([430,145],()=>1);
 m4.add(a.n);m4.add(b.n);
 const ca=depthSpace(()=>22,[-430,145],.9),cb=depthSpace(()=>22,[430,145],.9);
 m4.add(ca.box(-160,200,20,55,45,40,P.green));
 m4.add(cb.box(()=>-160+progress()*230,200,20,55,45,40,P.green));
 m4.add(label('카메라 고정 · 조명만 변경',-430,-200,31,P.orange));
 m4.add(label('조명 고정 · 카메라만 변경',430,-200,31,P.teal));
 m4.add(label('노출 · 후처리 고정 · 두 변수를 한꺼번에 바꾸지 않기',0,325,29,P.muted));

 const m5=layer(5),s5=depthSpace(()=>22,[0,130],1);
 for(let i=0;i<4;i++){
  const x=-330+i*220;
  m5.add(s5.box(x,0,0,175,170,25,P.surfaceTop));
  m5.add(new Node({opacity:()=>i<=step()?1:.2,children:[s5.box(x,0,26,175,170,12,P.orange)]}));
  m5.add(s5.label(String(i+1),x,0,60,34));
 }
 m5.add(label(()=>`갱신 예산 예: 지금 처리하는 묶음 ${Math.min(4,step()+1)}`,0,-195,34,P.yellow));
 m5.add(label('추적 → 저장 → 분할 갱신 · 매 프레임 전체 계산과 구분',0,310,30,P.teal));
 m5.add(label('4개 묶음은 독립 도식 · 실제 Lumen 갱신량/프레임 수 아님',0,355,24,P.muted));
 const controls={mode,progress},poses=Array.from({length:6},(_,i)=>[{mode:i,progress:0},{mode:i,progress:1}]).flat();
 return{node,controls,poses,reset(p:Record<string,number>){mode(p.mode);progress(p.progress);},*transition(p:Record<string,number>,seconds:number){yield*all(mode(p.mode,seconds,linear),progress(p.progress,seconds,linear));}};
}
