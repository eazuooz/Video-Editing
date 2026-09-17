import {Circle, Node, Rect, Txt, View2D} from '@motion-canvas/2d';
import {createSignal, tween, waitFor} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';
import plan from '../../../../../projects/let-them-play/planning/scenes.json';
import {NARRATION_FPS, SEGMENT_SECONDS, SEGMENT_DURATIONS} from '../timing';
import {editorialSections} from '../editorial/layout';

const clamp=(n:number)=>Math.max(0,Math.min(1,n));
const phase=(t:number,a:number,b:number)=>clamp((t-a)/(b-a));
const lerp=(a:number,b:number,t:number)=>a+(b-a)*t;

// Deterministic explanatory animation, not gameplay input or measured player data.
function* application(area:Node,index:number){
  const s=plan.scenes[index], kind=s.application.kind;
  const progress=createSignal(0);
  const stage=()=>Math.min(2,Math.floor(progress()*3));
  const actorX=createSignal(()=>lerp(-620,610,phase(progress(),0.12,0.86)));
  const actorY=createSignal(115);
  const caption=new Txt({y:270,text:()=>s.application.steps[stage()],fontFamily:P.font,fontSize:34,fill:P.ink});
  area.add(<>
    <Txt y={-230} text={s.application.title} fontFamily={P.font} fontSize={34} fill={P.blue}/>
    <Rect y={150} width={1510} height={3} fill={P.line}/>
    <Txt y={330} text={'자체 설명용 시연 · 경로/수치 사전 설정 · 실제 유저 실험 아님'} fontFamily={P.font} fontSize={23} fill={P.muted}/>
  </>);
  area.add(caption);
  if(kind==='goal'||kind==='recap'){
    const target=kind==='recap'?0:600;
    actorX(()=>lerp(-620,target,phase(progress(),0.12,0.70)));
    area.add(<>
      <Rect x={target} y={110} width={74} height={74} stroke={P.blue} lineWidth={3} fill={()=>progress()>0.72?P.yellow:P.panel}/>
      <Txt x={target} y={-15} text={'목표'} fontFamily={P.font} fontSize={28} fill={P.ink}/>
    </>);
    if(kind==='recap') area.add(<>
      <Rect x={610} y={110} width={74} height={74} opacity={()=>phase(progress(),0.72,0.82)} stroke={P.blue} lineWidth={3}/>
      <Txt x={610} y={-15} opacity={()=>phase(progress(),0.72,0.82)} text={'다음 목표'} fontFamily={P.font} fontSize={28} fill={P.ink}/>
    </>);
  } else if(kind==='switch'){
    actorX(()=>progress()<0.4?lerp(-620,-100,phase(progress(),0.1,0.35)):lerp(-100,610,phase(progress(),0.62,0.92)));
    area.add(<>
      <Rect x={-100} y={145} width={90} height={12} fill={()=>progress()>0.4?P.yellow:P.blue}/>
      <Txt x={-100} y={-60} text={'스위치'} fontFamily={P.font} fontSize={28} fill={P.ink}/>
      <Rect x={290} y={150} offset={[0,1]} width={30} height={()=>220*(1-phase(progress(),0.43,0.6))} fill={P.muted}/>
      <Txt x={300} y={-190} text={'출구'} fontFamily={P.font} fontSize={28} fill={P.ink}/>
    </>);
  } else if(kind==='route'){
    actorX(()=>lerp(-620,610,phase(progress(),0.14,0.88)));
    actorY(()=>115-205*Math.sin(Math.PI*phase(progress(),0.14,0.88)));
    area.add(<>
      <Rect x={0} y={70} width={260} height={115} fill={P.panel} stroke={P.line} lineWidth={2}/>
      <Txt y={70} text={'장애물'} fontFamily={P.font} fontSize={28} fill={P.muted}/>
      <Txt y={-130} text={'위로 돌아가기'} fontFamily={P.font} fontSize={28} fill={P.blue}/>
      <Txt y={205} text={'아래로 돌아가기 — 다른 경로'} fontFamily={P.font} fontSize={26} fill={P.muted}/>
      <Circle x={610} y={115} size={70} fill={P.yellow}/>
    </>);
  } else if(kind==='health'){
    actorX(()=>lerp(-620,-30,phase(progress(),0.1,0.43)));
    area.add(<>
      <Circle x={0} y={115} size={42} opacity={()=>1-phase(progress(),0.44,0.49)} fill={P.yellow}/>
      <Rect x={0} y={-80} width={640} height={36} fill={P.panel}/>
      <Rect x={-320} y={-80} offset={[-1,0]} width={()=>lerp(160,530,phase(progress(),0.58,0.77))} height={36} fill={P.blue}/>
      <Txt y={-140} text={'설명용 체력 막대'} fontFamily={P.font} fontSize={28} fill={P.ink}/>
    </>);
  } else if(kind==='bridge'){
    actorX(()=>progress()<0.5?lerp(-620,-300,phase(progress(),0.1,0.25)):lerp(-300,610,phase(progress(),0.65,0.92)));
    area.add(<>
      <Rect y={160} width={360} height={38} fill={P.background}/>
      <Rect x={()=>lerp(-430,0,phase(progress(),0.32,0.62))} y={()=>lerp(-55,145,phase(progress(),0.32,0.62))} width={380} height={18} fill={P.blue}/>
      <Txt y={215} text={'틈'} fontFamily={P.font} fontSize={28} fill={P.muted}/>
      <Txt y={-130} text={'발판 이동 도구'} fontFamily={P.font} fontSize={28} fill={P.ink}/>
    </>);
  } else if(kind==='hazard'){
    actorX(()=>progress()<0.35?lerp(-620,-100,phase(progress(),0.1,0.3)):progress()<0.52?lerp(-100,-420,phase(progress(),0.35,0.5)):lerp(-420,610,phase(progress(),0.62,0.93)));
    area.add(<>
      <Rect x={170} y={25} width={530} height={245} fill={P.blueLight}/>
      <Txt x={170} y={-140} text={'위험 구역'} fontFamily={P.font} fontSize={28} fill={P.ink}/>
      <Txt y={-70} text={()=>progress()<0.32?'진입':progress()<0.56?'경고 → 되돌아가기':'보호 ON → 다시 시도'} fontFamily={P.font} fontSize={30} fill={P.blue}/>
      <Circle x={actorX} y={actorY} size={88} opacity={()=>phase(progress(),0.55,0.61)} stroke={P.blue} lineWidth={3}/>
    </>);
  } else if(kind==='unlock'){
    actorX(()=>progress()<0.45?lerp(-620,-150,phase(progress(),0.1,0.36)):progress()<0.7?lerp(-150,180,phase(progress(),0.48,0.65)):lerp(180,640,phase(progress(),0.77,0.94)));
    area.add(<>
      <Circle x={-150} y={115} size={80} fill={()=>progress()>0.36?P.yellow:P.panel}/>
      <Circle x={180} y={115} size={80} fill={()=>progress()>0.65?P.yellow:P.panel}/>
      <Txt x={-150} y={-40} text={'목표 A'} fontFamily={P.font} fontSize={28} fill={P.ink}/>
      <Txt x={180} y={-40} text={'목표 B'} fontFamily={P.font} fontSize={28} fill={P.ink}/>
      <Rect x={480} y={150} offset={[0,1]} width={25} height={()=>200*(1-phase(progress(),0.69,0.76))} fill={P.muted}/>
      <Txt y={-145} text={'A → B / B → A 모두 가능 · 시연은 A → B'} fontFamily={P.font} fontSize={28} fill={P.muted}/>
    </>);
  }
  // Original neutral geometric character, not a Zelda asset.
  area.add(<Rect x={actorX} y={actorY} width={48} height={60} fill={P.blue}>
    <Circle x={-10} y={-12} size={7} fill={P.background}/>
    <Circle x={10} y={-12} size={7} fill={P.background}/>
  </Rect>);
  // Scene completion emits one final frame; include it in the third segment budget.
  yield* tween(SEGMENT_SECONDS-1/NARRATION_FPS,t=>progress(t));
}

import {designComparison} from './design-comparison';
import {showGameplay} from './gameplay';

export function* legacyConceptCard(view:View2D,index:number){
  const seconds=SEGMENT_DURATIONS[index];
  const s=plan.scenes[index];view.fill(P.background);
  const section=new Txt({x:-864,y:-477,offset:[-1,0],text:'1/3 · 야숨 사례 관찰',fontFamily:P.font,fontSize:24,fill:P.muted});
  view.add(<>
    <Txt x={-864} y={-394} offset={[-1,0]} width={1650} textWrap text={s.title} fontFamily={P.font} fontSize={48} fill={P.ink}/>
    <Rect y={405} width={1728} height={90} fill={P.panel}>
      <Txt text={s.key} fontFamily={P.font} fontSize={32} fill={P.ink}/>
    </Rect>
  </>);
  const gameplay=showGameplay(view,index);
  // Resolve metadata/seeking before play; yielding a resource does not add frames.
  yield gameplay.video;
  gameplay.video.play();
  yield* waitFor(seconds);gameplay.close();
  section.text('2/3 · 게임 디자인 설명');
  let area=new Node({});view.add(area);
  const steps=s.diagram.split(' → ');
  const progress=createSignal(0);
  const active=()=>Math.min(steps.length-1,Math.floor(progress()*steps.length));
  const stepWidth=Math.min(370,1500/steps.length);
  steps.forEach((step,i)=>{
    const x=(i-(steps.length-1)/2)*(stepWidth+35);
    area.add(<>
      <Rect x={x} y={0} width={stepWidth} height={155} fill={()=>active()===i?P.blueLight:P.panel} stroke={P.line} lineWidth={2}/>
      <Txt x={x} y={0} width={stepWidth-25} textWrap textAlign={'center'} text={step} fontFamily={P.font} fontSize={30} fill={P.ink}/>
    </>);
    if(i<steps.length-1)area.add(<Txt x={x+stepWidth/2+18} y={0} text={'→'} fontFamily={P.font} fontSize={28} fill={P.blue}/>);
  });
  area.add(<Txt y={-200} text={'관찰한 행동을 설계 원리로 연결'} fontFamily={P.font} fontSize={32} fill={P.blue}/>);
  yield* tween(seconds,t=>progress(t));area.remove();
  section.text('3/3 · 첫 장면 설계 비교 · 2.5D');
  area=new Node({});view.add(area);
  yield* designComparison(area,index,seconds-1/NARRATION_FPS);
}

// Approved 2026-09-14: editorial typography + original 2.5D chapter-specific art.
// The eight scene wrappers and measured thirds remain unchanged.
export function* conceptCard(view:View2D,index:number){
  const seconds=SEGMENT_DURATIONS[index];view.fill(P.background);
  const gameplay=showGameplay(view,index);yield gameplay.video;
  gameplay.video.play();yield* waitFor(seconds);gameplay.close();
  yield* editorialSections(view,index,seconds);
}
