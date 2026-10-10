import {Line,Node,Txt,View2D} from '@motion-canvas/2d';
import {createSignal,usePlayback} from '@motion-canvas/core';
import {DARK as D} from '../../styles/research-dark';

type V3=[number,number,number];
type Value=number|(()=>number);
export type CharacterTiming={durationSeconds:number;paragraphStarts:number[];measured:true;blackIntervals:{startFrame:number;frames:number}[]};
const value=(v:Value)=>typeof v==='function'?v():v;
const smooth=(v:number)=>{const x=Math.min(1,Math.max(0,v));return x*x*(3-2*x);};
const shade=(hex:string,k:number)=>'#'+[1,3,5].map(i=>Math.round(parseInt(hex.slice(i,i+2),16)*k).toString(16).padStart(2,'0')).join('');

/** XY floor, Z height; yaw and perspective project each actual face.
 * All primitives here are explanation. They never count as gameplay. */
function projection(yaw:()=>number){
 const rotate=(x:Value,y:Value):[number,number]=>{const a=yaw()*Math.PI/180;return[value(x)*Math.cos(a)-value(y)*Math.sin(a),value(x)*Math.sin(a)+value(y)*Math.cos(a)];};
 const point=(x:Value,y:Value,z:Value=0):[number,number]=>{
  const [X,Y]=rotate(x,y);const p=1550/(1550-Y*.30);
  return[.80*p*X,84+.80*p*(Y*.42-value(z))];
 };
 const poly=(pts:()=>V3[],fill:string,stroke:string=D.line)=><Line points={()=>pts().map(p=>point(...p))} closed fill={fill} stroke={stroke} lineWidth={2}/>;
 const box=(x:Value,y:Value,z:Value,w:number,d:number,h:Value,color:string)=>{
  const p=(a:number,b:number,c:Value):V3=>[value(x)+a,value(y)+b,value(z)+value(c)];
  return<Node>
   {poly(()=>[p(-w/2,d/2,0),p(w/2,d/2,0),p(w/2,d/2,h),p(-w/2,d/2,h)],shade(color,.68))}
   {poly(()=>[p(w/2,-d/2,0),p(w/2,d/2,0),p(w/2,d/2,h),p(w/2,-d/2,h)],shade(color,.43))}
   {poly(()=>[p(-w/2,-d/2,h),p(w/2,-d/2,h),p(w/2,d/2,h),p(-w/2,d/2,h)],color)}
  </Node>;
 };
 const solid=(x:Value,y:Value,z:Value,w:number,d:number,h:Value,color:string)=>new Node({zIndex:()=>rotate(x,y)[1]+value(z)*.01,children:box(x,y,z,w,d,h,color)});
 const label=(text:string|(()=>string),x:Value,y:Value,z:Value,size=30,color:string=D.ink)=><Txt text={text} position={()=>point(x,y,z)} fontFamily={D.font} fontWeight={600} fontSize={size} fill={color} zIndex={4000}/>;
 const path=(points:()=>V3[],color:string=D.teal,progress:Value=1)=><Line zIndex={-4000} points={()=>points().map(p=>point(...p))} stroke={color} lineWidth={5} endArrow arrowSize={15} end={()=>value(progress)}/>;
 return{point,rotate,poly,solid,label,path};
}

const HEADINGS:Record<string,[string,string,string]>={
 '01-overview':['숫자에서 플레이 방식으로','공통 동작 → 고유 규칙 → 강점과 약점의 선택','먼저 두 캐릭터의 공통 이동·점프·공격을 봅니다'],
 '02-common-baseline':['공통 기준부터 만들기','차이를 넣기 전에 누구나 쓸 수 있는 행동부터','최소 성능 위에 각자의 경로와 기회를 만듭니다'],
 '03-rule-not-scale':['숫자 밖의 차이','상대의 상태 · 공간 · 사용할 수 있는 행동','불·물은 같은 피해 수치가 아니라 다른 관찰 대상'],
 '04-information-rule':['상대가 읽는 정보도 바뀐다','겉모습 · 실제 판정 · 대응 방법을 구분하기','연기의 가림만으로 무적을 주장하지 않습니다'],
 '05-useful-strength':['강점이 선택을 바꾸는가','유리한 상황과 그곳에 들어갈 방법을 함께','근접 압박은 설계 예시 · 실제 배율표가 아닙니다'],
 '06-role-and-limitation':['약점에도 역할을 남기기','돌아갈 선택과 상대의 대응이 있는가','통로·적의 조합은 설계 예시 · 플레이테스트 필요'],
 '07-state-not-base':['기본 성능과 현재 상태','기본값 · 현재 피해 상태 · 판단을 나누기','과거 경기의 한 순간으로 현재 순위를 정하지 않습니다'],
 '08-resources-and-actions':['기술이 능력치를 바꾸는 순간','방어 · 동전 · 상대 주사위가 서로 다른 대상','별도 전투 샷 · 이번 턴의 상태와 고정된 기본 능력치 구분'],
 '09-condition-and-time':['효과에는 조건과 시점이 있다','발동 조건 → 바뀌는 대상 → 적용 시점','SNIPE 주사위는 다음 턴 · 현재 STA에 즉시 +6 아님'],
 '10-balance-preserves-role':['조정하면서 개성 보존하기','문제 상황을 고치고 유용한 역할은 남기기','여러 조건의 반복 검토 · 한 경기로 공정함을 확정하지 않기'],
 '11-cost-and-summary':['고유 규칙의 구현 비용','발동 · 유지 · 종료 · 다음 턴의 조합','핵심 규칙을 짧게 적으면 테스트 질문이 분명해집니다'],
 '12-conclusion':['한 문장으로 기억되는 역할','어떤 상황에서 어떤 선택으로 기억되는가','능력치 표를 채우기 전에 역할 문장을 먼저'],
};

export function* characterExplanationMeasured(view:View2D,id:string,timing:CharacterTiming){
 const count=id==='06-role-and-limitation'?4:3;
 if(!HEADINGS[id]||timing.durationSeconds<=0||timing.paragraphStarts.length!==count)throw Error('Independent character scene/timing contract missing');
 const t=createSignal(0);
 const phase=(i:number,d=1.2)=>smooth((t()-timing.paragraphStarts[i])/d);
 const part=(i:number)=>smooth((t()-timing.paragraphStarts[i])/Math.max(1,(timing.paragraphStarts[i+1]??timing.durationSeconds)-timing.paragraphStarts[i]));
 const s=projection(()=>10+8*smooth(t()/Math.min(7,timing.durationSeconds)));
 const world=new Node({scale:.93});view.fill(D.background);
 view.add(<>
  <Txt text={'얌얌코딩 · 게임 기획과 디자인'} y={-470} fill={D.muted} fontFamily={D.font} fontSize={26}/>
  <Txt text={HEADINGS[id][0]} y={-385} fill={D.title} fontFamily={D.font} fontSize={52} fontWeight={650}/>
  <Txt text={HEADINGS[id][1]} y={-306} fill={D.ink} fontFamily={D.font} fontSize={30}/>
  <Txt text={HEADINGS[id][2]} y={300} fill={D.muted} fontFamily={D.font} fontSize={27}/>
 </>);
 view.add(world);
 world.add(new Node({zIndex:-5000,children:s.solid(0,0,0,1580,620,20,D.surfaceTop)}));
 const block=(x:Value,y:Value,h:Value,color:string,w=130,d=120,z:Value=20)=>world.add(s.solid(x,y,z,w,d,h,color));
 const tag=(text:string|(()=>string),x:Value,y:Value=255,z:Value=28,size=30,color:string=D.ink)=>world.add(s.label(text,x,y,z,size,color));
 const arrow=(points:()=>V3[],color:string=D.teal,progress:Value=1)=>world.add(s.path(points,color,progress));
 const token=(x:Value,y:Value,z:Value,color:string=D.orange,w=65,h=60)=>world.add(s.solid(x,y,z,w,w,h,color));

 if(id==='01-overview'){
  [-500,0,500].forEach((x,i)=>{block(x,0,80+i*28,[D.teal,D.title,D.orange][i],250,210);tag(['공통 동작','고유 규칙','상황별 선택'][i],x,255);});
  token(()=>-500+500*phase(1)+500*phase(2),0,()=>130+28*phase(1)+28*phase(2),D.orange,64);
  arrow(()=>[[-310,0,28],[-170,0,28]],D.teal,()=>phase(1));arrow(()=>[[170,0,28],[320,0,28]],D.title,()=>phase(2));
 }else if(id==='02-common-baseline'){
  [-500,0,500].forEach((x,i)=>{block(x,-120,65,D.surfaceTop,245,180);tag(['이동','점프','공격'][i],x,-160,170);});
  const p=()=>phase(2);
  token(()=>-620+1240*part(1),85,75,D.teal);
  token(()=>-620+1240*part(1),()=>-65-120*Math.sin(Math.PI*part(1)),()=>75+135*Math.sin(Math.PI*part(1)),D.title);
  arrow(()=>[[-620,85,30],[0,85,30],[620,85,30]],D.teal,()=>phase(1));
  tag('공통 바닥 = 비교 기준',0,280,26,30);
  arrow(()=>[[0,60,30],[260+250*p(),-70,30]],D.orange,p);
 }else if(id==='03-rule-not-scale'){
  token(-390,0,20,D.surfaceTop,100,160);tag('상대 상태',-390,265,25);
  world.add(<Line points={()=>Array.from({length:49},(_,i)=>{const a=i*Math.PI/24;return s.point(-390+120*Math.cos(a),90*Math.sin(a),()=>120+25*part(0));})} closed stroke={D.orange} lineWidth={7} zIndex={500}/>);
  block(380,-45,12,D.teal,370,220);tag('물의 위치',380,255,24);
  token(()=>220+320*part(1),()=>-45+75*Math.sin(Math.PI*part(1)),()=>36+90*Math.sin(Math.PI*part(1)),D.teal);
  arrow(()=>[[-210,-80,35],[200,-80,35]],D.title,()=>phase(2));
  tag('무엇이 달라지는가?',0,-170,200,31,D.title);
 }else if(id==='04-information-rule'){
  // The fog is a world plane with depth sorting. It actually hides portions
  // of the rear figure; its off-plane labels stay outside that obstruction.
  block(-360,-130,165,D.teal,125,115);block(260,110,165,D.title,125,115);
  const fogY=()=>-230+390*phase(1);
  const fogX=()=>-120+180*part(1);
  const fog=new Node({zIndex:()=>s.rotate(fogX,fogY)[1],opacity:()=>.85*phase(1),children:s.poly(()=>[
   [fogX()-330,fogY(),35],[fogX()+330,fogY(),35],[fogX()+330,fogY(),265],[fogX()-330,fogY(),265]
  ],'#4c565b',D.muted)});
  world.add(fog);tag('닮은 형체',-480,240,25);tag('가려지는 정보',400,260,25);
  arrow(()=>[[-650,240,90],[-120,-100,90]],D.orange,()=>phase(2));
 }else if(id==='05-useful-strength'){
  block(-470,20,50,D.surfaceTop,280,240);block(40,-150,140,D.surfaceTop,230,190);block(520,70,70,D.surfaceTop,220,200);
  tag('지상',-470,265);tag('높은 발판',40,-190,340);tag('바깥 공간',520,270);
  token(()=>-530+580*part(1),()=>100-250*part(1),()=>85+145*part(1),D.orange,66);
  arrow(()=>[[-540,70,80],[-200,-50,135],[40,-150,205]],D.teal,()=>phase(1));
  tag('접근 도구 + 공격 뒤 선택',0,270,25,29,D.title);
  arrow(()=>[[60,-150,205],[410,50,130]],D.orange,()=>phase(2));
 }else if(id==='06-role-and-limitation'){
  block(-380,-125,80,D.surfaceTop,540,80);block(-380,165,80,D.surfaceTop,540,80);
  block(370,-75,100,D.surfaceTop,530,85);block(370,75,100,D.surfaceTop,530,85);
  token(()=>-610+440*phase(1),40,35,D.teal,65);
  token(()=>220+380*part(3),0,35,D.orange,65);
  arrow(()=>[[-600,30,35],[-100,30,35],[0,180,35],[-550,235,35]],D.teal,()=>phase(1));
  arrow(()=>[[150,0,35],[570,0,35]],D.orange,()=>phase(3));
  const obstacle=new Node({zIndex:()=>s.rotate(480,25)[1],opacity:()=>phase(3),children:s.solid(480,25,20,95,90,190,D.red)});world.add(obstacle);
  const secondEnemy=new Node({zIndex:()=>s.rotate(620,25)[1],opacity:()=>phase(3),children:s.solid(620,25,20,80,85,155,D.red)});world.add(secondEnemy);
  tag('돌아갈 선택',-380,300,26);tag(()=>phase(3)<.5?'보이는 준비와 빈틈':'적의 배치·조합 예시',400,290,26,29);
  tag('설계 예시',0,-240,150,29,D.title);
 }else if(id==='07-state-not-base'){
  block(-450,0,160,D.teal,220,180);tag('기본 성능',-450,270);
  token(()=>10+110*part(0),-100,()=>90+65*part(1),D.orange,105);tag('현재 피해 상태',70,270);
  token(480,()=>-130+190*part(2),80,D.title,110);tag('플레이 판단',490,280);
  tag('고정 기준',-450,-100,245,28,D.teal);
  arrow(()=>[[-260,0,32],[-70,0,32]],D.orange,()=>phase(1));
  tag('세 항목을 섞어 비교하지 않기',0,-185,330,30);
 }else if(id==='08-resources-and-actions'){
  block(-520,0,()=>95+95*phase(0),D.teal,180,150);
  tag(()=>phase(0)<.5?'DEF 3':'DEF 6',-520,-100,()=>175+95*phase(0),31,D.teal);tag('REACT → 방어',-520,280);
  [0,1,2].forEach(i=>token(-85+i*80,()=>70-100*phase(1),()=>50+20*i,D.title,52,35));
  tag('STEAL → 동전',0,285,25,29);tag('자원 변화',0,-170,200,29,D.title);
  token(480,-45,20,D.surfaceTop,140,160);token(535,-25,()=>190-80*phase(1),D.orange,65);
  tag('STUN → 상대 주사위',480,285,25,28);tag('상대의 현재 상태',500,-165,235,27,D.orange);
  arrow(()=>[[-420,50,35],[-260,50,35]],D.teal,()=>phase(2));
  arrow(()=>[[190,50,35],[330,50,35]],D.title,()=>phase(2));
 }else if(id==='09-condition-and-time'){
  block(-350,150,45,D.surfaceTop,540,220);block(360,-150,110,D.surfaceTop,540,220);
  tag('현재 턴',-350,310,25);tag('다음 턴',360,100,25);
  const flight=()=>phase(0,2.2);
  [0,1].forEach(i=>{token(()=>-360+720*flight()+i*85,()=>100-250*flight(),()=>95+105*flight()+65*Math.sin(Math.PI*flight()),D.title,72,65);});
  tag('STA 주사위 2개',360,-180,330,30,D.title);
  const currentEffect=s.label('피해 / 현재 효과',-350,520,25,29,D.orange);
  currentEffect.opacity(()=>1-phase(1,.45));world.add(currentEffect);
  const separateStrike=s.label('별도 STRIKE: 하트 감소',-350,520,25,27,D.orange);
  // Separate the labels in time so both remain legible during the transition.
  separateStrike.opacity(()=>smooth((t()-timing.paragraphStarts[1]-.55)/.45));world.add(separateStrike);
  arrow(()=>[[-310,50,40],[290,-80,130]],D.teal,()=>phase(2));
 }else if(id==='10-balance-preserves-role'){
  [-500,0,500].forEach((x,i)=>{block(x,0,60+i*20,D.surfaceTop,280,240);tag(['거리','장소','상대'][i],x,280);});
  block(0,-120,170,D.teal,95,95,100);tag('역할 유지',0,-175,305,30,D.teal);
  token(()=>-500+500*phase(1)+500*phase(2),100,()=>100+20*phase(1)+20*phase(2),D.orange);
  const gap=()=>50+100*phase(2);
  block(()=>480-gap(),-60,115,D.red,70,100);block(()=>480+gap(),-60,115,D.red,70,100);
  arrow(()=>[[340,150,45],[620,150,45]],D.orange,()=>phase(2));
 }else if(id==='11-cost-and-summary'){
  const nodes:V3[]=[[-560,120,20],[-70,-150,20],[470,80,20],[-30,200,20]];
  const labels=['발동','유지','종료','다음 턴'];
  nodes.forEach(([x,y,z],i)=>{block(x,y,95,D.surfaceTop,190,150,z);tag(labels[i],x,y+115,z+30,29);});
  arrow(()=>[[-470,80,45],[-160,-110,45]],D.teal,()=>phase(0));
  arrow(()=>[[40,-100,45],[360,30,45]],D.title,()=>phase(1));
  arrow(()=>[[-50,-50,45],[-30,100,45]],D.orange,()=>phase(2));
  token(()=>-540+480*part(0),()=>100-220*part(0),()=>135+45*Math.sin(Math.PI*part(0)),D.teal);
  token(()=>-40+450*part(1),()=>-120+180*part(1),140,D.title);
  tag('조건이 늘면 검사 경로도 늘어납니다',0,-235,300,28);
 }else if(id==='12-conclusion'){
  [-500,0,500].forEach((x,i)=>{block(x,0,95+i*30,[D.teal,D.title,D.orange][i],230,190);tag(['공통 기준','조건과 시점','선택과 대응'][i],x,285,25,29);});
  token(()=>-520+520*phase(1)+520*phase(2),()=>120-110*part(2),()=>140+30*phase(1)+30*phase(2),D.orange);
  arrow(()=>[[-340,80,35],[-155,80,35]],D.teal,()=>phase(1));arrow(()=>[[160,80,35],[340,80,35]],D.title,()=>phase(2));
  tag('역할을 한 문장으로',0,-170,265,32,D.title);
 }
 // Prototype timings are clearly separate from measured narration contracts.
 if(!timing.measured)throw Error('Frame-exact input requires reviewed measured timing');
 const fps=usePlayback().fps;
 const frames=Math.round(timing.durationSeconds*fps);
 if(fps!==60||Math.abs(frames/fps-timing.durationSeconds)>1e-7)throw Error('Measured input must use an integer 60fps duration');
 let end=0;
 for(const interval of timing.blackIntervals){
  if(!Number.isInteger(interval.startFrame)||!Number.isInteger(interval.frames)||interval.frames<=0||interval.startFrame<end||interval.startFrame+interval.frames>frames)throw Error('Invalid selected black interval');
  for(let frame=0;frame<interval.frames;frame++){t((interval.startFrame+frame)/fps);yield;}
  end=interval.startFrame+interval.frames;
 }
 t(end/fps);
}
