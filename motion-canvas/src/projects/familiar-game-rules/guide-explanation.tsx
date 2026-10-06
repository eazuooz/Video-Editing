import {Circle, Line, Rect, Txt, View2D} from '@motion-canvas/2d';
import {all, createRef, waitFor} from '@motion-canvas/core';
import {PAPER} from '../../styles/research-paper';

/** New, voiced comparisons may supplement the original six explanations without replacing them. */
export function* guideExplanation(view:View2D, id:'14'|'17', frames:number, lookdev=false) {
  if (!Number.isInteger(frames) || frames<120) throw new Error('Measured explanation needs at least120 frames.');
  view.removeChildren(); view.fill(PAPER.background);
  const title=id==='14' ? '같은 도구에 연결되는 여러 행동' : '몸의 이동과 목표 선택을 나누어 보기';
  view.add(<Txt text={`${id} · 실제 사례에서 기능 비교`} x={-855} y={-465} offset={[-1,0]} fontFamily={PAPER.font} fontSize={28} fill={PAPER.muted}/>);
  view.add(<Txt text={title} x={-855} y={-385} offset={[-1,0]} fontFamily={PAPER.font} fontSize={48} fill={PAPER.ink}/>);
  let used=0;
  if (id==='14') {
    const tool=createRef<Rect>();
    view.add(<Rect ref={tool} y={-135} width={490} height={160} opacity={0}>
      <Rect x={14} y={14} width={490} height={160} fill={PAPER.line}/>
      <Rect width={490} height={160} fill={PAPER.blueLight} stroke={PAPER.line} lineWidth={2}/>
      <Txt text={'같은 우산'} fontFamily={PAPER.font} fontSize={38} fill={PAPER.ink}/>
    </Rect>);
    yield* all(tool().opacity(1,.18),tool().y(-151,.18));used+=.18;
    const labels=['이동','도구 상태','공격 방향'];
    const details=['몸이 지나가는 길','펼침과 닫힘','대상을 향하는 쪽'];
    for (let i=0;i<3;i++) {
      const x=(i-1)*540;const card=createRef<Rect>();const arrow=createRef<Line>();
      view.add(<Line ref={arrow} points={[[0,-68],[x,-2],[x,46]]} stroke={PAPER.blue} lineWidth={5} endArrow end={0}/>);
      view.add(<Rect ref={card} x={x} y={140} width={450} height={170} opacity={0}>
        <Rect x={12} y={12} width={450} height={170} fill={PAPER.line}/>
        <Rect width={450} height={170} fill={PAPER.panel} stroke={PAPER.line} lineWidth={2}/>
        <Txt text={labels[i]} y={-37} fontFamily={PAPER.font} fontSize={34} fill={PAPER.ink}/>
        <Txt text={details[i]} y={35} fontFamily={PAPER.font} fontSize={27} fill={PAPER.muted}/>
      </Rect>);
      yield* all(arrow().end(1,.22),card().opacity(1,.22));used+=.22;
    }
    view.add(<Txt text={'보이는 행동의 관계 · 실제 버튼 배치의 확인과는 별도'} y={325} fontFamily={PAPER.font} fontSize={24} fill={PAPER.muted}/>);
  } else {
    const labels=['몸의 이동','총의 목표'];
    for (let i=0;i<2;i++) {
      const x=i===0?-435:435;
      view.add(<Rect x={x} y={-18} width={650} height={365}>
        <Rect x={14} y={14} width={650} height={365} fill={PAPER.line}/>
        <Rect width={650} height={365} fill={i===0?PAPER.panel:PAPER.blueLight} stroke={PAPER.line} lineWidth={2}/>
        <Txt text={labels[i]} y={-135} fontFamily={PAPER.font} fontSize={35} fill={PAPER.ink}/>
      </Rect>);
    }
    const body=createRef<Circle>();const left=createRef<Line>();const right=createRef<Line>();
    view.add(<Line points={[[-630,46],[-250,46]]} stroke={PAPER.muted} lineWidth={5} endArrow/>);
    view.add(<Circle ref={body} x={-610} y={46} size={36} fill={PAPER.green}/>);
    view.add(<Circle x={435} y={46} size={36} fill={PAPER.green}/>);
    view.add(<Circle x={230} y={-15} size={38} stroke={PAPER.blue} lineWidth={4}/>);
    view.add(<Circle x={640} y={-15} size={38} stroke={PAPER.blue} lineWidth={4}/>);
    view.add(<Line ref={left} points={[[420,46],[250,-8]]} stroke={PAPER.blue} lineWidth={6} endArrow end={0}/>);
    view.add(<Line ref={right} points={[[450,46],[620,-8]]} stroke={PAPER.blue} lineWidth={6} endArrow end={0}/>);
    yield* all(body().x(-280,.6),left().end(1,.6),right().end(1,.6));used+=.6;
    view.add(<Txt text={'경로를 따라 이동'} x={-435} y={235} fontFamily={PAPER.font} fontSize={29} fill={PAPER.muted}/>);
    view.add(<Txt text={'서로 다른 대상을 선택'} x={435} y={235} fontFamily={PAPER.font} fontSize={29} fill={PAPER.muted}/>);
    view.add(<Txt text={'이동의 방향과 목표 선택은 다른 역할'} y={325} fontFamily={PAPER.font} fontSize={24} fill={PAPER.muted}/>);
  }
  if (lookdev) view.add(<Rect y={430} width={1460} height={100}>
    <Rect x={10} y={10} width={1460} height={100} fill={'#315d45'}/>
    <Rect width={1460} height={100} fill={'#ffffff'} stroke={'#202020'} lineWidth={2}/>
    <Txt text={'내레이션 자막은 항상 아래 가운데에 고정합니다.'} fontFamily={PAPER.font} fontSize={48} fill={'#111111'}/>
  </Rect>);
  yield* waitFor(frames/60-used);
}
