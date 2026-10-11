import {Node,Txt} from '@motion-canvas/2d';
import {all,createSignal,linear} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {depthSpace} from '../../game-lighting-history-shared/depth-space';

// Vendor-described input/output roles. No claim to reconstruct a neural network or measured game quality.
export function dlssLatestModel(){
 const node=new Node({}),mode=createSignal(0),progress=createSignal(0),p=progress;
 const layer=(i:number)=>{const n=new Node({opacity:()=>Math.round(mode())===i?1:0});node.add(n);return n;};
 const text=(t:string|(()=>string),x:number,y:number,size=30,c:string=P.ink)=>new Txt({text:t,x,y,fontSize:size,fontFamily:P.font,fill:c,textAlign:'center'});
 const note=(n:Node,t:string)=>n.add(text(t,0,350,23,P.muted));
 for(const i of[0,1]){
  const n=layer(i),s=depthSpace(()=>12,[0,95],1),count=i===0?3:5,step=i===0?330:235,start=i===0?-495:-587.5;
  for(let j=0;j<=count;j++){const x=start+j*step,generated=j>0,block=new Node({opacity:()=>generated?Math.min(1,.15+Math.max(0,p()*count-j+1)*.85):1});
   block.add(s.box(x,0,0,i===0?250:185,240,generated?42:85,generated?P.orange:P.teal));
   block.add(s.label(generated?'G'+j:'R0',x,0,165,34,P.ink));n.add(block);
  }
  n.add(text(i===0?'2025 · DLSS4: R 하나 + G 최대3개':'2026 · DLSS4.5: R 하나 + G 최대5개',0,-230,34,P.yellow));
  n.add(text(i===0?'표시 프레임4개 ≠ 광선 계산4회':'6X는 지원 조건에서의 최대 구성 · 동적 모드는 조절',0,285,31));
  note(n,'R은 렌더링한 프레임 · G는 생성한 표시 프레임 · 동일 개수의 게임 상태 갱신·레이 표본이 아님');
 }
 const c=layer(2),cs=depthSpace(()=>12,[0,100],1);
 for(const[x,t,col]of[[-590,'게임의 색 + 움직임',P.surfaceTop],[0,'DLSS5: 시각적 표현',P.orange],[590,'한 프레임 출력',P.teal]]as[number,string,string][]){c.add(cs.box(x,0,0,430,300,70,col));c.add(text(t,x,285,28,P.ink));}
 c.add(cs.path(()=>[[-340,0,115],[-245,0,115]],P.yellow,p));c.add(cs.path(()=>[[245,0,115],[340,0,115]],P.yellow,p));
 c.add(cs.box(-670,-45,75,65,85,20,P.green));c.add(cs.path(()=>[[-650,120,100],[-530,120,100]],P.teal,p));
 c.add(text('2026 · NBA2K27 · 제조사의 입력/출력 설명',0,-230,33,P.yellow));
 note(c,'3D 안내는 게임 화면에 기반 · 도식은 신경망 내부·실제 품질 측정·새 기하 입력의 재현이 아님');

 const d=layer(3),ds=depthSpace(()=>14,[0,90],1);
 d.add(ds.box(-470,0,0,540,340,40,P.surfaceTop));
 for(let j=0;j<3;j++)for(let i=0;i<4;i++)d.add(ds.box(-470+(i-1.5)*100,(j-1)*90,45,88,78,25,i<2?P.teal:P.surfaceTop));
 d.add(text('적용 영역 / 제외 영역',-470,-230,32,P.yellow));
 for(const[y,t,col]of[[-110,'구조 강도',P.orange],[80,'색조 강도',P.teal]]as[number,string,string][]){d.add(ds.box(380,y,0,460,65,20,P.surfaceTop));d.add(ds.box(()=>180+360*p(),y,25,35,70,45,col));d.add(text(t,470,y===-110?-225:-80,31,P.ink));}
 d.add(text('예술적 의도에 따른 조절 · 물리 경로의 완전 계산과 별개',0,285,30));
 note(d,'공식 Structure/Tone 강도와 마스크의 역할 도식 · 예시 조절값은 실제 SDK 결과가 아님');

 const e=layer(4),es=depthSpace(()=>12,[0,105],1);
 for(const[x,t,col]of[[-550,'실제 계산',P.teal],[0,'시간적 복원',P.green],[550,'표시 프레임 생성',P.orange]]as[number,string,string][]){e.add(es.box(x,0,0,430,300,90,col));e.add(text(t,x,-230,33,P.ink));}
 e.add(es.path(()=>[[-295,0,145],[-255,0,145]],P.yellow,p));e.add(es.path(()=>[[255,0,145],[295,0,145]],P.yellow,p));
 e.add(text('기기 · 게임 버전 · 내부 해상도 · 지연',0,285,33,P.yellow));
 note(e,'역할 분리는 통합 순서의 고정 명세가 아님 · 버전 숫자만으로 모든 기능이 대체되었다고 하지 않음');
 const poses=Array.from({length:5},(_,i)=>[{mode:i,progress:0},{mode:i,progress:1}]).flat();
 return{node,poses,reset(v:Record<string,number>){mode(v.mode);progress(v.progress);},*transition(v:Record<string,number>,seconds:number){yield*all(mode(v.mode,seconds,linear),progress(v.progress,seconds,linear));}};
}
