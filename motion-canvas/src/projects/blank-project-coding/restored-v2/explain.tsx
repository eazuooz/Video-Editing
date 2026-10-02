import {Circle,Line,Node,Rect,Txt,View2D} from '@motion-canvas/2d';
import {all,createRef,sequence,waitFor} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';
import visuals from './visuals.json';
import timing from './timing.json';
const PURPLE='#7C3AAD',AMBER='#BA750C',RED='#C34242',GREEN='#23875B',BLUE='#245CA8';
const T=(text:string,x:number,y:number,size=32,color:string=P.ink,width=1600)=><Txt text={text} x={x} y={y} width={width} textAlign={'center'} textWrap fontFamily={P.font} fontSize={size} fill={color}/>;
function panel(title:string,detail:string,x:number,y:number,w:number,color:string,ref:any){return <Node ref={ref} x={x} y={y} opacity={0}><Rect x={14} y={17} width={w} height={230} rotation={-1.5} fill={'#DCE3EC'}/><Rect width={w} height={230} rotation={-1.5} fill={'#FFFFFF'} stroke={color} lineWidth={3}/><Rect x={-w/2+16} width={7} height={174} fill={color}/>{T(title,0,-46,34,color,w-44)}{T(detail,0,52,27,P.muted,w-48)}</Node>;}
export function* explain(view:View2D,id:string){
 const c=visuals.find(v=>v.id===id)!,D=(timing as Record<string,number>)[id];view.fill(P.background);
 const body=createRef<Node>(),footer=createRef<Node>();const a=[createRef<Node>(),createRef<Node>(),createRef<Node>()],ar=[createRef<Line>(),createRef<Line>()];
 view.add(<>
  <Rect x={-938} y={-25} width={10} height={930} fill={c.risk?RED:GREEN}/>
  <Txt text={`AI 시대의 개발자 · ${String(c.chapter).padStart(2,'0')}장`} x={-850} y={-478} offset={[-1,0]} fontFamily={P.font} fontSize={23} fill={P.muted}/>
  {c.inference?<Txt text={'추론'} x={828} y={-477} fontFamily={P.font} fontSize={24} fill={AMBER}/>:null}
  <Txt text={c.title} x={-850} y={-393} offset={[-1,0]} width={1710} textWrap fontFamily={P.font} fontSize={c.title.length>32?45:53} fontWeight={700} fill={c.risk?RED:P.ink}/>
  <Txt text={c.sub} x={-850} y={-291} offset={[-1,0]} width={1690} textWrap fontFamily={P.font} fontSize={29} fill={P.muted}/>
  <Node ref={body}/>
  <Node ref={footer} y={283} opacity={0}><Rect x={11} y={12} width={1680} height={98} fill={'#DCE8E2'}/><Rect width={1680} height={98} fill={'#FFFFFF'} stroke={GREEN} lineWidth={2}/><Txt text={c.summary} width={1590} textAlign={'center'} textWrap fontFamily={P.font} fontSize={c.summary.length>55?27:31} fontWeight={600} fill={P.ink}/></Node>
 </>);
 let active:any[]=[];let arrows:any[]=[];
 if(c.kind==='dependency'){
  const center=createRef<Node>();body().add(<Node ref={center} y={-26} opacity={0}><Rect x={12} y={15} width={310} height={156} fill={'#E3DAEB'}/><Rect width={310} height={156} fill={'#FFFFFF'} stroke={PURPLE} lineWidth={4}/>{T(c.chapter===10?'아이템 잠금':'기존 시스템',0,0,36,PURPLE,284)}</Node>);active.push(center);
  const xs=[-605,0,605],ys=[-180,-180,-180];
  c.labels.forEach((label,i)=>{const x=xs[i],y=i===1?137:-45;const ref=createRef<Node>(),line=createRef<Line>();
   body().add(<><Line ref={line} points={i===1?[[0,54],[0,90]]:i===0?[[-158,-26],[-362,-26]]:[[158,-26],[362,-26]]} stroke={PURPLE} lineWidth={5} endArrow arrowSize={18} end={0}/><Node ref={ref} x={x} y={y} opacity={0}><Rect x={10} y={11} width={460} height={137} fill={'#DFE6EE'}/><Rect width={460} height={137} fill={'white'} stroke={BLUE} lineWidth={2}/>{T(label,0,-24,31,BLUE,422)}{T(c.details[i],0,31,23,P.muted,422)}</Node></>);active.push(ref);arrows.push(line);
  });
 }else if(c.kind==='blank'){
  body().add(<Node ref={a[0]} x={-300} y={-18} opacity={0}><Rect x={14} y={18} width={1080} height={382} fill={'#DCE3EC'}/><Rect width={1080} height={382} fill={'#F7F9FC'} stroke={P.line} lineWidth={2}/><Txt text={'main.cpp'} x={-476} y={-151} offset={[-1,0]} fontFamily={P.mono} fontSize={25} fill={P.muted}/><Line points={[[-510,-116],[510,-116]]} stroke={P.line} lineWidth={2}/><Txt text={'int'} x={-446} y={-65} fontFamily={P.mono} fontSize={50} fill={BLUE}/><Txt text={'main()'} x={-252} y={-65} fontFamily={P.mono} fontSize={50} fill={PURPLE}/><Txt text={'{\n\n}'} x={-472} y={58} fontFamily={P.mono} fontSize={50} fill={P.ink}/><Rect x={-418} y={58} width={4} height={49} fill={GREEN}/></Node>);
  body().add(<Node ref={a[1]} x={615} y={-20} opacity={0}>{c.labels.map((v,i)=><><Circle x={-196} y={-110+i*103} size={15} fill={[BLUE,PURPLE,GREEN][i]}/>{T(v,13,-110+i*103,31,[BLUE,PURPLE,GREEN][i],373)}{T(c.details[i],13,-70+i*103,24,P.muted,373)}</>)}</Node>);active=a.slice(0,2);
 }else if(c.kind==='tetris'){
  body().add(<Node ref={a[0]} x={-622} y={-16} opacity={0}>{Array.from({length:60},(_,i)=><Rect x={(i%6-2.5)*44} y={(Math.floor(i/6)-4.5)*37} width={42} height={35} fill={i>47?['#D9E4EE','#245CA8','#23875B','#7C3AAD'][i%4]:'#F7F9FC'} stroke={P.line} lineWidth={1}/>)}{[[1,1],[2,1],[2,2],[3,2]].map(([x,y])=><Rect x={(x-2.5)*44} y={(y-3)*37} width={42} height={35} fill={AMBER} shadowColor={'#DDD2BA'} shadowOffset={[6,7]} shadowBlur={0}/>)}</Node>);
  body().add(<Node ref={a[1]} x={240} y={-20} opacity={0}>{c.labels.map((v,i)=><><Rect x={0} y={-145+i*137} width={1010} height={98} fill={'#FFFFFF'} stroke={[BLUE,PURPLE,GREEN][i]} lineWidth={2} shadowColor={'#DFE6EE'} shadowOffset={[10,12]} shadowBlur={0}/>{T(v,-261,-145+i*137,32,[BLUE,PURPLE,GREEN][i],430)}{T(c.details[i],231,-145+i*137,26,P.muted,490)}</>)}</Node>);active=a.slice(0,2);
 }else{
  const n=c.labels.length,compare=n===2,xs=compare?[-442,442]:[-590,0,590],ys=c.kind==='stairs'||c.kind==='gap'?[77,-10,-97]:[-25,-25,-25];
  c.labels.forEach((v,i)=>{body().add(panel(v,c.details[i],xs[i],ys[i],compare?730:465,c.kind==='risk'||compare?[RED,GREEN,BLUE][i]:[BLUE,PURPLE,GREEN][i],a[i]));active.push(a[i]);});
  if(!compare){for(let i=0;i<2;i++){body().add(<Line ref={ar[i]} points={[[xs[i]+252,ys[i]],[xs[i+1]-252,ys[i+1]]]} stroke={i===0?BLUE:GREEN} lineWidth={5} endArrow arrowSize={18} end={0}/>);arrows.push(ar[i]);}}
  if(c.kind==='coaching')body().add(T('yamyamcoding.com',0,174,34,BLUE));
 }
 function* animation(){
  yield*sequence(.13,...active.map((r,i)=>all(r().opacity(1,.55),r().rotation(0,.55))));
  yield*waitFor(Math.max(.1,D*.19));
  if(arrows.length)yield*all(...arrows.map(r=>r().end(1,.65)));
  if(c.kind==='gap'){yield*all(active[0]().opacity(.20,.65),active[0]().y(103,.65),active[0]().scale(.78,.65));}
  else if(active.length>1)yield*active[active.length-1]().scale(1.025,.4);
  yield*footer().opacity(1,.4);
 }
 yield*all(animation(),waitFor(D+1e-7));
}
