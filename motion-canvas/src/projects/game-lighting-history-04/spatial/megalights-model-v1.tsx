import {Circle,Node,Txt} from '@motion-canvas/2d';
import {all,createSignal,linear} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {depthSpace,V3} from '../../game-lighting-history-shared/depth-space';

// Independent teaching geometry: no game capture, measured light budget or engine implementation.
export function megalightsModel(){
 const node=new Node({}),mode=createSignal(0),progress=createSignal(0),p=progress;
 const layer=(i:number)=>{const n=new Node({opacity:()=>Math.round(mode())===i?1:0});node.add(n);return n;};
 const text=(t:string,x:number,y:number,size=30,c:string=P.ink)=>new Txt({text:t,x,y,fontSize:size,fontFamily:P.font,fill:c,textAlign:'center'});
 const note=(n:Node,t:string)=>n.add(text(t,0,350,23,P.muted));
 const lamps:V3[]=Array.from({length:12},(_,i)=>[-600+(i%6)*240,-220+Math.floor(i/6)*145,120]);
 const a=layer(0),as=depthSpace(()=>18,[0,85],.9);
 a.add(as.box(0,90,0,1500,500,20,P.surfaceTop));
 for(const l of lamps)a.add(as.box(...l,54,54,30,P.yellow));
 a.add(as.box(0,235,20,110,90,35,P.teal));
 for(const i of [0,4,7,11])a.add(as.path(()=>[[0,235,65],lamps[i]],P.orange,p));
 a.add(text('2024 · UE5.5 실험 기능',0,-230,34,P.yellow));
 a.add(text('많은 광원 → 유용한 직접광 표본에 작업 집중',0,285,32,P.ink));
 note(a,'12개 광원·4개 화살표는 원리 설명용 · 실제 고정 표본 수나 성능 측정이 아님');

 const b=layer(1),bs=depthSpace(()=>18,[0,90],1);
 b.add(bs.box(0,70,0,1380,420,20,P.surfaceTop));
 const cand:V3[]=[[-560,-100,100],[-240,-100,100],[180,-100,100],[550,-100,100]];
 for(let i=0;i<4;i++){b.add(bs.box(...cand[i],75,60,45,i===0?P.muted:P.yellow));b.add(bs.label('후보'+(i+1),cand[i][0],cand[i][1],185,27,P.ink));}
 b.add(bs.box(0,230,20,115,90,40,P.teal));b.add(bs.box(-150,50,20,180,35,190,P.surfaceFront));
 b.add(bs.path(()=>[[0,230,65],[-120,70,170]],P.red,p));
 b.add(bs.path(()=>[[0,230,65],cand[2]],P.green,p));
 b.add(text('후보의 중요도 ≠ 실제 가시성',0,-230,34,P.yellow));
 b.add(text('선택한 뒤 가림 검사 · 차단된 기여 제외',0,285,32));
 note(b,'초록은 도달 · 빨강은 벽에서 종료 · 목록에 있다는 이유만으로 빛을 더하지 않음');

 const c=layer(2),cs=depthSpace(()=>15,[0,90],1);
 for(const[x,label]of[[-450,'Forward+: 후보 목록 계산'],[450,'확률적 선택 + 재사용·복원']]as[number,string][]){
  c.add(cs.box(x,0,0,650,400,22,P.surfaceTop));c.add(text(label,x,-230,28,P.yellow));
  for(let i=0;i<6;i++)c.add(cs.box(x-210+(i%3)*210,-90+Math.floor(i/3)*160,25,80,65,45,P.yellow));
  c.add(cs.box(x,250,25,100,85,35,P.teal));
  for(let i=0;i<6;i++){const selected=x<0||i===1||i===4;c.add(new Node({opacity:()=>selected?1:.14,children:[cs.path(()=>[[x,250,65],[x-210+(i%3)*210,-90+Math.floor(i/3)*160,75]],x<0?P.teal:P.orange,p)]}));}
 }
 c.add(text('목록을 줄이는 일과 표본을 고르는 일은 다른 단계',0,285,31));
 note(c,'두 전략의 책임 비교 · 동일 비용·동일 품질 또는 MegaLights의 정확한 내부 도식이 아님');

 const d=layer(3),ds=depthSpace(()=>18,[0,90],1);
 d.add(ds.box(0,40,0,1280,450,20,P.surfaceTop));
 for(let i=0;i<4;i++)d.add(ds.box(-460+i*300,-150,25,60,60,70,i===0?P.yellow:P.muted));
 d.add(ds.box(()=>-430+860*p(),-150,110,90,80,35,P.orange));d.add(ds.box(0,200,25,100,80,35,P.teal));
 d.add(ds.path(()=>[[0,200,65],[-430,-150,145]],P.yellow,1));
 d.add(text('밝은 기여가 이동하면 예전 선택이 부족할 수 있음',0,-230,32,P.yellow));
 d.add(text('고정 표본 예산 · 복잡한 가림 · 노이즈와 잔상',0,285,31));
 note(d,'고정된 화살표와 움직이는 주황 광원의 불일치 · 광원 증가에도 품질이 일정하다고 하지 않음');

 const e=layer(4),es=depthSpace(()=>18,[0,125],1);
 e.add(es.box(-450,-120,20,90,80,65,P.yellow));e.add(es.box(0,100,0,480,300,35,P.surfaceTop));e.add(es.box(540,-130,0,280,40,210,P.teal));
 e.add(es.path(()=>[[-450,-120,100],[0,100,40]],P.yellow,p));
 e.add(es.path(()=>[[0,100,40],[540,-130,110]],P.teal,p));
 e.add(text('MegaLights: 직접광',-470,-220,32,P.yellow));e.add(text('Lumen: 간접광',430,-220,32,P.teal));
 e.add(text('광원 → 첫 표면 → 다른 표면',0,285,34));
 note(e,'역할 연결 도식 · 직접광을 켜는 것만으로 모든 간접 반사를 정확하게 계산하지 않음');

 const f=layer(5),fs=depthSpace(()=>18,[0,115],.92);
 f.add(fs.box(-440,0,0,580,420,20,P.surfaceTop));f.add(fs.box(440,0,0,580,420,20,P.surfaceTop));
 for(const x of[-440,440])f.add(fs.box(x,0,20,35,35,110,P.orange));
 for(let i=0;i<15;i++){const x=-440+((i%5)-2)*77,y=(Math.floor(i/5)-1)*65;f.add(fs.box(x,y,110+((i*7)%3)*25,55,38,16,P.green));}
 for(let j=0;j<3;j++)for(let i=0;i<4;i++)f.add(new Node({opacity:()=>.2+.8*p(),children:[fs.box(440+(i-1.5)*105,(j-1)*100,110,92,85,70,P.teal)]}));
 f.add(text('식물 세부',-440,-225,34,P.green));f.add(text('거리별 기하 표현',440,-225,34,P.teal));
 f.add(text('2025 · UE5.7 실험적 Nanite Foliage',0,285,32,P.yellow));
 note(f,'기하 표현 확장 · 실제 Nanite 변환 결과나 새로운 간접광 해법을 재현한 것이 아님');
 const poses=Array.from({length:6},(_,i)=>[{mode:i,progress:0},{mode:i,progress:1}]).flat();
 return{node,poses,reset(v:Record<string,number>){mode(v.mode);progress(v.progress);},*transition(v:Record<string,number>,seconds:number){yield*all(mode(v.mode,seconds,linear),progress(v.progress,seconds,linear));}};
}
