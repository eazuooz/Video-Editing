import {Node,Rect,Txt,Line,Circle,View2D} from '@motion-canvas/2d';
import {createSignal,tween} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';
import {OpeningWorld} from '../editorial-sample/world';
import {DesignWorld} from './world';
import {editorialContent} from './content';
import {ramp,lerp} from './art';

function hint(parent:Node,x:number,y:number,text:string,opacity:()=>number,width=210){
 parent.add(<Rect x={x} y={y} width={width} height={49} fill={P.background} stroke={P.line} lineWidth={1} opacity={opacity}>
  <Txt text={text} fontFamily={P.font} fontSize={26} fill={P.ink}/>
 </Rect>);
}

function diorama(parent:Node,index:number,progress:()=>number,clock:()=>number,comparison=false,bad=false){
 const scale=comparison?.75:1,world=index===2?new OpeningWorld({y:25,scale}):new DesignWorld({y:25,scale});parent.add(world);
 if(world instanceof OpeningWorld){world.clock(clock);world.focus(()=>bad?0:ramp(progress(),.4,.56));world.annotations(()=>comparison?0:ramp(progress(),.66,.77))}
 else{world.chapter(index);world.phase(progress);world.clock(clock);world.alternative(bad);world.comparison(comparison)}
 // Labels describe the fictional design choice, not production status or sources.
 if(index===0){
  ['세계의 배경','조작 방법','여행의 목표'].forEach((s,j)=>hint(parent,0,-151+j*68,s,()=>comparison?(bad?1-ramp(progress(),.54,.66):0):ramp(progress(),.54,.62)*(1-ramp(progress(),.88,.95)),comparison?396:430));
 }
 if(index===1&&comparison&&bad)hint(parent,147,121,'출구는 화면 밖 →',()=>1,275);
 if(index===2&&!comparison){
  const marker=new Node({x:302,y:-253,opacity:()=>ramp(progress(),.57,.63)});parent.add(marker);
  marker.add(<><Txt text={'첫 관심 대상'} fontFamily={P.font} fontSize={29} fontWeight={600} fill={P.blue}/><Line points={[[0,26],[0,62],[-27,91]]} stroke={P.blue} lineWidth={2}/></>);
 }
 if(index===3){
  const labels=['살펴보기','줍기','사용하기'];
  labels.forEach((s,j)=>hint(parent,-205+j*205,-153,s,()=>{
   if(comparison&&bad)return 1;
   return j===0?1-ramp(progress(),.39,.45):j===1?ramp(progress(),.4,.46)*(1-ramp(progress(),.65,.71)):ramp(progress(),.67,.75);
  },177));
 }
 if(index===4){
  if(comparison&&bad)hint(parent,153,111,'문 반응은 화면 밖 →',()=>ramp(progress(),.38,.48),288);
  else hint(parent,99,-189,'스위치 → 열린 길',()=>ramp(progress(),.4,.57),282);
 }
 if(index===5){
  const health=()=>1-.38*ramp(progress(),.48,.62);
  parent.add(<>
   <Txt x={-237} y={-191} text={'상태'} fontFamily={P.font} fontSize={26} fill={P.ink}/>
   <Rect x={-237} y={-153} width={184} height={19} fill={P.panel} stroke={P.line} lineWidth={1}/>
   <Rect x={-329} y={-153} offset={[-1,0]} width={()=>184*health()} height={19} fill={()=>health()<.8?P.red:P.blue}/>
  </>);
  if(!bad){hint(parent,130,-178,'위험 구역',()=>1,185);parent.add(<Line points={[[93,-151],[52,-107]]} endArrow stroke={P.blue} lineWidth={2}/>)}
 }
 if(index===6){
  ['움직여 살펴보기','가까운 대상 조사','문 너머로 이동'].forEach((s,j)=>hint(parent,0,comparison&&bad?-153+j*65:comparison?-203:-242,s,()=>{
   if(comparison&&bad)return 1-ramp(progress(),.78,.9);
   return j===0?1-ramp(progress(),.26,.33):j===1?ramp(progress(),.31,.38)*(1-ramp(progress(),.59,.67)):ramp(progress(),.65,.73);
  },400));
 }
 if(index===7){
  hint(parent,-152,comparison?-169:-205,'첫 목표 도착',()=>ramp(progress(),.53,.59),212);
  if(!bad)hint(parent,comparison?217:294,comparison?-186:-270,'다음 관심사',()=>ramp(progress(),.68,.78),212);
 }
 return world;
}

/** One shared art direction, eight independent chapter scenes and visual lessons.
 * Duration comes from the measured narration timeline; no audio/SRT regeneration.
 */
export function* editorialSections(view:View2D,index:number,seconds:number){
 const cfg=editorialContent[index],t=createSignal(0),p=()=>t()/seconds,cp=()=>Math.max(0,(t()-seconds)/seconds);
 const explanation=new Node({opacity:()=>ramp(t(),0,.35)*(1-ramp(t(),seconds-.35,seconds))});view.add(explanation);
 explanation.add(<>
  <Txt x={-852} y={-394} offset={[-1,0]} text={cfg.eyebrow} fontFamily={P.font} fontSize={30} fontWeight={600} fill={P.blue}/>
  <Txt x={-856} y={-283} offset={[-1,0]} text={cfg.title} fontFamily={P.font} fontSize={60} fontWeight={700} lineHeight={86} fill={P.ink}/>
  <Line points={[[-850,-150],[-782,-150]]} stroke={P.blue} lineWidth={5}/>
 </>);
 cfg.words.forEach((word,j)=>{
  const active=()=>p()>.12+j*.22;
  explanation.add(<>
   <Circle x={-839} y={-50+j*100} size={10} fill={()=>active()?P.blue:P.line}/>
   <Txt x={-807} y={-50+j*100} offset={[-1,0]} text={word} fontFamily={P.font} fontSize={36} fontWeight={600} fill={()=>active()?P.blue:P.ink}/>
   <Txt x={-654} y={-47+j*100} offset={[-1,0]} text={cfg.notes[j]} fontFamily={P.font} fontSize={27} fill={P.muted}/>
  </>);
 });
 explanation.add(<>
  <Txt x={-852} y={334} offset={[-1,0]} text={cfg.bottom[0]} fontFamily={P.font} fontSize={31} fill={P.ink}/>
  <Txt x={-852} y={382} offset={[-1,0]} text={cfg.bottom[1]} fontFamily={P.font} fontSize={31} fontWeight={600} fill={P.blue}/>
 </>);
 const heroFrame=new Rect({x:322,y:111,width:1070,height:700,clip:true});explanation.add(heroFrame);
 const main=diorama(heroFrame,index,p,t);main.scale(()=>lerp(.98,1.02,ramp(p(),0,1)));
 const compare=new Node({opacity:()=>ramp(t(),seconds,seconds+.35)});view.add(compare);
 compare.add(<>
  <Txt x={-852} y={-399} offset={[-1,0]} text={cfg.compare} fontFamily={P.font} fontSize={55} fontWeight={700} fill={P.ink}/>
  <Txt x={-851} y={-318} offset={[-1,0]} text={index===2?'지형과 대상은 그대로 · 강조만 바꿔봅니다':index===1||index===4?'같은 대상 · 같은 동작 · 다른 카메라 구도':index===6?'전달할 정보는 그대로 · 시점만 바꿔봅니다':'첫 플레이 장면의 설계 비교'} fontFamily={P.font} fontSize={29} fill={P.muted}/>
  <Line points={[[0,-217],[0,300]]} stroke={P.line} lineWidth={1}/>
 </>);
 for(const [side,x] of [-440,440].entries()){
  const panel=new Rect({x,y:77,width:786,height:554,clip:true});compare.add(panel);
  diorama(panel,index,cp,t,true,side===0);
  compare.add(<>
   <Line points={[[x-390,-215],[x-342,-215]]} stroke={side?P.blue:P.ink} lineWidth={4}/>
   <Txt x={x-315} y={-215} offset={[-1,0]} text={side?cfg.after:cfg.before} fontFamily={P.font} fontSize={32} fontWeight={600} fill={side?P.blue:P.ink}/>
  </>);
 }
 const takeaway=new Node({y:397,opacity:()=>ramp(cp(),.46,.53)});compare.add(takeaway);
 takeaway.add(<>
  <Line points={[[-668,-47],[668,-47]]} stroke={P.line} lineWidth={1}/>
  <Txt text={cfg.takeaway} fontFamily={P.font} fontSize={39} fontWeight={600} fill={P.ink}/>
  <Line points={[[125,29],[535,29]]} stroke={P.yellow} lineWidth={7} opacity={.7}/>
 </>);
 yield* tween(seconds*2-1/60,v=>t(v*(seconds*2-1/60)));
}
