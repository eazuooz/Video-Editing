import {makeScene2D,Img,Node,Txt,Rect,Line,Circle} from '@motion-canvas/2d';
import {createSignal,linear,Vector2} from '@motion-canvas/core';
import timing from '../../../../projects/shorts-mario-one-action/production/visual-timing.json';
import previewReward from '../../../../projects/shorts-mario-one-action/production/local/capture-preview-v2/reward-trace.json';
import previewCapture from '../../../../projects/shorts-mario-one-action/production/local/capture-preview-v2/capture-trace.json';
import {createReactionMascot,reactionPresence} from './reaction-mascot';
const C={white:'#FFFFFF',yellow:'#FFD25A',green:'#92DF9C',red:'#F27C70',teal:'#73D7CD',muted:'#B8C3BC'};
const FONT='Malgun Gothic';
const ROOT='/@fs/D:/Github/VideoEditing/projects/shorts-mario-one-action/production/local/';
const PREFLIGHT=new URLSearchParams(window.location.search).get('preflight')==='1';
export default makeScene2D(function*(view){
 const t=createSignal(0),clamp=(x:number,a=0,b=1)=>Math.max(a,Math.min(b,x));
 const sections=timing.sections as any[];
 const section=()=>sections.find(s=>t()>=s.start&&t()<s.end)??sections[sections.length-1];
 const game=()=>section().kind==='game',closing=()=>section().state==='closing',elapsed=()=>t()-section().start;
 const frame=()=>clamp(Math.floor(elapsed()*60+1e-5),0,Math.round((section().end-section().start)*60)-1);
 const reaction=()=>reactionPresence(t);
 const previewState=()=>{const state=section().state==='reward'?previewReward:previewCapture;const f=(section().sourceStart+elapsed())*60;return state.frames.reduce((a,b)=>Math.abs(b.frame-f)<Math.abs(a.frame-f)?b:a);};
 const record=()=>{const s=section();return s.kind==='game'?null:PREFLIGHT?previewState():(timing.traces as any)[s.state]?.frames[clamp(Math.floor((s.sourceStart+elapsed())*60+1e-5),0,389)];};
 const point=(p:any)=>new Vector2((p?.x??540)-540,(p?.y??540)-540);
 view.fill('#000000');
 const world=new Node({position:[-30,-45],x:()=>-30-120*reaction(),scale:()=>1-.19*reaction()});view.add(world);
 const picture=new Rect({width:1000,height:920,clip:true,opacity:()=>closing()?0:1});world.add(picture);
 picture.add(<Img src={()=>PREFLIGHT&&!game()?ROOT+'capture-preview-v2/'+(section().state==='reward'?'reward':'capture')+'-'+String(previewState().frame).padStart(4,'0')+'.png':ROOT+'frames/'+(closing()?'new-target':section().id)+'/frame-'+String(closing()?160:frame()).padStart(4,'0')+'.jpg'} width={1000} height={()=>game()?562.5:1000} smoothing={true}/>);
 // A trace comes only from our executable collider query; never from the game.
 const guides=new Node({opacity:()=>game()?0:1,scale:1000/1080});picture.add(guides);
 guides.add(<Circle width={90} height={90} position={()=>point(record()?.projectile)} stroke={C.teal} lineWidth={7} opacity={()=>record()?.input&&!record()?.contact?1:0}/>);
 guides.add(<Circle width={115} height={115} position={()=>point(record()?.target)} stroke={C.green} lineWidth={7} opacity={()=>record()?.contact?1:0}/>);
 const marks=(timing as any).annotations??[];
 const marker=()=>marks.find((m:any)=>m.section===section().id&&elapsed()>=m.start&&elapsed()<m.end);
 const target=()=>{const m=marker();if(!m)return null;const anchors=m.anchors as number[][];let a=anchors[0],b=anchors[anchors.length-1];for(let i=0;i<anchors.length-1;i++)if(elapsed()>=anchors[i][0]&&elapsed()<=anchors[i+1][0]){a=anchors[i];b=anchors[i+1];break;}const u=clamp((elapsed()-a[0])/Math.max(.001,b[0]-a[0]));return {x:(a[1]*(1-u)+b[1]*u-960)*1000/1920,y:(a[2]*(1-u)+b[2]*u-540)*1000/1920};};
 picture.add(<Circle width={()=>marker()?.width??140} height={()=>marker()?.height??140} position={()=>{const p=target();return p?[p.x,p.y]:[0,0];}} stroke={C.green} lineWidth={7} opacity={()=>game()&&target()?1:0}/>);
 // Fixed claim and game/implementation chips survive every scene boundary.
 view.add(<Rect width={1080} height={488} position={[0,-716]} fill="#000000"/>);
 view.add(<Txt text="얌얌코딩" fontFamily={FONT} fontSize={37} fontWeight={700} fill={C.muted} position={[-340,-820]}/>);
 view.add(<Txt text="코인 줍던 모자로" fontFamily={FONT} fontSize={77} fontWeight={700} fill={C.white} position={[-30,-700]}/>);
 view.add(<Txt text="공룡까지?" fontFamily={FONT} fontSize={88} fontWeight={700} fill={C.yellow} position={[-30,-590]}/>);
 view.add(<Txt text={()=>game()?'SUPER MARIO ODYSSEY':'우리 구현 · 같은 입력 / 같은 던지기'} fontFamily={FONT} fontSize={31} fill={()=>game()?C.muted:C.teal} position={[-30,-475]}/>);
 view.add(<Txt text={()=>section().label??''} fontFamily={FONT} fontSize={39} fontWeight={700} fill={C.yellow} position={[-30,-395]}/>);
 view.add(<Txt text={()=>marker()?.label??''} fontFamily={FONT} fontSize={30} fill={C.green} position={[-30,285]} opacity={()=>game()&&marker()?1:0}/>);
 // One input -> throw -> target response. Highlight actual state after the query.
 const flow=new Node({position:[-30,205],opacity:()=>game()||closing()?0:1-reaction()});view.add(flow);
 const flowStep=()=>record()?.contact?2:record()?.input?1:0;
 const xs=[-325,-40,265],names=['같은 버튼','같은 던지기','다른 결과'];
 for(let i=0;i<3;i++)flow.add(<Txt text={names[i]} fontFamily={FONT} fontSize={33} fontWeight={700} fill={()=>flowStep()>=i?(i===2?C.green:C.teal):C.muted} position={[xs[i],0]}/>);
 for(let i=0;i<2;i++)flow.add(<Line points={[[xs[i]+95,0],[xs[i+1]-100,0]]} stroke={C.teal} lineWidth={5} endArrow arrowSize={14} end={()=>flowStep()>i?1:clamp((elapsed()-.6-i*.35)/.35)}/>);
 view.add(<Txt text={()=>game()||closing()?'':record()?.contact?(section().state==='reward'?'보상 0 → '+record()?.rewards:reaction()>.1?'상대를 조종':'조종 대상 → 상대 캐릭터'):'대상에게 던져 보세요'} fontFamily={FONT} fontSize={37} fontWeight={700} fill={()=>record()?.contact?C.green:C.white} position={()=>[reaction()>.1?-300:-30,285]}/>);
 const comparison=new Node({position:[-30,-60],opacity:()=>closing()?1:0});view.add(comparison);
 for(let i=0;i<2;i++){
  const pane=new Rect({width:455,height:455,clip:true,position:[i===0?-245:245,0],stroke:i===0?C.teal:C.green,lineWidth:4});comparison.add(pane);
  pane.add(<Img src={PREFLIGHT?ROOT+'capture-preview-v2/'+(i===0?'reward':'capture')+'-0235.png':ROOT+'frames/closing-'+(i===0?'reward':'capture')+'.jpg'} width={455} height={455}/>);
  comparison.add(<Txt text={i===0?'같은 던지기 → 보상':'같은 던지기 → 조종'} fontFamily={FONT} fontSize={34} fontWeight={700} fill={i===0?C.teal:C.green} position={[i===0?-245:245,270]}/>);
 }
 comparison.add(<Txt text="하던 행동에 새 쓰임을 연결" fontFamily={FONT} fontSize={41} fontWeight={700} fill={C.white} position={[0,-290]}/>);
 // Large Korean meanings point to the unmodified native Dash/Attack prompt.
 const prompt=new Node({opacity:()=>t()>=timing.controlPromptCue.start&&t()<timing.controlPromptCue.end?1:0});view.add(prompt);
 prompt.add(<Line points={[[-150,245],[-150,205],[-55,150]]} stroke={C.teal} lineWidth={3}/>);
 prompt.add(<Line points={[[160,245],[160,205],[95,150]]} stroke={C.green} lineWidth={3}/>);
 prompt.add(<Txt text="이동·돌진" fontFamily={FONT} fontSize={42} fontWeight={700} fill={C.teal} position={[-150,280]}/>);
 prompt.add(<Txt text="공격" fontFamily={FONT} fontSize={42} fontWeight={700} fill={C.green} position={[160,280]}/>);
 view.add(createReactionMascot(t));
 // Final keyword ASS captions are encoded above all diagrams and the cat.
 yield* t(timing.durationSeconds,timing.durationSeconds,linear);
});
