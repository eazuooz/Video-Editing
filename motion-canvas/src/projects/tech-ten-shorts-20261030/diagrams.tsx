import {Circle, Line, Node, Rect, Txt} from '@motion-canvas/2d';
import {DARK} from '../../styles/research-dark';
import {clamp, COMMANDS, Point, replayState, Section, smooth, walkableCell} from './model';

const C = DARK, FONT = 'Malgun Gothic';
export type DiagramClock = {section: () => Section; phase: () => number; elapsed: () => number; event: (name: string, defaults: [number, number]) => number};
const label = (text: string, position: Point, color: string = C.ink, size = 30) =>
  <Txt text={text} position={position} fill={color} fontFamily={FONT} fontSize={size} fontWeight={700}/>;

/** The cell-size change is real code. The bridge image and sampling domain stay fixed. */
export function gridDiagram(parent: Node, clock: DiagramClock) {
  const stage = () => clock.section().unityStage ?? 0;
  // Baseline/diagonal chapters stay coarse; only the explicitly bound change
  // chapter switches cell size. No autonomous reveal can alter the lesson.
  const fine = () => stage() === 2 || (stage() === 3 && clock.event('fine-grid', [.48, .75]) > .5);
  const reveal = () => stage() >= 1 ? 1 : clock.event('grid-reveal', [.20, .56]);
  parent.add(label('그림은 비스듬해도, 판정은 네모 격자', [0, -385], C.title, 37));
  const world = new Node({position: [0, -30]}); parent.add(world);
  world.add(<Rect size={592} fill="#111e21" stroke={C.line} lineWidth={2}/>);
  world.add(<Line points={[[-296, -177.6], [-177.6, -296], [296, 177.6], [177.6, 296]]}
    closed fill="#776c4c" stroke="#c7b887" lineWidth={6}/>);
  for (let cells of [4, 16]) {
    const grid = new Node({opacity: () => reveal() * ((cells === 16) === fine() ? 1 : 0)}); world.add(grid);
    const size = 592 / cells;
    for (let y = 0; y < cells; y++) for (let x = 0; x < cells; x++) {
      const open = walkableCell(x, y, cells);
      grid.add(<Rect position={[-296 + (x + .5) * size, -296 + (y + .5) * size]} size={size - 1}
        fill={open ? '#315c50' : '#301f24'} opacity={.82} stroke={open ? C.green : C.red} lineWidth={cells === 4 ? 3 : 1.5}/>);
    }
  }
  world.add(<Rect position={[-74, -74]} size={148} fill="#00000000"
    stroke={C.title} lineWidth={5} opacity={() => fine() ? 1 : 0}/>);
  world.add(<Line points={[[-239, -239], [-93, -93], [55, 55], [239, 239]]}
    stroke={C.title} lineWidth={7} endArrow arrowSize={17} end={() => clock.event('path-trace', [.15, .70])}/>);
  world.add(<Circle size={35} position={() => {const p = clock.event('path-trace', [.15, .70]); return [-239 + 478 * p, -239 + 478 * p];}}
    fill={C.title} stroke="#000000" lineWidth={4}/>);
  parent.add(<Txt text={() => fine() ? '기존 1칸: 32 ÷ 8 = 4  →  4 × 4 = 16칸' : '길찾기 한 칸 32 × 32픽셀'}
    position={[0, 338]} fill={fine() ? C.teal : C.ink} fontFamily={FONT} fontSize={34} fontWeight={700}/>);
  parent.add(label('초록: 통행 가능   붉은색: 통행 불가', [0, -350], C.muted, 27));
}

/** High-level supported player-data read; no arbitrary-address exploit demonstration. */
export function eudDiagram(parent: Node, clock: DiagramClock) {
  const stage = () => clock.section().unityStage ?? 0;
  const trigger = () => stage() === -1;
  const translated = () => stage() >= 1 || trigger();
  const travel = () => clock.event('request-travel', [.12, .75]);
  const otherRead = () => trigger() && clock.event('read-other-data', [.38, .72]) > .1;
  const arrived = () => translated() && (trigger() ? otherRead() : clock.event('value-return', [.72, .94]) > .05);
  parent.add(<Txt text={() => trigger() ? '조건이 맞으면, 동작을 실행' : '옛 요청을, 새 게임이 이해하게'}
    position={[0, -368]} fill={C.title} fontFamily={FONT} fontSize={38} fontWeight={700}/>);
  const nodes: {x: number; title: string; sub: string; role: string}[] = [
    {x: -340, title: '옛 유즈맵', sub: '이름을 읽어 줘', role: C.ink},
    {x: 0, title: '호환 계층', sub: '지원하는 요청 처리', role: C.teal},
    {x: 340, title: '새 게임', sub: '현재 이름 데이터', role: C.green},
  ];
  for (let i = 0; i < nodes.length; i++) {
    const item = nodes[i];
    parent.add(<Rect position={[item.x, -155]} size={[260, 170]} radius={12}
      fill={C.panel} stroke={item.role} lineWidth={4} opacity={() => i === 1 && !translated() ? .2 : 1}>
      <Txt text={() => trigger() ? ['유저맵', '읽기 기능', otherRead() ? '다른 데이터' : '사망 횟수'][i] : item.title} position={[0, -28]} fill={item.role} fontFamily={FONT} fontSize={35} fontWeight={700}/>
      <Txt text={() => trigger() ? ['조건 → 트리거', '사망 횟수 읽기', otherRead() ? '의도 밖의 활용' : '원래 읽는 값'][i] : item.sub} position={[0, 37]} fill={C.muted} fontFamily={FONT} fontSize={25}/>
    </Rect>);
  }
  for (let x of [-170, 170]) parent.add(<Line points={[[x - 34, -155], [x + 34, -155]]}
    stroke={() => translated() ? C.teal : C.red} lineWidth={6} endArrow arrowSize={14}/>);
  parent.add(<Rect size={[58, 20]} radius={5} position={() => [-340 + (translated() ? 680 : 166) * travel(), -155]}
    fill={C.title} stroke={C.background} lineWidth={3}/>);
  const block = new Node({opacity: () => translated() ? 0 : 1, position: [-170, -155]}); parent.add(block);
  block.add(<Line points={[[-16, -22], [16, 22]]} stroke={C.red} lineWidth={8}/>);
  block.add(<Line points={[[16, -22], [-16, 22]]} stroke={C.red} lineWidth={8}/>);
  parent.add(<Txt text={() => trigger() ? otherRead() ? '사망 횟수 기능으로, 다른 정보까지 읽음' : '조건을 확인하고 정해진 동작 실행' : translated() ? '지원하는 이름 읽기 요청을 처리' : '구버전의 요청이 바로 통하지 않음'}
    position={[0, -11]} fill={() => translated() ? C.teal : C.red} fontFamily={FONT} fontSize={32} fontWeight={700}/>);
  parent.add(<Rect position={[0, 166]} size={[814, 188]} fill="#0e1916" stroke={C.line} lineWidth={2}/>);
  parent.add(<Txt text={() => trigger() ? otherRead() ? '게임 데이터 → 읽은 값' : '조건 → 트리거 → 동작' : '플레이어 이름'}
    position={[0, 116]} fill={C.muted} fontFamily={FONT} fontSize={30}/>);
  parent.add(<Txt text={() => trigger() ? otherRead() ? '기능의 쓰임이 확장됨' : '원래 정해 둔 기능' : arrived() ? 'YAMYAM' : '?'}
    position={[0, 192]} fill={() => arrived() ? C.green : C.muted} fontFamily={FONT} fontSize={45} fontWeight={700}/>);
  parent.add(<Txt text={() => trigger() ? '' : arrived() ? '새 데이터에서 이름 값을 찾아 반환' : '요청한 이름 값 · 응답 대기'} position={[0, 303]}
    fill={() => arrived() ? C.green : C.muted} fontFamily={FONT} fontSize={31} fontWeight={700}/>);
  parent.add(<Txt text={() => trigger() ? 'EUD · Extended Unit Death' : stage() === 2 ? '패치 1.21.0 · 일부 옛 EUD 맵 호환' : 'YAMYAM은 설명용 이름 예시'}
    position={[0, 343]} fill={C.muted} fontFamily={FONT} fontSize={26}/>);
}

/** Two actual deterministic state machines receive the identical tick-indexed commands. */
export function replayDiagram(parent: Node, clock: DiagramClock) {
  const tick = () => {
    if (clock.section().id === 'replay') {
      const move = clock.event('move-command', [.12, .45]), attack = clock.event('attack-command', [.45, .70]);
      return attack > 0 ? 240 + Math.floor(90 * attack) : move > 0 ? 120 + Math.floor(119 * move) : 0;
    }
    return Math.floor(clock.event('replay-run', [.10, .88]) * 330);
  };
  const mismatch = () => (clock.section().unityStage ?? 0) >= 2
    && clock.event('restore-rules', [.90, .99]) <= .1;
  parent.add(label('화면 대신, 입력을 다시 실행', [0, -375], C.title, 39));
  const positions: Point[] = [[-250, -103], [250, -103]];
  for (let i = 0; i < 2; i++) {
    const [ox, oy] = positions[i];
    parent.add(label(i ? '리플레이' : '처음 플레이', [ox, -284], i ? C.teal : C.ink, 32));
    parent.add(<Rect position={[ox, oy]} size={[440, 300]} fill="#101c17" stroke={i ? C.teal : C.ink} lineWidth={3}/>);
    for (let x = 0; x < 8; x++) parent.add(<Line points={[[ox - 190 + x * 54, oy - 124], [ox - 190 + x * 54, oy + 124]]} stroke="#283c32" lineWidth={1}/>);
    for (let y = 0; y < 6; y++) parent.add(<Line points={[[ox - 190, oy - 124 + y * 48], [ox + 190, oy - 124 + y * 48]]} stroke="#283c32" lineWidth={1}/>);
    const state = () => replayState(tick(), i && mismatch() ? 50 : 30, 7);
    parent.add(<Circle size={34} position={() => {const p = state().position; return [ox - 190 + p[0] * 54, oy - 124 + p[1] * 48];}}
      fill={i ? C.teal : C.title} stroke={C.ink} lineWidth={3}/>);
    parent.add(<Rect size={[35, 46]} position={[ox - 190 + 6 * 54, oy - 124 + 2 * 48]} fill={C.red} stroke={C.ink} lineWidth={2}/>);
    parent.add(<Line points={() => {const p = state().position; return [[ox - 190 + p[0] * 54, oy - 124 + p[1] * 48], [ox - 190 + 6 * 54, oy - 124 + 2 * 48]];}}
      stroke={C.title} lineWidth={6} opacity={() => state().attacking ? 1 : 0}/>);
    parent.add(<Txt text={() => `표적 체력 ${state().health}`} position={[ox, 87]} fill={() => i && mismatch() ? C.red : C.green}
      fontFamily={FONT} fontSize={27} fontWeight={700}/>);
  }
  parent.add(label('입력 기록', [-370, 135], C.title, 30));
  parent.add(<Txt text={() => `예시 시간 ${(tick() / 60).toFixed(1)}초`} position={[272, 135]}
    fill={C.muted} fontFamily={FONT} fontSize={26}/>);
  for (let i = 1; i < COMMANDS.length; i++) {
    const c = COMMANDS[i]; const y = 128 + i * 58;
    parent.add(<Txt text={`${c.tick / 60}초  ·  ${c.label} → ${c.kind === 'attack' ? '같은 표적' : '(' + c.target.join(', ') + ')'}`} position={[-118, y]}
      fill={() => tick() >= c.tick ? C.teal : C.muted} fontFamily={FONT} fontSize={29} fontWeight={700}/>);
    parent.add(<Line points={[[215, y], [382, y]]} stroke={C.teal} lineWidth={5} endArrow arrowSize={12}
      opacity={() => tick() >= c.tick ? 1 : .15}/>);
  }
  parent.add(<Txt text={() => mismatch() ? '규칙이 달라지면, 결과도 달라짐' : '같은 시작 · 같은 입력 · 같은 규칙'}
    position={[0, 300]} fill={() => mismatch() ? C.red : C.green} fontFamily={FONT} fontSize={32} fontWeight={700}/>);
  parent.add(<Txt text={() => mismatch() ? '같은 맵 · 다른 규칙 · 같은 시드 7  |  자체 모형' : '같은 맵 · 같은 버전 · 같은 시드 7  |  자체 모형'}
    position={[0, 335]} fill={C.muted} fontFamily={FONT} fontSize={23} fontWeight={700}/>);
}
