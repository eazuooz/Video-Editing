import {Circle,Line,Node,Txt} from '@motion-canvas/2d';
import {all,createSignal,linear} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {depthSpace,V3} from '../../game-lighting-history-shared/depth-space';

// Independent principle diagrams. Counts, weights and grids are pedagogical
// examples, never measurements of a game's implementation or performance.
function base(count:number){
 const node=new Node({}),mode=createSignal(0),progress=createSignal(0);
 const layer=(i:number)=>{const n=new Node({opacity:()=>Math.round(mode())===i?1:0});node.add(n);return n;};
 const text=(t:string|(()=>string),x:number,y:number,size=30,c:string=P.ink)=>new Txt({text:t,x,y,fontFamily:P.font,fontSize:size,fill:c,textAlign:'center'});
 const note=(n:Node,t:string)=>n.add(text(t,0,345,24,P.muted));
 const space=(x=0,scale=1)=>depthSpace(()=>22,[x,100],scale);
 const grid=(n:Node,s:ReturnType<typeof depthSpace>,side:number,step:number,color=P.surfaceTop)=>{for(let j=0;j<side;j++)for(let i=0;i<side;i++)n.add(s.box((i-(side-1)/2)*step,(j-(side-1)/2)*step,0,step-5,step-5,14,color));};
 const poses=Array.from({length:count},(_,i)=>[{mode:i,progress:0},{mode:i,progress:1}]).flat();
 return {node,mode,progress,layer,text,note,space,grid,poses,
  reset(p:Record<string,number>){mode(p.mode);progress(p.progress);},
  *transition(p:Record<string,number>,seconds:number){yield*all(mode(p.mode,seconds,linear),progress(p.progress,seconds,linear));}};
}

export function representationModel(){
 const m=base(8),{layer,text,note,space,grid,progress:p}=m;
 const a=layer(0),sa=space(-520,.8),sb=space(0,.8),sc=space(520,.8);
 for(const s of[sa,sb,sc])a.add(s.box(0,0,0,390,300,18,P.surfaceTop));
 for(let j=0;j<3;j++)for(let i=0;i<3;i++){
  a.add(sa.box((i-1)*95,(j-1)*95,20,88,88,()=>20+p()*(i+j)*14,P.teal));
  a.add(sb.label(String((i-1)*2), (i-1)*95,(j-1)*95,50,27,i===0?P.orange:P.teal));
  a.add(sc.box((i-1)*95,(j-1)*95,20,60,60,()=>40+p()*45,P.orange));
 }
 a.add([text('화면 깊이',-520,-190,34,P.teal),text('거리장',0,-190,34,P.yellow),text('공간 격자',520,-190,34,P.orange)]);
 a.add(text('다른 좌표 · 다른 저장 값 · 다른 질문',0,285,34,P.yellow));note(a,'거리장 숫자는 역할 도식 · 실제 거리장 표본은 다음 비교에서 계산');

 const b=layer(1),s=space(0,1);
 b.add(s.box(0,0,0,900,420,15,P.surfaceTop));
 b.add(s.box(0,-110,15,105,105,95,P.orange));
 b.add(new Node({opacity:()=>.2+.8*p(),children:[s.box(0,150,15,420,25,270,P.surfaceFront)]}));
 b.add(s.box(()=>-300+p()*100,280,15,55,40,40,P.teal));
 b.add(s.path(()=>[[-300+p()*100,280,60],[0,150,100]],P.teal,p));
 b.add(text('깊이 버퍼: 그 화면에서 처음 보인 표면',0,-195,32,P.teal));
 b.add(text('뒤 표면의 값은 이 깊이 버퍼에 없음',0,295,32,P.yellow));note(b,'벽 투명 표시는 뒤 물체 위치 확인용 · 카메라 변경은 정보의 범위를 바꿈');

 const c=layer(2),sd=space(0,1);
 c.add(sd.box(0,0,0,200,260,170,P.surfaceFront));
 for(const x of[-300,-180,-40,40,180,300]){
  const d=Math.abs(x)-100,color=d<0?P.orange:P.teal;
  c.add(new Circle({position:sd.point(x,0,85),size:20,fill:color}));
  c.add(sd.label(String(d),x,0,220,29,color));
  c.add(sd.path(()=>[[x,0,85],[Math.sign(x)*100,0,85]],color,p));
 }
 c.add(text('벽 중앙 단면: d = |x| − 100',0,-195,35,P.yellow));
 c.add(text('밖은 양수 · 안은 음수 · 경계는 0',0,285,32,P.ink));note(c,'독립 상자 단면 · 복잡한 메시의 거리장을 생성한 결과로 표시하지 않음');

 const d=layer(3),sv=depthSpace(()=>22,[-130,155],.85);
 for(let z=0;z<3;z++)for(let j=0;j<3;j++)for(let i=0;i<3;i++){
  const occupied=i===1&&j===1,color=occupied?P.orange:P.surfaceTop;
  d.add(new Node({opacity:()=>z<=Math.floor(p()*2)?1:.18,children:[sv.box((i-1)*115,(j-1)*115,z*80,100,100,65,color)]}));
 }
 d.add([text('복셀: 공간을 나눈 저장 칸',0,-235,34,P.orange),text('점유 · 재질 · 방향별 빛은 별도 저장 항목',0,290,31,P.yellow)]);
 note(d,'격자는 표현 형식 · 이 격자 자체가 하나의 간접광 알고리즘은 아님');

 const e=layer(4),ea=space(-450,.85),eb=space(450,.85);
 for(const ss of[ea,eb]){e.add(ss.box(0,0,0,410,300,16,P.surfaceTop));e.add(ss.box(0,100,16,220,20,180,P.surfaceFront));}
 e.add(ea.path(()=>[[-120,0,20],[0,100,110]],P.muted,p));
 e.add(eb.box(-130,-90,16,80,80,55,P.orange));
 e.add(eb.path(()=>[[-130,-90,90],[0,100,110],[130,40,20]],P.orange,p));
 e.add([text('AO: 주변 가림',-450,-195,34,P.teal),text('GI: 빛의 전달',450,-195,34,P.orange),text('어두워 보이는 결과만으로 같은 계산이라 말하지 않기',0,295,29,P.yellow)]);
 note(e,'AO 가시성과 표면 간 빛 전달의 역할 비교 · 광량을 수치로 시뮬레이션한 장면 아님');

 const f=layer(5),fa=space(-470,.9),fb=space(470,.9);
 for(const ss of[fa,fb]){grid(f,ss,3,110);f.add(ss.box(190,0,15,70,70,80,P.orange));}
 f.add(fa.polygon(()=>[[-155,-160,20],[155,-160,20],[155,160,20],[-155,160,20]],'#164f4e',P.teal));
 f.add(fb.path(()=>[[-110,80,25],[190,0,60]],P.orange,p));
 f.add([text('SSGI: 화면에서 얻은 자료',-470,-195,31,P.teal),text('거리장 AO: 세계 표현 질의',470,-195,31,P.orange)]);
 f.add(text('주황 물체는 화면 밖 · 질의 자료의 범위를 확인',0,295,30,P.yellow));note(f,'AO와 GI의 물리 역할은 별도 · 실제 엔진 설정 비교는 원본 시연으로 확인');

 const g=layer(6),ga=space(-430,.9),gb=space(430,.9);
 grid(g,ga,4,85);grid(g,gb,2,170);
 g.add(ga.box(0,0,14,20,290,100,P.orange));
 g.add(new Node({opacity:()=>1-p(),children:[gb.box(0,0,14,20,290,100,P.orange)]}));
 g.add([text('세밀한 격자',-430,-195,34,P.teal),text('거친 격자',430,-195,34,P.orange)]);
 g.add(text('얇은 구조가 표현에서 사라질 수 있음',0,295,32,P.yellow));note(g,'독립 해상도 예 · 저장 방식/복셀화 조건에 따라 결과가 달라짐');

 const h=layer(7),sh=space(0,1);
 for(let i=0;i<5;i++){const x=-400+i*200;h.add(sh.box(x,0,0,150,150,100,i===1?P.orange:P.surfaceTop));}
 h.add(sh.path(()=>[[-650,-170,70],[-200,0,70]],P.teal,p));
 h.add(new Node({opacity:p,children:[sh.box(-200,0,105,180,180,10,P.teal)]}));
 h.add(text('레이 질의: 관련 없는 삼각형을 어떻게 건너뛸까?',0,-195,32,P.yellow));
 h.add(text('다음: 경계 상자의 계층으로 후보를 좁히기',0,295,32,P.teal));note(h,'상자/삼각형 교차의 역할은 다음 BVH 장에서 분리');
 return m;
}

export function dynamicRayModel(){
 const m=base(6),{layer,text,note,space,grid,progress:p}=m;
 const a=layer(0),s=depthSpace(()=>0,[0,80],1);
 // TLAS has three instances;two distinct references lead to ONE shared BLAS A.
 const instances=[{x:-440,label:'인스턴스 1 → A',to:-300},{x:0,label:'인스턴스 2 → A',to:-300},{x:440,label:'인스턴스 3 → B',to:300}];
 for(const i of instances)a.add(s.box(i.x,-140,80,200,150,55,P.orange));
 for(const x of[-300,300])a.add(s.box(x,180,0,250,190,65,P.teal));
 for(const i of instances)a.add(s.path(()=>[[i.x,-65,95],[i.to,80,50]],P.yellow,p));
 for(const i of instances)a.add(text(i.label,i.x,-170,28,P.orange));
 for(const[x,label]of[[-300,'共有 BLAS A'.replace('共有','공유')],[300,'BLAS B']]as[number,string][])a.add(text(label,x,105,32,P.teal));
 a.add(text('TLAS: 세 인스턴스와 각각의 변환',0,-250,34,P.orange));
 a.add(text('인스턴스 1·2 → 같은 기하 BLAS A',0,295,31,P.yellow));note(a,'BLAS는 기하 · TLAS는 인스턴스 · 서로 다른 가속 구조');

 const b=layer(1),ba=space(-460,.9),bb=space(460,.9);
 b.add(ba.box(()=>-100+p()*200,0,0,100,100,100,P.teal));
 b.add(ba.box(()=>-100+p()*200,0,105,140,140,8,P.yellow));
 b.add(bb.polygon(()=>[[-120,-60,10],[120,-60,10],[p()*110,120,140]],P.orange));
 b.add([text('강체: 인스턴스 변환',-460,-195,33,P.teal),text('변형: 정점 위치 변경',460,-195,33,P.orange)]);
 b.add(text('갱신 대상과 허용 조건이 다름',0,295,34,P.yellow));note(b,'API의 갱신 허용 플래그와 기하 개수/형식 조건을 함께 확인');

 const c=layer(2),ca=space(-430,.9),cb=space(430,.9);
 for(const ss of[ca,cb])for(const x of[-140,140])c.add(ss.box(x,0,0,75,75,80,P.orange));
 c.add(ca.box(0,0,95,480,300,8,P.muted));
 for(const x of[-140,140])c.add(new Node({opacity:p,children:[cb.box(x,0,95,110,110,8,P.teal)]}));
 c.add([text('빠른 경계 갱신',-430,-195,33,P.orange),text('다시 구성한 계층',430,-195,33,P.teal)]);
 c.add(text('구축 비용과 이후 탐색 효율을 함께 보기',0,295,32,P.yellow));note(c,'느슨한 경계의 원리 예 · 모든 장면에서 재구축이 더 빠르다는 뜻이 아님');

 const d=layer(3),da=space(-400,.85),db=space(400,.85);grid(d,da,4,95);grid(d,db,4,95);
 for(let i=0;i<4;i++)d.add(db.path(()=>[[-140+i*95,60,20],[-140+i*95,-160,150]],P.orange,()=>Math.max(0,Math.min(1,p()*2-i*.2))));
 d.add([text('기본 화면: 래스터화',-400,-195,33,P.teal),text('선택 효과: 레이 질의',400,-195,33,P.orange)]);
 d.add(text('반사·그림자처럼 필요한 효과를 결합',0,295,32,P.yellow));note(d,'하이브리드 구성 비교 · 모든 픽셀의 전체 빛 경로를 추적하는 장면 아님');

 const e=layer(4),se=space(0,1);
 e.add(se.box(-280,0,0,330,220,80,P.teal));e.add(se.box(280,0,0,330,220,80,P.orange));
 e.add(se.path(()=>[[-90,0,55],[90,0,55]],P.yellow,p));
 e.add([text('Battlefield V · 2018 DXR 반사',0,-195,35,P.yellow),text('래스터 화면',-280,255,33,P.teal),text('레이 반사',280,255,33,P.orange)]);
 note(e,'공식 게임 시연은 별도 삽입 · 발표/지원 패치와 전체 패스 트레이싱을 구별');

 const f=layer(5),sf=space(0,1);grid(f,sf,5,85);
 for(let j=0;j<5;j++)for(let i=0;i<5;i++)f.add(new Circle({position:sf.point((i-2)*85,(j-2)*85,35),size:20,fill:(i+j)%3===0?P.orange:P.teal,opacity:()=>.2+p()*((i+j)%3===0?.8:.35)}));
 f.add(text('화면 밖 접근은 가능 · 적은 표본의 노이즈는 별도',0,-195,32,P.yellow));
 f.add(text('다음: 어떤 표본을 몇 개 계산하고 재사용할까?',0,295,32,P.teal));note(f,'표본 패턴은 독립 도식 · 특정 게임의 난수/필터 출력 재현 아님');
 return m;
}

export function samplingModel(){
 const m=base(6),{layer,text,note,space,grid,progress:p}=m;
 const bars=(n:Node,s:ReturnType<typeof depthSpace>,values:number[],labels:string[])=>values.forEach((v,i)=>{const x=(i-(values.length-1)/2)*260;n.add(s.box(x,0,0,140,140,()=>v*24*(.35+.65*p()),i%2?P.orange:P.teal));n.add(s.label(labels[i],x,0,v*24+60,30,i%2?P.orange:P.teal));});
 const a=layer(0);bars(a,space(),[2,8],['값 2','값 8']);a.add(text('표본의 기여와 선택 확률을 함께 보기',0,-195,34,P.yellow));a.add(text('선택을 바꾸면 추정식도 함께 바뀜',0,295,33,P.ink));note(a,'단순 평균은 동일 확률의 예에만 바로 적용');

 const b=layer(1);bars(b,space(-370,.9),[2,8],['2','8']);
 b.add(text('동일 확률: (2+8)/2 = 5',360,-155,33,P.yellow));
 b.add(text('P(2)=¼ · P(8)=¾',360,-90,32,P.ink));
 b.add(text(()=>p()<.5?'보정 없는 평균 기대값: 6.5':'보정: f / (2p) → 기대값 5',360,0,31,P.orange));
 b.add(text('값이 큰 후보를 자주 뽑고 그냥 평균하면 편향',0,295,30,P.yellow));note(b,'두 후보의 합을 평균으로 환산하는 독립 예 · ReSTIR 전체 추정식이 아님');

 const c=layer(2);bars(c,space(),[4,5.333333],['2 / (2×¼) = 4','8 / (2×¾) ≈ 5.33']);
 c.add(text('확률이 작은 큰 기여 → 큰 표본 가중치',0,-195,34,P.yellow));
 c.add(text('평균 = ¼×4 + ¾×5.33… = 5',0,295,32,P.teal));note(c,'기여/PDF의 역할 비교 · 희귀한 큰 가중치는 분산을 키울 수 있음');

 const d=layer(3),sd=space();bars(d,sd,[6,3],['N: SE 1','4N: SE ½']);
 d.add(text('SE ∝ 1/√N',0,-235,42,P.yellow));d.add(text('독립·유한 분산: 표본 4배 → 표준오차 ½',0,295,31,P.teal));note(d,'막대 높이: 상대 표준오차 · 상관 표본/시간 필터/전체 성능에는 별도 조건');

 const e=layer(4),ea=space(-420,.9),eb=space(420,.9);grid(e,ea,3,120);grid(e,eb,3,120);
 e.add(ea.box(0,0,15,90,90,90,P.teal));e.add(eb.box(()=>p()*150,0,15,90,90,90,P.orange));
 e.add([text('정지 장면의 누적',-420,-195,34,P.teal),text('움직인 표면의 대응',420,-195,34,P.orange)]);
 e.add(text('같은 화면 좌표 ≠ 같은 표면',0,295,35,P.yellow));note(e,'이전 표본을 섞기 전에 현재 표면과 대응하는지 확인');

 const f=layer(5),fa=space(-390,.9),fb=space(390,.9);for(const ss of[fa,fb])grid(f,ss,3,120);
 f.add(fa.box(-80,0,15,80,80,75,P.orange));f.add(fb.box(()=>-80+p()*140,0,15,80,80,75,P.orange));
 f.add(fb.path(()=>[[-80,0,110],[-80+p()*140,0,110]],P.orange,1));
 f.add(fb.path(()=>[[140,100,50],[140-p()*100,100,50]],P.teal,1));
 f.add([text('이전 프레임',-390,-195,34,P.muted),text('현재 프레임',390,-195,34,P.ink)]);
 f.add(text('주황: 물체 이동 · 청록: 카메라 이동의 별도 대응',0,295,30,P.yellow));note(f,'이동 방향 예 · 실제 엔진 벡터의 부호/좌표/지터 규약은 별도');
 return m;
}

export function temporalModel(){
 const m=base(7),{layer,text,note,space,grid,progress:p}=m;
 const a=layer(0),s=depthSpace(()=>0,[0,100],1);
 for(const[x,y,z,label,c]of[[-440,20,0,'현재 저해상도',P.teal],[-100,-110,30,'이전 출력',P.green],[240,20,0,'움직임',P.orange],[590,20,0,'복원 출력',P.yellow]]as[number,number,number,string,string][]){a.add(s.box(x,y,z,200,170,65,c));a.add(s.label(label,x,y,z+190,29,c));}
 a.add(s.path(()=>[[-330,20,90],[480,20,90]],P.teal,p));a.add(s.path(()=>[[-100,-110,115],[480,20,90]],P.green,p));
 a.add(text('DLSS 2 · 2020 · 현재 입력과 시간 정보',0,-250,34,P.yellow));a.add(text('낮은 해상도의 렌더 자료 → 높은 해상도의 출력',0,295,31,P.ink));note(a,'신경망 내부 구조의 재현 아님 · 실제 렌더 입력은 여전히 필요');

 const b=layer(1),sb=depthSpace(()=>0,[0,100],1);for(const[x,label,c]of[[-430,'렌더링',P.teal],[0,'재구성',P.orange],[430,'표시',P.green]]as[number,string,string][]){b.add(sb.box(x,0,0,230,180,90,c));b.add(sb.label(label,x,0,220,33,c));}
 b.add(sb.path(()=>[[-300,0,70],[-140,0,70]],P.teal,p));b.add(sb.path(()=>[[140,0,70],[300,0,70]],P.orange,p));
 b.add(text('재구성은 렌더된 입력을 소비하는 별도 단계',0,-195,34,P.yellow));b.add(text('절약한 비용과 복원 비용을 모두 포함',0,295,33,P.ink));note(b,'레이 질의/시뮬레이션을 이 도식의 복원 단계와 합치지 않기');

 const c=layer(2),ca=space(-420,.9),cb=space(420,.9);grid(c,ca,4,100);grid(c,cb,2,200);
 c.add([text('4×4 = 16 픽셀',-420,-195,34,P.teal),text('2×2 = 4 픽셀',420,-195,34,P.orange)]);
 c.add(cb.path(()=>[[-180,260,18],[180,260,18]],P.orange,p));
 c.add(text('가로½ × 세로½ = 픽셀¼',0,290,35,P.yellow));note(c,'기하·시뮬레이션·전송·복원 비용까지 전체¼이 되는 것은 아님');

 const d=layer(3),sd=space();grid(d,sd,4,110);
 for(const[x,y]of[[-140,-100],[140,100]])d.add(sd.path(()=>[[x,y,30],[x+p()*120,y-p()*70,30]],P.orange,1));
 d.add(text('현재 표면 → 이전 대응 위치',0,-195,35,P.yellow));d.add(text('방향 · 단위 · 지터 규약 확인',0,295,34,P.teal));note(d,'단일 화면 이동 벡터로 모든 물체를 옮기는 도식이 아님');

 const e=layer(4),se=space();grid(e,se,4,110);
 e.add(se.box(0,-100,15,80,80,70,P.teal));
 e.add(se.box(()=>p()*540,130,15,440,25,270,P.surfaceFront));
 e.add(new Node({opacity:p,children:[se.box(0,-100,90,100,100,12,P.orange)]}));
 e.add(text('새로 드러난 표면: 믿을 이전 값이 없음',0,-195,34,P.yellow));e.add(text('깊이·표면 일치 검사 → 부적절한 이력 거절',0,295,31,P.orange));note(e,'과거 벽의 색을 새 물체의 값으로 그대로 사용하지 않기');

 const f=layer(5),fa=space(-400,.9),fb=space(400,.9);
 for(const ss of[fa,fb]){grid(f,ss,3,115);for(let i=0;i<4;i++)f.add(ss.box(-130+i*85,0,15,12,180,100,P.teal));}
 for(let i=0;i<4;i++)f.add(new Node({opacity:()=>p()*.4,children:[fb.box(-165+i*85,0,15,12,180,100,P.orange)]}));
 f.add([text('현재의 얇은 구조',-400,-195,34,P.teal),text('맞지 않는 과거 잔상',400,-195,34,P.orange)]);
 f.add(text('정지 화면의 선명도와 이동 중 안정성을 함께 확인',0,295,30,P.yellow));note(f,'잔상은 실패 원리 도식 · 특정 DLSS 버전의 캡처 결과가 아님');

 const g=layer(6),sg=depthSpace(()=>0,[0,100],1);for(const[x,label,c]of[[-430,'입력 조건',P.teal],[0,'복원 결과',P.green],[430,'실패 조건',P.orange]]as[number,string,string][]){g.add(sg.box(x,0,0,230,170,110,c));g.add(sg.label(label,x,0,235,32,c));}
 g.add(sg.path(()=>[[-295,0,85],[-135,0,85]],P.teal,p));g.add(sg.path(()=>[[135,0,85],[295,0,85]],P.orange,p));
 g.add(text('정보·대응·검증으로 재구성 결과를 이해',0,-195,34,P.yellow));g.add(text('없는 정보를 자동으로 정확히 회복한다고 가정하지 않기',0,295,29,P.ink));note(g,'다음: 공간의 프로브와 표본 후보의 재사용');
 return m;
}

export function navigationModel(){
 const m=base(4),{layer,text,note,space,progress:p}=m;
 const labels=[['장면 표현','레이 가속','공간·시간 재사용'],['질의: BVH','저장: 프로브','선택: 저장소'],['Nanite: 기하','Lumen: 조명','커버리지·예산'],['그림자·경로','복원·후처리','DLSS 5 경계']];
 for(let j=0;j<4;j++){
  const n=layer(j),s=space();
  for(let i=0;i<3;i++){const x=-470+i*470,c=[P.teal,P.orange,P.green][i];n.add(s.box(x,0,0,250,210,()=>60+Math.max(0,Math.min(1,p()*3-i))*60,c));n.add(s.label(labels[j][i],x,0,260,30,c));if(i<2)n.add(s.path(()=>[[x+140,0,100],[x+325,0,100]],P.yellow,()=>Math.max(0,Math.min(1,p()*3-i))));}
  n.add(text(['화면 밖 정보를 다루는 서로 다른 방법','저장·질의·선택을 같은 기능으로 합치지 않기','기하 공급과 조명 갱신을 따로 비교','다음 편: 계산한 화면과 생성한 화면'][j],0,-195,34,P.yellow));
  n.add(text(['표현 → 가속 → 재사용 → 기하와 조명','알고리즘마다 관리하는 정보와 오류가 다름','커버리지 · 품질 예산 · 지연 조건','그림자 페이지 · 패스 트레이싱 · 최종 재구성'][j],0,295,31,P.ink));
  note(n,'역할을 연결하는 입체 도식 · 기능의 성능/권리/지원 조건은 별도 확인');
 }
 return m;
}
