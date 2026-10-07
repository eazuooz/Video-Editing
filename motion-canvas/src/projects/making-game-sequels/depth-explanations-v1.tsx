import {Node,Txt,View2D} from '@motion-canvas/2d';
import {createSignal,linear} from '@motion-canvas/core';
import {depthSpace,heading,V3} from '../../shared/depth-diagrams';
import {PAPER as P} from '../../styles/research-paper';
import plan from './depth-reel-plan-v1.json';
const smooth=(x:number)=>{const u=Math.max(0,Math.min(1,x));return u*u*(3-2*u);};
const titles:any={'01':['남길 행동과 다시 할 이유','핵심 행동 → 새 결정 → 제작의 재사용을 구분'], '03':['제작의 재사용과 플레이의 이유','개발사의 코드·제작비는 자료화면으로 알 수 없습니다'],'04':['새 도구가 다른 거리와 위치를 요구하는가?','이 질문의 답은 자신의 속편 기획에서 검증합니다'],'05':['목록의 개수보다 달라진 결정','같은 배치 행동 · 다른 경로와 접근 조건'],'07':['익숙함의 약속을 행동으로 적기','계속 할 활동과 바꿀 수 있는 조건'],'09':['무엇을 고르는가 + 언제 고르는가','준비와 전투 사이에서 선택의 시점을 설계합니다'],'11':['익숙한 사람과 처음 보는 사람에게 확인','남긴 활동과 첫 선택의 이해를 따로 검토합니다']};
const notes:any={'01':['익숙한 다음 작품에서 무엇을 남기고 바꿀까요?','배치와 직접 전투에서 핵심 행동 찾기','제작 재사용과 플레이의 새 판단을 구분','먼저 벽 함정 배치와 직접 공격부터'], '03':['도구·시스템 재사용 가능성은 별도 확인','제작 요소 / 새로 고민할 플레이 결정','편집기 활용 뒤에도 새 통로와 접근 방향 검수는 남습니다','제작이 편한 이유와 다시 플레이할 이유를 나누기'],'04':['새 도구 → 다른 거리·위치 선택? · 우리 기획의 질문'],'05':['전작의 결정과 다시 판단할 이유를 적기','가상 예시: 통로 하나에서 두 갈래로','유지할 활동 · 바꿀 조건 · 예상할 선택','추가 개수는 목록 · 결정의 변화는 행동으로 확인'],'07':['남길 활동을 먼저 약속으로 적기','준비 공간 · 전투 도구 · 다음 준비 조건','내부 결정 추정이 아닌 자기 기획의 약속','다른 공간에서 공통 배치 활동을 관찰합니다'],'09':['무엇을 선택하는지와 선택 시점을 함께 설계','싸우는 도중 / 다음 준비로 넘어갈 때','카드 강조 화면만으로 효과를 확정하지 않기','준비 전에 한 번 / 전투 뒤 다시 · 작은 검증 과제'],'11':['전작 경험: 남길 활동 / 처음: 첫 선택의 이해','두 갈래 중 왜 그쪽을 골랐는지 묻기','같은 선택만 반복하거나 뜻을 모르면 조건·안내 재검토','성공·매출을 보장하지 않고 실제 검증에서 수정']};
export function* depthExplanation(view:View2D,inputId:string,frames:number){
 const row=plan.rows.find(r=>r.id===inputId);if(!row||row.frames!==frames)throw Error('Retained duration mismatch');const id=row.sceneId,t=createSignal(0),starts=row.paragraphStarts.map(f=>f/60),u=(p:number,d=2)=>smooth((t()-(starts[p]||0))/d),phase=()=>{let p=0;starts.forEach((v,i)=>{if(t()>=v)p=i;});return p;};const s=depthSpace(()=>20+9*u(1)-5*u(3),[0,30],.68),g=new Node({});view.fill(P.background);view.add(heading(id,titles[id][0],titles[id][1],'게임 속편 기획'));view.add(g);
 const text=(v:string,x:number,y:number,col:string=P.ink,size=30)=><Txt text={v} x={x} y={y} fill={col} fontFamily={P.font} fontWeight={600} fontSize={size}/>;
 const base=(x:number,w=620)=>s.box(x,0,0,w,500,35,'#e8eef1');
 const route=(pts:()=>V3[],p:number=1,col:string=P.blue)=>s.path(pts,col,()=>u(p));
 const trap=(x:number|(()=>number),y:number|(()=>number))=><Node>{s.box(x,y,35,120,130,24,'#c7d9bd')}{s.box(x,y,59,85,90,50,'#a9bf9b')}</Node>;
 if(id==='01'){
  [-570,0,570].forEach((x,i)=>{g.add(base(x,420));g.add(s.box(x,0,35,180,150,100,['#dce6f0','#dce8d8','#ebe1d6'][i]));g.add(text(['남길 핵심 행동','새로 할 결정','제작 재사용'][i],x,-170,P.ink,31));});g.add(route(()=>[[-320,0,75],[-240,0,75]]));g.add(route(()=>[[240,0,75],[320,0,75]],2,P.green));g.add(text('핵심 행동과 새 선택을 실제 장면에서 구분',0,315,P.blue,31));
 }else if(id==='03'){
  g.add(base(-450));g.add(base(460));g.add(s.box(-450,0,35,260,180,95,'#dce6f0'));g.add(s.box(-450,-15,130,200,35,130,'#e7edf2'));g.add(trap(300,100));g.add(trap(650,-100));g.add(route(()=>[[200,-120,45],[400,-120,45],[400,150,45],[700,150,45]],1,P.green));g.add(<Node>{text('도구·시스템 활용 가능성',-450,-170,P.blue,30)}{text('새 통로·접근 방향·검수',460,-170,P.green,30)}{text('제작 범위의 질문',-450,265,P.blue,31)}{text('플레이어 결정의 질문',460,265,P.green,31)}{text('실제 개발사의 코드와 비용을 입증하는 도식이 아닙니다',0,315,P.muted,27)}</Node>);
 }else if(id==='04'){
  g.add(base(0,1450));g.add(s.actor(-450,0,P.blue));g.add(s.box(480,0,35,100,100,125,'#d5b5a8'));g.add(route(()=>[[-360,0,110],[420,0,110]],0));g.add(s.box(-100,0,35,120,120,80,'#e3d4c1'));g.add(<Node>{text('멀리서 고를 위치',-450,-170,P.blue,32)}{text('가까이 다가갈 위치',450,-170,P.green,32)}{text('도구가 늘었을 때 거리·위치 판단도 달라지는가?',0,315,P.ink,31)}</Node>);
 }else if(id==='05'){
  g.add(base(-450));g.add(base(460));g.add(route(()=>[[-700,0,45],[-200,0,45]],0));g.add(trap(-450,0));g.add(route(()=>[[200,0,45],[410,0,45],[700,-170,45]],1));g.add(route(()=>[[410,0,45],[700,170,45]],1,P.green));g.add(trap(()=>530,()=>-70+140*u(3)));g.add(<Node>{text('기존: 한 통로의 배치',-450,-170,P.blue,31)}{text('변경: 어느 갈래부터 준비할까?',470,-170,P.green,30)}{text('가상의 설계 연습 · 실제 맵 개선 결과가 아닙니다',0,315,P.muted,29)}</Node>);
 }else if(id==='07'){
  g.add(base(-450));g.add(base(460));g.add(trap(-570,100));g.add(s.actor(-330,-80,P.blue));g.add(route(()=>[[-550,-80,60],[-350,-80,60]],0));g.add(trap(350,130));g.add(s.box(660,-80,35,100,100,120,'#d5b5a8'));g.add(route(()=>[[230,-120,45],[500,0,45],[700,160,45]],1,P.green));g.add(<Node>{text('남길 활동: 준비·배치·직접 전투',-450,-170,P.blue,28)}{text('바꿀 조건: 공간·도구·다음 준비',460,-170,P.green,28)}{text('자기 기획의 약속과 변경 범위를 함께 표시',0,315,P.ink,30)}</Node>);
 }else if(id==='09'){
  for(const [i,x] of [-580,0,580].entries()){g.add(base(x,440));g.add(s.box(x,0,35,170,170,80,['#dce6f0','#ebe1d6','#dce8d8'][i]));g.add(text(['준비 전 선택','전투 중 판단','전투 뒤 다음 준비'][i],x,-170,P.ink,30));if(i<2)g.add(route(()=>[[x+240,0,75],[x+340,0,75]],1));}
  g.add(<Node opacity={()=>u(3)}>{s.box(-580,0,150,90,20,120,'#b8cee5')}{s.box(580,0,150,90,20,120,'#c3d7b4')}{text('한 번 선택 / 전투 뒤 다시 선택',0,265,P.green,31)}</Node>);g.add(text('선택 순서 관찰과 효과 검증은 별도',0,315,P.muted,30));
 }else{
  g.add(base(-450));g.add(base(460));g.add(s.actor(-450,-90,P.blue));g.add(s.actor(460,-90,P.green));g.add(route(()=>[[-700,140,40],[-460,140,40],[-220,40,40]],1));g.add(route(()=>[[200,140,40],[440,140,40],[700,40,40]],1,P.green));g.add(<Node>{text('전작을 아는 사람',-450,-170,P.blue,33)}{text('처음 보는 사람',460,-170,P.green,33)}{text('남길 활동이 가능한가?',-450,265,P.blue,31)}{text('첫 선택을 이해하는가?',460,265,P.green,31)}{text('제안하는 검증 과제 · 실제 이용자 조사 결과가 아닙니다',0,315,P.muted,28)}</Node>);
 }
 view.add(<Txt text={()=>notes[id][Math.min(phase(),notes[id].length-1)]} y={-255} fill={P.blue} fontFamily={P.font} fontWeight={600} fontSize={27}/>);yield* t(frames/60,frames/60,linear);
}
