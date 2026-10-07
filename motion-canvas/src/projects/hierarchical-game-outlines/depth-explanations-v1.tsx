import {Node,Txt,View2D} from '@motion-canvas/2d';
import {createSignal,linear} from '@motion-canvas/core';
import {depthSpace,heading,V3} from '../../shared/depth-diagrams';
import {PAPER as P} from '../../styles/research-paper';
import plan from './depth-reel-plan-v1.json';
const smooth=(x:number)=>{const u=Math.max(0,Math.min(1,x));return u*u*(3-2*u);};
const titles:any={
 '02':['목표 → 기능 → 조절값','부모가 정한 질문에 하위 항목이 답합니다'],
 '04':['나란한 항목은 질문의 크기도 나란히','높이 숫자 하나와 기능 전체를 같은 층에 섞지 않습니다'],
 '06':['접어서 읽고, 펼쳐서 확인하기','세부 내용은 남아 있고 보이는 범위만 달라집니다'],
 '08':['제목과 하위 규칙을 한 가지로 옮기기','항목 보존과 새 부모 아래의 의미는 별개입니다'],
 '10':['포함 관계와 참고 관계를 구분하기','세로 가지는 포함 · 옆 화살표는 기준 항목을 참고'],
 '12':['다음 질문을 찾을 수 있는 구조','문서를 정리한 것과 설계를 검증한 것을 구분합니다']};
const notes:any={
 '02':['상위 항목이 읽는 질문을 정합니다','배치 · 선로 · 입구는 목표 아래의 기능','높이 값은 선로 설계 아래에','부모의 질문에 답하는 항목인지 다시 읽기'],
 '04':['기능과 세부값을 한 줄에 섞지 않기','기능끼리 나란히 · 값은 해당 기능 아래','단계 수보다 포함 관계를 찾을 수 있는지','질문의 크기를 맞추고 필요한 부모를 추가'],
 '06':['잠시 숨김 · 내용 삭제가 아닙니다','전체는 접어서 · 필요한 규칙은 펼쳐서','접힌 제목도 범위를 알려야 합니다','제목만 읽어도 규칙의 위치를 예상할 수 있는지'],
 '08':['제목과 하위 내용을 함께 이동','항목 수가 같아도 의미가 달라질 수 있습니다','높이 규칙을 입구 아래에 두면 관계가 어색합니다','새 부모의 질문에 답하는지 다시 확인'],
 '10':['포함 관계가 제작 순서나 원인을 뜻하지는 않습니다','공통 규칙은 한 곳에 · 다른 항목은 참고','세로 포함과 옆 참고를 나눠 읽기','확인할 관계는 질문으로 남겨 둡니다'],
 '12':['필요한 질문과 그 목표를 찾기','기능은 나란히 · 세부는 아래 · 참고는 옆으로','접기 → 펼치기 → 이동 → 미해결 질문 확인','다음에 확인할 내용을 찾을 수 있는 기획서']};
export function* depthExplanation(view:View2D,id:string,frames:number){
 const row=plan.rows.find(r=>r.id===id);if(!row||row.frames!==frames)throw Error('Retained duration mismatch');
 const t=createSignal(0),starts=row.paragraphStarts.map(f=>f/60),u=(p:number,d=2)=>smooth((t()-(starts[p]||0))/d);
 const phase=()=>{let p=0;starts.forEach((s,i)=>{if(t()>=s)p=i;});return p;};
 const s=depthSpace(()=>20+8*u(1)-5*u(3),[0,40],.62),g=new Node({});view.fill(P.background);view.add(heading(id,titles[id][0],titles[id][1],'계층형 기획서'));view.add(g);
 const text=(v:string,x:number,y:number,col:string=P.ink,size=30)=><Txt text={v} x={x} y={y} fill={col} fontFamily={P.font} fontWeight={600} fontSize={size}/>;
 const sheet=(name:string,x:number|(()=>number),y:number|(()=>number),z:number,col='#dce6f0',w=250)=><Node>{s.box(x,y,z,w,130,22,col)}{s.label(name,x,y,z+82,28)}</Node>;
 const edge=(a:V3,b:V3,col:string=P.blue,progress:number|(()=>number)=1)=>s.path(()=>[a,b],col,progress);
 if(id==='02'||id==='04'){
  g.add(s.box(0,0,0,1510,700,24,'#eef1f3'));
  g.add(sheet('관람객이 이용한다',0,-240,230,'#dce8d8',400));
  for(const x of [-520,0,520])g.add(edge([0,-200,230],[x,0,115],P.blue,()=>u(0)));
  ['배치','선로 설계','입구 연결'].forEach((name,i)=>g.add(sheet(name,[-520,0,520][i],0,115)));
  if(id==='02'){
   g.add(<Node opacity={()=>u(2)}>{edge([0,40,115],[0,260,30],P.green)}{sheet('높이 조절값',0,260,30,'#e4eadb')}</Node>);
   g.add(<Node>{text('목표',-735,-105,P.green)}{text('기능',-735,75,P.blue)}{text('세부 규칙',-735,270,P.green)}{text('화면 관찰을 바탕으로 만든 설명용 구성',180,315,P.muted,28)}</Node>);
  }else{
   const z=()=>115-85*u(1),y=()=>-50+310*u(1),x=()=>-520+520*u(1);
   g.add(<Node opacity={()=>1-u(1)}>{sheet('높이 3',-520,-55,115,'#f0d9cf',155)}</Node>);
   g.add(<Node opacity={()=>u(1)}>{sheet('높이 · 회전',x,y,30,'#e5eadb',300)}{edge([0,40,115],[0,260,30],P.green)}</Node>);
   g.add(<Node>{text('기능끼리 같은 층',0,-165,P.blue,33)}{text('조절값은 선로 설계 아래',0,315,P.green,31)}</Node>);
  }
 }else if(id==='06'){
  g.add(s.box(0,0,0,1450,660,24,'#eef1f3'));
  for(const [i,x] of [-510,0,510].entries()){
   g.add(sheet(['배치','선로 규칙','입구 연결'][i],x,-170,180,['#dce6f0','#dce8d8','#ebe2d6'][i]));
   const opened=()=>i===1?1-u(0)+u(1):1-u(0);
   g.add(<Node opacity={opened}>{edge([x,-100,180],[x,130,35],P.blue)}{sheet(['위치 조건','높이 · 연결 조건','접근 조건'][i],x,150,35,'#e9edf0',310)}</Node>);
   g.add(<Node opacity={()=>1-opened()}>{s.box(x,-170,158,250,130,15,'#dce2e8')}{s.box(x,-170,142,250,130,15,'#e7ebee')}</Node>);
  }
  g.add(<Node>{text('보이는 범위만 줄어듭니다',0,265,P.blue,33)}{text('기준 항목과 세부 내용은 그대로 보존',0,315,P.muted,29)}</Node>);
 }else if(id==='08'){
  g.add(s.box(-440,0,0,600,620,24,'#eef1f3'));g.add(s.box(450,0,0,600,620,24,'#eef1f3'));
  g.add(sheet('선로 설계',-440,-200,170,'#dce6f0',350));g.add(sheet('입구 연결',450,-200,170,'#dce8d8',350));
  const move=()=>u(1),x=()=>-440+890*move();
  g.add(s.path(()=>[[-440,-120,160],[x(),120,50]],P.blue));
  g.add(<Node>{sheet('높이 조절',x,120,50,'#ebe1d6',310)}{sheet('연결 조건',x,285,25,'#e5eadb',310)}</Node>);
  g.add(<Node opacity={()=>u(2)}>{text('항목 2개 보존',-470,265,P.green,29)}{text('새 부모의 질문과 맞는가?',450,265,P.red,30)}</Node>);
  g.add(text('제목과 자식은 함께 · 관계의 뜻은 다시 읽기',0,315,P.ink,30));
 }else if(id==='10'){
  g.add(s.box(0,0,0,1510,670,24,'#eef1f3'));
  g.add(sheet('이용 목표',0,-260,230,'#dce8d8',330));
  for(const [i,x] of [-520,520].entries()){
   g.add(edge([0,-200,230],[x,-40,135],P.blue));g.add(sheet(['입구 연결','장식 배치'][i],x,-40,135,'#dce6f0',320));
   g.add(s.path(()=>[[x,0,135],[x,210,75],[0,210,75]],P.green,()=>u(1),[10,10]));
  }
  g.add(sheet('기준 규칙 하나',0,210,50,'#e5eadb',370));
  g.add(<Node>{text('세로: 설명에 포함',-570,-150,P.blue,30)}{text('옆: 같은 기준을 참고',470,265,P.green,30)}{text('복사본을 늘리지 않고 기준을 가리킵니다',0,315,P.muted,29)}</Node>);
 }else{
  g.add(s.box(0,0,0,1510,700,24,'#eef1f3'));g.add(sheet('다음에 확인할 목표',0,-230,230,'#dce8d8',470));
  ['기능 질문','세부 규칙','미해결 질문'].forEach((name,i)=>{
   const x=[-520,0,520][i];g.add(edge([0,-180,230],[x,30,100],i===2?P.red:P.blue,()=>u(1)));g.add(sheet(name,x,30,100,['#dce6f0','#e5eadb','#f0ddd4'][i],310));
  });
  g.add(<Node opacity={()=>u(2)}>{sheet('관련 조건',-520,270,25,'#e7ecef',280)}{sheet('기준을 참고',0,270,25,'#e7ecef',280)}{s.path(()=>[[0,220,55],[330,220,55]],P.green,1,[10,10])}</Node>);
  g.add(text('정리 완료 ≠ 설계 검증 완료',0,315,P.ink,32));
 }
 view.add(<Txt text={()=>notes[id][phase()]} y={-272} fill={P.blue} fontFamily={P.font} fontWeight={600} fontSize={27}/>);
 yield* t(frames/60,frames/60,linear);
}
