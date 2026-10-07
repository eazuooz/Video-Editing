import {Node,Txt,View2D} from '@motion-canvas/2d';
import {createSignal,linear} from '@motion-canvas/core';
import {depthSpace,heading,V3} from '../../shared/depth-diagrams';
import {PAPER as P} from '../../styles/research-paper';
import plan from './depth-reel-plan-v1.json';
const smooth=(x:number)=>{const u=Math.max(0,Math.min(1,x));return u*u*(3-2*u);};
const titles:any={'01':['익숙한 약속과 새 조작을 나누기','이동·발차기 → 여러 도구 행동 → 이동과 목표 선택'],'03':['입력의 역할을 일관되게 남기기','새로움은 경로·대상·행동을 조합할 상황에도 있습니다'],'05':['버튼 재배치는 연결을 옮기는 일','행동을 없애지 않고 동시 실행과 안내를 함께 점검'],'14':['몸의 이동과 도구의 상태를 분리','같은 우산이 여러 행동에 쓰이는 모습을 관찰합니다'],'07':['버튼 위치와 장치 기능은 다른 문제','눌림·떼어짐과 연속 방향 선택을 구분합니다'],'17':['몸의 방향 하나와 목표 두 개','이동과 서로 다른 목표 선택은 별도 역할입니다'],'09':['선택 범위와 선택 과정을 대조하기','직접 방향 · 후보 전환 · 자동 선택 보조'],'11':['역할·동시 행동·안내를 함께 확인','다른 경로에서도 원하는 결정을 내릴 수 있는지']};
const notes:any={'01':['남길 익숙한 조작과 새 행동의 연결','앵거 풋 → 건브렐라 → 마이 프렌드 페드로','약속 / 버튼 배치 / 장치 기능을 나누어 점검','먼저 방향을 잡고 발로 차는 행동부터'],'03':['입력하면 어떤 행동을 예상하는가?','같은 역할의 입력을 일관되게','새 경로·대상·동시 행동이 만드는 새로운 상황','처음 보는 사람의 이해와 새 안내는 따로 확인'],'05':['입력과 행동의 연결을 바꾸기','이동하면서 점프하는 조합도 실행','상황별 역할과 화면 안내를 함께 갱신','메뉴 연결 변경 뒤에도 실제 행동과 안내 검수'],'07':['버튼 재배치 / 제공 기능 변경','눌림·떼어짐 / 계속 바뀌는 방향·위치','조준이라는 이름만 옮겨도 방향 기능은 옮겨지지 않습니다','선택 대상 · 범위 · 연속성을 먼저 적기'],'09':['가상 대안: 직접 방향 / 후보 전환 / 자동 보조','같은 결과를 항상 주는 세 방식이 아닙니다','이동과 목표 변경이 함께 필요한 상황에서 확인','동작 이름보다 내릴 결정을 지켰는지 대조'],'11':['입력 역할을 남기고 새 행동을 명확히 연결','재배치는 동시 행동·안내 / 장치 변경은 방향·대상 선택','다른 경로에서도 의도한 결정이 가능한지 실행']};
export function* depthExplanation(view:View2D,id:string,frames:number){
 const row=plan.rows.find(r=>r.id===id);if(!row||row.frames!==frames)throw Error('Retained duration mismatch');const t=createSignal(0),starts=row.paragraphStarts.map(f=>f/60),u=(p:number,d=2)=>smooth((t()-(starts[p]||0))/d),move=()=>smooth(t()/Math.min(4,frames/60));
 const phase=()=>{let p=0;starts.forEach((v,i)=>{if(t()>=v)p=i;});return p;};const s=depthSpace(()=>22+7*move(),[0,30],.68),g=new Node({});view.fill(P.background);view.add(heading(id,titles[id][0],titles[id][1],'익숙한 게임 조작'));view.add(g);
 const text=(v:string,x:number,y:number,col:string=P.ink,size=30)=><Txt text={v} x={x} y={y} fill={col} fontFamily={P.font} fontWeight={600} fontSize={size}/>;
 const base=(x:number,w=620)=>s.box(x,0,0,w,490,35,'#e8eef1');const path=(pts:()=>V3[],col:string=P.blue,p:number|(()=>number)=move)=>s.path(pts,col,p);
 const button=(name:string,x:number,y:number,col:string=P.blue)=> <Node>{s.box(x,y,35,140,120,32,'#d8dfe7')}{s.box(x,y,()=>67-14*move(),110,95,35,col)}{s.label(name,x,y,135,29)}</Node>;
 const target=(x:number,y:number)=> <Node>{s.box(x,y,35,80,80,110,'#d5b5a8')}{s.box(x,y,145,100,100,15,'#e8d2c3')}</Node>;
 if(id==='01'||id==='11'){
  [-570,0,570].forEach((x,i)=>{g.add(base(x,420));g.add(s.box(x,0,35,170,150,100,['#dce6f0','#dce8d8','#ebe1d6'][i]));g.add(text((id==='01'?['익숙한 약속','버튼 연결','장치의 기능']:['역할 유지','동시 행동·안내','방향·대상 선택'])[i],x,-170,P.ink,31));if(i<2)g.add(path(()=>[[x+235,0,75],[x+335,0,75]],P.blue,()=>u(i+1)));});g.add(text(id==='01'?'새 행동이 기존 행동과 어떻게 이어지는가?':'다른 경로에서도 의도한 선택을 실제로 확인',0,315,P.blue,31));
 }else if(id==='03'){
  g.add(base(-450));g.add(base(460));g.add(button('입력',-600,0));g.add(s.actor(-250,0,P.blue));g.add(path(()=>[[-500,0,75],[-350,0,75]]));g.add(s.actor(340,0,P.green));g.add(target(700,-120));g.add(s.box(530,80,35,140,150,90,'#e3d4c1'));g.add(path(()=>[[230,0,60],[430,0,60],[650,160,60]],P.green,()=>u(2)));g.add(<Node>{text('같은 역할의 연결',-450,-232,P.blue,32)}{text('경로·대상·새 상황',460,-170,P.green,32)}{text('익숙한 역할을 활용해도 새 행동의 안내는 필요합니다',0,315,P.muted,29)}</Node>);
 }else if(id==='05'){
  g.add(base(-450));g.add(base(460));g.add(button('입력 1',-620,-100));g.add(button('입력 2',-620,130,P.green));g.add(button('점프',-200,20,P.blue));g.add(path(()=>[[-500,-100,75],[-300,20,75]],P.blue,()=>1-u(1)));g.add(path(()=>[[-500,130,75],[-300,20,75]],P.green,()=>u(1)));g.add(s.actor(()=>250+370*u(1),0,P.green,'●',()=>35+100*Math.sin(Math.PI*u(1))));g.add(s.box(440,0,35,100,160,80,'#e3d4c1'));g.add(<Node>{text('가상의 재배치 예시',-450,-232,P.blue,31)}{text('이동 + 점프 + 바뀐 안내',460,-170,P.green,31)}{text('입력 연결이 바뀌어도 필요한 행동을 실행할 수 있는지',0,315,P.ink,28)}</Node>);
 }else if(id==='14'){
  g.add(base(0,1400));g.add(s.actor(()=>-470+240*move(),0,P.blue,'●',()=>35+50*move()));g.add(s.box(350,0,35,12,12,200,'#a7b1bc'));g.add(s.polygon(()=>[[350,0,285],[230,-90,235],[470,-90,235]],'#bfd6e9'));g.add(s.polygon(()=>[[350,0,285],[470,-90,235],[470,90,235]],'#9fbdd7'));g.add(s.polygon(()=>[[350,0,285],[470,90,235],[230,90,235]],'#cde0ed'));g.add(<Node>{text('몸의 이동',-450,-170,P.blue,32)}{text('우산의 상태·도구 사용',440,-170,P.green,31)}{text('같은 도구의 여러 역할 · 모든 결과를 이 컷으로 확정하지 않기',0,315,P.muted,27)}</Node>);
 }else if(id==='07'){
  g.add(base(-450));g.add(base(460));g.add(button('눌림 / 떼어짐',-450,0));g.add(s.box(460,0,35,170,200,90,'#dce6f0'));g.add(s.box(()=>460+80*Math.cos(move()*Math.PI),()=>70*Math.sin(move()*Math.PI),125,55,55,50,'#a8bed5'));g.add(path(()=>[[460,0,125],[460+210*Math.cos(move()*Math.PI),210*Math.sin(move()*Math.PI),125]],P.green));g.add(<Node>{text('단순 버튼 상태',-450,-232,P.blue,32)}{text('연속 방향·위치 선택',460,-170,P.green,32)}{text('이름이 같은가? → 필요한 기능이 제공되는가?',0,315,P.ink,31)}</Node>);
 }else if(id==='17'){
  g.add(base(0,1450));g.add(target(-570,0));g.add(target(570,0));g.add(s.actor(()=>-60+120*move(),0,P.blue,'●',()=>60+90*Math.sin(Math.PI*move())));g.add(path(()=>[[-60,0,165],[-500,0,165]],P.blue));g.add(path(()=>[[60,0,165],[500,0,165]],P.green));g.add(<Node>{text('몸의 이동',0,-170,P.ink,32)}{text('왼쪽 목표',-570,265,P.blue,31)}{text('오른쪽 목표',570,265,P.green,31)}{text('두 목표의 선택을 몸의 방향 하나로 대신하지 않기',0,315,P.muted,28)}</Node>);
 }else{
  const xs=[-570,0,570];for(let i=0;i<3;i++){
   g.add(base(xs[i],430));g.add(s.actor(xs[i]-85,100,P.blue));g.add(target(xs[i]+110,-130));g.add(target(xs[i]+110,150));
   g.add(path(()=>[[xs[i]-50,100,130],[xs[i]+80,i===0?-130+(280*move()):i===1?(move()<.5?-130:150):150,130]],[P.blue,P.green,P.red][i]));g.add(text(['직접 방향 선택','후보 순서 전환','자동 선택 보조'][i],xs[i],-170,P.ink,31));
  }
  g.add(text('가상의 세 대안 · 원하는 대상과 선택 과정은 같지 않습니다',0,315,P.muted,28));
 }
 view.add(<Txt text={()=>notes[id]?.[Math.min(phase(),notes[id].length-1)]||'설명용 도식 · 이동과 도구 사용, 목표 선택의 역할을 구분'} y={-272} fill={P.blue} fontFamily={P.font} fontWeight={600} fontSize={27}/>);yield* t(frames/60,frames/60,linear);
}
