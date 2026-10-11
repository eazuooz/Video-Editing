import {Node,Txt} from '@motion-canvas/2d';
import {all,createSignal,linear} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {depthSpace} from '../../game-lighting-history-shared/depth-space';

// Independent small-grid/one-complete-adjacent-frame-interval diagrams. No captured game,
// latency measurement, neural architecture or vendor quality claim is implied.
export function upscalingModel(){
 const node=new Node({}),mode=createSignal(0),progress=createSignal(0),p=progress;
 const layer=(i:number)=>{const n=new Node({opacity:()=>Math.round(mode())===i?1:0});node.add(n);return n;};
 const text=(t:string|(()=>string),x:number,y:number,size=30,c:string=P.ink)=>new Txt({text:t,x,y,fontSize:size,fontFamily:P.font,fill:c,textAlign:'center'});
 const grid=(n:Node,origin:[number,number],side:number,span:number,c:string)=>{const s=depthSpace(()=>16,origin,1),step=span/side;for(let y=0;y<side;y++)for(let x=0;x<side;x++)n.add(s.box((x-(side-1)/2)*step,(y-(side-1)/2)*step,0,step-5,step-5,18,c));return s;};
 const note=(n:Node,t:string)=>n.add(text(t,0,350,24,P.muted));
 const a=layer(0),low=grid(a,[-460,115],2,330,P.teal),high=grid(a,[460,115],4,330,P.surfaceTop),link=depthSpace(()=>0,[0,0],1);
 a.add(low.box(-80,-80,18,70,70,80,P.orange));
 a.add(new Node({opacity:p,children:[high.box(-100,-100,18,70,70,80,P.orange)]}));
 a.add(link.path(()=>[[-225,100/.48,0],[220,100/.48,0]],P.yellow,p));
 a.add([text('현재 낮은 내부 해상도',-460,-200,31,P.teal),text('더 높은 출력 해상도',460,-200,31,P.yellow),text('현재 입력 + 이전 정보 → 출력 복원',0,295,33,P.ink)]);
 note(a,'출력의 모든 조명 표본을 새로 계산했다는 뜻은 아님');

 const b=layer(1),s=depthSpace(()=>0,[0,145],1);
 for(const [y,label,c]of[[-165,'TSR',P.teal],[165,'DLSS SR',P.orange]]as[number,string,string][]){b.add(s.box(-390,y,0,270,140,60,c));b.add(s.box(390,y,0,270,140,60,c));b.add(s.label('낮은 입력',-390,y,110,29));b.add(s.label('높은 출력',390,y,110,29));b.add(s.path(()=>[[-230,y,40],[230,y,40]],c,p));b.add(text(label,0,145+y*.48-85,30,c));}
 b.add(text('같은 역할: 낮은 입력에서 높은 출력 복원',0,-200,32,P.yellow));b.add(text('통합·입력 규칙·하드웨어 요구는 각각 확인',0,295,30,P.ink));note(b,'동일한 구현이나 모든 장면에서 같은 품질이라는 주장 아님');

 const c=layer(2);grid(c,[-430,105],4,350,P.teal);grid(c,[430,105],2,350,P.orange);
 c.add([text('4 × 4 = 16',-430,-210,36,P.teal),text('2 × 2 = 4',430,-210,36,P.orange),text('가로½ × 세로½ = 픽셀¼',0,280,35,P.yellow)]);
 c.add(text(()=>p()<.5?'줄어드는 내부 픽셀 수':'남는 비용: 기하·그림자·복원·기타',0,320,28,P.ink));note(c,'작업 비율 ≠ 전체 프레임 시간 비율 · 독립 숫자 예');

 const d=layer(3),old=grid(d,[-430,120],4,350,P.surfaceTop),cur=grid(d,[430,120],4,350,P.surfaceTop);
 d.add(old.box(-80,0,18,70,70,85,P.orange));d.add(cur.box(()=>-80+p()*150,0,18,70,70,85,P.orange));
 d.add(cur.path(()=>[[-80+p()*150,0,125],[-80,0,125]],P.teal,p));
 d.add([text('이전 표면 위치',-430,-205,33,P.muted),text('현재 → 이전 대응',430,-205,33,P.teal),text('투영 · 물체 움직임 · 지터 규칙을 일치시키기',0,295,30,P.yellow)]);
 note(d,'청록선은 개념상 대응 방향 · 실제 벡터의 부호/단위는 엔진 규약으로 확인');

 const e=layer(4),es=grid(e,[0,155],4,420,P.surfaceTop);
 e.add(es.box(0,-120,18,85,85,75,P.orange));e.add(es.box(()=>p()*580,135,18,440,24,260,P.surfaceFront));
 e.add(new Node({opacity:p,children:[es.box(0,-120,95,115,115,10,P.red)]}));
 e.add(text('새로 드러난 표면: 올바른 과거 값이 없을 수 있음',0,-200,31,P.yellow));e.add(text('잘못된 이력 거절 · 투명/입자/얇은 구조/UI 별도 처리',0,295,28,P.ink));note(e,'빈 정보를 과거 벽 색으로 채우면 잔상이 생기는 원리 예');

 const f=layer(5),fs=depthSpace(()=>0,[0,95],1);
 const frames=[{x:-470,label:'렌더 R0',c:P.teal,g:false},{x:0,label:'생성 G½',c:P.orange,g:true},{x:470,label:'렌더 R1',c:P.teal,g:false}];
 for(const fr of frames){f.add(new Node({opacity:()=>fr.g?.15+.85*p():1,children:[fs.box(fr.x,0,0,260,190,80,fr.c),fs.label(fr.label,fr.x,0,215,31,fr.c)]}));}
 for(let i=0;i<2;i++)f.add(fs.path(()=>[[-320+i*470,0,55],[-155+i*470,0,55]],P.yellow,p));
 f.add(text('DLSS 3 · 2022 · 표시용 프레임 생성',0,-220,33,P.yellow));f.add(text(()=>`독립 예: 실제 렌더 2 · 표시 ${p()<.5?2:3} · 시뮬레이션 2`,0,280,33,P.ink));note(f,'생성 프레임에 새 게임 시뮬레이션/레이 표본이 하나씩 추가된 것은 아님');

 const g=layer(6),gs=depthSpace(()=>12,[0,130],1),rows=[['내부/출력','입력2×2 / 출력4×4'],['실제 렌더','2개'],['표시 프레임','3개'],['지연 시간','별도로 측정']];
 for(let i=0;i<rows.length;i++){const y=-210+i*130;g.add(gs.box(-280,y,0,380,100,30,P.teal));g.add(gs.box(280,y,0,430,100,30,i===2?P.orange:P.surfaceTop));g.add(gs.label(rows[i][0],-280,y,68,29));g.add(gs.label(rows[i][1],280,y,68,29));}
 g.add(text('해상도 · 실제 계산 · 표시 · 반응성을 따로 기록',0,-260,31,P.yellow));g.add(text('표시 숫자 하나가 네 가지를 동시에 설명하지 않음',0,295,29,P.ink));note(g,'표의 숫자는 역할 설명용 · 실제 게임 성능/지연 측정값 아님');
 const poses=Array.from({length:7},(_,i)=>[{mode:i,progress:0},{mode:i,progress:1}]).flat();
 return{node,controls:{mode,progress},poses,reset(v:Record<string,number>){mode(v.mode);progress(v.progress);},*transition(v:Record<string,number>,seconds:number){yield*all(mode(v.mode,seconds,linear),progress(v.progress,seconds,linear));}};
}
