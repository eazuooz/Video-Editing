import {Circle,Line,Node,Rect,Txt,View2D} from '@motion-canvas/2d';
import {createSignal,linear} from '@motion-canvas/core';
import {depthSpace,heading} from '../../shared/depth-diagrams';
import {PAPER as P} from '../../styles/research-paper';
import plan from './depth-reel-plan-v1.json';
const smooth=(a:number,b:number,t:number)=>{const u=Math.max(0,Math.min(1,(t-a)/(b-a)));return u*u*(3-2*u);};
const titles:any={
 '02':['대상 · 이유 · 상황은 서로 다릅니다','한 공간의 세 질문을 나눠서 확인하세요'],
 '04':['여러 단서는 같은 참가자를 가리켜야 합니다','가려졌다가 다시 나와도 표식과 몸을 함께 찾습니다'],
 '06':['응원할 이유를 다음 행동에 연결하세요','외형 · 행동 방식 · 익숙한 사람은 서로 다른 출발점입니다'],
 '08':['대상과 바로 앞의 위험을 함께 보여주세요','대상 → 장애물 → 목표를 같은 공간에 놓고 읽습니다'],
 '10':['그냥 보기와 나중에 바꾸기도 남겨 두세요','화면을 이해한 증거와 재미있다는 반응은 별도로 확인합니다'],
 '12':['네 질문이 행동의 흐름으로 이어지는가','누구 → 왜 → 지금 → 실제 결과를 놓치지 않고 따라갑니다'],
};
const notes:any={
 '02':['대상을 찾기','관심을 둘 이유','이름표 하나로 위험까지 설명할 수는 없습니다','끊긴 연결부터 점검하기','실제 행동에서 세 질문 확인하기'],
 '04':['단서를 더하는 것보다 연결이 먼저','외형 · 이름 · 표식이 같은 사람인가?','별이라는 소개와 달 표식은 충돌합니다','가림 뒤에 다시 찾을 수 있는가?','표식이 핵심 동작을 덮지 않게'],
 '06':['외형 · 방식 · 사람','긴 소개보다 행동에 연결되는 정보','차분한 경로와 어려운 경로의 다음 행동','보상이나 결제를 바꾸는 선택이 아닙니다','관심이 생겼는지는 사람에게 확인'],
 '08':['이름과 순위만으로 동작은 설명되지 않습니다','착지할 곳과 목표까지의 관계','통계로 손과 발을 덮지 않기','대상 · 장애물 · 목표부터 연결','화면의 강조와 실제 상태를 일치시키기'],
 '10':['선택 절차가 관전을 막지 않게','그냥 보기 · 고르기 · 바꾸기','대상 식별과 관심을 구분','화면 점검 + 실제 관전자 반응','자동 점검으로 재미를 단정하지 않기'],
 '12':['누구 · 왜 · 지금 · 실제 결과','정보를 실제 행동에 연결','표시를 키워도 행동을 놓치면 다시 확인','이해 점검과 재미 평가를 구분','신경 쓰는 대상의 행동을 놓치지 않게'],
};
export function* depthExplanation(view:View2D,id:string,frames:number){
 const row=plan.rows.find(s=>s.id===id);if(!row||row.frames!==frames)throw Error('Exact retained white duration required');
 const t=createSignal(0);
 const starts=row.paragraphStarts.map(n=>n/60);
 const phase=()=>{let n=0;starts.forEach((v,i)=>{if(t()>=v)n=i;});return n;};
 const u=(p:number,seconds=1.4)=>smooth(starts[p]??0,(starts[p]??0)+seconds,t());
 const yaw=()=>24+7*u(1)-5*u(3);
 const s=depthSpace(yaw,[0,id==='04'?160:['08','12'].includes(id)?135:70],id==='04'?.82:1),g=new Node({});view.fill(P.background);
 view.add(heading(id,titles[id][0],titles[id][1]));view.add(g);
 const text=(txt:string,x:number,y:number,color:string=P.ink,size=29)=><Txt text={txt} x={x} y={y} fill={color} fontFamily={P.font} fontSize={size} fontWeight={600}/>;
 if(id==='02'){
  for(const x of [-550,0,550])g.add(s.box(x,0,0,390,240,28,'#e8eef1'));
  g.add(<Node>{s.actor(-550,0,P.blue)}{s.label('대상',-550,-10,200,37,P.blue)}{s.label('누구를 보는가',-550,180,0,28)}
   {s.actor(0,0,'#b79556')}{s.label('♥',0,0,178,63,P.red)}{s.label('이유',0,-10,240,37,'#9a732e')}{s.label('왜 계속 보는가',0,180,0,28)}
   {s.box(520,0,28,85,85,90,'#d8b994')}{s.flag(665,0)}{s.label('상황',550,-10,220,37,P.green)}{s.label('지금 무엇이 위험한가',550,180,0,28)}
   {s.path(()=>[[-360,0,30],[-250,0,30]],P.blue,()=>u(3))}{s.path(()=>[[200,0,30],[330,0,30]],P.green,()=>u(3))}
  </Node>);
  g.add(<Node opacity={()=>u(2)}>{s.label('이름표',-550,0,150,32,P.blue)}<Line points={()=>[s.point(-520,0,151),s.point(-490,0,95)]} stroke={P.blue} lineWidth={2}/></Node>);
 }else if(id==='04'){
  for(const x of [-470,470])g.add(s.box(x,0,0,720,360,34,'#ecf0f3'));
  g.add(s.actor(()=>-580+210*u(3),0,P.blue,'●',34));g.add(s.actor(()=>350+230*u(3),0,P.blue,'★',34));
  // The foreground cuboid actually occludes the participant during its passage.
  g.add(s.box(-470,95,34,110,55,143,'#dde3e8'));g.add(s.box(470,95,34,110,55,143,'#dde3e8'));
  g.add(<Node>{text('단서가 충돌',-465,-200,P.red,34)}{text('단서가 일치',465,-200,P.green,34)}
   {text('★ 별  /  몸체는 ●',-465,-145,P.red)}{text('★ 별  /  몸체도 ★',465,-145,P.green)}
   {text('가림 뒤에 다른 표식',-465,340,P.red)}{text('가림 뒤에도 같은 표식',465,340,P.green)}
  </Node>);
 }else if(id==='06'){
  g.add(s.box(0,0,0,1500,370,30,'#eaf0ed'));
  g.add(s.actor(-530,0,P.blue,'★',30));g.add(s.label('좋아하는 외형',-530,-110,135,32,P.blue));
  g.add(s.path(()=>[[-250,-70,32],[-80,-70,32],[120,60,32]],'#b79556',()=>u(2)));
  g.add(s.path(()=>[[-250,-70,32],[-120,65,32],[20,-20,32],[120,60,32]],P.green,()=>u(2)));
  g.add(s.actor(()=>-230+350*u(2,4),()=>-70+130*u(2,4),'#b79556','◆',30));
  g.add(s.label('보고 싶은 행동',0,-135,150,32,'#9a732e'));g.add(s.flag(260,80));
  g.add(s.actor(540,0,P.green,'●',30));g.add(s.actor(640,70,P.green,'●',30));g.add(s.label('알고 있는 사람',550,-110,135,32,P.green));
  g.add(text('다음 행동을 기다릴 단서',0,250,P.ink,36));
 }else if(id==='08'){
  g.add(s.box(-60,0,-32,1500,300,58,'#e8edf0'));
  g.add(s.path(()=>[[-660,0,29],[-190,0,29],[210,0,29],[600,0,29]],P.blue,()=>u(3,2)));
  g.add(s.actor(()=>-640+290*u(1,3),0,P.blue,'★',()=>26+55*Math.sin(Math.PI*u(1,3))));
  g.add(s.box(0,0,26,140,160,115,'#d8b994'));g.add(s.flag(595,0));
  g.add(<Node>{text('대상',-600,-190,P.blue,34)}{text('장애물',0,-100,'#9a732e',34)}{text('목표',580,-10,P.green,34)}
   {text('다음 발 디딜 곳',-300,240,P.blue)}{text('아직 목표에 도착하지 않았습니다',360,240,P.green)}
  </Node>);
  g.add(<Rect x={()=>-410+330*u(3)} y={45} width={()=>380+520*u(3)} height={310} stroke={P.blue} lineWidth={3} opacity={()=>.7*u(2)} radius={6}/>);
 }else if(id==='10'){
  g.add(s.box(0,10,0,1530,430,34,'#eaf0ed'));
  for(const [x,name,col] of [[-560,'그냥 보기',P.blue],[0,'한 명 고르기','#b79556'],[560,'나중에 바꾸기',P.green]] as const){
   g.add(s.box(x,-65,34,160,110,50,col));g.add(s.label(name,x,-90,145,32,col));
   g.add(s.path(()=>[[x,-5,38],[x,165,38]],col,()=>u(1)));
  }
  g.add(s.actor(()=>-560+560*u(1,3)+560*u(3,3),150,P.blue,'★',34));
  g.add(<Node opacity={()=>u(2)}>{text('대상을 찾을 수 있는가?',-410,265,P.blue,32)}{text('계속 보고 싶은가?',435,265,P.green,32)}
   {text('화면 · 입력 기록',-410,310,P.muted,26)}{text('실제 사람의 반응',435,310,P.muted,26)}</Node>);
 }else{
  const x=[-650,-225,225,650],cols=[P.blue,'#b79556',P.green,P.blue];
  for(let i=0;i<4;i++){
   g.add(s.box(x[i],0,0,355,270,36+30*i,'#e9eef2'));
   if(i===0)g.add(s.actor(x[i],0,cols[i],'★',36));
   if(i===1)g.add(s.label('♥',x[i],0,155,70,P.red));
   if(i===2){g.add(s.box(x[i]-55,0,96,72,80,80,'#d8b994'));g.add(s.flag(x[i]+60,0));}
   if(i===3){g.add(s.actor(x[i],0,P.blue,'★',126));}
   g.add(s.label(['누구','왜','지금','실제 결과'][i],x[i],-35,200+10*i+(i===3?80:0),34,cols[i]));
   if(i<3)g.add(s.path(()=>[[x[i]+170,0,44+30*i],[x[i+1]-170,0,74+30*i]],cols[i],()=>u(1,2)));
  }
  g.add(<Node opacity={()=>u(3)}>{text('이해하기 쉬운가?',-400,255,P.blue,32)}{text('정말 재미있는가?',400,255,P.green,32)}{text('실제 화면으로 점검',-400,303,P.muted,26)}{text('사람에게 보여 주고 듣기',400,303,P.muted,26)}</Node>);
 }
 // Caption-safe bottom note changes at actual preserved paragraph onset.
 view.add(<Txt text={()=>notes[id][Math.min(phase(),notes[id].length-1)]} y={-255} fill={P.blue} fontFamily={P.font} fontSize={27} fontWeight={600}/>);
 yield* t(frames/60,frames/60,linear);
}
