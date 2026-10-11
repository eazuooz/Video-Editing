import {Circle,Line,Node,Txt} from '@motion-canvas/2d';
import {all,createSignal,linear} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {depthSpace,V3} from '../../game-lighting-history-shared/depth-space';
import {vsmModel} from './vsm-model-v2';

export const prerequisiteIds=['vsm-address','upscaling-grid','visibility-interpolation','mobile-local-memory','path-probability','path-survival','reconstruction-boundary','direct-versus-transparent','generated-frame-count','display-transform','capture-dataflow'] as const;
export type PrerequisiteId=typeof prerequisiteIds[number];
export const prerequisiteTitles=['주소와 실제 저장은 다르다','8픽셀 입력에서32픽셀 출력으로','삼각형에서 한 점의 UV로','계산 순서와 저장 장소를 구별','방향 선택을 바꿔도 평균은5','살아남은 경로의 기여를 보정','같은 표면인가, 실제 경계인가','빛을 구하는 일과 층을 합치는 일','렌더1개와 생성3개 또는5개','조명값과 화면의 표시값','입력 색에서 반환값까지 따라가기'];

// These independently instantiated scenes teach declared small examples.
// They are explanation time, never gameplay/profiler measurements. Progress
// will be retimed from measured narration; the proof uses a separate8s clock.
export function prerequisiteModel(id:PrerequisiteId){
 if(id==='vsm-address'){
  const m=vsmModel();
  return{node:m.node,reset(p:number){m.reset({mode:3,progress:p});},*transition(p:number,s:number){yield*m.transition({mode:3,progress:p},s);}};
 }
 const node=new Node({}),p=createSignal(0),s=depthSpace(()=>18,[0,125],1);
 const phase=(start:number,end:number)=>()=>Math.max(0,Math.min(1,(p()-start)/(end-start)));
 const text=(t:string|(()=>string),x:number,y:number,size=30,c:string=P.ink)=>new Txt({text:t,x,y,fontSize:size,fontFamily:P.font,fill:c,textAlign:'center'});
 const note=(t:string)=>node.add(text(t,0,350,23,P.muted));
 const wire=(pts:()=>V3[],c:string=P.teal,progress:()=>number=p)=>s.path(pts,c,progress);
 const box=(x:number,y:number,w:number,d:number,h:number,c:string,label:string)=>{
  node.add(s.box(x,y,0,w,d,h,c));node.add(s.label(label,x,y,h+43,29));
 };
 if(id==='upscaling-grid'){
  const grid=(origin:[number,number],nx:number,ny:number,c:string,show:()=>number)=>{
   const g=depthSpace(()=>18,origin,.85),step=72;
   for(let y=0;y<ny;y++)for(let x=0;x<nx;x++)node.add(new Node({opacity:show,children:[g.box((x-(nx-1)/2)*step,(y-(ny-1)/2)*step,0,66,66,20,c)]}));
  };
  // Narration first declares32 pixels, then halves both lengths to8, then
  // returns to32 output pixels. Do not reveal the8-pixel input first.
  grid([-410,100],8,4,P.surfaceTop,phase(.02,.38));grid([410,100],4,2,P.teal,phase(.4,.73));
  node.add(text(()=>p()<.75?'원래8×4=32':'출력8×4=32',-410,-190,34,P.yellow));node.add(text('새 내부4×2=8',410,-190,34,P.teal));
  node.add(new Line({points:[[-100,15],[175,15]],stroke:P.orange,lineWidth:5,endArrow:true,end:phase(.4,.73)}));
  node.add(new Line({points:[[175,180],[-100,180]],stroke:P.teal,lineWidth:5,endArrow:true,end:phase(.75,1)}));
  node.add(text('현재 내부 화면 + 과거 정보 → 더 큰 출력',0,270,31));
  node.add(text('가로½ × 세로½ = 내부 픽셀¼',0,310,31,P.yellow));
  note('해상도만 비교하는 독립 예 · 전체 프레임 시간이4배 빨라진다는 뜻은 아님');
 }
 if(id==='visibility-interpolation'){
  const a:V3=[-600,-160,40],b:V3=[-190,-160,40],c:V3=[-600,210,40],q:V3=[-497.5,-67.5,40];
  node.add(s.polygon(()=>[a,b,c],P.surfaceTop));node.add(s.polygon(()=>[[-600,-160,0],[-190,-160,0],b,a],P.surfaceSide));
  [a,b,c].forEach((v,i)=>{node.add(new Circle({position:s.point(...v),size:16,fill:[P.teal,P.orange,P.green][i]}));node.add(s.label(['UV₀=(0,0)','UV₁=(1,0)','UV₂=(0,1)'][i],v[0],v[1],v[2]+42,25,[P.teal,P.orange,P.green][i]));node.add(wire(()=>[v,q],P.teal,phase(.15,.6)));});
  node.add(new Circle({position:s.point(...q),size:20,fill:P.yellow,opacity:phase(.25,.6)}));
  node.add(s.box(470,0,0,350,260,25,P.surfaceTop));
  node.add(s.label('같은 점의 UV',470,-200,65,29));
  node.add(s.path(()=>[[300,-100,28],[550,-100,28]],P.orange,phase(.6,.85)));
  node.add(s.path(()=>[[300,-100,28],[300,130,28]],P.teal,phase(.6,.85)));
  node.add(new Circle({position:s.point(362.5,-42.5,28),size:22,fill:P.yellow,opacity:phase(.6,.85)}));
  node.add(text('가중치 (½,¼,¼) · 합계1',-350,-190,32,P.yellow));
  node.add(text(()=>p()<.6?'먼저 같은 원근 조건을 선언':'½(0,0)+¼(1,0)+¼(0,1)=(.25,.25)',0,280,30));
  note('독립 좌표 예 · clip-space w가 같을 때 · 다르면 원근 보정 필요');
 }
 if(id==='mobile-local-memory'){
  node.add(s.box(0,-100,-25,1250,240,18,P.surfaceTop));
  box(-410,-100,280,150,35,P.teal,'재질 정보를 만들기');box(410,-100,280,150,35,P.orange,'조명 단계가 읽기');
  node.add(s.label('같은 타일의 가까운 메모리',0,-220,40,30,P.teal));
  node.add(wire(()=>[[-245,-100,55],[245,-100,55]],P.teal,phase(0,.4)));
  box(0,310,470,110,24,P.surfaceSide,'외부 메모리');
  node.add(wire(()=>[[-410,0,55],[-410,310,55],[-245,310,55]],P.orange,phase(.45,.7)));
  node.add(wire(()=>[[245,310,55],[410,310,55],[410,0,55]],P.orange,phase(.7,1)));
  node.add(text('가까이 만들고 → 곧바로 소비',0,-200,32,P.teal));
  node.add(text('다른 경로: 밖으로 저장 → 다시 읽기',0,295,30,P.orange));
  note('포워드/디퍼드: 계산 구성 · 타일 내 유지: 저장 장소 · 대역폭 수치 가정 없음');
 }
 if(id==='path-probability'){
  box(-420,-60,190,180,60,P.teal,'어두운 방향:2');box(420,-60,190,180,130,P.orange,'밝은 방향:8');
  node.add(wire(()=>[[0,250,40],[-420,-60,100]],P.teal,phase(0,.3)));
  node.add(wire(()=>[[0,250,40],[420,-60,170]],P.orange,phase(0,.3)));
  node.add(text('목표의 가중치: 둘 다0.5 → 평균5',0,-200,32,P.yellow));
  node.add(text('선택 확률 q=0.2',-420,230,28,P.teal));node.add(text('선택 확률 q=0.8',420,230,28,P.orange));
  node.add(new Node({opacity:phase(.36,.63),children:[text('8×0.5÷0.8=5',420,280,32,P.orange)]}));
  node.add(new Node({opacity:phase(.65,.84),children:[text('2×0.5÷0.2=5',-420,280,32,P.teal)]}));
  node.add(text(()=>p()<.9?'새 선택 확률의 역수로 보정':'이 예에서는 어느 쪽을 골라도 추정값5',0,320,30,P.yellow));
  note('평균5의 독립 두 방향 예 · 합계10이나 일반 분포의 완전 복원을 뜻하지 않음');
 }
 if(id==='path-survival'){
  box(-550,0,160,170,60,P.surfaceTop,'원래 기여1');box(0,-220,250,120,90,P.teal,'생존:1.25');box(0,220,250,120,25,P.surfaceSide,'종료:0');box(550,0,190,170,60,P.orange,'기대값1');
  node.add(wire(()=>[[-460,0,70],[-270,0,70],[-140,-220,90]],P.teal,phase(0,.35)));
  node.add(wire(()=>[[-270,0,70],[-140,220,35]],P.red,phase(0,.35)));
  node.add(s.label('확률0.8',-250,-230,70,27,P.teal));node.add(s.label('확률0.2',-250,215,60,27,P.red));
  node.add(wire(()=>[[140,-220,90],[460,0,70]],P.teal,phase(.45,.85)));node.add(wire(()=>[[140,220,35],[460,0,70]],P.red,phase(.45,.85)));
  node.add(text('생존 기여×1/0.8',0,-225,32,P.yellow));
  node.add(new Node({opacity:phase(.45,.9),children:[text('0.8×1.25 + 0.2×0 = 1',0,295,34,P.yellow)]}));
  note('기대값 보존 · 매번5개 중1개를 지우는 규칙 아님 · 개별 값의 분산은 증가 가능');
 }
 if(id==='reconstruction-boundary'){
  node.add(s.box(-120,0,0,500,300,18,P.surfaceTop));node.add(s.box(290,0,0,300,300,18,P.blueLight));
  node.add(s.label('같은 벽',-180,-220,60,31,P.teal));node.add(s.label('창문',290,-220,60,31,P.orange));
  const points:[number,number,string][]=[[-260,10,P.teal],[-80,10,P.teal],[255,10,P.orange]];
  for(const[x,y,c]of points){node.add(new Circle({position:s.point(x,y,40),size:20,fill:c}));node.add(wire(()=>[[x,y,40],[x,y,125]],c,phase(0,.35)));}
  node.add(wire(()=>[[-260,10,55],[-80,10,55]],P.teal,phase(.35,.7)));
  node.add(wire(()=>[[-80,10,55],[255,10,55]],P.red,phase(.35,.7)));
  node.add(new Txt({text:'×',position:s.point(135,10,80),fontFamily:P.font,fontSize:62,fill:P.red,opacity:phase(.65,.85)}));
  node.add(text('깊이·표면 방향을 비교한 뒤 값을 섞기',0,285,31,P.yellow));
  note('표면 적격성을 설명하는 도식 · 특정DLSS의 비공개 판정식을 재현하지 않음');
 }
 if(id==='direct-versus-transparent'){
  node.add(s.box(-520,-240,0,70,70,100,P.yellow));node.add(s.label('선택한 빛',-520,-240,145,29,P.yellow));
  for(const [y,c]of[[-130,P.teal],[100,P.orange]]as[number,string][]){node.add(new Node({opacity:.65,children:[s.box(20,y,0,420,22,200,c)]}));node.add(wire(()=>[[-520,-240,110],[20,y,110]],P.yellow,phase(0,.4)));}
  node.add(s.label('뒤층',170,-130,240,28,P.teal));node.add(s.label('앞층',170,100,240,28,P.orange));
  node.add(s.box(-120,360,0,70,70,30,P.surfaceTop));node.add(s.label('카메라',-120,360,65,28));
  node.add(wire(()=>[[-120,360,60],[20,100,100],[20,-130,100]],P.teal,phase(.45,1)));
  node.add(text('빛 계산 → 각 층의 색 → 앞뒤 순서로 합성',0,290,32,P.yellow));
  note('오래된 투명도 문제를 현재 프레임과 연결 · MegaLights 뒤에 생긴 기법이 아님');
 }
 if(id==='generated-frame-count'){
  const rows=[{y:-70,n:3},{y:170,n:5}];
  rows.forEach(({y,n},row)=>{const g=depthSpace(()=>10,[0,y],1),start=row*.5,step=.45/n;for(let i=0;i<=n;i++){const x=-510+i*(1020/n),show=i===0?()=>1:phase(start+(i-1)*step,start+i*step);node.add(new Node({opacity:show,children:[g.box(x,0,0,125,90,45,i===0?P.ink:P.teal),g.label(i===0?'R':'G',x,0,94,29,i===0?P.ink:P.teal)]}));}node.add(new Node({opacity:phase(start+.45,start+.5),children:[text(`1R + ${n}G = ${n+1}표시`,0,y-135,31,P.yellow)]}));node.add(g.path(()=>[[-530,95,5],[530,95,5]],P.line,()=>1));node.add(g.box(-510,95,6,15,28,26,P.orange));});
  node.add(text('주황 게임 계산 눈금은 늘리지 않기',0,310,30,P.orange));
  note('한 렌더 간격의 개수 예 · 표시 수≠시뮬레이션 횟수 · 실측FPS가 아님');
 }
 if(id==='display-transform'){
  const xs=[-630,-210,210,630],labels=['조명 선형값2','노출×0.5','곡선의 입력1','표시'];
  xs.forEach((x,i)=>{box(x,0,250,180,38,i===1?P.orange:i===3?P.teal:P.surfaceTop,labels[i]);if(i<3)node.add(wire(()=>[[x+135,0,60],[xs[i+1]-135,0,60]],P.teal,phase(i*.25,(i+1)*.25)));});
  const curve=depthSpace(()=>0,[210,130],1);
  node.add(curve.path(()=>Array.from({length:30},(_,i)=>{const u=i/29;return[-85+u*170,0,40+100*u/(u+.35)] as V3;}),P.teal,phase(.5,.85)));
  node.add(text('2×0.5=1은 톤 매핑 이전의 값',0,280,33,P.yellow));
  node.add(text('광원을 바꾸지 않아도 표시는 변화 가능',0,320,29));
  note('곡선은 역할 도식 · ACES/엔진의 정확한 변환식이나 실측 픽셀이 아님');
 }
 if(id==='capture-dataflow'){
  box(-520,0,300,190,38,P.orange,'COLOR입력');box(0,0,300,190,38,P.surfaceTop,'return input.color');box(520,0,300,190,38,P.teal,'SV_Target');
  node.add(wire(()=>[[-355,0,60],[-165,0,60]],P.orange,phase(.1,.45)));node.add(wire(()=>[[165,0,60],[355,0,60]],P.teal,phase(.45,.8)));
  node.add(text('Frame622 / EID14 · 같은 선택 명령',0,-205,32,P.yellow));
  node.add(text('(.96125, .01312, .02562, 1)',-520,240,24,P.orange));
  // Keep the returned values on black ground below the projected front face.
  node.add(new Node({opacity:phase(.6,.85),children:[text('(.96125, .01312, .02562, 1)',520,275,24,P.ink)]}));
  node.add(text('검사할 입력 → 실행 줄 → 출력',0,310,30));
  note('채널 원본에서 관찰한 단순 색 반환 · 복잡한 조명 패스 전체의 증거가 아님');
 }
 return{node,reset(v:number){p(v);},*transition(v:number,seconds:number){yield*all(p(v,seconds,linear));}};
}
