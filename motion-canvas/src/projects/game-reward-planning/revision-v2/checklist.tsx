import {Line, makeScene2D, Node, Rect, Txt} from '@motion-canvas/2d';
import {all, createRef, createSignal, easeInOutCubic, waitFor} from '@motion-canvas/core';
import {DARK as D} from '../../../styles/research-dark';

// Independently authored explanation, not a reproduction of Kirby UI.
// Preview timings are deliberately separate from future narration-aligned cuts.
export default makeScene2D(function* (view) {
  const condition = createRef<Txt>();
  const current = createRef<Rect>();
  const next = createRef<Rect>();
  const currentLabel = createRef<Txt>();
  const nextLabel = createRef<Txt>();
  const path = createRef<Line>();
  const state = createRef<Txt>();
  const progress = createRef<Txt>();
  const caption = createRef<Txt>();
  const complete = createSignal(0);
  const fillProgress = createRef<Rect>();
  const note = createRef<Txt>();
  view.fill(D.background);
  view.add(<>
    <Txt x={-850} y={-459} offset={[-1, 0]} text={'얌얌코딩  /  게임 보상 기획'} fontFamily={D.font} fontSize={28} fill={D.muted}/>
    <Txt x={-850} y={-360} offset={[-1, 0]} text={'보상 다음에, 할 일이 보이게'} fontFamily={D.font} fontSize={66} fontWeight={700} fill={D.title}/>
    <Txt x={-850} y={-278} offset={[-1, 0]} text={'설명용 과제판 · 실제 게임의 조건과 수치가 아닙니다'} fontFamily={D.font} fontSize={32} fill={D.muted}/>
    <Node x={-430} y={30}>
      {[0, 1, 2].flatMap(row => [0, 1, 2].map(col => {
        const isCurrent = row === 1 && col === 1;
        const isNext = row === 1 && col === 2;
        return <Node x={(col - 1) * 260} y={(row - 1) * 156}>
          <Rect ref={isCurrent ? current : isNext ? next : undefined} width={196} height={136}
            fill={D.background} stroke={isCurrent ? D.title : D.line} lineWidth={isCurrent ? 8 : 3}/>
          <Txt ref={isCurrent ? currentLabel : isNext ? nextLabel : undefined}
            text={isCurrent ? '첫 완주' : '?'} fontFamily={D.font} fontSize={isCurrent ? 42 : 52}
            fill={isCurrent ? D.title : D.muted} fontWeight={600}/>
        </Node>;
      }))}
      <Txt y={270} text={() => `완료 ${complete()} / 9`} fontFamily={D.font} fontSize={44} fill={D.ink}/>
    </Node>
    <Line ref={path} points={[[-324, 30], [-276, 30]]} stroke={D.teal} lineWidth={9} endArrow arrowSize={20} end={0}/>
    <Node x={475}>
      <Txt ref={state} y={-155} text={'현재 목표'} fontFamily={D.font} fontSize={38} fill={D.title}/>
      <Txt ref={condition} y={-70} text={'첫 코스를 완주하기'} fontFamily={D.font} fontSize={48} fill={D.ink} fontWeight={700}/>
      <Txt ref={progress} y={30} text={'아직 완료하지 않았어요'} fontFamily={D.font} fontSize={36} fill={D.muted}/>
      <Rect x={0} y={120} width={560} height={14} fill={D.panel}/>
      <Rect ref={fillProgress} x={-280} y={120} offset={[-1, 0]} width={0} height={14} fill={D.green}/>
      <Txt ref={note} y={230} text={'조건을 달성하면 칸이 열립니다'} fontFamily={D.font} fontSize={36} fill={D.muted}/>
    </Node>
    <Rect y={430} x={12} width={1680} height={146} fill={'#073c32'}/>
    <Rect y={430} width={1680} height={146} fill={'#ffffff'} stroke={'#161b18'} lineWidth={3}/>
    <Txt ref={caption} y={430} text={'가운데 칸의 조건은\n첫 코스를 완주하는 것입니다.'}
      fontFamily={'Noto Sans KR, Malgun Gothic, sans-serif'} fontSize={48} lineHeight={62} fontWeight={500} fill={'#080b09'}/>
  </>);
  yield* waitFor(4);
  // Change only the relevant condition; pending cells stay unchanged.
  caption().text('완주하면 그 칸이 완료 상태로 바뀌고\n보상을 얻습니다.');
  progress().text('첫 코스 완주!');
  yield* fillProgress().width(560, 1, easeInOutCubic);
  yield* all(current().stroke(D.green, .5), currentLabel().fill(D.green, .5));
  currentLabel().text('완료'); complete(1); state().text('조건 달성');
  note().text('획득 보상: 새 음악');
  yield* waitFor(3);
  caption().text('이어 옆 칸에 코인을 세 개 모으라는\n힌트가 나타납니다.');
  yield* path().end(1, 1.2, easeInOutCubic);
  yield* all(next().stroke(D.teal, .5), nextLabel().fill(D.teal, .5));
  nextLabel().text('코인 3개'); nextLabel().fontSize(36);
  state().text('새로 보이는 목표'); state().fill(D.teal);
  condition().text('코인 세 개 모으기'); progress().text('현재 0 / 3개');
  note().text('힌트 공개 ≠ 조건 완료');
  fillProgress().width(0);
  yield* waitFor(4);
  caption().text('모든 정답을 한꺼번에 알려 주지 않아도,\n지금 시도할 일을 발견할 수 있죠.');
  yield* all(path().opacity(0, .5), current().lineWidth(3, .5), next().lineWidth(8, .5));
  yield* waitFor(4);
  caption().text('코인 하나를 얻으면 세 개 중 하나.\n진행과 완료는 서로 다른 상태입니다.');
  progress().text('현재 1 / 3개');
  yield* fillProgress().width(560 / 3, 1, easeInOutCubic);
  note().text('아직 미완료 · 보상은 지급하지 않음');
  yield* waitFor(4);
});
