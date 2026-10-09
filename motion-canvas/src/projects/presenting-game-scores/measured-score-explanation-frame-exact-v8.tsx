import {Line,Node,Txt,View2D} from '@motion-canvas/2d';
import {createSignal,usePlayback} from '@motion-canvas/core';
import {DARK as D} from '../../styles/research-dark';

type V3=[number,number,number];
type Value=number|(()=>number);
export type ExplanationTiming={durationSeconds:number;paragraphStarts:number[];measured:boolean};
const value=(a:Value)=>typeof a==='function'?a():a;
const smooth=(a:number)=>{const x=Math.max(0,Math.min(1,a));return x*x*(3-2*x);};
const shade=(color:string,k:number)=>'#'+[1,3,5].map(i=>Math.round(parseInt(color.slice(i,i+2),16)*k).toString(16).padStart(2,'0')).join('');

/** World XY is the floor; Z is height. Camera yaw, depth perspective and
 * independently projected top/front/right faces produce real spatial motion.
 * These props explain a metric, and never count as actual existing-game time. */
function projection(yaw:()=>number){
 const rotate=(x:Value,y:Value):[number,number]=>{const a=yaw()*Math.PI/180;return[value(x)*Math.cos(a)-value(y)*Math.sin(a),value(x)*Math.sin(a)+value(y)*Math.cos(a)];};
 const point=(x:Value,y:Value,z:Value=0):[number,number]=>{
  const [X,Y]=rotate(x,y);const perspective=1450/(1450-Y*.34);
  return[.80*perspective*X,68+.80*perspective*(Y*.47-value(z))];
 };
 const polygon=(pts:()=>V3[],fill:string,stroke:string=D.line)=><Line points={()=>pts().map(p=>point(...p))} closed fill={fill} stroke={stroke} lineWidth={2}/>;
 const box=(x:Value,y:Value,z:Value,w:number,d:number,h:Value,color:string)=>{
  const p=(a:number,b:number,c:Value):V3=>[value(x)+a,value(y)+b,value(z)+value(c)];
  return<Node>
   {polygon(()=>[p(-w/2,d/2,0),p(w/2,d/2,0),p(w/2,d/2,h),p(-w/2,d/2,h)],shade(color,.70))}
   {polygon(()=>[p(w/2,-d/2,0),p(w/2,d/2,0),p(w/2,d/2,h),p(w/2,-d/2,h)],shade(color,.46))}
   {polygon(()=>[p(-w/2,-d/2,h),p(w/2,-d/2,h),p(w/2,d/2,h),p(-w/2,d/2,h)],color)}
  </Node>;
 };
 const solid=(x:Value,y:Value,z:Value,w:number,d:number,h:Value,color:string)=>new Node({zIndex:()=>rotate(x,y)[1]+value(z),children:box(x,y,z,w,d,h,color)});
 const label=(text:string,x:Value,y:Value,z:Value,size=32,color:string=D.ink)=><Txt text={text} position={()=>point(x,y,z)} fontFamily={D.font} fontWeight={600} fontSize={size} fill={color} zIndex={4000}/>;
 const path=(points:()=>V3[],color:string=D.teal,progress:Value=1)=> <Line zIndex={-4000} points={()=>points().map(p=>point(...p))} stroke={color} lineWidth={5} endArrow arrowSize={16} end={()=>value(progress)}/>;
 const floor=()=> <Node zIndex={-5000}>{box(0,0,0,1580,660,22,D.surfaceTop)}</Node>;
 return{point,rotate,polygon,solid,label,path,floor};
}

const HEADINGS:Record<string,[string,string]>={
 '01-overview':['점수는 무엇을 말해 줄까?','양과 평가 → 비교 기준 → 계산 표현'],
 '02-score-and-lines':['진행량과 평가는 다르다','지운 줄 수와 점수는 서로 다른 정보를 읽게 합니다'],
 '03-same-count':['같은 양, 다른 점수','같은 수량이 같은 평가를 뜻하지는 않습니다'],
 '04-evaluation-weights':['무엇을 높게 평가할까?','어떤 행동을 값으로 연결할지 정하는 기준'],
 '05-events-and-total':['이번 행동과 누적 결과','새 기여를 잠깐 강조하고 총점은 남겨 둡니다'],
 '06-relative-gap':['누구와 비교한 숫자일까?','총점 · 지운 줄 · 상대와의 차이를 구분하기'],
 '07-name-and-unit':['이름과 단위를 붙이기','무엇을 세는지 · 단위 · 좋은 방향'],
 '08-scoring-feedback':['계산을 읽는 순간','중요한 기여 → 계산 → 읽을 수 있는 결과'],
 '09-feedback-hierarchy':['남아 있는 숫자와 지나가는 알림','지속적으로 읽는 값과 잠깐 강조하는 변화'],
 '10-audit-and-close':['세 가지 질문으로 점검하기','의미가 있는가? 기준이 있는가? 변화가 읽히는가?'],
};

export function* scoreExplanationMeasuredV8(view:View2D,requestedId:string,timing:ExplanationTiming){
 const snapshot=requestedId==='06-observed-2920'?1:requestedId==='06-observed-141'?2:0;
 const id=snapshot?'06-relative-gap':requestedId;
 if(!timing.measured)throw Error('Measured current voice timing required');
 if(!HEADINGS[id]||timing.durationSeconds<=0||timing.paragraphStarts.length!==3)throw Error('Independent scene/timing contract missing');
 const t=createSignal(0);
 const phase=(i:number,d=1.3)=>snapshot&&i===2?(snapshot===1?0:1):smooth((t()-timing.paragraphStarts[i])/d);
 const part=(i:number)=>smooth((t()-timing.paragraphStarts[i])/Math.max(1,(timing.paragraphStarts[i+1]??timing.durationSeconds)-timing.paragraphStarts[i]));
 const s=projection(()=>12+10*smooth(t()/Math.min(7,timing.durationSeconds)));
 const world=new Node({scale:.94});view.fill(D.background);
 view.add(<>
  <Txt text={'얌얌코딩 · 게임 기획과 디자인'} y={-470} fill={D.muted} fontFamily={D.font} fontSize={26}/>
  <Txt text={HEADINGS[id][0]} y={-385} fill={D.title} fontFamily={D.font} fontSize={52} fontWeight={650}/>
  <Txt text={snapshot===1?'앞서 본 같은 27줄의 순간':snapshot===2?'다른 관찰 순간: 줄 수와 점수의 앞섬':HEADINGS[id][1]} y={-306} fill={D.ink} fontFamily={D.font} fontSize={30}/>
 </>);
 view.add(world);world.add(s.floor());
 const solid=(x:Value,y:Value,h:Value,color:string,w=145,d=130,z:Value=22)=>world.add(s.solid(x,y,z,w,d,h,color));
 const tag=(text:string,x:Value,y:Value=260,z:Value=28,size=30,color:string=D.ink)=>world.add(s.label(text,x,y,z,size,color));
 const note=(text:string)=>view.add(<Txt text={text} y={285} fontSize={27} fontFamily={D.font} fill={D.muted}/>);
 const arrow=(points:()=>V3[],color:string=D.teal,progress:Value=1)=>world.add(s.path(points,color,progress));
 const token=(x:Value,y:Value,z:Value,color:string=D.orange,w=76)=>world.add(s.solid(x,y,z,w,w,52,color));

 if(id==='01-overview'){
  [-550,0,550].forEach((x,i)=>{solid(x,0,80,[D.teal,D.title,D.orange][i],270,240);tag(['양 / 평가','상대 기준','계산 표현'][i],x,225);});
  solid(-610,-20,()=>100+70*phase(0),D.teal,85,85,102);solid(-460,35,()=>150+35*part(0),D.title,85,85,102);
  solid(-60,-40,130,D.teal,80,80,102);solid(85,60,190,D.title,80,80,102);
  [0,1,2].forEach(i=>solid(470+i*70,-55+i*50,()=>60+50*phase(2),D.orange,52,52,102));
  token(()=>-550+550*phase(1)+550*phase(2),()=>100-120*Math.sin(Math.PI*part(1)),()=>260+25*Math.sin(Math.PI*part(2)));
  arrow(()=>[[-350,0,27],[-180,0,27]],D.teal,()=>phase(1));arrow(()=>[[200,0,27],[360,0,27]],D.title,()=>phase(2));
  note('먼저 테트리스의 서로 다른 두 숫자를 읽어 봅니다');
 }else if(id==='02-score-and-lines'){
  solid(-370,-30,()=>120+55*phase(2),D.teal,210,170);
  solid(370,30,()=>120+75*phase(1)+55*phase(2),D.title,210,170);
  tag('지운 줄 수',-370);tag('점수',370);tag('수량',-370,-110,()=>155+55*phase(2),26,D.teal);
  tag('평가',370,-40,()=>235+75*phase(1)+55*phase(2),26,D.title);
  token(()=>-20+390*phase(1),-50,()=>290-80*phase(1));
  arrow(()=>[[-230,0,27],[210,0,27]],D.orange,()=>phase(1));
  note('블록을 놓는 변화와 줄을 지우는 변화를 따로 관찰');
 }else if(id==='03-same-count'){
  [-450,450].forEach(x=>{solid(x-100,170,150,D.teal,140,120);tag('같은 줄 수',x,300);});
  solid(-390,-120,()=>190+55*phase(1),D.title,170,130);solid(510,-120,()=>265+40*phase(1),D.title,170,130);
  tag('평가 A',-390,-160,310,27,D.title);tag('평가 B',510,-160,375,27,D.title);
  arrow(()=>[[-210,-100,30],[230,-100,30]],D.teal,()=>phase(2));
  note('높이가 다른 점수 탑 · 배점 공식의 재현이 아닌 개념 비교');
 }else if(id==='04-evaluation-weights'){
  [-430,0,430].forEach((x,i)=>{solid(x,-145,115,D.surfaceTop,190,125);tag(['행동 A','행동 B','행동 C'][i],x,-210,250,29);token(x,()=>-180+340*phase(1),()=>160+35*Math.sin(Math.PI*part(1)),[D.teal,D.title,D.orange][i]);
   solid(x,170,()=>55+(70+i*35)*phase(2),[D.teal,D.title,D.orange][i],160,120);});
  tag('평가 기준',0,340,28,29,D.title);note('높이와 행동 기호는 설계 설명용 · Tetris 실제 배점표가 아닙니다');
 }else if(id==='05-events-and-total'){
  solid(290,30,()=>190+65*phase(1),D.teal,270,230);
  token(()=>-480+770*phase(1),()=>-140+170*phase(1),()=>250+75*Math.sin(Math.PI*part(1)));
  arrow(()=>[[-450,-140,30],[250,30,30]],D.orange,()=>phase(1));tag('누적 결과',290,260);
  world.add(<Node opacity={()=>1-phase(2)}>{s.label('이번 기여',()=>-480+770*phase(1),()=>-140+170*phase(1),()=>350+90*phase(1),31,D.orange)}</Node>);
  tag('남겨 둘 값',630,60,260,28,D.teal);note('강조는 사라져도 읽을 기준은 남습니다');
 }else if(id==='06-relative-gap'){
  // Fade the old text completely before the new observation appears. Both
  // values must never overlap and look like one simultaneous game state.
  const oldText=()=>1-smooth(phase(2)*2);
  const newText=()=>smooth((phase(2)-.5)*2);
  solid(-350,-20,()=>220+30*phase(2),D.teal,180,150);solid(350,20,()=>285-40*phase(2),D.title,180,150);
  [-350,350].forEach((x,i)=>solid(x,195,()=>115+(i===0?15:30)*phase(2),D.surfaceTop,115,85));
  world.add(<Node opacity={oldText}>{s.label('14,096',-350,-100,280,30,D.teal)}{s.label('17,016',350,-55,350,30,D.title)}{s.label('27줄',-350,290,28,29)}{s.label('27줄',350,290,28,29)}</Node>);
  world.add(<Node opacity={newText}>{s.label('19,919',-350,-100,310,30,D.teal)}{s.label('19,778',350,-55,310,30,D.title)}{s.label('29줄',-350,290,28,29)}{s.label('32줄',350,290,28,29)}</Node>);
  world.add(<Node opacity={oldText}>{s.label('차이 2,920',0,0,170,36,D.orange)}</Node>);
  world.add(<Node opacity={newText}>{s.label('다른 순간: +141',0,0,170,36,D.orange)}</Node>);
  arrow(()=>[[-210,-10,280],[210,10,280]],D.orange,()=>phase(1));
  note(snapshot===1?'같은 줄 수 · 다른 점수 · 차이 2,920':snapshot===2?'29줄 / 32줄 · 왼쪽 +141 · 최종 승리와 구분':'서로 다른 관찰 순간 · 중간 점수 차이가 최종 승리는 아닙니다');
 }else if(id==='07-name-and-unit'){
  solid(-440,-5,45,D.surfaceTop,430,260);
  [0,1,2].forEach(i=>token(-570+i*125,25,()=>80+55*phase(1),D.teal));
  solid(420,-40,230,D.title,220,180);tag('회수한 물품: 3개',-440,260);tag('평가: 점',420,260);
  tag('이름 + 단위',0,-180,170,34,D.orange);
  arrow(()=>[[-170,50,30],[220,50,30]],D.orange,()=>phase(2));
  note('물품과 값은 독립 설계 예제 · 실제 게임 정보로 오인하지 않기');
 }else if(id==='08-scoring-feedback'){
  solid(-540,-20,()=>95+25*phase(0),D.teal,180,150);solid(-90,-20,()=>120+40*phase(1),D.title,180,150);
  solid(520,20,()=>70+190*phase(2),D.orange,210,190);tag('칩: 2',-540,255);tag('배수: 3',-90,255);tag('예제 결과: 6',520,255);
  solid(100,-75,24,D.surfaceTop,220,110,240);tag('×',-300,-10,205,48,D.ink);tag('→',190,-10,210,46,D.teal);
  token(()=>-530+1040*phase(2),()=>-10+75*Math.sin(Math.PI*part(2)),()=>320+35*Math.sin(Math.PI*part(2)));
  note('2 × 3 = 6은 설명 예제 · 원본 클립의 최종 점수 재현이 아닙니다');
 }else if(id==='09-feedback-hierarchy'){
  solid(-370,10,230,D.teal,200,180);solid(360,70,160,D.title,200,180);
  tag('계속 읽는 총점',-370,280);tag('계속 읽는 수량',360,280);
  const eventY=()=>-260+450*phase(1);
  world.add(<Node opacity={()=>1-phase(2)}>{s.solid(0,eventY,()=>160+80*Math.sin(Math.PI*part(1)),92,80,55,D.orange)}</Node>);
  world.add(<Node opacity={()=>1-phase(2)}>{s.label('이번 행동',0,eventY,()=>300+80*Math.sin(Math.PI*part(1)),30,D.orange)}</Node>);
  arrow(()=>[[0,-220,27],[0,180,27]],D.orange,()=>phase(1));
  note('안정된 위치와 짧은 강조의 역할을 구분합니다');
 }else if(id==='10-audit-and-close'){
  [-530,0,530].forEach((x,i)=>{solid(x,-65,180,[D.teal,D.title,D.orange][i],210,140);tag(['무엇을 센 값?','누구와 비교?','변화가 읽히나?'][i],x,260,25,29);});
  token(()=>-530+530*phase(1)+530*phase(2),150,()=>95+35*Math.sin(Math.PI*part(1)));
  arrow(()=>[[-440,160,26],[-95,160,26]],D.teal,()=>phase(1));arrow(()=>[[95,160,26],[440,160,26]],D.title,()=>phase(2));
  note('게임 프로그래밍 과외 · 정확한 안내 링크는 설명란과 회원 엔딩에');
 }
 // Current sample-measured candidate timing. Final encoded caption/motion pixels
 // and final mixed ASR remain mandatory gates; this is a silent input renderer.
 // Integer steps avoid float thread end-time comparisons adding a frame.
 const fps=usePlayback().fps;
 const frames=Math.round(timing.durationSeconds*fps);
 for(let frame=0;frame<frames;frame++){t(frame/fps);yield;}
 t(timing.durationSeconds);
}
