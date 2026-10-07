import {Node,Txt,View2D} from '@motion-canvas/2d';
import {createSignal,linear} from '@motion-canvas/core';
import {depthSpace,heading,V3} from '../../shared/depth-diagrams';
import {PAPER as P} from '../../styles/research-paper';
import plan from './depth-reel-plan-v1.json';
const smooth=(x:number)=>{const u=Math.max(0,Math.min(1,x));return u*u*(3-2*u);};
const titles:any={
 '01':['보상 한 줄을 설계하는 순서','기능 → 조건과 한계 → 필요한 제작 작업'],
 '03':['아이템 이름보다 달라지는 행동부터','강화 · 새로운 선택 · 표현과 수집의 역할'],
 '04-potion-state-study':['연구 상태와 제작 가능은 별도','완료 표시와 재료 부족 문구를 함께 관찰합니다'],
 '05':['얻기 · 만들기 · 사용하기의 조건','영상으로 확인하지 못한 획득 조건은 질문으로 남깁니다'],
 '07':['강화의 상한과 함께 쓸 조합','자기 게임의 목표에 맞춰 제한과 교환을 결정합니다'],
 '09':['외형과 기능을 따로 기록하기','표현 · 기억 · 생산과 이동을 같은 역할로 묶지 않습니다'],
 '11':['게임 속 재료와 제작 작업을 구분','아이콘 · 모델 · 동작 · 효과 · 안내 · 검수'],
 '13':['설명할 수 있는 보상 한 줄부터','행동 · 조건 · 조합 · 제작 작업을 연결합니다']};
const notes:any={
 '01':['성장 구조를 흔들지 않을 첫 질문','탄약 기능과 조건 → 목장 행동의 제작 범위','기능 · 조건 · 작업을 한 줄에 기록','먼저 얼리기와 길 만들기를 비교합니다'],
 '03':['획득 뒤 바뀌는 행동을 먼저 적기','강화 / 새 선택 / 표현과 수집','우리 기획의 후보를 실제 게임의 기능으로 단정하지 않기'],
 '04-potion-state-study':['연구 · 제작 · 실제 사용을 따로 기록'],
 '05':['언제 얻는지 · 선행 조건 · 제작 조건','우회 경로와 그 시점의 재료 확보를 확인','미확인 조건은 가정으로 채우지 않고 질문으로'],
 '07':['성장 목표와 대등한 경쟁은 다른 설계 조건','상한 · 동시 사용 · 교체 조건은 우리 설계 제안','수치 조정 또는 선택의 교환을 검토'],
 '09':['많다는 이유로 필요한 보상이 되지는 않습니다','개성 표현 · 플레이의 기억 · 새 행동을 구분','겉모양과 기능은 별도 칸에'],
 '11':['한 항목을 만드는 작업을 펼쳐 보기','기존 자료 활용과 새 작업을 구분','개발사의 실제 예산이 아닌 우리의 계획 도구'],
 '13':['행동 → 조건 → 조합 → 작업','빈칸부터 결정하고 다른 목적의 후보도 검토','실제 플레이와 제작 범위 양쪽에서 확인']};
export function* depthExplanation(view:View2D,id:string,frames:number){
 const row=plan.rows.find(r=>r.id===id);if(!row||row.frames!==frames)throw Error('Retained duration mismatch');id=row.id==='potion-state-study'?'04-potion-state-study':row.sceneId;const t=createSignal(0),starts=row.paragraphStarts.map(f=>f/60),u=(p:number,d=2)=>smooth((t()-(starts[p]||0))/d);
 const phase=()=>{let p=0;starts.forEach((s,i)=>{if(t()>=s)p=i;});return p;};
 const s=depthSpace(()=>22+8*u(1)-4*u(2),[0,30],.68),g=new Node({});view.fill(P.background);view.add(heading(id.split('-')[0],titles[id][0],titles[id][1],'보상 기획'));view.add(g);
 const text=(v:string,x:number,y:number,col:string=P.ink,size=30)=><Txt text={v} x={x} y={y} fill={col} fontFamily={P.font} fontWeight={600} fontSize={size}/>;
 const pedestal=(x:number,name:string,col='#dce6f0')=><Node>{s.box(x,0,0,350,330,35,col)}{text(name,x,-165,P.ink,31)}</Node>;
 const bottle=(x:number,y:number,col:string)=><Node>{s.box(x,y,35,100,90,120,col)}{s.box(x,y,155,45,42,40,'#e8edf0')}{s.box(x,y,195,60,55,18,'#9a7752')}</Node>;
 const arrow=(a:V3,b:V3,p=1,col:string=P.blue)=>s.path(()=>[a,b],col,()=>u(p));
 if(id==='01'||id==='13'){
  const labels=id==='01'?['달라지는 행동','조건 · 한계','제작 작업']:['행동','획득 조건','허용 조합','제작 작업'];const xs=id==='01'?[-560,0,560]:[-660,-220,220,660];
  labels.forEach((label,i)=>{g.add(s.box(xs[i],0,0,id==='01'?410:320,350,45,'#e7ecef'));g.add(s.box(xs[i],0,45,180,150,100,['#dce6f0','#e4eadb','#ebe1d6','#dce6f0'][i]));g.add(text(label,xs[i],-165,P.ink,31));if(i<xs.length-1)g.add(arrow([xs[i]+(id==='01'?230:170),0,75],[xs[i+1]-(id==='01'?230:170),0,75],Math.min(i+1,2)));});
  g.add(<Node>{text(id==='01'?'위저드 위드 어 건 → 컬트 오브 더 램':'빈칸을 결정한 뒤 목록을 늘립니다',0,265,P.blue,32)}{text(id==='01'?'우리 목록에 필요한 행동과 작업을 찾기':'검토: 실제 플레이 + 감당할 제작 범위',0,315,P.muted,29)}</Node>);
 }else if(id==='03'){
  [-560,0,560].forEach((x,i)=>g.add(pedestal(x,['강해지기','새 선택 열기','표현 · 수집'][i])));
  g.add(bottle(-560,0,'#cddff2'));g.add(s.box(0,-50,35,95,90,90,'#d8e6ca'));g.add(s.box(0,80,35,200,80,38,'#d8e6ca'));g.add(s.flag(560,0,'#af8846'));
  g.add(<Node>{text('수치가 바뀌는가?',-560,265,P.blue,29)}{text('새 행동이 가능한가?',0,265,P.green,29)}{text('무엇을 표현·기억하는가?',560,265,'#94712e',27)}{text('아직 없는 장식은 우리 기획의 후보',0,315,P.muted,28)}</Node>);
 }else if(id==='04-potion-state-study'){
  g.add(pedestal(-440,'연구 상태','#dce8d8'));g.add(pedestal(450,'제작 재료','#f0ded5'));g.add(bottle(-440,0,'#d0e3c5'));g.add(s.box(450,0,35,150,150,70,'#e8edf0'));g.add(s.path(()=>[[375,0,125],[525,0,125]],P.red));
  g.add(<Node>{text('완료 표시',-440,265,P.green,34)}{text('재료 부족 문구',450,265,P.red,34)}{text('획득·사용 완료를 이 화면만으로 추정하지 않습니다',0,315,P.muted,29)}</Node>);
 }else if(id==='05'){
  ['재료 확보','연구','제작 · 사용'].forEach((v,i)=>{const x=[-560,0,560][i];g.add(pedestal(x,v));g.add(i===2?bottle(x,0,'#d0e3c5'):s.box(x,0,35,160,150,90,['#ebe1d6','#dce6f0'][i]));});
  g.add(arrow([-330,0,75],[-240,0,75]));g.add(arrow([240,0,75],[330,0,75]));g.add(<Node opacity={()=>u(1)}>{s.path(()=>[[-560,190,45],[0,260,45],[560,190,45]],P.red,1,[10,10])}{text('다른 획득 경로는?',0,265,P.red,32)}</Node>);g.add(text('확인하지 못한 조건은 미확인으로 남깁니다',0,315,P.muted,28));
 }else if(id==='07'){
  g.add(s.box(-440,0,0,600,440,35,'#e9eef2'));g.add(s.box(460,0,0,600,440,35,'#e9eef2'));
  for(let i=0;i<4;i++)g.add(s.box(-650+i*140,0,35,100,110,40+i*45,'#d0dff0'));
  g.add(s.path(()=>[[-730,0,220],[-150,0,220]],P.red));g.add(bottle(320,0,'#cfdeef'));g.add(bottle(590,0,'#dce6ca'));g.add(s.path(()=>[[380,0,90],[530,0,90]],P.green,()=>u(2)));
  g.add(<Node>{text('강해지는 폭과 상한',-440,-165,P.blue,33)}{text('동시 사용 · 교체',460,-165,P.green,33)}{text('경험 목표에 맞춰 결정',0,315,P.ink,32)}</Node>);
 }else if(id==='09'){
  ['겉모양','기능'].forEach((v,i)=>{const x=i?460:-440;g.add(pedestal(x,v,i?'#dce8d8':'#dce6f0'));});g.add(bottle(-530,0,'#cddff2'));g.add(bottle(-310,0,'#e5d6e8'));g.add(s.actor(330,0,P.green));g.add(s.box(620,0,35,150,80,50,'#d9e5cf'));
  g.add(<Node>{text('꾸미기 · 기록 · 수집',-440,265,P.blue,32)}{text('새 생산 · 이동 · 행동',460,265,P.green,32)}{text('외형이 다르다고 기능을 같거나 다르다고 추정하지 않기',0,315,P.muted,28)}</Node>);
 }else{
  g.add(s.box(-590,0,0,430,500,40,'#ebe1d6'));g.add(bottle(-590,0,'#d2e2cb'));g.add(text('게임 속 재료 조건',-570,-165,'#94712e',32));
  const names=['이미지 · 모델','동작 · 효과','안내 · 검수'];for(let i=0;i<3;i++){
   const y=-140+i*190,z=150-i*45;g.add(s.box(370,y,z,700,140,28,['#dce6f0','#e4eadb','#ebe1d6'][i]));g.add(s.label(names[i],370,y,z+68,29));
  }
  g.add(s.path(()=>[[-330,0,70],[-30,0,70]],P.blue,()=>u(0)));g.add(<Node>{text('개발 쪽의 필요한 작업',450,-165,P.blue,32)}{text('기존 자료 활용 / 새 제작 / 확인할 상황',250,315,P.ink,30)}</Node>);
 }
 view.add(<Txt text={()=>notes[id][Math.min(phase(),notes[id].length-1)]} y={-255} fill={P.blue} fontFamily={P.font} fontWeight={600} fontSize={27}/>);yield* t(frames/60,frames/60,linear);
}
