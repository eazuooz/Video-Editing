import {Line,Node,Txt,View2D} from '@motion-canvas/2d';
import {createSignal,linear} from '@motion-canvas/core';
import {DARK as D} from '../../styles/research-dark';

type V3=[number,number,number];
type Value=number|(()=>number);
type Color=string|(()=>string);
export type ColorTiming={durationSeconds:number;paragraphStarts:number[];measured:boolean};
const n=(x:Value)=>typeof x==='function'?x():x;
const color=(x:Color)=>typeof x==='function'?x():x;
const smooth=(x:number)=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x);};
const shade=(c:Color,k:number)=>()=> '#'+[1,3,5].map(i=>Math.round(parseInt(color(c).slice(i,i+2),16)*k).toString(16).padStart(2,'0')).join('');

/** Each front/side/top vertex is projected from XYZ, with yaw and perspective.
 * These animated comparisons are explanation time, never gameplay quota. */
function projection(yaw:()=>number){
 const rotate=(x:Value,y:Value):[number,number]=>{const a=yaw()*Math.PI/180;return[n(x)*Math.cos(a)-n(y)*Math.sin(a),n(x)*Math.sin(a)+n(y)*Math.cos(a)];};
 const point=(x:Value,y:Value,z:Value=0):[number,number]=>{const [X,Y]=rotate(x,y);const p=1600/(1600-Y*.28);return[.8*p*X,80+.8*p*(Y*.43-n(z))];};
 const poly=(pts:()=>V3[],fill:Color,stroke:Color=D.line,width=2)=><Line points={()=>pts().map(p=>point(...p))} closed fill={fill} stroke={stroke} lineWidth={width}/>;
 const line=(pts:()=>V3[],stroke:Color=D.teal,width=4)=><Line points={()=>pts().map(p=>point(...p))} stroke={stroke} lineWidth={width}/>;
 const box=(x:Value,y:Value,z:Value,w:number,d:number,h:Value,fill:Color,stroke:Color=D.line)=>{
  const p=(a:number,b:number,c:Value):V3=>[n(x)+a,n(y)+b,n(z)+n(c)];
  return<Node>
   {poly(()=>[p(-w/2,d/2,0),p(w/2,d/2,0),p(w/2,d/2,h),p(-w/2,d/2,h)],shade(fill,.68),stroke)}
   {poly(()=>[p(w/2,-d/2,0),p(w/2,d/2,0),p(w/2,d/2,h),p(w/2,-d/2,h)],shade(fill,.43),stroke)}
   {poly(()=>[p(-w/2,-d/2,h),p(w/2,-d/2,h),p(w/2,d/2,h),p(-w/2,d/2,h)],fill,stroke)}
  </Node>;
 };
 const solid=(x:Value,y:Value,z:Value,w:number,d:number,h:Value,fill:Color,stroke:Color=D.line)=>new Node({zIndex:()=>rotate(x,y)[1]+n(z)*.01,children:box(x,y,z,w,d,h,fill,stroke)});
 const label=(text:string|(()=>string),x:Value,y:Value,z:Value,size=28,fill:string=D.ink)=><Txt text={text} position={()=>point(x,y,z)} fontFamily={D.font} fontSize={size} fill={fill} fontWeight={600} zIndex={4000}/>;
 const arrow=(pts:()=>V3[],progress:Value=1,stroke:string=D.teal)=><Line points={()=>pts().map(p=>point(...p))} stroke={stroke} lineWidth={5} endArrow arrowSize={15} end={()=>n(progress)} zIndex={-2000}/>;
 return{point,rotate,poly,line,solid,label,arrow};
}
const HEAD:Record<string,[string,string,string]>={
 '01-overview':['색이 달라도 읽히는 화면','집의 윤곽 → 식물의 높이와 움직임 → 어둠 속 대비','첫 사례: 칠해도 남는 집과 길의 선'],
 '02-contours':['색칠과 윤곽을 나누기','채움은 달라져도 구조의 경계는 남기기','면의 색과 구조를 알려 주는 선을 구분합니다'],
 '03-pattern-and-erasing':['무늬도 정보를 남긴다','색 · 무늬 · 형태에 서로 다른 단서 담기','손잡이 비교는 가상의 설계 예시입니다'],
 '04-height-and-motion':['높이와 움직임으로 읽는 발판','발판의 윗면과 상태 변화를 따라가기','특정 색의 정답이나 최적 경로를 증명하는 도식이 아닙니다'],
 '05-state-not-hue':['현재 상태를 보여 주기','칠 여부와 현재 높이를 함께 읽기','서로 다른 샷 · 일부 식물은 다시 높아집니다'],
 '06-route-information':['중요한 단서를 겹쳐 놓기','캐릭터 · 발판 윗면 · 도착할 경계','장식이 행동에 필요한 정보를 가리지 않게'],
 '07-local-contrast':['어둠 속에서 대비를 남기기','분위기를 위한 어둠과 물체를 읽는 밝기 차이','제한된 밝은 영역 · 주변 전체의 밝기 상승이 아닙니다'],
 '08-check-and-conclusion':['색은 더하고 단서는 남기기','윤곽 · 무늬 · 높이와 움직임 · 밝기 차이','미리보기는 문제 찾기 보조 · 실제 플레이 확인 필요'],
};

export function* colorExplanation(view:View2D,id:string,timing:ColorTiming){
 if(!HEAD[id]||timing.durationSeconds<=0||timing.paragraphStarts.length!==3)throw Error('Independent color scene/timing contract missing');
 const t=createSignal(0);
 const phase=(i:number,d=1.6)=>smooth((t()-timing.paragraphStarts[i])/d);
 const part=(i:number)=>smooth((t()-timing.paragraphStarts[i])/Math.max(1,(timing.paragraphStarts[i+1]??timing.durationSeconds)-timing.paragraphStarts[i]));
 const s=projection(()=>10+8*smooth(t()/Math.min(8,timing.durationSeconds)));
 view.fill(D.background);
 view.add(<>
  <Txt text={'얌얌코딩 · 게임 기획과 디자인'} y={-470} fill={D.muted} fontFamily={D.font} fontSize={26}/>
  <Txt text={HEAD[id][0]} y={-385} fill={D.title} fontFamily={D.font} fontSize={52} fontWeight={650}/>
  <Txt text={HEAD[id][1]} y={-306} fill={D.ink} fontFamily={D.font} fontSize={30}/>
  <Txt text={HEAD[id][2]} y={300} fill={D.muted} fontFamily={D.font} fontSize={26}/>
 </>);
 const world=new Node({scale:.93});view.add(world);
 world.add(new Node({zIndex:-5000,children:s.solid(0,0,0,1600,610,20,D.surfaceTop)}));
 const block=(x:Value,y:Value,h:Value,c:Color=D.surfaceTop,w=120,d=110,z:Value=20,stroke:Color=D.line)=>world.add(s.solid(x,y,z,w,d,h,c,stroke));
 const tag=(text:string|(()=>string),x:Value,y:Value=265,z:Value=28,size=28,c:string=D.ink)=>world.add(s.label(text,x,y,z,size,c));
 const token=(x:Value,y:Value,z:Value,c:string=D.orange)=>world.add(s.solid(x,y,z,54,54,62,c,D.ink));
 const arrow=(points:()=>V3[],p:Value=1,c:string=D.teal)=>world.add(s.arrow(points,p,c));
 const house=(x:number,fill:Color,edge:Color=D.ink,pattern=true)=>{
  const y=0,w=240,d=190,h=195,z=20;
  const faces=new Node({zIndex:()=>s.rotate(x,y)[1],children:s.solid(x,y,z,w,d,h,fill,edge)});
  // Two inclined roof surfaces and a front triangle have real spatial depth.
  faces.add(s.poly(()=>[[x-w*.6,y+d*.6,z+h],[x+w*.6,y+d*.6,z+h],[x,y+d*.6,z+h+105]],shade(fill,.75),edge));
  faces.add(s.poly(()=>[[x,y-d*.6,z+h+105],[x,y+d*.6,z+h+105],[x+w*.6,y+d*.6,z+h],[x+w*.6,y-d*.6,z+h]],fill,edge));
  faces.add(s.poly(()=>[[x-w*.6,y-d*.6,z+h],[x-w*.6,y+d*.6,z+h],[x,y+d*.6,z+h+105],[x,y-d*.6,z+h+105]],shade(fill,.55),edge));
  faces.add(s.poly(()=>[[x-33,y+d*.5+.3,z],[x+33,y+d*.5+.3,z],[x+33,y+d*.5+.3,z+105],[x-33,y+d*.5+.3,z+105]],D.surfaceSide,edge));
  faces.add(s.poly(()=>[[x+65,y+d*.5+.5,z+100],[x+105,y+d*.5+.5,z+100],[x+105,y+d*.5+.5,z+145],[x+65,y+d*.5+.5,z+145]],D.surfaceSide,edge));
  if(pattern)for(let i=0;i<5;i++)faces.add(s.line(()=>[[x+20+i*22,y-d*.6,z+h+90-i*16],[x+20+i*22,y+d*.6,z+h+90-i*16]],edge,2));
  world.add(faces);
 };
 const flower=(x:number,y:number,height:Value,c:Color)=>{
  block(x,y,height,c,125,100);block(x,y,25,c,210,160,()=>20+n(height));
 };
 const cave=(x:number,y:number,lightX:Value,lightY:Value,brightness:Value=1)=>{
  // Floor layers precede all room objects; center-based depth must not put
  // a large floor in front of an obstacle located in the rear half.
  world.add(new Node({zIndex:-3000,children:s.solid(x,y,20,640,380,16,'#090c0e')}));
  const circle=new Node({zIndex:-2900,children:s.poly(()=>Array.from({length:48},(_,i)=>{const a=i*2*Math.PI/48;return[x+n(lightX)+170*Math.cos(a),y+n(lightY)+155*Math.sin(a),42] as V3;}),()=>n(brightness)>.5?'#b8b8b8':'#202428','#494e52',2)});
  world.add(circle);
  block(x+80,y-65,115,()=>n(brightness)>.5?'#e5e5e5':'#25292b',92,95,40,D.ink);
  token(()=>x+n(lightX),()=>y+n(lightY),48,D.teal);
  // This front wall really occludes part of the rear room as the view yaws.
  block(x+180,y+135,135,D.surfaceSide,270,55,36);
 };

 if(id==='01-overview'){
  house(-550,D.teal);tag('윤곽',-550,280);
  flower(0,-20,()=>85+90*phase(1),D.title);tag('높이와 움직임',0,285);
  block(560,-20,15,'#0d1012',310,280);block(560,-20,95,D.ink,85,85);tag('어둠 속 대비',560,285);
  token(()=>-540+540*phase(1)+560*phase(2),()=>145-60*part(2),()=>70+90*phase(1),D.orange);
  arrow(()=>[[-330,110,32],[-165,110,32]],()=>phase(1));arrow(()=>[[155,110,32],[350,110,32]],()=>phase(2));
 }else if(id==='02-contours'){
  const fill=()=>phase(1)<.5?D.teal:D.orange;
  house(-380,fill,D.ink);house(390,fill,()=>phase(2)<.5?D.ink:'#1a2428',false);
  tag('남겨 둔 윤곽',-380,275,28,30,D.teal);tag('약해진 경계',390,275,28,30,D.orange);
  arrow(()=>[[-230,60,35],[230,60,35]],()=>phase(1),D.title);
 }else if(id==='03-pattern-and-erasing'){
  const fill=()=>phase(0)<.6?D.orange:D.surfaceTop;
  house(-490,fill,D.ink);tag('지워도 남는 빗금',-490,290);
  block(135,0,170,D.teal,125,125);block(520,0,170,D.teal,125,125);
  world.add(s.line(()=>Array.from({length:33},(_,i)=>{const a=i*2*Math.PI/32;return[135+28*Math.cos(a),64,115+28*Math.sin(a)] as V3;}),D.ink,5));
  world.add(s.line(()=>[[490,64,90],[550,64,90],[550,64,150],[490,64,150],[490,64,90]],D.ink,5));
  tag('둥근 손잡이',135,285);tag('각진 손잡이',520,285);
  token(()=>-610+240*part(0),-50,340,D.ink);
  tag('가상의 장치 비교',340,-95,300,27,D.title);
 }else if(id==='04-height-and-motion'){
  const p=()=>part(2);
  [-490,0,490].forEach((x,i)=>{const h=()=>75+95*phase(0)-55*smooth((p()-i/4)*3);flower(x,-45,h,[D.teal,D.title,D.orange][i]);tag(['색 A','색 B','색 C'][i],x,285);});
  token(()=>-490+980*p(),-45,()=>230+100*Math.sin(Math.PI*3*p()),D.orange);
  arrow(()=>[[-620,90,40],[620,90,40]],()=>phase(1),D.teal);
  tag('윗면과 현재 높이',0,-155,345,29,D.ink);
 }else if(id==='05-state-not-hue'){
  const short=()=>195-105*phase(0)+80*phase(1);
  flower(-440,-30,short,()=>phase(0)<.5?D.surfaceTop:D.orange);
  flower(420,-30,()=>90+100*phase(2),()=>phase(2)<.5?D.orange:D.surfaceTop);
  token(()=>-540+240*part(1),-30,()=>135+90*(1-phase(1)),D.teal);
  tag('칠하기 → 일부 다시 높아짐',-440,290,28,27);
  tag('별도 장면: 지우기 → 높아짐',420,290,28,27);
  arrow(()=>[[-200,90,40],[190,90,40]],()=>phase(2),D.title);
 }else if(id==='06-route-information'){
  [-520,-100,300].forEach((x,i)=>flower(x,-120+i*75,95+i*28,D.teal));
  block(690,60,200,D.surfaceTop,120,250);
  const travel=()=>part(0);
  token(()=>-550+1200*travel(),()=>-115+175*travel(),()=>160+100*travel()+90*Math.sin(Math.PI*3*travel()),D.orange);
  const decorY=()=>-260+390*phase(1)-390*phase(2);
  const decor=new Node({zIndex:()=>s.rotate(80,decorY)[1],children:s.poly(()=>[[-300,decorY(),35],[410,decorY(),35],[410,decorY(),245],[-300,decorY(),245]],D.panel,D.muted)});
  world.add(decor);
  arrow(()=>[[-590,140,35],[700,140,35]],()=>phase(2),D.title);
  tag('배경 장식',80,()=>decorY()+10,280,26,D.muted);
  tag('도착할 턱',690,280,28,26,D.ink);
 }else if(id==='07-local-contrast'){
  const x=()=>-120+200*part(0),y=()=>-60+80*part(0);
  cave(-370,0,x,y,1);cave(370,0,x,y,()=>1-phase(1)+phase(2));
  tag('주변 윤곽이 남음',-370,285,28,28,D.teal);tag('명도 차이를 비교',370,285,28,28,D.title);
 }else if(id==='08-check-and-conclusion'){
  house(-520,()=>phase(0)<.5?D.teal:D.surfaceTop,D.ink);
  flower(0,-45,()=>90+95*phase(1),()=>phase(0)<.5?D.orange:D.surfaceTop);
  block(530,-45,12,'#101416',320,270);block(530,-45,125,D.ink,100,100);
  tag('윤곽 · 무늬',-520,285);tag('높이 · 움직임',0,285);tag('밝기 차이',530,285);
  token(()=>-530+530*phase(1)+530*phase(2),150,90,D.orange);
  arrow(()=>[[-325,140,35],[-155,140,35]],()=>phase(1));arrow(()=>[[160,140,35],[340,140,35]],()=>phase(2),D.title);
 }
 yield* t(timing.durationSeconds,timing.durationSeconds,linear);
}
