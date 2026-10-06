import {Circle,Line,Rect,Txt,View2D} from '@motion-canvas/2d';
import {all,createRef,waitFor} from '@motion-canvas/core';
import {PAPER} from '../../styles/research-paper';
import plan from './scene-plan.json';
// Exact existing drawing primitives; these silent inputs do not bypass production gates.
export function* timedWhiteInput(view:View2D,id:string,frames:number){
const scene=plan.scenes.find(s=>s.id===id);if(!scene?.diagram)throw new Error('Independent explanation required');
const d=scene.diagram;view.removeChildren();
      view.fill(PAPER.background);
      view.add(<Txt text={`${id} · 익숙한 게임 조작`} x={-855} y={-465} offset={[-1,0]} fontFamily={PAPER.font} fontSize={28} fill={PAPER.muted}/>);
      view.add(<Txt text={scene.title} x={-855} y={-388} offset={[-1,0]} fontFamily={PAPER.font} fontSize={48} fill={PAPER.ink}/>);
      const cards=d.labels.map(()=>createRef<Rect>());
      const layout=d.kind==='bindings' ? [[-550,-85],[0,-85],[550,105]] :
        d.kind==='function' ? [[-550,-40],[0,-40],[550,115]] :
        d.kind==='checklist' ? [[-545,-120],[0,-20],[545,80]] : [[-555,-15],[0,-15],[555,-15]];
      for (let i=0;i<cards.length;i++) {
        const [x,y]=layout[i];
        view.add(<Rect ref={cards[i]} x={x} y={y+24} width={470} height={248} opacity={0}>
          <Rect x={14} y={16} width={470} height={248} fill={PAPER.line}/>
          <Rect width={470} height={248} fill={i===1?PAPER.blueLight:PAPER.panel} stroke={PAPER.line} lineWidth={2}/>
          <Txt text={d.labels[i]} y={-66} width={426} textWrap={'pre'} fontFamily={PAPER.font} fontSize={34} fill={PAPER.ink}/>
          <Txt text={d.details[i]} y={33} width={426} textWrap={'pre'} fontFamily={PAPER.font} fontSize={28} fill={PAPER.muted}/>
        </Rect>);
      }
      let used=0;
      for (let i=0;i<cards.length;i++) {
        yield* all(cards[i]().opacity(1,.3),cards[i]().y(layout[i][1],.3));
        yield* waitFor(.2); used+=.5;
      }
      const arrow=createRef<Line>();
      if (d.kind==='bindings') {
        view.add(<Line ref={arrow} points={[[-315,-85],[-250,-180],[-40,-180]]} stroke={PAPER.blue} lineWidth={6} endArrow end={0}/>);
        view.add(<Txt text={'연결 변경'} x={-175} y={-222} fontFamily={PAPER.font} fontSize={29} fill={PAPER.blue}/>);
      } else if (d.kind==='function') {
        view.add(<Line ref={arrow} points={[[220,-40],[285,-40],[315,60]]} stroke={PAPER.blue} lineWidth={6} endArrow end={0}/>);
        view.add(<Line points={[[-550,115],[-550,210],[215,210],[315,180]]} stroke={PAPER.green} lineWidth={5} endArrow/>);
        view.add(<Txt text={'선택 범위 · 연속성'} x={-175} y={240} fontFamily={PAPER.font} fontSize={29} fill={PAPER.green}/>);
      } else if (d.kind==='alternatives') {
        view.add(<Line ref={arrow} points={[[-555,-242],[0,-285],[555,-242]]} stroke={PAPER.blue} lineWidth={5} endArrow startArrow end={0}/>);
        view.add(<Txt text={'서로 다른 선택 과정'} y={220} fontFamily={PAPER.font} fontSize={31} fill={PAPER.blue}/>);
      } else if (d.kind==='checklist') {
        view.add(<Line ref={arrow} points={[[-305,-120],[-230,-120],[-240,-20]]} stroke={PAPER.blue} lineWidth={6} endArrow end={0}/>);
        view.add(<Line points={[[235,-20],[300,-20],[310,80]]} stroke={PAPER.blue} lineWidth={6} endArrow/>);
      } else {
        view.add(<Line ref={arrow} points={[[-320,-15],[-240,-15]]} stroke={PAPER.blue} lineWidth={6} endArrow end={0}/>);
        view.add(<Line points={[[235,-15],[315,-15]]} stroke={PAPER.blue} lineWidth={6} endArrow/>);
      }
      yield* arrow().end(1,.6); used+=.6;
      // Animated emphasis traces the chapter's comparison without moving the caption anchor.
      const marker=createRef<Circle>();
      view.add(<Circle ref={marker} x={layout[0][0]} y={layout[0][1]-146} size={18} fill={PAPER.blue}/>);
      for (let i=1;i<layout.length;i++) {yield* all(marker().x(layout[i][0],.45),marker().y(layout[i][1]-146,.45)); used+=.45;}
      view.add(<Txt text={d.footer} y={325} width={1640} fontFamily={PAPER.font} fontSize={24} textWrap={'pre'} fill={PAPER.muted}/>);

yield*waitFor(Math.max(0,frames/60-used));
// UI recalculation returned1262 for the1263-frame conclusion; preserve its last frame.
if(id==='11'&&frames===1263)yield;
}
