import {makeScene2D, Img, Line, Node, Rect, Txt} from '@motion-canvas/2d';
import {createSignal, linear} from '@motion-canvas/core';
import timingInput from '../../../../projects/shorts-factorio-belt-gaps/production/visual-timing.json';
import configInput from '../../../../projects/shorts-factorio-belt-gaps/production/visual-config.json';
import realize from '../../../../shared/assets/branding/cat-reactions-v1/realize.png';
import relief from '../../../../shared/assets/branding/cat-reactions-v1/relief.png';
import {DARK} from '../../styles/research-dark';
import {
  BELT_LENGTH, ITEM_WIDTH, INITIAL_POSITIONS, blockedPositions, clamp01,
  freeGaps, lastPositiveInternalGap, smooth, translate,
} from './model';

type SectionId = 'game' | 'cost' | 'gaps' | 'ends' | 'blocked' | 'cache' | 'close';
type Point = [number, number];
type Cue = {startFrame: number; endFrame?: number; durationFrames?: number};
type Section = {
  id: SectionId; visualId?: SectionId; startFrame: number; endFrame: number;
  start: number; end: number; forceDiagram?: boolean; frameDirectory?: string;
};
type Timing = {
  fps: number; frames: number; durationSeconds?: number; sections: Section[];
  events?: Record<string, Cue>;
  reactions?: {start: number; end: number; kind: 'realize' | 'relief'}[];
};
type Cut = {
  in: number;
  frameDirectory?: string; firstFrame?: number; maxDuration: number;
  pattern?: string; digits?: number;
  crop?: {center: Point; width: number};
};
type FootageMark = {
  start: number; end: number; label: string;
  keyframes: {at: number; center: Point; size: Point}[];
};
type Config = {
  game?: string; frameRoot?: string; cuts?: Partial<Record<SectionId, Cut>>;
  footageAnnotations?: Partial<Record<SectionId, FootageMark[]>>;
  /** Local section fractions, provisional until exact speech cues are supplied. */
  phaseAt?: Record<string, [number, number]>;
};

const timing = timingInput as Timing;
// JSON imports infer number[] rather than two-element tuples. Validate source
// coordinate tuples before using the typed crop/annotation configuration.
const config = configInput as unknown as Config;
const validPoint = (p: Point) => Array.isArray(p) && p.length === 2 && p.every(Number.isFinite);
for (const c of Object.values(config.cuts ?? {})) {
  if (c?.crop && (!validPoint(c.crop.center) || c.crop.width <= 0 || c.crop.width > 1920))
    throw new Error('Invalid inspected gameplay crop.');
}
for (const marks of Object.values(config.footageAnnotations ?? {})) {
  for (const m of marks ?? []) {
    if (!(m.end > m.start) || !m.keyframes.length || m.keyframes.some((k, i) =>
      !Number.isFinite(k.at) || !validPoint(k.center) || !validPoint(k.size)
      || (i > 0 && k.at <= m.keyframes[i - 1].at)))
      throw new Error('Invalid inspected footage annotation keyframes.');
  }
}
const C = {...DARK, metal: '#71838b', metalLight: '#b9cbd0', rail: '#4b555a'};
const FONT = 'Malgun Gothic';
const FPS = timing.fps || 60;
const LEFT = -429;
const UNIT = 66;
const BELT_Y = -150;
const GAP_Y = -42;
const ITEM_NAMES = ['A', 'B', 'C', 'D'];
const GAP_NAMES = ['시작', 'A–B', 'B–C', 'C–D', '끝'];
const ROOT = config.frameRoot ?? '/@fs/D:/Github/VideoEditing/projects/shorts-factorio-belt-gaps/production/local/frames/';
const xOf = (units: number) => LEFT + units * UNIT;
const format = (value: number) => Math.abs(value - Math.round(value)) < .015
  ? String(Math.round(value)) : value.toFixed(1);

/**
 * Portrait 1080×1920. Static header is supplied by the finishing pass (y 0–440).
 * This scene owns y 460–1400; it does not draw or move the fixed caption box.
 * All figures are an authored illustration, never measured Factorio internals.
 * The same conveyor and ore models persist from cost through cache.
 */
export default makeScene2D(function* (view) {
  view.fill(C.background);
  const time = createSignal(0);
  const frame = () => Math.min(timing.frames - 1, Math.floor(time() * FPS + .0001));
  const section = () => timing.sections.find(s => frame() >= s.startFrame && frame() < s.endFrame)
    ?? timing.sections[timing.sections.length - 1];
  const id = () => section().visualId ?? section().id;
  const elapsed = () => time() - section().start;
  const phase = () => clamp01(elapsed() / Math.max(1 / FPS, section().end - section().start));
  const cue = (name: string, defaults: [number, number]) => {
    const event = timing.events?.[name];
    if (event) {
      const end = event.endFrame ?? event.startFrame + (event.durationFrames ?? FPS);
      return smooth((frame() - event.startFrame) / Math.max(1, end - event.startFrame));
    }
    const [a, b] = config.phaseAt?.[name] ?? defaults;
    return smooth((phase() - a) / Math.max(.001, b - a));
  };
  const cueStarted = (name: string, fallback: number) => {
    const event = timing.events?.[name];
    return event ? frame() >= event.startFrame : phase() >= (config.phaseAt?.[name]?.[0] ?? fallback);
  };
  const cut = () => config.cuts?.[id()];
  const footage = () => !section().forceDiagram && Boolean(cut()) && elapsed() < (cut()?.maxDuration ?? 0);
  const pictureLabel = () => footage() ? '실제 게임 녹화' : '해설용 모형';
  const showTerm = () => !footage() && ['gaps', 'ends', 'blocked', 'cache', 'close'].includes(id());
  const defaultReaction = () => {
    if (id() === 'gaps' && elapsed() >= .5 && elapsed() < 2.25)
      return {start: section().start + .5, end: section().start + 2.25, kind: 'realize' as const};
    if (id() === 'close' && elapsed() >= Math.max(0, section().end - section().start - 2.7))
      return {start: Math.max(section().start, section().end - 2.7), end: section().end, kind: 'relief' as const};
    return undefined;
  };
  const reaction = () => timing.reactions
    ? timing.reactions.find(r => time() >= r.start && time() < r.end)
    : defaultReaction();
  const catOpacity = () => {
    const r = reaction();
    return r ? smooth((time() - r.start) / .18) * smooth((r.end - time()) / .2) : 0;
  };

  // Source-kind labels are content, not source/creator credits. Keep the
  // separate header zone and final fixed caption geometry entirely untouched.
  view.add(<Txt text="운송 라인 · Transport line" position={[-445, -485]} offset={[-1, 0]}
    fill={C.teal} fontFamily={FONT} fontSize={27} fontWeight={700} opacity={() => showTerm() ? 1 : 0}/>);
  view.add(<Txt text="2017 · 벨트 최적화" position={[-445, -450]} offset={[-1, 0]}
    fill={C.muted} fontFamily={FONT} fontSize={24} opacity={() => showTerm() ? 1 : 0}/>);
  view.add(<Txt text={pictureLabel} position={[450, -485]} offset={[1, 0]}
    fill={C.muted} fontFamily={FONT} fontSize={26}/>);

  const diagram = new Node({opacity: () => footage() ? 0 : 1});
  view.add(diagram);
  const titles: Record<SectionId, string> = {
    game: '수많은 물건이 같은 방향으로', cost: '좌표는 바뀌어도, 간격은 그대로',
    gaps: '위치 대신, 빈틈을 저장', ends: '함께 이동하면 양 끝만 변경',
    blocked: '출구가 막히면, 빈틈이 닫힌다', cache: '앞쪽의 남은 빈틈을 기억',
    close: '같은 움직임 · 바뀌는 정보만 갱신',
  };
  diagram.add(<Txt text={() => titles[id()]} position={[0, -402]} fill={C.title}
    fontFamily={FONT} fontSize={42} fontWeight={700}/>);
  diagram.add(<Txt text={() => id() === 'close' ? '물건 4개를 놓은 같은 해설 모형'
    : '길이 13 · 물건 너비 1 · 숫자는 해설용 단위'} position={[0, -340]} fill={C.muted}
    fontFamily={FONT} fontSize={29}/>);

  const costMove = () => cue('costMove', [.12, .55]);
  const endMove = () => cue('endMove', [.12, .58]);
  const reachEnd = () => cue('blockReachEnd', [.08, .32]);
  const packFront = () => cue('blockPackFront', [.43, .88]);
  const packNext = () => cue('cachePackNext', [.12, .53]);
  const positions = (): number[] => {
    if (id() === 'cost') return translate(INITIAL_POSITIONS, costMove());
    if (id() === 'gaps') return translate(INITIAL_POSITIONS, 1);
    // The small "same movement again" marker explicitly identifies the repeat;
    // it is an illustrative A/B comparison, not duplicated game footage.
    if (id() === 'ends') return translate(INITIAL_POSITIONS, endMove());
    if (id() === 'blocked') return blockedPositions(reachEnd(), packFront());
    if (id() === 'cache') return blockedPositions(1, 1, packNext());
    return translate(INITIAL_POSITIONS, 1);
  };
  const gaps = () => freeGaps(positions());
  const gapMode = () => ['gaps', 'ends', 'blocked', 'cache'].includes(id());
  const blocked = () => id() === 'blocked' || id() === 'cache';
  const moving = () => id() === 'cost' ? costMove() > 0 && costMove() < 1
    : id() === 'ends' ? endMove() > 0 && endMove() < 1
    : id() === 'blocked' ? reachEnd() < 1 || (packFront() > 0 && packFront() < 1)
    : id() === 'cache' ? packNext() > 0 && packNext() < 1 : false;
  const lastGap = () => lastPositiveInternalGap(positions());
  const currentGap = () => id() === 'cache' ? lastGap() : id() === 'blocked' && reachEnd() >= .999 ? 3 : -1;
  const stage = new Node({opacity: () => id() === 'close' ? 0 : 1});
  diagram.add(stage);

  stage.add(<Txt text={() => id() === 'ends' ? '같은 +1 이동을 간격으로 다시 보기'
    : blocked() ? '이동 방향 →  |  출구만 막음' : '이동 방향 →  |  모든 물건이 같은 속도'}
    position={[0, -275]} fill={blocked() ? C.red : C.ink} fontFamily={FONT} fontSize={29}/>);
  stage.add(<Rect position={[0, BELT_Y]} size={[BELT_LENGTH * UNIT + 18, 122]}
    radius={18} fill={C.panel} stroke={C.rail} lineWidth={4}/>);
  for (const y of [-48, 48]) stage.add(<Line points={[[LEFT, BELT_Y + y], [-LEFT, BELT_Y + y]]}
    stroke={C.rail} lineWidth={7}/>);
  // Static, directional conveyor slats avoid suggesting a different speed or
  // inventing looping item motion to pad the explanation.
  for (let i = 0; i < 13; i++) stage.add(<Line points={[
    [xOf(i + .22), BELT_Y + 32], [xOf(i + .58), BELT_Y], [xOf(i + .22), BELT_Y - 32],
  ]} stroke="#39434a" lineWidth={5} lineJoin="round"/>);
  for (let i = 0; i <= BELT_LENGTH; i++) stage.add(<Line
    points={[[xOf(i), BELT_Y + 62], [xOf(i), BELT_Y + 72]]} stroke={C.rail} lineWidth={3}/>);
  stage.add(<Txt text="0" position={[LEFT, BELT_Y + 92]} fill={C.muted} fontFamily={FONT} fontSize={25}/>);
  stage.add(<Txt text="13" position={[-LEFT, BELT_Y + 92]} fill={C.muted} fontFamily={FONT} fontSize={25}/>);

  for (let i = 0; i < 4; i++) {
    const item = new Node({position: () => [xOf(positions()[i] + ITEM_WIDTH / 2), BELT_Y]});
    stage.add(item);
    // Original faceted ore glyph; no extracted game sprite or competitor asset.
    item.add(<Line points={[[-33, -14], [-18, -31], [10, -33], [33, -8], [29, 22], [6, 33], [-25, 25]]}
      closed fill={C.metal} stroke={C.metalLight} lineWidth={3} lineJoin="round"/>);
    item.add(<Line points={[[-18, -28], [2, -9], [29, -7], [6, 29], [2, -9], [-27, 22]]}
      stroke="#41585e" lineWidth={3}/>);
    item.add(<Line points={[[-17, -29], [10, -30], [2, -9]]} closed fill={C.metalLight}/>);
    item.add(<Txt text={ITEM_NAMES[i]} position={[0, -81]} fill={C.ink}
      fontFamily={FONT} fontSize={30} fontWeight={700}/>);
    item.add(<Rect size={[UNIT + 10, 80]} radius={12} lineWidth={4} stroke={C.teal}
      opacity={() => id() === 'cost' && moving() ? .85 : 0}/>);
  }

  // Gap arrows use item EDGES, not centers: 3 center-to-center units minus the
  // item width of 1 means a free gap of 2. These are consistent in every state.
  const gapSpan = (i: number): [number, number] => [
    i === 0 ? 0 : positions()[i - 1] + ITEM_WIDTH,
    i === 4 ? BELT_LENGTH : positions()[i],
  ];
  for (let i = 0; i < 5; i++) {
    const color = () => currentGap() === i ? C.red : (i === 0 || i === 4) ? C.title : C.teal;
    const group = new Node({opacity: () => gapMode() ? 1
      : id() === 'cost' && i > 0 && i < 4 ? cue('costGapReveal', [.63, .75]) : 0});
    stage.add(group);
    group.add(<Line points={() => {
      const [a, b] = gapSpan(i); return [[xOf(a), GAP_Y], [xOf(b), GAP_Y]];
    }} stroke={color} lineWidth={6} startArrow endArrow arrowSize={12}
      opacity={() => gaps()[i] >= .2 ? 1 : 0}/>);
    group.add(<Line points={() => {const [a] = gapSpan(i); return [[xOf(a), GAP_Y - 9], [xOf(a), GAP_Y + 9]];}}
      stroke={color} lineWidth={4}/>);
    group.add(<Line points={() => {const [, b] = gapSpan(i); return [[xOf(b), GAP_Y - 9], [xOf(b), GAP_Y + 9]];}}
      stroke={color} lineWidth={4}/>);
    group.add(<Txt text={() => format(gaps()[i])}
      position={() => {const [a, b] = gapSpan(i); return [xOf((a + b) / 2), GAP_Y + 38];}}
      fill={color} fontFamily={FONT} fontSize={32} fontWeight={700}/>);
  }
  stage.add(<Rect position={[xOf(BELT_LENGTH) + 14, BELT_Y]} size={[20, 146]}
    fill={C.red} opacity={() => blocked() ? 1 : 0}/>);
  stage.add(<Txt text="막힘" position={[xOf(BELT_LENGTH) - 32, BELT_Y - 115]} fill={C.red}
    fontFamily={FONT} fontSize={28} fontWeight={700} opacity={() => blocked() ? 1 : 0}/>);

  const coordinates = new Node({opacity: () => id() === 'cost' ? 1 : 0});
  stage.add(coordinates);
  for (let i = 0; i < 4; i++) {
    const x = -336 + i * 224;
    coordinates.add(<Txt text={ITEM_NAMES[i]} position={[x, 26]} fill={C.muted}
      fontFamily={FONT} fontSize={28}/>);
    coordinates.add(<Txt text={() => `${INITIAL_POSITIONS[i]} → ${format(positions()[i])}`}
      position={[x, 80]} fill={C.teal} fontFamily={FONT} fontSize={43} fontWeight={700}/>);
  }
  coordinates.add(<Txt text="왼쪽 끝의 좌표: 4개 값을 변경" position={[0, 154]}
    fill={C.ink} fontFamily={FONT} fontSize={33} fontWeight={700}/>);
  coordinates.add(<Txt text="물건 사이 빈틈은 여전히 2" position={[0, 219]}
    fill={C.teal} fontFamily={FONT} fontSize={34} fontWeight={700}
    opacity={() => cue('costGapReveal', [.63, .75])}/>);

  const data = new Node({opacity: () => gapMode() ? 1 : 0});
  stage.add(data);
  for (let i = 0; i < 5; i++) {
    const x = -356 + i * 178;
    const active = () => currentGap() === i;
    data.add(<Rect position={[x, 71]} size={[152, 110]} radius={10} fill={C.panel}
      stroke={() => active() ? C.red : i === 0 || i === 4 ? C.title : C.teal}
      lineWidth={() => active() ? 5 : 2}/>);
    data.add(<Txt text={GAP_NAMES[i]} position={[x, 38]} fill={C.muted}
      fontFamily={FONT} fontSize={25}/>);
    data.add(<Txt text={() => format(gaps()[i])} position={[x, 88]}
      fill={() => active() ? C.red : i === 0 || i === 4 ? C.title : C.teal}
      fontFamily={FONT} fontSize={43} fontWeight={700}/>);
  }
  // All late notes stay left of the mascot's reserved x=600..1060 area.
  stage.add(<Txt text={() => id() === 'gaps' ? '가운데 빈틈 2 · 2 · 2\n이동해도 그대로'
    : id() === 'ends' ? '시작 1 → 2 · 끝 2 → 1\n가운데 3개는 유지'
    : id() === 'blocked' ? '끝 빈틈 0 → 앞 물건 정지\n바로 뒤 빈틈 2 → 0'
    : id() === 'cache' ? '기억한 빈틈이 0이 되면\n그 뒤의 빈틈으로 이동' : ''}
    position={[-435, 242]} offset={[-1, 0]} fill={C.ink} fontFamily={FONT}
    fontSize={31} lineHeight={46} fontWeight={700} opacity={() => gapMode() ? 1 : 0}/>);

  const cache = new Node({opacity: () => id() === 'cache' ? 1 : 0});
  stage.add(cache);
  cache.add(<Line points={() => {
    const x = -356 + Math.max(1, lastGap()) * 178;
    return [[x, 156], [x, 132]];
  }} stroke={C.red} lineWidth={5} endArrow arrowSize={12}
    opacity={() => cueStarted('cacheExceptions', .70) ? 0 : 1}/>);
  cache.add(<Txt text={() => `기억한 위치: ${GAP_NAMES[Math.max(1, lastGap())]}`}
    position={[0, 178]} fill={C.red} fontFamily={FONT} fontSize={32} fontWeight={700}
    opacity={() => cueStarted('cacheExceptions', .70) ? 0 : 1}/>);
  cache.add(<Txt text="넣기 · 빼기 · 라인 경계 → 별도 처리" position={[0, 178]}
    fill={C.muted} fontFamily={FONT} fontSize={29}
    opacity={() => cueStarted('cacheExceptions', .70) ? 1 : 0}/>);

  // Same-object, same-motion A/B recap. Counts refer ONLY to the illustrated
  // four position fields versus two terminal-gap fields, not measured CPU cost.
  const recap = new Node({opacity: () => id() === 'close' ? 1 : 0});
  diagram.add(recap);
  const recapMove = () => cue('closeMove', [.10, .56]);
  for (let row = 0; row < 2; row++) {
    const y = row === 0 ? -214 : 38;
    recap.add(<Txt text={row === 0 ? '물건별 위치 저장' : '간격으로 저장'} position={[-434, y - 84]}
      offset={[-1, 0]} fill={row === 0 ? C.ink : C.teal} fontFamily={FONT} fontSize={31} fontWeight={700}/>);
    recap.add(<Rect position={[0, y]} size={[858, 90]} radius={14} fill={C.panel} stroke={C.rail} lineWidth={3}/>);
    for (let i = 0; i < 4; i++) recap.add(<Line
      points={[[-28, -14], [-12, -28], [12, -27], [28, -3], [20, 24], [-15, 27], [-28, 10]]}
      position={() => [xOf(INITIAL_POSITIONS[i] + .5 + recapMove()), y]} closed
      fill={C.metal} stroke={C.metalLight} lineWidth={3}/>);
    recap.add(<Txt text={row === 0 ? '갱신: 좌표 4개' : '갱신: 양 끝 간격 2개'} position={[434, y + 81]}
      offset={[1, 0]} fill={row === 0 ? C.ink : C.teal} fontFamily={FONT} fontSize={31} fontWeight={700}/>);
  }
  // Keep the recap conclusion above y=1250 and left of the cat reserve;
  // the final fixed caption starts near y=1284 and must never be moved.
  recap.add(<Txt text="같은 속도 · 막힘 없음" position={[-435, 174]} offset={[-1, 0]}
    fill={C.muted} fontFamily={FONT} fontSize={27}/>);
  recap.add(<Txt text={'움직임은 같게\n바뀌는 정보만'} position={[-435, 244]} offset={[-1, 0]}
    fill={C.title} fontFamily={FONT} fontSize={34} lineHeight={42} fontWeight={700}/>);

  // Original 60 fps gameplay, with a fixed 16:9 crop chosen from inspected FHD
  // source frames. The crop, marks and camera-pan keyframes share source pixels.
  const game = new Node({opacity: () => footage() ? 1 : 0});
  view.add(game);
  const viewport = new Rect({size: [1000, 562.5], position: [0, -140], clip: true});
  game.add(viewport);
  const cropScale = () => 1000 / (cut()?.crop?.width ?? 1920);
  const cropCenter = (): Point => cut()?.crop?.center ?? [960, 540];
  const sourcePoint = (point: Point): Point => [
    (point[0] - cropCenter()[0]) * cropScale(),
    (point[1] - cropCenter()[1]) * cropScale(),
  ];
  const sourceTime = () => (cut()?.in ?? 0) + elapsed();
  const mark = () => config.footageAnnotations?.[id()]?.find(m =>
    sourceTime() >= m.start && sourceTime() < m.end);
  const markGeometry = () => {
    const keys = mark()?.keyframes;
    if (!keys?.length) return {center: [0, 0] as Point, size: [0, 0] as Point};
    const next = keys.findIndex(k => k.at >= sourceTime());
    if (next <= 0) return keys[next < 0 ? keys.length - 1 : 0];
    const a = keys[next - 1], b = keys[next];
    const t = clamp01((sourceTime() - a.at) / (b.at - a.at));
    const mix = (u: Point, v: Point): Point => [u[0] + (v[0] - u[0]) * t, u[1] + (v[1] - u[1]) * t];
    return {center: mix(a.center, b.center), size: mix(a.size, b.size)};
  };
  const markReveal = () => mark() ? smooth((sourceTime() - mark()!.start) / .18) : 0;
  const markOpacity = () => mark() ? smooth((mark()!.end - sourceTime()) / .12) : 0;
  viewport.add(<Img src={() => {
    const c = cut() ?? config.cuts?.game;
    if (!c) return '';
    const dir = section().frameDirectory ?? c.frameDirectory ?? id();
    const n = (c.firstFrame ?? 0) + Math.max(0, Math.min(
      section().endFrame - section().startFrame - 1,
      Math.ceil(c.maxDuration * FPS) - 1, frame() - section().startFrame,
    ));
    const name = (c.pattern ?? '{frame}.jpg').replace('{frame}', String(n).padStart(c.digits ?? 6, '0'));
    return ROOT + (dir ? dir.replace(/\/$/, '') + '/' : '') + name;
  }} size={() => [1920 * cropScale(), 1080 * cropScale()]}
    position={() => sourcePoint([960, 540])}/>);
  // Hollow editor-drawn guide: no detector scores, invented speed or hidden
  // engine measurement. Every guide disappears before the inspected source cut.
  const marker = new Node({opacity: markOpacity});
  viewport.add(marker);
  marker.add(<Line points={() => {
    const g = markGeometry(), [x, y] = sourcePoint(g.center);
    const w = g.size[0] * cropScale() / 2, h = g.size[1] * cropScale() / 2;
    return [[x - w, y - h], [x + w, y - h], [x + w, y + h], [x - w, y + h], [x - w, y - h]];
  }} end={markReveal} stroke={C.teal} lineWidth={7} lineJoin="round"/>);
  marker.add(<Line points={() => {
    const g = markGeometry(), [x, y] = sourcePoint(g.center);
    return [[x, y + g.size[1] * cropScale() / 2 + 2], [x, y + 72]];
  }} end={markReveal} stroke={C.teal} lineWidth={5}/>);
  marker.add(<Rect size={[300, 52]} position={() => {
    const [x, y] = sourcePoint(markGeometry().center); return [x, y + 98];
  }} fill={C.background} radius={8} opacity={markReveal}>
    <Txt text={() => mark()?.label ?? ''} fill={C.teal} fontFamily={FONT} fontSize={31} fontWeight={700}/>
  </Rect>);
  game.add(<Txt text={config.game ?? 'Factorio'} position={[-445, -448]} offset={[-1, 0]}
    fill={C.ink} fontFamily={FONT} fontSize={34} fontWeight={700}/>);

  // The full cat reserve is x600..1060, y1320..1880. Keep both eyes, nose and
  // mouth below the two-line fixed caption (bottom around1475). Ears may pass
  // behind that box; no data cell or conveyor enters the face's reserved area.
  const cat = new Rect({size: [460, 560], position: [290, 640], clip: true, opacity: catOpacity});
  view.add(cat);
  cat.add(<Img src={() => reaction()?.kind === 'relief' ? relief : realize}
    size={560} position={() => [55 + 24 * (1 - catOpacity()), 0]}/>);

  yield view.toPromise();
  const duration = timing.durationSeconds ?? timing.frames / FPS;
  yield* time(duration, duration, linear);
});
