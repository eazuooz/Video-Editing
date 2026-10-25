import {Circle, Img, Line, Node, Rect, Txt, type View2D} from '@motion-canvas/2d';
import {createSignal, linear} from '@motion-canvas/core';
import {DARK as D} from '../../../styles/research-dark';

export type LessonKind = 'overview' | 'complete' | 'choice' | 'purpose' | 'role' | 'effort' | 'effortExamples' | 'cooperation' | 'appeals' | 'conclusion';
export interface Timing {
  duration: number;
  /** Starts of the relevant narration/teaching steps, relative to this cut; negatives are valid. */
  cues?: number[];
  /** Steps already revealed before this cut: keep opacity/path reveal visible without changing mechanic motion or the speech clock. */
  initialVisible?: number[];
  title?: string;
  exampleSummary?: string;
  /** Independently inspected 16:9 screenshot paths: drgs/mining, mm2/creator, social/versus/mm2vs. */
  imagePaths?: Record<string, string>;
  preflight?: boolean;
}
type Point = [number, number];
type SymbolKind = 'control' | 'rules' | 'result' | 'finish' | 'pickaxe' | 'pencil' | 'route' | 'switch' | 'detail';
const clamp = (v: number) => Math.max(0, Math.min(1, v));
const smooth = (v: number) => {const x = clamp(v); return x * x * (3 - 2 * x);};
/** A route illustration, without invented game speed or distance readouts. */
function along(points: Point[], progress: number): Point {
  const lengths = points.slice(1).map((p, i) => Math.hypot(p[0] - points[i][0], p[1] - points[i][1]));
  let remaining = clamp(progress) * lengths.reduce((a, b) => a + b, 0);
  for (let i = 0; i < lengths.length; i++) {
    if (remaining <= lengths[i] || i === lengths.length - 1) {
      const u = lengths[i] > 0 ? clamp(remaining / lengths[i]) : 1;
      return [points[i][0] + (points[i + 1][0] - points[i][0]) * u,
        points[i][1] + (points[i + 1][1] - points[i][1]) * u];
    }
    remaining -= lengths[i];
  }
  return points[points.length - 1];
}
const TITLES: Record<LessonKind, string> = {
  overview: '익숙한 구조에, 고를 이유를 더합니다',
  complete: '입력부터 끝까지, 한 작품으로 완성하기',
  choice: '같은 출발점에서, 다른 선택을 만들기',
  purpose: '살아남는 움직임에, 채굴 목표를 더하면',
  role: '플레이하던 사람이, 길을 설계한다면',
  effort: '익숙한 구조 위에, 새 경험을 다듬기',
  effortExamples: '세 가지 경험에 공들이기',
  cooperation: '상대의 움직임이, 내 선택을 바꿉니다',
  appeals: '고를 이유는, 여러 방향으로 생깁니다',
  conclusion: '내 게임을 선택할 이유를 남기기',
};
const ALIASES: Record<string, LessonKind> = {
  introduction: 'overview', completion: 'complete', differentiation: 'choice',
  mining: 'purpose', creator: 'role', polish: 'effort', coop: 'cooperation', competition: 'cooperation', versus: 'cooperation',
  appeal: 'appeals', recap: 'conclusion',
};
const STEPS: Record<LessonKind, number> = {overview: 3, complete: 4, choice: 4, purpose: 4, role: 4, effort: 4, effortExamples: 4, cooperation: 4, appeals: 4, conclusion: 3};

const text = (value: string, x: number, y: number, size = 56, color: string = D.ink, width = 1700) =>
  <Txt text={value} x={x} y={y} width={width} textAlign={'center'} textWrap
    fontSize={size} lineHeight={size * 1.2} fill={color} fontWeight={600} fontFamily={D.font}/>;

/** Independent pictograms describe abstract roles; they are not reconstructed game output. */
function symbol(kind: SymbolKind, x: number, y: number, color: string = D.teal, scale = 1) {
  const lines = (points: Point[], width = 6) => <Line points={points} stroke={color} lineWidth={width} lineCap={'round'} lineJoin={'round'}/>;
  let figure: any;
  switch (kind) {
    case 'control': figure = <>
      <Rect width={156} height={88} radius={25} stroke={color} lineWidth={6}/>
      {lines([[-60, 0], [-20, 0]])}{lines([[-40, -20], [-40, 20]])}
      <Circle x={43} y={-12} size={14} fill={color}/><Circle x={65} y={13} size={14} fill={color}/>
    </>; break;
    case 'rules': figure = <>
      <Rect width={130} height={145} radius={8} stroke={color} lineWidth={6}/>
      {[-40, 0, 40].map(v => <Node>{lines([[-46, v], [-36, v + 11], [-17, v - 12]], 5)}{lines([[0, v], [45, v]], 5)}</Node>)}
    </>; break;
    case 'result': figure = <>
      <Circle size={132} stroke={color} lineWidth={6}/>
      {lines([[-39, 1], [-10, 30], [45, -35]], 11)}
    </>; break;
    case 'finish': figure = <>
      {lines([[-53, 66], [-53, -66]], 7)}
      <Line points={[[-50, -64], [66, -34], [-50, -4]]} closed fill={D.surfaceFront} stroke={color} lineWidth={6}/>
      {lines([[-72, 70], [-10, 70]], 7)}
    </>; break;
    case 'pickaxe': figure = <>
      {lines([[-48, 63], [35, -42]], 17)}
      {lines([[-58, -33], [-24, -62], [25, -61], [65, -29]], 13)}
      {lines([[-62, -29], [-66, -12]], 8)}
    </>; break;
    case 'pencil': figure = <>
      <Line points={[[-52, 57], [-40, 10], [37, -67], [67, -37], [-10, 40]]} closed stroke={color} lineWidth={6}/>
      {lines([[-40, 10], [-10, 40]], 5)}{lines([[23, -53], [53, -23]], 5)}
      <Line points={[[-52, 57], [-45, 35], [-30, 50]]} closed fill={color}/>
    </>; break;
    case 'route': figure = <>
      <Line points={[[-72, 49], [-18, 49], [-18, -43], [68, -43]]} stroke={color} lineWidth={9} endArrow arrowSize={22} lineJoin={'round'}/>
      <Circle x={-72} y={49} size={26} fill={D.background} stroke={color} lineWidth={5}/>
    </>; break;
    case 'switch': figure = <>
      <Rect y={42} width={152} height={38} radius={6} stroke={color} lineWidth={6}/>
      <Rect y={13} width={86} height={29} radius={5} stroke={color} lineWidth={6}/>
      <Circle y={-20} width={83} height={35} stroke={color} lineWidth={6}/>
    </>; break;
    default: figure = <>
      <Circle x={-12} y={-13} size={99} stroke={color} lineWidth={7}/>
      {lines([[27, 26], [69, 68]], 14)}
      {lines([[-40, -13], [-20, 6], [14, -30]], 7)}
    </>;
  }
  return <Node x={x} y={y} scale={scale}>{figure}</Node>;
}

function imageUrl(raw: string) {
  const p = raw.split(String.fromCharCode(92)).join('/');
  if (/^https?:\/\//i.test(p)) throw Error('Supply an inspected local screenshot, not a remote webpage image');
  return p.startsWith('/') || p.startsWith('data:image/') ? p
    : '/@fs/' + (/^[A-Za-z]:\//.test(p) ? p : 'D:/Github/VideoEditing/' + p);
}

/**
 * Abstract relationships only. Actual game stills, when supplied, remain
 * explanation imagery and keep their16:9 aspect. No game measurements, fake
 * engine buffers, source credits or copyrighted characters are invented.
 * All content ends at y<=320; captions stay at (0,430), unchanged.
 */
export function* lesson(view: View2D, requested: string, timing: Timing) {
  const resolved = (ALIASES[requested] ?? requested) as LessonKind;
  if (!(resolved in TITLES)) throw Error(`Unknown D22 relationship lesson: ${requested}`);
  if (!(timing.duration > 0) || !Number.isFinite(timing.duration)) throw Error('A measured positive duration is required');
  const kind = resolved, t = createSignal(0), duration = timing.duration;
  const motionScale = Math.min(1, duration / 8);
  if (timing.cues?.some((cue, i, cues) => !Number.isFinite(cue) || (i > 0 && cue < cues[i - 1]))) {
    throw Error('D22 cue starts must be finite and chronological; cut-relative negative starts are valid');
  }
  // Several diagram steps may belong to one spoken paragraph. If the caller
  // supplies fewer cue starts, share its last actual cue instead of inventing
  // another paragraph time. Full step-level starts may also be supplied.
  const at = (index: number) => timing.cues?.length
    ? timing.cues[Math.min(index, timing.cues.length - 1)]
    : duration * index / STEPS[kind];
  const reveal = (cue: number, delay = 0, length = .55) => () => timing.initialVisible?.includes(cue)
    ? 1 : smooth((t() - at(cue) - delay * motionScale) / (length * motionScale));
  const interval = (from: number, until?: number) => () => reveal(from)() * (until === undefined || t() < at(until) ? 1 : 0);
  const add = (cue: number, children: any, delay = 0) => view.add(<Node opacity={reveal(cue, delay)}>{children}</Node>);
  const during = (from: number, until: number | undefined, children: any) => view.add(<Node opacity={interval(from, until)}>{children}</Node>);
  const label = (value: string, x: number, y: number, cue = 0, color: string = D.ink, size = 56, width = 1700) => add(cue, text(value, x, y, size, color, width));
  const arrow = (points: Point[], cue: number, color: string = D.teal, delay = .15, parent: Node | View2D = view) =>
    parent.add(<Line points={points} stroke={color} lineWidth={9} endArrow arrowSize={23}
      end={reveal(cue, delay, .8)} lineCap={'round'} lineJoin={'round'}/>);
  const object = (icon: SymbolKind, value: string, x: number, y: number, cue: number, color: string = D.teal, subtitle?: string) => {
    add(cue, symbol(icon, x, y - 53, color));
    label(value, x, y + 69, cue, color, 58, 385);
    if (subtitle) label(subtitle, x, y + 130, cue, D.muted, 35, 380);
  };
  const paths = timing.imagePaths ?? {};
  const photo = (keys: string[], x: number, y: number, width: number, caption: string, color: string, fallback: SymbolKind) => {
    const raw = keys.map(key => paths[key]).find(Boolean);
    const height = width * 9 / 16;
    return <Node>
      {raw ? <>
        <Img src={imageUrl(raw)} x={x} y={y} width={width} height={height}/>
        <Rect x={x} y={y} width={width + 4} height={height + 4} stroke={D.line} lineWidth={2}/>
      </> : <>
        {symbol(fallback, x, y - 9, color, .9)}
        {text(timing.preflight ? '자료 화면 연결 전' : '관계 설명', x, y + 100, 31, D.muted, width)}
      </>}
      {text(keys.includes('drgs') ? '딥 록 갤럭틱 서바이버' : '슈퍼 마리오 메이커 2', x, y - height / 2 - 29, 30, D.muted, width + 16)}
      {text(caption, x, y + height / 2 + 32, 39, color, width + 16)}
    </Node>;
  };
  const examples = (staggered = false) => <>
    <Node opacity={staggered ? reveal(0) : 1}>{photo(['drgs', 'mining', 'purpose'], -585, -65, 510, '목표를 더하는 채굴', D.teal, 'pickaxe')}</Node>
    <Node opacity={staggered ? reveal(1) : 1}>{photo(['mm2', 'creator', 'role'], 0, -65, 510, '플레이에서 설계로', D.yellow, 'pencil')}</Node>
    <Node opacity={staggered ? reveal(2) : 1}>{photo(['social', 'versus', 'mm2vs'], 585, -65, 510, '같은 출발점에서 대결하기', D.green, 'route')}</Node>
  </>;

  view.fill(D.background);
  view.add(<>
    {text('얌얌코딩  /  게임 디자인', -615, -483, 28, D.muted, 610)}
    {text(timing.preflight ? '설명 시안 · 발화 동기화 전' : '설명용 관계도', 620, -483, 28, D.muted, 630)}
    {text(kind === 'effortExamples' ? TITLES[kind] : timing.title ?? TITLES[kind], 0, -393, 65, D.title, 1728)}
  </>);

  switch (kind) {
    case 'overview': {
      add(0, examples(true));
      label('알고 있는 행동', -470, 230, 1, D.ink, 58, 700);
      arrow([[-80, 230], [150, 230]], 1, D.teal, .25);
      label('새 작품을 고를 이유', 500, 230, 2, D.green, 58, 700);
      break;
    }
    case 'complete': {
      const start: Point = [-650, 35], blocked: Point = [-70, 35], goal: Point = [650, 35];
      const detour: Point[] = [start, [-270, 35], [-270, -130], [260, -130], [260, 35], goal];
      // The spoken middle clause contains both movement and retry. Its actual
      // interval drives one abstract state demonstration, not a game measurement.
      const u = () => clamp((t() - at(1)) / Math.max(.6, at(2) - at(1)));
      const retry = () => u() >= .28 && u() < .5;
      const detourProgress = () => smooth((u() - .5) / .5);
      const position = (): Point => u() < .28 ? along([start, blocked], smooth(u() / .28))
        : u() < .42 ? blocked : u() < .5 ? start : along(detour, detourProgress());
      const state = () => t() < at(1) ? '입력을 기다리는 시작점'
        : u() < .28 ? '입력에 반응해 이동'
          : u() < .42 ? '장애물에 막히면'
            : u() < .5 ? '시작점에서 재시도'
              : u() < 1 ? '장애물을 피해 이동' : '목표 도달 · 종료';
      const stage = () => t() < at(1) ? 0 : u() < .28 ? 1 : u() < .5 ? 2 : u() < 1 ? 1 : 3;
      ['입력 반응', '이동과 규칙', '실패 · 재시도', '목표 도달'].forEach((value, i) => {
        const x = -660 + i * 440;
        const color = i === 2 ? D.red : i === 3 ? D.green : D.teal;
        add(0, <>
          <Txt text={value} x={x} y={-255} width={390} textAlign={'center'} fontSize={48}
            fill={() => stage() === i ? color : D.muted} fontWeight={600} fontFamily={D.font}/>
          <Line points={[[x - 135, -213], [x + 135, -213]]} stroke={color}
            lineWidth={5} opacity={() => stage() === i ? 1 : 0}/>
        </>);
      });
      add(0, <>
        <Line points={[start, goal]} stroke={D.line} lineWidth={4} lineDash={[12, 12]}/>
        <Line points={detour} stroke={D.line} opacity={.25} lineWidth={5} lineJoin={'round'}/>
        <Circle position={start} size={100} stroke={D.line} lineWidth={4}/>
        <Rect x={0} y={35} width={72} height={176} stroke={D.ink} fill={D.surfaceFront} lineWidth={5}/>
        {[-35, 20, 75].map(y => <Line points={[[-30, y], [30, y + 30]]} stroke={D.line} lineWidth={3}/>)}
        <Circle position={goal} size={112} stroke={D.green} lineWidth={5}/>
        {symbol('finish', 650, 35, D.green, .45)}
      </>);
      add(1, <>
        <Line points={[start, blocked]} stroke={D.teal} lineWidth={8} endArrow arrowSize={19}
          end={() => smooth(u() / .28)} opacity={() => u() < .5 ? 1 : .2}/>
        <Line points={detour} stroke={D.green} lineWidth={8} endArrow arrowSize={20}
          lineJoin={'round'} end={detourProgress}/>
        <Node opacity={() => retry() ? 1 : 0}>
          <Line points={[[-92, 13], [-48, 57]]} stroke={D.red} lineWidth={8}/>
          <Line points={[[-92, 57], [-48, 13]]} stroke={D.red} lineWidth={8}/>
          <Line points={[blocked, [-200, 35], [-200, 226], [-830, 226], [-830, 35], start]} stroke={D.red}
            lineWidth={6} endArrow arrowSize={19} lineJoin={'round'}
            end={() => smooth((u() - .28) / .15)}/>
          {text('다시 시작', -420, 185, 36, D.red, 400)}
        </Node>
      </>);
      add(0, <Node position={position}>
        <Circle size={62} fill={D.background} stroke={D.teal} lineWidth={6}/>
        <Circle size={15} fill={D.ink}/>
        {text('조작 표식', 0, -62, 42, D.ink, 210)}
      </Node>);
      label('시작점', -650, 148, 0, D.muted, 48, 250);
      label('장애물', 0, 164, 1, D.ink, 48, 280);
      label('목표 지점', 650, 150, 0, D.green, 48, 320);
      add(0, <Txt text={state} x={0} y={285} width={1700} textAlign={'center'}
        fontSize={48} fill={() => retry() ? D.red : u() >= 1 ? D.green : D.ink}
        fontWeight={600} fontFamily={D.font}/>);
      break;
    }
    case 'choice': {
      object('control', '익숙한 행동', -560, -65, 0, D.ink, '장르에서 배운 출발점');
      object('route', '새로운 판단', 0, -65, 1, D.teal, '무엇을 다르게 할까');
      object('result', '고를 이유', 560, -65, 2, D.green, '플레이가 만드는 차이');
      arrow([[-335, -110], [-205, -110]], 1);
      arrow([[220, -110], [345, -110]], 2, D.green);
      label('새 행동과 결과를, 직접 경험하게 만듭니다', 0, 260, 3, D.yellow, 54);
      break;
    }
    case 'purpose': {
      during(0, undefined, photo(['drgs', 'mining', 'purpose'], -480, -65, 750, '채굴의 실제 게임 화면', D.teal, 'pickaxe'));
      const start: Point = [160, 110], ore: Point = [750, -110];
      const avoid: Point[] = [start, [310, 170], [570, 170], [790, 150]];
      const mine: Point[] = [start, [290, 25], [540, -145], ore];
      const changed = () => t() >= at(1);
      const avoidProgress = () => smooth((t() - at(0)) / Math.max(.6, at(1) - at(0)));
      const mineProgress = () => smooth((t() - at(1)) / Math.max(.6, at(2) - at(1)));
      const position = () => changed() ? along(mine, mineProgress()) : along(avoid, avoidProgress());
      label('같은 조건의 설명용 경로', 500, -282, 0, D.muted, 32, 720);
      add(0, <Txt text={() => changed() ? '목표: 광물에 접근하기' : '목표: 적을 피하기'}
        x={500} y={-225} width={720} textAlign={'center'} fontSize={50}
        fill={() => changed() ? D.teal : D.ink} fontWeight={600} fontFamily={D.font}/>);
      add(0, <>
        <Circle position={start} size={82} stroke={D.line} lineWidth={4}/>
        <Line points={avoid} stroke={D.line} lineWidth={4} lineDash={[10, 10]} lineJoin={'round'}/>
        <Line points={mine} stroke={D.line} opacity={.4} lineWidth={4} lineDash={[10, 10]} lineJoin={'round'}/>
        <Circle x={415} y={45} size={90} stroke={D.red} lineWidth={5}/>
        <Line points={[[402, 32], [428, 58]]} stroke={D.red} lineWidth={6}/>
        <Line points={[[402, 58], [428, 32]]} stroke={D.red} lineWidth={6}/>
        <Line points={[[750, -153], [789, -110], [750, -67], [711, -110]]} closed
          fill={D.surfaceFront} stroke={D.teal} lineWidth={6}/>
      </>);
      add(0, <Line points={avoid} stroke={D.ink} lineWidth={8} lineJoin={'round'} endArrow arrowSize={20}
        end={avoidProgress} opacity={() => changed() ? .25 : .9}/>);
      add(1, <Line points={mine} stroke={D.teal} lineWidth={8} lineJoin={'round'} endArrow arrowSize={20}
        end={mineProgress}/>);
      add(0, <Node position={position} opacity={() => changed() ? clamp((t() - at(1)) / .18) : 1}>
        <Circle size={58} fill={D.background} stroke={() => changed() ? D.teal : D.ink} lineWidth={6}/>
        <Circle size={15} fill={D.ink}/>
      </Node>);
      label('같은 출발점', 160, 225, 0, D.muted, 33, 300);
      label('피할 적', 415, 115, 0, D.red, 48, 250);
      label('광물', 750, -22, 1, D.teal, 48, 250);
      arrow([[780, -110], [870, -110], [870, 145], [790, 175]], 2, D.green);
      label('빠져나갈 틈', 755, 232, 2, D.green, 48, 360);
      label('목표를 바꾸면, 고르는 길도 달라집니다', 0, 290, 2, D.green, 45);
      break;
    }
    case 'role': {
      during(0, undefined, photo(['mm2', 'creator', 'role'], -430, -35, 820, '월드의 길과 코스를 배치하기', D.yellow, 'pencil'));
      add(0, symbol('control', 480, -190, D.ink, .75));
      label('길을 지나가기', 480, -95, 0, D.ink, 56, 610);
      arrow([[480, -42], [480, 48]], 1, D.yellow);
      add(2, symbol('pencil', 480, 110, D.yellow, .65));
      label('길을 설계하기', 480, 208, 2, D.yellow, 56, 610);
      label('익숙한 규칙으로, 다른 역할을 맡게 합니다', 0, 285, 3, D.green, 48);
      break;
    }
    case 'effort': {
      object('rules', '익숙한 구조', -570, -80, 0, D.ink, '이미 이해한 행동과 규칙');
      object('detail', '다듬을 지점', 0, -80, 1, D.teal, '차이를 만드는 부분');
      object('result', '새로운 경험', 570, -80, 2, D.green, '선택한 목표와 맥락');
      arrow([[-345, -120], [-205, -120]], 1);
      arrow([[220, -120], [350, -120]], 2, D.green);
      label('완성도를 높일 곳을, 구체적으로 고릅니다', 0, 265, 3, D.yellow, 54);
      break;
    }
    case 'effortExamples': {
      add(0, examples(true));
      add(3, <>
        <Line points={[[-585, 160], [-585, 190], [585, 190], [585, 160]]}
          stroke={D.line} lineWidth={4} lineJoin={'round'}/>
        <Line points={[[0, 160], [0, 190]]} stroke={D.line} lineWidth={4}/>
      </>);
      label(timing.exampleSummary ?? '각 경험을 선명하게 다듬습니다', 0, 265, 3, D.ink, 54);
      break;
    }
    case 'cooperation': {
      during(0, undefined, photo(['social', 'versus', 'mm2vs'], -430, -35, 820, '같은 코스를 함께 출발하기', D.green, 'route'));
      label('같은 출발점', 490, -190, 0, D.ink, 56, 620);
      arrow([[490, -142], [490, -77]], 1, D.teal);
      label('서로의 위치', 490, -22, 1, D.teal, 56, 620);
      arrow([[490, 34], [490, 100]], 2, D.green);
      label('앞서기 위한 선택', 490, 159, 2, D.green, 56, 660);
      label('같은 규칙도, 상대가 있으면 다른 경험으로', 0, 285, 3, D.yellow, 48);
      break;
    }
    case 'appeals': {
      object('control', '행동', -660, -85, 0, D.teal, '반복하는 일');
      object('pickaxe', '목적', -220, -85, 1, D.yellow, '움직이는 이유');
      object('pencil', '역할', 220, -85, 2, D.yellow, '플레이 · 설계');
      object('route', '관계', 660, -85, 2, D.green, '상대와의 경험');
      // These are parallel dimensions, not a score or a causal/ranking chain.
      add(2, <>
        <Line points={[[-660, 140], [-660, 180], [660, 180], [660, 140]]}
          stroke={D.line} lineWidth={4} lineJoin={'round'}/>
        <Line points={[[-220, 140], [-220, 180]]} stroke={D.line} lineWidth={4}/>
        <Line points={[[220, 140], [220, 180]]} stroke={D.line} lineWidth={4}/>
      </>);
      label('여러 방향의 매력을, 하나의 경험으로 묶기', 0, 265, 3, D.ink, 51);
      break;
    }
    case 'conclusion': {
      add(0, examples());
      label('익숙한 요소를', -440, 228, 1, D.ink, 58, 670);
      arrow([[-75, 228], [130, 228]], 1, D.teal, .25);
      label('이 게임만의 경험으로', 490, 228, 2, D.green, 58, 760);
      break;
    }
  }
  yield* t(duration, duration, linear);
}
