import {Circle, Img, Line, Node, Rect, Txt, type View2D} from '@motion-canvas/2d';
import {createSignal, linear} from '@motion-canvas/core';
import {DARK as D} from '../../../styles/research-dark';

export interface Timing {
  duration: number;
  /** Scene-local starts of the corresponding narration.lines, indexed from 0. */
  cues?: number[];
  credit?: string;
  title?: string;
}

export type LessonKind = 'overview' | 'effects' | 'tradeoffs' | 'find' | 'auto' | 'test' | 'appearance' | 'conclusion';
type Point = [number, number];
type EquipmentKind = 'sword' | 'shield' | 'boots';
const ASSETS = '/@fs/D:/Github/VideoEditing/output/player-customization/preproduction-assets-v3/';
const clamp = (value: number) => Math.max(0, Math.min(1, value));
const smooth = (value: number) => {const x = clamp(value); return x * x * (3 - 2 * x);};

const text = (value: string, x: number, y: number, size = 45, color: string = D.ink) =>
  <Txt text={value} x={x} y={y} fontSize={size} lineHeight={size * 1.28}
    fill={color} fontWeight={600} fontFamily={D.font}/>;

/** Recognizable, independently authored equipment; never a captured game item. */
function equipment(kind: EquipmentKind, x: number, y: number, color: string = D.ink, scale = 1) {
  if (kind === 'sword') return <Node x={x} y={y} scale={scale}>
    <Line points={[[0, -83], [20, -56], [15, 26], [-15, 26], [-20, -56]]}
      closed fill={D.surfaceFront} stroke={color} lineWidth={5}/>
    <Line points={[[0, -68], [0, 22]]} stroke={color} lineWidth={3}/>
    <Line points={[[-42, 31], [42, 31]]} stroke={color} lineWidth={10} lineCap={'round'}/>
    <Rect y={56} width={18} height={39} radius={4} fill={D.background} stroke={color} lineWidth={5}/>
    <Circle y={83} width={26} height={20} fill={D.background} stroke={color} lineWidth={4}/>
  </Node>;
  if (kind === 'shield') return <Node x={x} y={y} scale={scale}>
    <Line points={[[0, -76], [63, -49], [57, 22], [34, 57], [0, 82], [-34, 57], [-57, 22], [-63, -49]]}
      closed fill={D.surfaceFront} stroke={color} lineWidth={6} lineJoin={'round'}/>
    <Line points={[[0, -55], [0, 57]]} stroke={color} lineWidth={5}/>
    <Line points={[[-41, -12], [41, -12]]} stroke={color} lineWidth={5}/>
    <Circle y={-12} width={27} height={27} fill={D.background} stroke={color} lineWidth={4}/>
  </Node>;
  return <Node x={x} y={y} scale={scale}>
    <Line points={[[-45, -71], [13, -71], [13, 7], [64, 34], [64, 69], [-55, 69], [-55, 26], [-45, 8]]}
      closed fill={D.surfaceFront} stroke={color} lineWidth={6} lineJoin={'round'}/>
    <Line points={[[-40, -52], [7, -52]]} stroke={color} lineWidth={5}/>
    <Line points={[[-26, -26], [5, -26]]} stroke={color} lineWidth={4}/>
    <Line points={[[-25, -4], [5, -4]]} stroke={color} lineWidth={4}/>
    <Line points={[[-51, 51], [59, 51]]} stroke={color} lineWidth={5}/>
  </Node>;
}

/** A generic material icon for classification; not a captured Zelda item. */
function material(x: number, y: number, color: string = D.green, scale = 1) {
  return <Node x={x} y={y} scale={scale}>
    <Line points={[[-65, 30], [-48, -38], [10, -68], [62, -18], [56, 45], [-7, 65]]}
      closed fill={D.surfaceFront} stroke={color} lineWidth={6} lineJoin={'round'}/>
    <Line points={[[-48, -38], [-3, -7], [10, -68]]} stroke={color} lineWidth={4}/>
    <Line points={[[-3, -7], [56, 45]]} stroke={color} lineWidth={4}/>
    <Line points={[[-65, 30], [-3, -7], [-7, 65]]} stroke={color} lineWidth={4}/>
  </Node>;
}

/** Fictional A/B weapons. Shape, numbers and performance are illustrative. */
function gun(x: number, y: number, heavy: boolean, color: string) {
  return <Node x={x} y={y}>
    <Rect x={-17} y={0} width={heavy ? 148 : 112} height={heavy ? 62 : 47}
      radius={8} fill={D.surfaceFront} stroke={color} lineWidth={5}/>
    <Rect x={heavy ? 112 : 87} y={-6} width={heavy ? 115 : 82} height={heavy ? 31 : 20}
      fill={D.background} stroke={color} lineWidth={5}/>
    <Line points={[[-92, -20], [-139, -35], [-139, 28], [-92, 14]]}
      closed fill={D.surfaceSide} stroke={color} lineWidth={5}/>
    <Line points={[[-22, 30], [-36, 83], [-2, 83], [17, 30]]}
      closed fill={D.background} stroke={color} lineWidth={5}/>
    <Line points={[[17, -31], [17, -49], [54, -49], [54, -31]]} stroke={color} lineWidth={5}/>
    <Line points={[[9, 34], [40, 34], [35, 56], [11, 56]]} stroke={color} lineWidth={4}/>
  </Node>;
}

/**
 * D21 independently authored explanations, using root-supplied independent
 * gameplay stills. Stills remain explanation footage, not moving gameplay.
 * Current V3 assets are independently inspected captures of the selected three
 * games; visual-assets.json records the exact source frames. Actual captioned
 * scene loading, layout and moving/mobile review are separate checks.
 * Image slots use 16:9; supplied captures must have that reviewed crop/aspect.
 * No in-image target or captured measurement is invented by this renderer.
 * The final caption anchor is MC (0,430); content ends above MC y=340.
 */
export function* lesson(view: View2D, kind: string, timing: Timing) {
  const titles: Record<LessonKind, string> = {
    overview: '고르는 시간도 게임의 재미가 됩니다',
    effects: '숫자 옆에, 바뀐 결과를 보여 주기',
    tradeoffs: '잘하는 일이 다르면, 고를 이유가 생깁니다',
    find: '원하는 후보를 먼저 찾을 수 있게',
    auto: '자동 장비는 정답보다 출발점',
    test: '바꾸기와 시험하기를 가깝게',
    appearance: '강해지는 것과, 마음에 드는 것은 다릅니다',
    conclusion: '무엇을 바꿀지, 어떻게 고르게 할지',
  };
  if (!(kind in titles)) throw Error(`Unknown player-customization explanation: ${kind}`);
  if (!(timing.duration > 0)) throw Error('D21 explanation needs a positive duration.');
  const sceneKind = kind as LessonKind;
  const paragraphCounts: Record<LessonKind, number> = {overview: 3, effects: 5, tradeoffs: 5, find: 5, auto: 4, test: 5, appearance: 4, conclusion: 4};
  const t = createSignal(0), duration = timing.duration;
  const motionScale = Math.min(1, duration / 8);
  const at = (index: number) => timing.cues?.[index] ?? duration * index / paragraphCounts[sceneKind];
  const reveal = (index: number, delay = 0, length = .55) => () => smooth((t() - at(index) - delay * motionScale) / (length * motionScale));
  // Incompatible paragraph states share positions. Clear the previous state
  // exactly at the next cue; only the new state reveals, so labels never mix.
  const interval = (start: number, end?: number) => () => reveal(start)() * (end === undefined || t() < at(end) ? 1 : 0);
  const add = (index: number, children: any, delay = 0) => view.add(<Node opacity={reveal(index, delay)}>{children}</Node>);
  const during = (start: number, end: number | undefined, children: any) => view.add(<Node opacity={interval(start, end)}>{children}</Node>);
  const label = (value: string, x: number, y: number, cue: number, color: string = D.ink, size = 45, delay = 0) => add(cue, text(value, x, y, size, color), delay);
  const trace = (points: Point[], cue: number, color: string = D.teal, delay = 0, parent: Node | View2D = view) =>
    parent.add(<Line points={points} stroke={color} lineWidth={8} endArrow arrowSize={20}
      end={reveal(cue, delay, .8)} lineCap={'round'} lineJoin={'round'}/>);
  const note = (value: string, cue: number, color: string = D.muted, size = 33) => label(value, 0, 311, cue, color, size);
  const image = (file: string, x: number, y: number, width: number, caption: string, color: string = D.ink) => {
    const height = width * 9 / 16;
    return <>
      <Rect x={x} y={y} width={width} height={height} fill={D.background}/>
      <Img src={ASSETS + file} x={x} y={y} width={width} height={height}/>
      <Rect x={x} y={y} width={width + 4} height={height + 4} stroke={D.line} lineWidth={2}/>
      {text(caption, x, y + height / 2 + 37, 33, color)}
    </>;
  };
  const step = (value: string, x: number, y: number, cue: number, color: string = D.teal, width = 310) => add(cue, <>
    <Rect x={x} y={y} width={width} height={86} radius={8} fill={D.background} stroke={color} lineWidth={4}/>
    {text(value, x, y, 42, color)}
  </>);

  view.fill(D.background);
  view.add(<>
    {text('얌얌코딩  /  커스터마이징', -615, -482, 29, D.muted)}
    {text(timing.title ?? titles[sceneKind], 0, -393, 55, D.title)}
  </>);
  if (timing.credit) view.add(<Txt text={timing.credit} x={545} y={-482} width={700}
    textAlign={'right'} textWrap fontSize={23} lineHeight={29} fontWeight={500} fontFamily={D.font} fill={D.muted}/>);

  switch (sceneKind) {
    case 'overview': {
      during(0, 1, image('acnh-before.png', 0, -26, 1040, '캐릭터를 고르는 순간부터'));
      during(1, 2, <>
        {image('raiders-equipment.png', -440, -55, 790, '선택의 결과를 보기', D.teal)}
        {image('acnh-after.png', 440, -55, 790, '마음에 드는 모습 찾기', D.green)}
        {text('결과 보기  →  고르기와 시험  →  나를 표현하기', 0, 294, 41, D.title)}
      </>);
      during(2, undefined, <>
        {image('raiders-equipment.png', -420, -35, 880, '스플래툰 레이더스 · 장비 고르기')}
        {text('장비를 고르면', 525, -155, 45, D.ink)}
        <Line points={[[525, -105], [525, 0]]} stroke={D.teal} lineWidth={8} endArrow arrowSize={20} end={reveal(2, .3, .8)}/>
        <Node opacity={reveal(2, 1.1)}>{text('사용 결과까지', 525, 60, 48, D.teal)}{text('함께 확인', 525, 129, 48, D.teal)}</Node>
      </>);
      break;
    }
    case 'effects': {
      during(0, 1, image('raiders-equipment.png', -420, -35, 880, '스플래툰 레이더스 · 장비 선택 화면'));
      during(1, 3, image('raiders-test.png', -420, -35, 880, '고른 장비를 시험하며 결과 보기'));
      during(3, undefined, image('raiders-choice.png', -420, -35, 880, '결정에 필요한 차이를 보여 주는 프리뷰'));
      during(0, 3, <>{text('고를 장비', 525, -196, 46, D.ink)}{text('선택', 525, -132, 39, D.muted)}</>);
      const effectsFlow = <Node opacity={interval(0, 3)}/>;
      view.add(effectsFlow);
      trace([[525, -85], [525, 6]], 0, D.teal, .35, effectsFlow);
      effectsFlow.add(<Node opacity={reveal(0, 1.15)}>{text('사용 결과', 525, 68, 49, D.teal)}</Node>);
      during(1, 3, text('공격 방식 · 준비 과정', 525, 153, 36, D.ink));
      during(2, 3, text('장비 선택 → 직접 사용 → 결과 확인', 0, 310, 35, D.title));
      during(3, 4, <>{text('프리뷰  /  Preview', 525, -146, 43, D.title)}{text('고르기 전에', 525, -26, 46)}{text('결과를 미리 확인', 525, 48, 44, D.teal)}{text('멋진 장면보다\n판단할 차이를 보여 주기', 525, 182, 35, D.ink)}</>);
      during(4, undefined, <>{text('차이가 보였다면', 525, -126, 44, D.teal)}{text('어느 쪽을\n고를 이유가 있을까요?', 525, 30, 43, D.title)}{text('모든 면에서 하나만 좋다면?', 0, 311, 37, D.ink)}</>);
      break;
    }
    case 'tradeoffs': {
      // Generic component/attack/preparation comparison only. Specific Raiders
      // equipment, component types and their actual differences await source
      // inspection; these reserved still names do not establish measured stats.
      during(0, 2, <>
        {image('raiders-test.png', -440, -75, 790, '장비를 사용한 모습', D.teal)}
        {image('raiders-choice.png', 440, -75, 790, '비교할 선택지', D.green)}
      </>);
      during(0, 1, <>
        {text('기준이 달라지면, 고를 이유도 달라집니다', 0, 249, 38, D.title)}
        {text('사용 방식을 관찰 · 특정 무기의 수치 비교가 아닙니다', 0, 311, 33, D.muted)}
      </>);
      during(1, 2, <>
        {text('트레이드오프  /  Trade-off', 0, 249, 39, D.title)}
        {text('얻는 것과 감수할 조건을 함께 보기', 0, 311, 36, D.ink)}
      </>);
      during(2, undefined, <>
        {text('A', -460, -279, 53, D.teal)}{text('B', 460, -279, 53, D.green)}
        {gun(-460, -180, true, D.teal)}{gun(460, -180, false, D.green)}
        <Node opacity={reveal(2, 4.3)}>{text('한 발 피해 100  /  간격 2초', -460, -45, 37, D.teal)}</Node>
        <Node opacity={reveal(2, 7.7)}>{text('한 발 피해 40  /  간격 0.5초', 460, -45, 37, D.green)}</Node>
        {text('설명용 수치 · 실제 게임 측정값이 아닙니다', 0, 311, 33, D.muted)}
      </>);
      during(2, 3, <>
        <Node opacity={reveal(2, 10.8)}>{text('초당 평균 피해 / Damage per second · DPS', 0, 35, 33, D.title)}{text('오래 계속 맞히는 조건으로 비교', 0, 253, 31, D.title)}</Node>
        <Node opacity={reveal(2, 11.3)}>{text('한 발 피해 ÷ 발사 간격', 0, 88, 37, D.ink)}</Node>
        <Node opacity={reveal(2, 12)}>{text('100 ÷ 2 = 50', -460, 171, 57, D.teal)}{text('40 ÷ 0.5 = 80', 460, 171, 57, D.green)}</Node>
      </>);
      during(3, 4, <>
        {text('한 번만 쏠 기회  ·  적의 남은 체력 90', 0, 50, 43, D.title)}
        <Node opacity={reveal(3, 1.1)}>{text('100 ≥ 90', -460, 145, 60, D.teal)}{text('40 < 90', 460, 145, 60, D.orange)}</Node>
        <Node opacity={reveal(3, 1.65)}>{text('한 발로 조건 충족', -460, 225, 34, D.teal)}{text('한 발로는 부족', 460, 225, 34, D.orange)}</Node>
        {text('빗나감 · 방어력 등은 제외', 0, 271, 28, D.muted)}
      </>);
      during(4, undefined, <>{text('상황이 달라지면, 유리한 선택도 달라집니다', 0, 79, 45, D.title)}{text('다음 과제: 원하는 후보를 쉽게 찾기', 0, 206, 42, D.ink)}</>);
      break;
    }
    case 'find': {
      during(0, 2, image('botw-inventory.png', -420, -35, 880, '브레스 오브 더 와일드 · 장비 분류'));
      during(2, 3, image('acnh-categories.png', -420, -35, 880, '모여봐요 동물의 숲 · 초기 외형 선택'));
      during(0, 1, <>
        {text('아이콘  /  Icon', 525, -238, 42, D.title)}
        {equipment('sword', 370, -83, D.teal, .72)}
        {material(665, -83, D.green, .72)}
        {text('무기', 370, 38, 42, D.teal)}{text('소재', 665, 38, 42, D.green)}
        {text('종류를 알려 주는 작은 그림', 525, 157, 34, D.ink)}
        {text('오른쪽 그림은 원리 설명용', 525, 226, 29, D.muted)}
      </>);
      during(1, 2, <>
        {text('모양 + 이름 + 기능', 525, -243, 40, D.title)}
        {equipment('sword', 380, -120, D.teal, .55)}
        {equipment('sword', 670, -120, D.green, .55)}
        {text('검 A', 380, -16, 40, D.teal)}{text('검 B', 670, -16, 40, D.green)}
        {text('넓게 베기', 380, 55, 33, D.ink)}{text('빠르게 찌르기', 670, 55, 31, D.ink)}
        {text('비슷하면 함께 읽을 단서', 525, 162, 34, D.title)}
        {text('설명용 아이콘 · 가상 무기', 525, 226, 29, D.muted)}
      </>);
      during(2, 3, <>
        {text('바꿀 항목 찾기', 525, -229, 43, D.title)}
        <Line points={[[525, -177], [525, -111]]} stroke={D.teal} lineWidth={8} endArrow arrowSize={20} end={reveal(2, .3, .8)}/>
        <Node opacity={reveal(2, 1.1)}>{text('항목 안의 모양 고르기', 525, -52, 38, D.teal)}</Node>
        <Line points={[[525, 7], [525, 75]]} stroke={D.green} lineWidth={8} endArrow arrowSize={20} end={reveal(2, 1.7, .8)}/>
        <Node opacity={reveal(2, 2.5)}>{text('캐릭터 미리보기', 525, 137, 41, D.green)}</Node>
        {text('처음 캐릭터를 만드는 화면', 525, 238, 31, D.muted)}
      </>);
      const rowY = [-146, -10, 126];
      const sortProgress = () => smooth((t() - at(3) - 1.9 * motionScale) / (.8 * motionScale));
      const bow = <Node>
        <Line points={[[-23, -48], [2, -27], [13, 0], [2, 27], [-23, 48]]} stroke={D.green} lineWidth={5} lineJoin={'round'}/>
        <Line points={[[-23, -48], [-23, 48]]} stroke={D.green} lineWidth={3}/>
        <Line points={[[-45, 0], [36, 0]]} stroke={D.green} lineWidth={4} endArrow arrowSize={12}/>
      </Node>;
      const toyRow = (name: string, attack: number, x: number, y: number | (() => number), color: string, type: number, opacity: number | (() => number) = 1) =>
        <Node x={x} y={y} opacity={opacity}>
          <Line points={[[-266, 58], [266, 58]]} stroke={D.line} lineWidth={2}/>
          <Node x={-205}>{type === 2 ? bow.clone() : equipment('sword', 0, 0, color, type === 0 ? .48 : .34)}</Node>
          {text(name, -23, 0, 45, color)}{text(String(attack), 206, 0, 50, color)}
        </Node>;
      during(3, 4, <>
        {text('정렬  /  Sorting · 기준에 따라 순서를 바꾸기', 0, -303, 36, D.title)}
        {text('기존 목록', -440, -238, 39, D.ink)}{text('공격력이 높은 순', 440, -238, 39, D.teal)}
        {toyRow('대검', 12, -440, rowY[0], D.ink, 0)}
        {toyRow('단검', 8, -440, rowY[1], D.ink, 1)}
        {toyRow('활', 10, -440, rowY[2], D.ink, 2)}
        {toyRow('대검', 12, 440, rowY[0], D.teal, 0)}
        {toyRow('단검', 8, 440, ()=>rowY[1] + 136 * sortProgress(), D.orange, 1)}
        {toyRow('활', 10, 440, ()=>rowY[2] - 136 * sortProgress(), D.green, 2,
          ()=>1-smooth((t()-at(3)-1.55*motionScale)/(.25*motionScale))+smooth((t()-at(3)-2.85*motionScale)/(.35*motionScale)))}
        <Line points={[[-95, -8], [95, -8]]} stroke={D.teal} lineWidth={8} endArrow arrowSize={20} end={reveal(3, .35, .8)}/>
        {text('같은 후보, 다른 순서', 0, 246, 39, D.title)}
        {text('설명용 목록 · 가상 장비 / 수치', 0, 311, 33, D.muted)}
      </>);
      during(4, undefined, <>
        {text('좁혀 놓은 후보', -440, -238, 42, D.teal)}
        {toyRow('대검', 12, -440, rowY[0], D.teal, 0)}
        {toyRow('활', 10, -440, rowY[1], D.green, 2)}
        {toyRow('단검', 8, -440, rowY[2], D.orange, 1)}
        {text('후보를 찾은 다음에는', 525, -135, 41, D.ink)}
        {text('시작할 조합을\n도와줄 수 있습니다', 525, 19, 45, D.green)}
        {text('설명용 목록 · 가상 장비 / 수치', 0, 311, 33, D.muted)}
      </>);
      break;
    }
    case 'auto': {
      view.add(text('설명용 UI · 특정 게임의 자동 장비를 재현한 화면이 아닙니다', 0, -300, 31, D.muted));
      label('기준', -590, -227, 0, D.title, 45);
      label('후보', 0, -227, 0, D.title, 45);
      label('시작할 조합', 590, -227, 0, D.title, 45);
      add(0, <>
        {equipment('sword', -145, -48, D.muted, .72)}
        {equipment('shield', 0, -48, D.muted, .72)}
        {equipment('boots', 145, -48, D.muted, .72)}
      </>);
      during(0, 2, <>{text('어떤 목표인가요?', -590, -73, 39, D.ink)}{text('아직 고르지 않음', 590, -63, 35, D.muted)}</>);
      during(1, 2, <>{text('공격 중심', -590, 44, 42, D.teal)}{text('추위 대비', -590, 126, 42, D.ink)}{text('목표가 다르면 답도 다릅니다', 0, 250, 38, D.title)}</>);
      add(2, <>
        <Rect x={-590} y={-68} width={330} height={100} radius={8} stroke={D.teal} lineWidth={5}/>
        {text('공격 중심', -590, -68, 45, D.teal)}
        {text('먼저 목표 선택', -590, 30, 33, D.muted)}
      </>);
      trace([[-401, -68], [-270, -68]], 2, D.teal, .3);
      add(2, <Node opacity={reveal(2, 1.1)}>
        <Rect x={0} y={-48} width={465} height={213} radius={8} stroke={D.teal} lineWidth={5}/>
        {text('기준에 맞는 후보 고르기', 0, 112, 33, D.teal)}
      </Node>);
      trace([[259, -68], [380, -68]], 2, D.green, 1.7);
      add(2, <Node opacity={reveal(2, 2.5)}>
        {equipment('sword', 445, -48, D.green, .72)}
        {equipment('shield', 590, -48, D.green, .72)}
        <Node opacity={()=>1-reveal(3,.5)()}>{equipment('boots', 735, -48, D.green, .72)}</Node>
        {text('장착', 590, 112, 40, D.green)}
      </Node>);
      add(3, <Node opacity={reveal(3, .5)}>
        {equipment('boots', 735, -48, D.orange, .72)}
        <Line points={[[713, -77], [742, -60], [713, -44]]} stroke={D.orange} lineWidth={5} lineJoin={'round'}/>
        <Rect x={735} y={-48} width={125} height={164} radius={8} stroke={D.orange} lineWidth={5}/>
        {text('부츠 B', 735, 74, 29, D.orange)}
        {text('한 항목은 직접 변경', 590, 210, 36, D.orange)}
      </Node>);
      during(2, 3, text('기준에 따른 출발점 · 모든 상황의 최적해가 아닙니다', 0, 311, 33, D.muted));
      during(3, undefined, text('자동으로 시작하고, 취향에 맞게 다시 고르기', 0, 311, 36, D.title));
      break;
    }
    case 'test': {
      during(0, 1, image('botw-inventory.png', -420, -35, 880, '고른 장비를 직접 확인하기'));
      during(1, 2, image('botw-test.png', -420, -35, 880, '브레스 오브 더 와일드 · 장비 선택 후 사용'));
      during(2, undefined, image('raiders-test.png', -420, -35, 880, '스플래툰 레이더스 · 장비 고르고 시험'));
      step('바꾸기', 525, -218, 0, D.teal, 300);
      trace([[525, -160], [525, -91]], 1, D.teal, .15);
      step('시험하기', 525, -27, 1, D.green, 300);
      trace([[525, 34], [525, 105]], 3, D.green, .15);
      step('다시 바꾸기', 525, 169, 3, D.orange, 340);
      trace([[718, 169], [811, 169], [811, -218], [700, -218]], 3, D.orange, 1.15);
      during(0, 3, text('오른쪽은 절차를 요약한 도식', 525, 270, 29, D.muted));
      during(3, 4, text('짧은 고리: 예상과 다른 결과도 다음 선택의 정보로', 0, 311, 35, D.title));
      during(4, undefined, text('좋아진 성능과 마음에 드는 모습은 같은 말일까요?', 0, 311, 35, D.title));
      break;
    }
    case 'appearance': {
      // The two inspected captures must use the same full-frame crop/anchor.
      // Replace the still at one anchor; no pan or fabricated character morph.
      const swapped = () => t() >= at(1) + .8 * motionScale ? 1 : 0;
      view.add(<>
        <Node opacity={()=>1-swapped()}>{image('acnh-before.png', -360, -55, 1000, '모여봐요 동물의 숲 · 고르기 전')}</Node>
        <Node opacity={swapped}>{image('acnh-after.png', -360, -55, 1000, '모여봐요 동물의 숲 · 다른 항목을 고른 뒤')}</Node>
      </>);
      during(0, 2, <>
        {text('얼굴 · 머리 모양', 640, -185, 40, D.title)}
        <Txt text={()=>swapped()?'선택한 모습':'처음 모습'} x={640} y={-61} fontSize={48} fill={D.teal} fontWeight={600} fontFamily={D.font}/>
        <Node opacity={reveal(1, 1.15)}>{text('내 취향에\n맞는지 확인', 640, 113, 44, D.green)}</Node>
      </>);
      during(2, 3, <>{text('잘 싸우는가?', 640, -137, 41, D.muted)}{text('마음에 드는가?', 640, -2, 43, D.green)}{text('서로 다른 선택의 이유', 640, 133, 32, D.ink)}</>);
      during(3, undefined, <>{text('지금 바꾸는 것', 640, -187, 40, D.title)}{text('성능', 640, -64, 45, D.teal)}{text('외형', 640, 37, 45, D.green)}{text('연결할지 · 분리할지는\n게임마다 다릅니다', 640, 168, 32, D.ink)}</>);
      during(2, 3, text('꾸미고 상상하는 과정도 하나의 재미가 됩니다', 0, 311, 36, D.title));
      during(3, undefined, text('고른 모습과 결과를 확인할 수 있게', 0, 311, 38, D.title));
      break;
    }
    case 'conclusion': {
      during(0, 2, <>{image('raiders-equipment.png', -440, -65, 790, '효과를 보고, 다음 조합으로', D.teal)}{image('botw-inventory.png', 440, -65, 790, '조건을 보고 장비 고르기', D.green)}</>);
      during(2, undefined, <>{image('raiders-choice.png', -440, -65, 790, '사용 방식을 고르는 재미', D.teal)}{image('acnh-after.png', 440, -65, 790, '취향을 표현하는 재미', D.green)}</>);
      during(0, 1, text('완성품뿐 아니라, 선택하는 과정을 설계하기', 0, 294, 40, D.title));
      during(1, 2, text('결과 보기  →  비교  →  찾기  →  시험', 0, 294, 43, D.title));
      during(2, 3, text('더 강해지는 것과 다른 재미도 있습니다', 0, 294, 41, D.title));
      during(3, undefined, text('가장 오래 머물렀던 장비창은 어떤 게임이었나요?', 0, 294, 40, D.title));
      break;
    }
  }
  yield* t(duration, duration, linear);
}
