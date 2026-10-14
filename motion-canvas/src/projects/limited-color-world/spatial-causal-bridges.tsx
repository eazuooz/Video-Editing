import {Line, Node, Txt, View2D} from '@motion-canvas/2d';
import {createSignal, linear} from '@motion-canvas/core';
import {DARK as D} from '../../styles/research-dark';

type V3 = [number, number, number];
type Value = number | (() => number);
type Paint = string | (() => string);
const value = (x: Value) => typeof x === 'function' ? x() : x;
const paint = (x: Paint) => typeof x === 'function' ? x() : x;
const smooth = (x: number) => {x = Math.min(1, Math.max(0, x)); return x*x*(3-2*x);};
const shade = (c: Paint, k: number) => () => '#'+[1,3,5].map(i => Math.round(parseInt(paint(c).slice(i,i+2),16)*k).toString(16).padStart(2,'0')).join('');
const titles: Record<string, [string, string]> = {
  '03b-static-to-state': ['구조에서 다음 움직임으로', '윤곽과 무늬 → 현재 높이와 다음 움직임'],
  '06b-outline-to-contrast': ['경계가 어둠에 묻히면', '길의 경계를 남기기 → 밝고 어두운 차이 확인'],
  '07b-cues-to-check': ['다른 색 조건에서도 남는가', '단서를 연결하기 → 다른 조건과 실제 플레이 확인'],
};

/** Additive bridges reuse the same objects and derive the next question.
 * The timing supplied by prototype wrappers is not measured narration timing. */
export function* causalColorBridge(view: View2D, id: string, duration: number) {
  if (!titles[id] || duration <= 0) throw Error('Missing independent causal bridge');
  const t = createSignal(0);
  const phase = (i: number) => smooth((t()/duration-i/3)*3);
  const yaw = () => (10+8*phase(0))*Math.PI/180;
  const depth = (x: Value, y: Value) => value(x)*Math.sin(yaw())+value(y)*Math.cos(yaw());
  const project = (x: Value, y: Value, z: Value): [number,number] => {
    const X=value(x)*Math.cos(yaw())-value(y)*Math.sin(yaw());
    const Y=depth(x,y), p=1600/(1600-Y*.28);
    return [.8*p*X,80+.8*p*(Y*.43-value(z))];
  };
  const polygon = (points: () => V3[], c: Paint, edge: Paint=D.line) =>
    <Line points={() => points().map(p => project(...p))} closed fill={c} stroke={edge} lineWidth={3}/>;
  const solid = (x: Value, y: Value, z: Value, w: number, d: number, h: Value, c: Paint, edge: Paint=D.line) => {
    const p=(a:number,b:number,k:Value):V3=>[value(x)+a,value(y)+b,value(z)+value(k)];
    return new Node({zIndex:()=>depth(x,y),children:<>
      {polygon(()=>[p(-w/2,d/2,0),p(w/2,d/2,0),p(w/2,d/2,h),p(-w/2,d/2,h)],shade(c,.68),edge)}
      {polygon(()=>[p(w/2,-d/2,0),p(w/2,d/2,0),p(w/2,d/2,h),p(w/2,-d/2,h)],shade(c,.43),edge)}
      {polygon(()=>[p(-w/2,-d/2,h),p(w/2,-d/2,h),p(w/2,d/2,h),p(-w/2,d/2,h)],c,edge)}
    </>});
  };
  const world = new Node({scale:.93});
  view.fill(D.background);
  view.add(<>
    <Txt text="얌얌코딩 · 게임 기획과 디자인" y={-470} fontFamily={D.font} fontSize={26} fill={D.muted}/>
    <Txt text={titles[id][0]} y={-385} fontFamily={D.font} fontSize={52} fontWeight={650} fill={D.title}/>
    <Txt text={titles[id][1]} y={-306} fontFamily={D.font} fontSize={30} fill={D.ink}/>
    <Txt text="앞의 결과에서 다음 확인 질문으로" y={300} fontFamily={D.font} fontSize={26} fill={D.muted}/>
    {world}
  </>);
  world.add(new Node({zIndex:-5000,children:solid(0,0,0,1600,610,20,D.surfaceTop)}));
  const label=(text:string,x:Value,y:Value=275,z:Value=30,c:string=D.ink)=>world.add(
    <Txt text={text} position={()=>project(x,y,z)} fontFamily={D.font} fontSize={28} fill={c} fontWeight={600} zIndex={4000}/>);
  const arrow=(a:V3,b:V3,progress:Value=1)=>world.add(<Line points={()=>[project(...a),project(...b)]} stroke={D.teal} lineWidth={5} endArrow arrowSize={15} end={()=>value(progress)} zIndex={-2000}/>);
  const house=(x:number,c:Paint)=>{
    world.add(solid(x,0,20,220,180,170,c,D.ink));
    const roof=new Node({zIndex:()=>depth(x,0)+1});
    roof.add(polygon(()=>[[x-132,108,190],[x+132,108,190],[x,108,285]],shade(c,.75),D.ink));
    roof.add(polygon(()=>[[x,-108,285],[x,108,285],[x+132,108,190],[x+132,-108,190]],c,D.ink));
    roof.add(polygon(()=>[[x-132,-108,190],[x-132,108,190],[x,108,285],[x,-108,285]],shade(c,.55),D.ink));
    for(let i=0;i<5;i++)roof.add(<Line points={()=>[[x+20+i*20,-108,272-i*14],[x+20+i*20,108,272-i*14]].map(p=>project(...p as V3))} stroke={D.ink} lineWidth={3}/>);
    world.add(roof);
  };
  const platform=(x:number,y:number,h:Value,c:Paint,edge:Paint=D.ink)=>{
    world.add(solid(x,y,20,95,95,h,c,edge));
    world.add(solid(x,y,()=>20+value(h),160,130,25,c,edge));
  };
  if(id==='03b-static-to-state'){
    house(-520,D.teal); label('멈춘 구조',-520,275,30,D.teal);
    const height=()=>65+115*phase(1)-45*phase(2);
    platform(280,-20,height,D.title);platform(650,20,110,D.teal);
    const travel=()=>phase(2);
    world.add(solid(()=>280+370*travel(),()=>-20+40*travel(),()=>value(height)+48+115*Math.sin(Math.PI*travel()),48,48,58,D.orange,D.ink));
    arrow([-300,100,35],[70,100,35],()=>phase(1));
    label('높이 변화와 이동',420,275);
  }else if(id==='06b-outline-to-contrast'){
    const contrast=()=>1-phase(1)+phase(2);
    const c=()=>contrast()>.5?D.teal:'#1b2124';
    const edge=()=>contrast()>.5?D.ink:'#22292d';
    platform(-480,-40,105,c,edge);platform(-70,0,145,c,edge);
    world.add(solid(580,50,20,210,240,190,c,edge));
    world.add(solid(()=>-470+970*phase(0),()=>-40+90*phase(0),()=>175+80*phase(0)+100*Math.sin(Math.PI*2*phase(0)),48,48,58,()=>contrast()>.5?D.orange:'#22272a',edge));
    label('윗면과 목적지 경계',-160,275);
    label('밝기 차이로 다시 확인',580,275,30,D.title);
    arrow([100,145,35],[450,145,35],()=>phase(2));
  }else{
    const gray=()=>phase(1)>.5;
    house(-520,()=>gray()?D.surfaceTop:D.teal);
    platform(0,-30,()=>80+90*phase(0),()=>gray()?D.surfaceTop:D.orange);
    world.add(solid(540,-30,20,260,240,16,'#101416'));
    world.add(solid(540,-30,36,85,85,110,D.ink,D.ink));
    world.add(solid(()=>-520+1060*phase(2),125,()=>90+55*Math.sin(Math.PI*3*phase(2)),48,48,58,D.orange,D.ink));
    label('윤곽 · 무늬',-520,275);label('높이 · 움직임',0,275);label('밝기 차이',540,275);
    arrow([-310,140,35],[-145,140,35],()=>phase(2));arrow([155,140,35],[330,140,35],()=>phase(2));
  }
  yield* t(duration,duration,linear);
}
