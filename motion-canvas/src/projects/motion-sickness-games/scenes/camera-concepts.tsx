import {Circle, Line, Node, Rect, Txt, View2D} from '@motion-canvas/2d';
import {all, createRef, easeInOutCubic, waitFor} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';

const headings = [
  ['다른 정보를 받는 눈과 몸', '일반적인 설명 이론 · 개인의 증상을 진단하는 도식은 아닙니다'],
  ['카메라 움직임을 역할로 나누기', '주변을 보기 · 도구를 조준하기 · 추가 연출'],
  ['한 번에 한 가지를 바꾸는 옵션', '설계 제안 · 실제 게임의 설정 화면이 아닙니다'],
  ['방향이 바뀌어도 현재 위치를 읽게', '설명용 비교 · 게임 규칙에 맞춰 선택을 설계합니다'],
  ['차이를 알고, 원래 값으로 돌아오기', '설계 제안 · 알아보기 → 확인하기 → 되돌리기'],
  ['효과보다 먼저 선택과 역할을 설계', '실제 행동과 연결해서 네 가지 질문을 확인하세요'],
];
const summaries = [
  '반응은 사람마다 다릅니다. 하나의 편안한 값을 약속하지 않습니다.',
  '필요한 시점 이동과 추가 연출은 서로 다른 역할입니다.',
  '값의 크기와 조작의 연결 방식을 구분해서 설명하세요.',
  '전환 뒤에도 목표와 현재 방향을 알아볼 수 있어야 합니다.',
  '옵션을 찾고, 차이를 확인하고, 부담 없이 되돌릴 수 있게.',
  '필요한 행동은 보존하고, 플레이어가 알아볼 수 있는 선택을 더하세요.',
];
function text(value: string, x: number, y: number, size = 29, color: string = P.ink, weight = 500) {
  return <Txt text={value} x={x} y={y} fontFamily={P.font} fontSize={size} fill={color} fontWeight={weight} textAlign={'center'}/>;
}
function card(x: number, y: number, width: number, height: number, title: string, detail: string, color: string = P.blue,
  positions?: {titleY?: number; detailY?: number}) {
  return <Node x={x} y={y}>
    <Rect x={13} y={16} width={width} height={height} rotation={-1} fill={'#dce3e6'}/>
    <Rect width={width} height={height} rotation={-1} fill={'white'} stroke={color} lineWidth={2}/>
    <Rect x={-width / 2 + 12} width={7} height={height - 28} fill={color}/>
    {text(title, 0, positions?.titleY ?? -height * .25, 31, color, 700)}
    {text(detail, 0, positions?.detailY ?? height * .22, 26, P.muted)}
  </Node>;
}
function arrow(points: [number, number][], color: string = P.blue, ref?: ReturnType<typeof createRef<Line>>) {
  return <Line ref={ref} points={points} stroke={color} lineWidth={5} endArrow arrowSize={16} end={ref ? 0 : 1}/>;
}

// Four narration paragraphs drive four stages. Eight-second lookdev uses
// proportional timing only; the production wrapper requires measured timings.
export function* cameraConcept(view: View2D, index: number, duration: number, paragraphEnds?: number[]) {
  if (index < 0 || index > 5 || duration < 7) throw new Error('Valid camera explanation and duration required');
  const boundaries = paragraphEnds ?? [duration * .25, duration * .5, duration * .75, duration];
  if (boundaries.length !== 4 || Math.abs(boundaries[3] - duration) > 1 / 60 || boundaries.some((n, i) => n <= (boundaries[i - 1] ?? 0))) {
    throw new Error('Four increasing measured paragraph ends required');
  }
  const stage = createRef<Node>(), focus = createRef<Node>(), summary = createRef<Node>();
  const a = createRef<Node>(), b = createRef<Node>(), c = createRef<Node>();
  const rays = [createRef<Line>(), createRef<Line>(), createRef<Line>()];
  const indicator = createRef<Rect>();
  view.fill(P.background);
  view.add(<>
    <Txt text={`${index + 1} / 6  ·  카메라와 플레이어의 선택`} x={-850} y={-470} offset={[-1, 0]} fontFamily={P.font} fontSize={25} fill={P.muted}/>
    <Txt text={headings[index][0]} x={-850} y={-391} offset={[-1, 0]} fontFamily={P.font} fontSize={50} fontWeight={700} fill={P.ink}/>
    <Txt text={headings[index][1]} x={-850} y={-315} offset={[-1, 0]} fontFamily={P.font} fontSize={28} fill={P.muted}/>
    <Node ref={stage} opacity={0} y={20}/>
    <Node ref={focus} opacity={0}/>
    <Node ref={summary} y={292} opacity={0}>
      <Rect x={11} y={12} width={1650} height={76} fill={'#dae6df'}/>
      <Rect width={1650} height={76} fill={'white'} stroke={P.green} lineWidth={2}/>
      {text(summaries[index], 0, 0, 29, P.ink, 600)}
    </Node>
  </>);
  if (index === 0) {
    stage().add(<>
      <Node ref={a}>{card(-570, -84, 448, 270, '눈이 보는 움직임', '화면의 방향 · 주변 풍경', P.blue, {detailY:112})}
        <Circle x={-570} y={-98} width={100} height={54} stroke={P.blue} lineWidth={3}/><Circle x={-570} y={-98} size={25} fill={P.blue}/>
      </Node>
      <Node ref={b}>{card(0, -84, 448, 270, '몸이 느끼는 움직임', '자세 · 움직임의 신호', P.green, {detailY:112})}
        <Circle y={-105} size={38} fill={P.green}/><Line points={[[0, -86], [0, -41], [-28, -20], [0, -41], [28, -20]]} stroke={P.green} lineWidth={7}/>
      </Node>
      <Node ref={c}>{card(570, -84, 448, 270, '기대하는 움직임', '이전 경험으로 예상', '#aa7b28', {detailY:112})}{text('?', 570, -100, 64, '#aa7b28', 700)}</Node>
      {arrow([[-570, 73], [-570, 137], [-170, 137]], P.blue, rays[0])}
      {arrow([[0, 73], [0, 110]], P.green, rays[1])}
      {arrow([[570, 73], [570, 137], [170, 137]], '#aa7b28', rays[2])}
      {text('정보 사이의 불일치', 0, 172, 35, P.ink, 700)}
    </>);
    focus().add(text('개인의 반응을 한 가지 값으로 판단할 수 없습니다.', 0, 230, 28, P.red));
  } else if (index === 1) {
    stage().add(<>
      <Node ref={a}>{card(-570, -73, 448, 300, '시점 회전', '다른 방향을 바라보기', P.blue, {detailY:109})}
        <Rect x={-570} y={-80} width={122} height={75} stroke={P.blue} lineWidth={3} skewY={-8}/>
        {arrow([[-620, -18], [-523, -18]], P.blue)}
      </Node>
      <Node ref={b}>{card(0, -73, 448, 300, '도구의 조준', '목표 표면을 따라가기', P.green, {detailY:109})}
        <Circle y={-76} size={77} stroke={P.green} lineWidth={3}/>
        <Line points={[[-61, -76], [61, -76]]} stroke={P.green} lineWidth={3}/><Line points={[[0, -120], [0, -31]]} stroke={P.green} lineWidth={3}/>
      </Node>
      <Node ref={c}>{card(570, -73, 448, 300, '추가 연출', '걷기 흔들림 · 충격 강조', '#aa7b28', {detailY:109})}
        <Line points={[[507, -75], [529, -99], [550, -52], [574, -99], [596, -52], [630, -75]]} stroke={'#aa7b28'} lineWidth={5}/>
      </Node>
      {arrow([[-570, 116], [-570, 183], [-100, 183]], P.blue, rays[0])}
      {arrow([[570, 116], [570, 183], [100, 183]], '#aa7b28', rays[1])}
      {text('역할에 맞게 따로 조절', 0, 213, 34, P.ink, 700)}
    </>);
    focus().add(<Rect x={570} y={-73} width={470} height={322} stroke={P.green} lineWidth={4}/>);
  } else if (index === 2) {
    stage().add(<>
      <Node ref={a}>{card(-440, -13, 710, 392, '설계 제안', '세 값은 서로 같은 뜻이 아닙니다', P.blue, {titleY:-152, detailY:153})}
        {text('시점 감도', -610, -91, 28)}{text('조준 연결', -610, -14, 28)}{text('추가 흔들림', -610, 63, 28)}
        <Line points={[[-450, -91], [-210, -91]]} stroke={P.line} lineWidth={7}/><Circle x={-313} y={-91} size={22} fill={P.blue}/>
        <Rect x={-330} y={-14} width={250} height={44} fill={P.blueLight}/>{text('독립 조준', -330, -14, 25, P.blue, 700)}
        <Line points={[[-450, 63], [-210, 63]]} stroke={P.line} lineWidth={7}/><Circle x={-424} y={63} size={22} fill={P.green}/>
      </Node>
      <Node ref={b}>{card(440, -94, 700, 177, '감도', '같은 입력에 얼마나 회전하는가', P.blue)}</Node>
      <Node ref={c}>{card(440, 120, 700, 177, '연결 방식', '시점과 조준이 함께 움직이는가', P.green)}</Node>
      {arrow([[-55, -90], [60, -90]], P.blue, rays[0])}{arrow([[-55, -14], [12, -14], [12, 121], [60, 121]], P.green, rays[1])}
    </>);
    focus().add(<Rect ref={indicator} x={-440} y={-91} width={678} height={63} stroke={P.green} lineWidth={4}/>);
  } else if (index === 3) {
    const landmark = (x: number, color: string) => <Node x={x}>
      <Rect y={53} width={570} height={68} skewX={-22} fill={'#e4ebe6'}/>
      <Rect x={-155} y={-32} width={65} height={140} skewY={-8} fill={P.blueLight} stroke={color} lineWidth={2}/>
      <Circle x={137} y={-16} size={57} fill={P.yellow} stroke={color} lineWidth={2}/>
      {text('목표', 137, 50, 24, color)}
    </Node>;
    stage().add(<>
      {card(-430, -30, 700, 366, '연속 회전', '', P.blue)}{card(430, -30, 700, 366, '순간 방향 전환', '', P.green)}
      <Node ref={a} x={-430} y={20}>{landmark(0, P.blue)}</Node>
      <Node ref={b} x={430} y={20}>{landmark(0, P.green)}</Node>
      {arrow([[-155, 173], [155, 173]], P.line, rays[0])}
      {text('설명용 비교', 0, 223, 28, P.muted, 600)}
    </>);
    focus().add(<>{text('전환 뒤: 목표는 어디에?', -430, 186, 27, P.blue, 600)}{text('현재 방향은 어디인가?', 430, 186, 27, P.green, 600)}</>);
  } else if (index === 4) {
    stage().add(<>
      <Node ref={a}>{card(-570, -111, 447, 205, '찾을 수 있는 곳', '일관된 메뉴 · 입력 접근', P.blue)}</Node>
      <Node ref={b}>{card(0, -111, 447, 205, '차이를 알려 주기', '짧은 설명 · 바뀌는 역할', '#aa7b28')}</Node>
      <Node ref={c}>{card(570, -111, 447, 205, '되돌릴 수 있게', '기존 값 · 초기화', P.green)}</Node>
      {arrow([[-325, -111], [-245, -111]], P.blue, rays[0])}{arrow([[245, -111], [325, -111]], P.green, rays[1])}
      {card(-412, 153, 716, 145, '작업 확인', '목표와 현재 방향이 읽히는가?', P.blue)}
      {card(412, 153, 716, 145, '사람의 선택', '계속하기 · 바꾸기 · 멈추기', P.green)}
    </>);
    focus().add(text('설정 값의 저장과 되돌리기도 함께 점검', 0, 27, 29, P.green, 600));
  } else {
    stage().add(<>
      <Node ref={a}>{card(-430, -126, 735, 184, '01  무엇이 움직였는가', '시점 · 조준 · 추가 연출', P.blue)}{card(430, -126, 735, 184, '02  작업이 이어지는가', '목표 · 현재 방향 · 필요한 입력', P.green)}</Node>
      <Node ref={b}>{card(-430, 104, 735, 172, '03  선택을 이해하는가', '짧은 의미 · 원래 값으로 복귀', '#aa7b28')}{card(430, 104, 735, 172, '04  반응을 들었는가', '실제 플레이 · 개인의 차이', P.blue)}</Node>
      <Node ref={c}/>{arrow([[-430, -19], [-430, 17]], P.blue, rays[0])}{arrow([[430, -19], [430, 17]], P.green, rays[1])}
    </>);
    focus().add(text('함께 구현하기  ·  설명과 마지막 화면의 프로그래밍 과외 링크', 0, 232, 26, P.green, 600));
  }
  let elapsed = 0;
  const reveal = .55;
  yield* all(stage().opacity(1, reveal), stage().y(0, reveal, easeInOutCubic)); elapsed += reveal;
  yield* waitFor(Math.max(0, boundaries[0] - elapsed)); elapsed = boundaries[0];
  const change = .6;
  if (index === 0) yield* all(...rays.map(r => r().end(1, change)));
  else if (index === 1) yield* all(a().x(16, change), b().x(27, change), c().y(17, change));
  else if (index === 3) yield* all(a().rotation(8, change, easeInOutCubic), b().rotation(8, 0), rays[0]().end(1, change));
  else yield* all(rays[0]().end(1, change), rays[1]().end(1, change));
  elapsed += change;
  yield* waitFor(Math.max(0, boundaries[1] - elapsed)); elapsed = boundaries[1];
  yield* all(focus().opacity(1, .45), index === 2 ? indicator().y(-14, .45) : a().scale(1.025, .45)); elapsed += .45;
  yield* waitFor(Math.max(0, boundaries[2] - elapsed)); elapsed = boundaries[2];
  yield* summary().opacity(1, .45); elapsed += .45;
  yield* waitFor(Math.max(0, duration - elapsed));
}
