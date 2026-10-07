import {Line,Node,Txt,View2D} from '@motion-canvas/2d';
import {createSignal,linear} from '@motion-canvas/core';
import {depthSpace,heading} from '../../shared/depth-diagrams';
import {PAPER as P} from '../../styles/research-paper';
import plan from './depth-reel-plan-v1.json';
const smooth=(x:number)=>{const u=Math.max(0,Math.min(1,x));return u*u*(3-2*u);};
const titles:any={
 '02':['움직이는 화면과 앉아 있는 몸','같은 움직임에도 사람의 반응은 다를 수 있습니다'],
 '04':['시점 · 조준 · 추가 흔들림을 분리하기','부가 연출을 낮춰도 필요한 조작은 남겨 둡니다'],
 '06':['감도와 에임 모드는 다른 선택입니다','설명과 되돌리기를 갖춘 설계 제안'],
 '08':['움직이는 시간과 도착 방향을 따로 보기','부드러운 전환이 모두에게 편하다는 뜻은 아닙니다'],
 '10':['찾기 · 저장하기 · 되돌리기를 확인하기','설정의 동작 확인과 사람의 편안함은 별도로 검토합니다'],
 '12':['선택의 의미와 책임을 나누는 설계','필요한 시점 이동 · 도구 조준 · 추가 연출'],
};
const notes:any={
 '02':['시각 신호와 몸의 움직임','개인 반응을 같은 값으로 단정하지 않기','조작에 필요한 움직임 / 추가 연출','두 역할을 하나의 값으로 묶지 않기'],
 '04':['역할이 다른 세 층','목표를 보는 방향과 추가 흔들림','옵션 제공과 편안함은 다른 검토','시점 회전은 남기고 추가 흔들림만 낮추기'],
 '06':['바뀌는 역할을 설명하기','같은 입력의 회전량 / 조준 연결 방식','실제 게임 메뉴를 복제한 화면이 아닙니다','차이 확인 → 기본값으로 복원'],
 '08':['전환 시간이 길수록 편하다는 보장은 없습니다','이동 시간과 공간 이해는 다른 문제','두 경로는 설명용 도식입니다','전환을 줄일 선택 + 도착 방향 단서'],
 '10':['플레이 중에도 찾을 수 있는 선택','바뀌는 것과 남는 것을 함께 설명','재실행 · 장치 변경 · 기본값 복원','동작 검수와 개인 피드백을 구분'],
 '12':['세 역할의 책임을 나누기','옵션 변경 뒤에도 방향과 목표를 읽기','알아볼 선택 · 복원 · 실제 플레이 피드백','자기 게임의 카메라와 조준부터 점검'],
};
export function* depthExplanation(view:View2D,id:string,frames:number){
 const row=plan.rows.find(r=>r.id===id);if(!row||row.frames!==frames)throw Error('Retained duration mismatch');
 const t=createSignal(0),starts=row.paragraphStarts.map(f=>f/60);
 const phase=()=>{let p=0;starts.forEach((s,i)=>{if(t()>=s)p=i;});return p;};
 const u=(p:number,d=2)=>smooth((t()-(starts[p]||0))/d);
 const s=depthSpace(()=>22+8*u(1)-5*u(3),[0,40],.70),g=new Node({});view.fill(P.background);
 view.add(heading(id,titles[id][0],titles[id][1],'게임 카메라 설계'));view.add(g);
 const text=(v:string,x:number,y:number,col:string=P.ink,size=30)=><Txt text={v} x={x} y={y} fill={col} fontFamily={P.font} fontWeight={600} fontSize={size}/>;
 const camera=(x:number|(()=>number),y:number|(()=>number),z:number|(()=>number),angle:()=>number,col:string)=>{
  const X=()=>typeof x==='function'?x():x,Y=()=>typeof y==='function'?y():y,Z=()=>typeof z==='function'?z():z;
  const aim=()=>[X()+240*Math.cos(angle()),Y()+240*Math.sin(angle()),Z()] as [number,number,number];
  return <Node>{s.box(X,Y,Z,80,66,58,col)}{s.polygon(()=>[[X(),Y(),Z()+25],[aim()[0]-55*Math.sin(angle()),aim()[1]+55*Math.cos(angle()),Z()+25],[aim()[0]+55*Math.sin(angle()),aim()[1]-55*Math.cos(angle()),Z()+25]],'#edf2f9',col)}{s.path(()=>[[X(),Y(),Z()+30],aim()],col)}</Node>;
 };
 if(id==='02'){
  g.add(s.box(-440,0,0,600,430,35,'#e8eef2'));g.add(s.box(460,0,0,600,430,35,'#eaf0ed'));
  g.add(camera(-590,20,40,()=>-.2+.6*u(2),P.blue));g.add(s.box(-220,-60,35,70,70,115,'#d8b994'));
  g.add(s.box(460,10,35,200,155,55,'#dce3e7'));g.add(s.actor(460,5,P.green,'●',90));
  g.add(<Node>{text('화면의 이동',-470,-170,P.blue,34)}{text('같은 자리에 있는 몸',440,-170,P.green,34)}{text('조작에 필요한 회전',-480,265,P.blue)}{text('개인의 반응은 별도 확인',450,265,P.green)}</Node>);
  g.add(<Node opacity={()=>u(3)}>{s.path(()=>[[-720,120,55],[-570,120,55]],P.red)}{text('추가 흔들림은 별도 역할',0,315,P.red,31)}</Node>);
 }else if(id==='04'){
  for(let i=0;i<3;i++)g.add(s.box(()=>i===2?Math.sin(t()*2)*24*(1-u(3)):0,20,30+i*85,1100,420,18,['#e7edf5','#e7efe7','#f4e5df'][i]));
  g.add(camera(-440,0,48,()=>-.15+.45*u(1),P.blue));
  g.add(s.path(()=>[[-260,-45,145],[40+170*u(1),30,145]],P.green));
  g.add(s.box(()=>430+Math.sin(t()*2)*30*(1-u(3)),0,220,95,95,70,'#dcb5a4'));
  g.add(<Node>{text('시점 회전',-680,10,P.blue)}{text('도구 조준',-680,-70,P.green)}{text('추가 연출',-680,-150,P.red)}{text('필요한 조작을 함께 끄지 않습니다',0,315,P.ink,34)}</Node>);
 }else if(id==='06'){
  for(const [i,x] of [-520,0,520].entries()){
   const colors=[P.blue,P.green,P.red];g.add(s.box(x,0,0,370,330,38,'#eaf0ed'));
   g.add(s.box(x,110,38,270,35,22,'#d8dfe5'));g.add(s.box(()=>x-75+150*u(1)*(1-u(3)),110,60,42,65,28,colors[i]));
   if(i===0)g.add(camera(x-80,-80,38,()=>-.3+.7*u(1)*(1-u(3)),colors[i]));
   if(i===1)g.add(s.path(()=>[[x-120,-40,80],[x+100*u(1)*(1-u(3)),-40,80]],colors[i]));
   if(i===2)g.add(s.box(x,()=>-50+Math.sin(t()*2)*25*u(1)*(1-u(3)),38,80,80,100,'#dcb5a4'));
  }
  g.add(<Node>{text('시점 감도',-500,-170,P.blue,33)}{text('조준 연결 방식',0,-170,P.green,33)}{text('추가 흔들림',500,-170,P.red,33)}{text('설계 제안 · 짧은 설명과 기본값 복원',0,315,P.ink,32)}</Node>);
 }else if(id==='08'){
  for(const x of [-440,460])g.add(s.box(x,0,0,690,450,34,'#e9eef2'));
  const slow=()=>u(0,6),instant=()=>t()>3?1:0;
  g.add(s.path(()=>[[-710,-60,40],[-490,70,40],[-230,-60,40]],P.blue,slow));
  g.add(camera(()=>-710+480*slow(),()=>-60+130*Math.sin(Math.PI*slow()),40,()=>-.4+.8*slow(),P.blue));
  g.add(s.path(()=>[[210,-60,40],[690,-60,40]],P.green,instant,[10,10]));g.add(camera(()=>210+480*instant(),-60,40,()=>-.4+.8*instant(),P.green));
  g.add(<Node>{text('움직이는 과정을 따라가기',-450,-170,P.blue,31)}{text('빠르게 바뀐 방향을 읽기',445,-170,P.green,31)}{text('이동하는 시간',-450,265,P.blue)}{text('도착 방향 단서',445,265,P.green)}{text('설명용 경로 · 개인의 편안함을 보장하지 않습니다',0,315,P.ink,30)}</Node>);
  g.add(<Node opacity={()=>u(3)}>{s.flag(-200,-60)}{s.flag(720,-60)}</Node>);
 }else if(id==='10'){
  for(const x of [-530,0,530])g.add(s.box(x,0,0,390,350,40,'#eaf0ed'));
  g.add(s.box(-530,0,40,170,210,85,'#dce5f0'));g.add(s.box(0,0,40,170,210,85,'#e5e0d6'));g.add(s.box(530,0,40,170,210,85,'#dce6d9'));
  for(let i=0;i<2;i++)g.add(s.path(()=>[[[-530,0][i]+200,0,60],[[0,530][i]-200,0,60]],i===0?P.blue:P.green,()=>u(i+1)));
  g.add(<Node>{text('찾을 수 있는 설정',-520,-170,P.blue,32)}{text('저장 · 재실행 · 장치',0,-170,'#94712e',30)}{text('기본값으로 돌아가기',520,-170,P.green,32)}{text('바뀌는 역할과 남는 조작을 함께 확인',0,265,P.ink,33)}{text('개인의 편안함은 별도 피드백',0,315,P.muted,30)}</Node>);
 }else{
  const xs=[-580,0,580],cols=[P.blue,P.green,P.red];
  for(let i=0;i<3;i++){g.add(s.box(xs[i],0,0,400,380,40,'#e8eef2'));g.add(s.box(xs[i],0,40,170,180,100,['#d8e3f3','#dce8d7','#eadbd4'][i]));g.add(s.label(['시점 이동','도구 조준','추가 연출'][i],xs[i],0,220,33,cols[i]));}
  g.add(s.path(()=>[[-340,0,50],[-230,0,50]],P.blue,()=>u(1)));g.add(s.path(()=>[[230,0,50],[340,0,50]],P.green,()=>u(1)));
  g.add(<Node opacity={()=>u(2)}>{text('선택의 설명',-450,315,P.blue,32)}{text('기본값 복원',0,315,P.green,32)}{text('실제 플레이 피드백',470,315,P.ink,32)}</Node>);
 }
 view.add(<Txt text={()=>notes[id][phase()]} y={-255} fill={P.blue} fontFamily={P.font} fontWeight={600} fontSize={27}/>);
 yield* t(frames/60,frames/60,linear);
}
