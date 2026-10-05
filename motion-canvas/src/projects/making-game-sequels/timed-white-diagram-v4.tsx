import {Line,Rect,Txt,View2D} from '@motion-canvas/2d';
import {all,createRef,waitFor} from '@motion-canvas/core';
import {PAPER} from '../../styles/research-paper';
import plan from './scene-plan.json';
// Exact drawing block extracted from the reviewed factory; production approval gates remain locked.
export function* measuredWhiteDiagram(view:View2D,id:string,frames:number){
const scene=plan.scenes.find(s=>s.id===id);if(!scene?.diagram)throw new Error('Reviewed white diagram required');
const diagram=scene.diagram;
      view.fill(PAPER.background);
      view.add(<Txt text={`${id} · 속편 기획`} x={-860} y={-466} fontSize={28}
        fill={PAPER.muted} fontFamily={PAPER.font} textAlign={'left'} offset={[-1,0]}/>);
      view.add(<Txt text={scene.title} x={-860} y={-399} fontSize={PAPER.titleSize}
        fill={PAPER.ink} fontFamily={PAPER.font} textAlign={'left'} offset={[-1,0]}/>);
      view.add(<Txt text={'우리의 설계 제안 · 실제 이용자 조사/개발사 내부 문서 아님'} x={-860} y={-316}
        fontSize={27} fill={PAPER.muted} fontFamily={PAPER.font} offset={[-1,0]}/>);
      const cards = diagram.labels.map(()=>createRef<Rect>());
      const positions = diagram.kind==='two-columns' ? [-470,470] :
        diagram.kind==='two-lanes' ? [-470,-470,470] : [-570,0,570];
      const vertical = diagram.kind==='two-lanes' ? [-150,150,0] : [0,0,0];
      for (let i=0;i<diagram.labels.length;i++) {
        const x=positions[i];
        view.add(<Rect ref={cards[i]} x={x} y={vertical[i]-15} width={470} height={270} opacity={0}>
          <Rect x={12} y={15} width={470} height={270} fill={PAPER.line}/>
          <Rect width={470} height={270} fill={i===1?PAPER.blueLight:PAPER.panel}
            stroke={PAPER.line} lineWidth={2}/>
          <Txt text={diagram.labels[i]} y={-67} width={424} fontSize={36} fill={PAPER.ink}
            fontFamily={PAPER.font} textWrap={'pre'}/>
          <Txt text={diagram.details[i]} y={34} width={416} fontSize={29} fill={PAPER.muted}
            fontFamily={PAPER.font} textWrap={'pre'}/>
        </Rect>);
      }
      for (let i=0;i<cards.length;i++) {
        yield* all(cards[i]().opacity(1,0.28),cards[i]().y(vertical[i],0.28));
        if(i>0 && diagram.kind!=='two-lanes') view.add(<Line points={[[positions[i-1]+240,0],[positions[i]-240,0]]}
          stroke={PAPER.blue} lineWidth={5} startArrow={diagram.kind==='two-columns'} endArrow={true} arrowSize={14}/>);
        yield* waitFor(0.3);
      }
      if(diagram.kind==='branch') {
        // Two distinct arrows show the proposed decision split, not a recreated game.
        view.add(<Line points={[[0,155],[180,230],[570,190]]} stroke={PAPER.blue} lineWidth={5} endArrow/>);
        view.add(<Line points={[[0,155],[180,270],[570,270]]} stroke={PAPER.blue} lineWidth={5} endArrow/>);
        view.add(<Txt text={'길 A'} x={705} y={190} fontSize={27} fill={PAPER.blue} fontFamily={PAPER.font}/>);
        view.add(<Txt text={'길 B'} x={705} y={270} fontSize={27} fill={PAPER.blue} fontFamily={PAPER.font}/>);
      }
      if(diagram.kind==='two-lanes') {
        view.add(<Line points={[[-225,-150],[0,-150],[225,-60]]} stroke={PAPER.blue} lineWidth={5} endArrow/>);
        view.add(<Line points={[[-225,150],[0,150],[225,60]]} stroke={PAPER.blue} lineWidth={5} endArrow/>);
        view.add(<Txt text={'각각 관찰하고 수정'} x={25} y={0} fontSize={27}
          fill={PAPER.blue} fontFamily={PAPER.font}/>);
      }
      if(diagram.kind==='two-columns') {
        view.add(<Txt text={'구분하여 검토'} y={75} fontSize={27}
          fill={PAPER.blue} fontFamily={PAPER.font}/>);
      }
      view.add(<Txt text={'유지할 활동 / 바꿀 조건 / 확인 과제'} y={315} fontSize={31}
        fill={PAPER.ink} fontFamily={PAPER.font}/>);

yield*waitFor(Math.max(0,frames/60-diagram.labels.length*.58));
// Actual UI recalculation returned594 for the595-frame two-card04 tail. Preserve its final frame explicitly.
if(id==='04'&&frames===595)yield;
}
