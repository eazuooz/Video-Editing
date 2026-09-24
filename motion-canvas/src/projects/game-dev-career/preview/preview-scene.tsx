import {Node,Rect,Txt,Line,View2D} from '@motion-canvas/2d';
import {createSignal,tween} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';
import {ChestWorld,ramp} from './chest-world';
import {CaptionBox} from './caption-box';
import timing from './timing.generated.json';

export function* previewScene(view:View2D,index:number,timeline:typeof timing=timing,boxedCaptions=false){
  const s=timeline.scenes[index] as typeof timing.scenes[number] & {labels?:string[];notes?:string[]},t=createSignal(0),p=()=>t()/s.duration;
  view.fill(P.background);
  const root=new Node({opacity:()=>ramp(t(),0,.28)*(1-ramp(t(),s.duration-.28,s.duration))});view.add(root);
  const right=new ChestWorld({x:440,y:110,scale:()=>.74+.03*ramp(p(),.03,.97)});
  right.clock(t);right.phase(p);right.chapter(index);root.add(right);
  root.add(<>
    <Line points={[[-846,-433],[-800,-433]]} stroke={P.blue} lineWidth={5}/>
    <Txt x={-778} y={-433} offset={[-1,0]} text={s.role} fontSize={23} fontFamily={P.font} fontWeight={600} fill={P.blue} letterSpacing={2}/>
    <Txt x={-850} y={-293} offset={[-1,0]} text={s.headline} lineHeight={82} fontSize={60} fontFamily={P.font} fontWeight={700} fill={P.ink}/>
  </>);
  const labels=s.labels??[['기획','프로그래밍','2D · 3D 아트'],['조건','결과','예외'],['C++ 기초','자료구조 · 알고리즘','디버깅'],['도형화','비례 · 원근','명암 · 색'],['형태 · 공간','면 구조 · 표면','회전축'],['관찰하고','직접 만들고','다시 고치기']][index];
  const active=()=>index===0?Math.min(2,Math.floor(p()*3)):index===2?(p()<.3?0:p()<.65?1:2):Math.min(2,Math.floor(p()*3.05));
  const notes=s.notes??[['한 가지 게임을','서로 다른 시선으로'],['열쇠가 없다면?','가방이 가득 찼다면?','같은 규칙을 이해하도록'],['데이터와 실행 흐름','어떻게 저장하고 찾을까?','중복 지급의 원인은?'],['큰 덩어리부터','방향이 달라도 자연스럽게','작은 화면에서도 선명하게'],['여러 각도에서 확인','표면은 어떻게 구성될까?','여기를 중심으로 열립니다'],['무엇이 다른지 보고','작은 것에 적용하고','바꾼 이유를 설명하기']][index];
  if(index!==2){
    labels.forEach((text,i)=>root.add(<Node y={-62+i*93}>
      <Line points={[[-843,-18],[-843,18]]} lineWidth={4} stroke={()=>active()===i?P.blue:P.line}/>
      <Txt x={-816} offset={[-1,0]} text={text} fontSize={37} fontWeight={600} fontFamily={P.font} fill={()=>active()===i?P.blue:P.muted}/>
    </Node>));
    root.add(<Txt x={-845} y={286} offset={[-1,0]} text={()=>notes[Math.min(notes.length-1,active())]} fontFamily={P.font} fontSize={27} fill={P.muted}/>);
  }else{
    root.add(<>
      <Rect x={-499} y={30} width={710} height={240} fill={P.panel}/>
      <Rect x={-507} y={()=>active()===2?54:active()===1?7:-40} width={625} height={37} fill={P.yellow} opacity={.4}/>
      <Txt x={-820} y={-62} offset={[-1,-1]} text={'if (!opened && hasKey) {\n  inventory.push_back(item);\n  opened = true;\n}'} fontFamily={P.mono} fontSize={28} lineHeight={47} fill={P.ink}/>
      <Txt x={-845} y={223} offset={[-1,0]} text={()=>labels[active()]} fontFamily={P.font} fontSize={36} fontWeight={600} fill={P.blue}/>
      <Txt x={-845} y={287} offset={[-1,0]} text={()=>notes[active()]} fontFamily={P.font} fontSize={27} fill={P.muted}/>
    </>);
  }
  if(index===1)root.add(<Txt x={449} y={-305} text={()=>p()<.6?'LOCKED':'OPEN'} fontFamily={P.font} fontSize={25} fontWeight={600} letterSpacing={4} fill={()=>p()<.6?P.muted:P.blue}/>);
  // Burn-in is opt-in for the reference-style sample. Clean masters stay clean.
  if(boxedCaptions){
    const caption=new CaptionBox({y:430});
    caption.text(()=>timeline.captions.find(c=>t()+s.firstFrame/60>=c.start&&t()+s.firstFrame/60<c.end)?.ko??'');
    view.add(caption);
  }
  yield* tween(s.frames/60,progress=>t(progress*s.duration));
}
