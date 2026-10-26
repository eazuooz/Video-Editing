import {makeScene2D, Circle, Img, Line, Node, Rect, Txt} from '@motion-canvas/2d';
import {createSignal, linear} from '@motion-canvas/core';
import puzzled from '../../../../shared/assets/branding/cat-reactions-v1/puzzled.png';
import realize from '../../../../shared/assets/branding/cat-reactions-v1/realize.png';
import relief from '../../../../shared/assets/branding/cat-reactions-v1/relief.png';
import {DARK as C} from '../../styles/research-dark';
import {clamp01, displayedNumber, recentThreeFrames, sampleAt, smooth, type Rate} from './model';
import {requireProductionInput, type SectionId} from './production-input';

const FONT = 'Malgun Gothic';
const X = [-300, 0, 300];
const ROUTE_LEFT = -420;
const ROUTE_RIGHT = 420;
const routeX = (units: number) => ROUTE_LEFT + (ROUTE_RIGHT - ROUTE_LEFT) * units / 240;
const images = {puzzled, realize, relief};

/**
 * Portrait1080×1920. Finishing owns header y0..440 and the fixed captions.
 * Samples/values stay above y1110. Only the position24 comparison uses the
 * second marker row down to y1270; the cat is absent for that whole beat.
 * The moving markers are an authored sample diagram, not a game simulation.
 */
export default makeScene2D(function* (view) {
  const {timing, config} = requireProductionInput();
  view.fill(C.background);
  const time = createSignal(0);
  const frame = () => Math.min(timing.frames - 1, Math.floor(time() * timing.fps + .0001));
  const section = () => timing.sections.find(s => frame() >= s.startFrame && frame() < s.endFrame)
    ?? timing.sections[timing.sections.length - 1];
  const id = (): SectionId => section().visualId ?? section().id;
  const start = () => section().startFrame / timing.fps;
  const elapsed = () => time() - start();
  const rangeProgress = (first: string, last: string) => clamp01(
    (frame() - timing.events[first].startFrame) /
    Math.max(1, timing.events[last].endFrame - timing.events[first].startFrame - 1),
  );
  const cut = () => config.cuts[id()];
  const footage = () => !section().forceDiagram && Boolean(cut()) && elapsed() < (cut()?.maxDuration ?? 0);
  const sourceKind = () => footage() ? '실제 게임 영상' : '우리 표본화 도식';
  const modelFrame = () => {
    if (id() === 'frames') return Math.floor(5 * rangeProgress('p2-1', 'p2-4'));
    if (id() === 'pose24') return Math.floor(60 * rangeProgress('p4-2', 'p4-3'));
    if (id() === 'position24') return Math.floor(60 * rangeProgress('p5-1', 'p5-4'));
    if (id() === 'close') return 5;
    return 0;
  };
  const poseRate = (): Rate => id() === 'frames' ? 60 : 24;
  const positionRate = (): Rate => id() === 'position24' ? 24 : 60;
  const selected = () => sampleAt(modelFrame(), poseRate(), positionRate());
  const three = () => recentThreeFrames(modelFrame());

  const reaction = () => {
    // Two full-width sampling rows are more important than a reaction overlay.
    if (id() === 'position24') return undefined;
    if (timing.reactions) return timing.reactions.find(r => time() >= r.start && time() < r.end);
    const definitions = [
      {cue: 'p1-2', kind: 'puzzled' as const},
      {cue: 'p4-3', kind: 'realize' as const},
      {cue: 'p6-3', kind: 'relief' as const},
    ];
    for (const d of definitions) {
      const cue = timing.events[d.cue];
      const a = cue.startFrame / timing.fps;
      const b = Math.min(cue.endFrame / timing.fps, a + 2.3);
      if (time() >= a && time() < b) return {start: a, end: b, kind: d.kind};
    }
    return undefined;
  };
  const catOpacity = () => {
    const r = reaction();
    return r ? smooth((time() - r.start) / .16) * smooth((r.end - time()) / .18) : 0;
  };

  view.add(<Txt text="그림 재생 · 화면 위치" position={[-445, -485]} offset={[-1, 0]}
    fill={C.teal} fontFamily={FONT} fontSize={28} fontWeight={700}/>);
  view.add(<Txt text={sourceKind} position={[450, -485]} offset={[1, 0]}
    fill={C.muted} fontFamily={FONT} fontSize={27}/>);

  const diagram = new Node({opacity: () => footage() ? 0 : 1});
  view.add(diagram);
  const titles: Record<SectionId, string> = {
    game: '그림과 위치는 따로 바뀐다',
    frames: '그림 한 장 · 놓이는 위치',
    'source-rates': '그림24fps · 게임60fps',
    pose24: '같은 그림이어도 위치는 앞으로',
    position24: '위치까지 줄이면 중간 점이 줄어든다',
    close: '만화의 질감과 매끄러운 이동을 함께',
  };
  const definition = () => id() === 'source-rates' && frame() < timing.events['p3-2'].startFrame;
  diagram.add(<Txt text={() => titles[id()]} position={[0, -402]}
    fill={C.title} fontFamily={FONT} fontSize={41} fontWeight={700}
    opacity={() => definition() ? 0 : 1}/>);
  diagram.add(<Txt text="표본 확대 · A/B/C는 그림 예시 · 숫자는 도식값" position={[0, -340]}
    fill={C.muted} fontFamily={FONT} fontSize={28}
    opacity={() => definition() ? 0 : 1}/>);

  // Three-line canonical definition, collapsing to the persistent term chip.
  const definitionCard = new Node({opacity: () => definition() ? 1 : 0});
  diagram.add(definitionCard);
  definitionCard.add(<Txt text="Frame rate · fps" position={[0, -444]}
    fill={C.title} fontFamily={FONT} fontSize={34} fontWeight={700}/>);
  definitionCard.add(<Txt text="프레임 레이트" position={[0, -402]}
    fill={C.ink} fontFamily={FONT} fontSize={34} fontWeight={700}/>);
  definitionCard.add(<Txt text="일 초에 재생하거나 표시하는 프레임 수" position={[0, -358]}
    fill={C.ink} fontFamily={FONT} fontSize={29}/>);

  const samples = new Node({opacity: () => definition() ? .22 : 1});
  diagram.add(samples);
  for (let i = 0; i < 3; i++) {
    const sampledFrame = () => three()[i];
    const state = () => sampleAt(sampledFrame(), poseRate(), positionRate());
    const current = () => sampledFrame() === modelFrame();
    const known = () => sampledFrame() <= modelFrame();
    const card = new Rect({position: [X[i], -165], size: [250, 240], radius: 12,
      fill: C.panel, stroke: () => current() ? C.title : C.line,
      lineWidth: () => current() ? 5 : 2, opacity: () => known() ? 1 : .22});
    samples.add(card);
    card.add(<Img src={() => config.poseImages[state().poseKey]} size={[172, 172]} position={[0, -15]}/>);
    card.add(<Txt text={() => `그림 ${state().poseKey}`} position={[0, 94]}
      fill={C.title} fontFamily={FONT} fontSize={33} fontWeight={700}/>);
    samples.add(<Txt text={() => `${state().timeSeconds.toFixed(3)}초`}
      position={[X[i], -298]} fill={C.ink} fontFamily={FONT} fontSize={31} fontWeight={700}
      opacity={() => known() ? 1 : .22}/>);
    samples.add(<Line points={[[X[i], -42], [X[i], -20]]} stroke={C.teal} lineWidth={4}
      endArrow arrowSize={11} opacity={() => known() ? 1 : .22}/>);
    samples.add(<Txt text={() => `위치 ${displayedNumber(state().position)}`}
      position={[X[i], 17]} fill={C.teal} fontFamily={FONT} fontSize={38} fontWeight={700}
      opacity={() => known() ? 1 : .22}/>);
  }

  // A common model-time cursor drives BOTH schedules; a separate axis shows
  // held drawing versus advancing position. The expanded timeline is labeled
  // as a diagram and is not a slowed/counterfeit real-game recording.
  const comparison = () => id() === 'position24';
  const firstY = () => comparison() ? 132 : 120;
  const addRoute = (row: 0 | 1, rate: Rate, label: string, color: string) => {
    const y = () => row === 0 ? firstY() : 255;
    const show = () => row === 0 || comparison();
    const value = () => sampleAt(modelFrame(), poseRate(), rate).position;
    const group = new Node({opacity: () => show() ? 1 : 0});
    samples.add(group);
    group.add(<Txt text={label} position={() => [-440, y() - (row === 0 ? 60 : 38)]} offset={[-1, 0]}
      fill={color} fontFamily={FONT} fontSize={29} fontWeight={700}/>);
    group.add(<Line points={() => [[ROUTE_LEFT, y()], [ROUTE_RIGHT, y()]]}
      stroke={C.line} lineWidth={4}/>);
    for (let tick = 0; tick <= 6; tick++) group.add(<Circle
      position={() => [routeX(tick * 40), y()]} size={9} fill={C.line}/>);
    group.add(<Circle position={() => [routeX(value()), y()]} size={32}
      fill={C.background} stroke={color} lineWidth={7}/>);
    group.add(<Txt text={() => displayedNumber(value())}
      position={() => [routeX(value()), y() + (row === 0 ? -24 : 42)]} fill={color}
      fontFamily={FONT} fontSize={32} fontWeight={700}/>);
  };
  addRoute(0, 60, '위치60회 · 같은 시간', C.teal);
  addRoute(1, 24, '위치24회 · 중간 위치가 적다', C.red);

  // Notes stay left of the approved large lower-right cat reserve.
  const notes = new Node({opacity: () => comparison() ? 0 : 1});
  diagram.add(notes);
  notes.add(<Txt text={() => `도식 시간 ${(selected().timeSeconds).toFixed(3)}초`}
    position={[-435, 250]} offset={[-1, 0]} fill={C.ink}
    fontFamily={FONT} fontSize={31} fontWeight={700}/>);
  notes.add(<Txt text={() => id() === 'pose24' ? '그림은 유지 · 위치는 갱신'
    : id() === 'frames' ? '그림의 모양 ≠ 화면의 위치'
    : id() === 'close' ? '그림24fps + 위치60회 도식'
    : '24는 그림 · 60은 게임'} position={[-435, 309]} offset={[-1, 0]}
    fill={C.title} fontFamily={FONT} fontSize={31} fontWeight={700}/>);

  const game = new Node({opacity: () => footage() ? 1 : 0});
  view.add(game);
  game.add(<Img src={() => {
    if (!footage()) return config.poseImages.A;
    const c = cut() ?? config.cuts.game;
    if (!c) return config.poseImages.A;
    const limit = Math.max(1, Math.ceil(c.maxDuration * timing.fps));
    const n = (c.firstFrame ?? 0) + Math.max(0, Math.min(limit - 1, frame() - section().startFrame));
    const name = (c.pattern ?? '{frame}.jpg').replace('{frame}', String(n).padStart(c.digits ?? 6, '0'));
    return config.frameRoot.replace(/\/$/, '') + '/' +
      (section().frameDirectory ?? c.frameDirectory).replace(/\/$/, '') + '/' + name;
  }} size={[1000, 562.5]} position={[0, -140]}/>);
  game.add(<Txt text="Cuphead" position={[-445, -448]} offset={[-1, 0]}
    fill={C.ink} fontFamily={FONT} fontSize={34} fontWeight={700}/>);
  game.add(<Txt text="그림24fps · 게임60fps" position={[-435, 250]} offset={[-1, 0]}
    fill={C.title} fontFamily={FONT} fontSize={32} fontWeight={700}
    opacity={() => id() === 'source-rates' || id() === 'close' ? 1 : 0}/>);

  const focus = () => {
    if (!footage()) return undefined;
    const keys = cut()?.focus ?? [];
    const t = elapsed();
    if (!keys.length || t < keys[0].time || t > keys[keys.length - 1].time) return undefined;
    const b = keys.findIndex(k => k.time >= t);
    if (b <= 0) return keys[0];
    const a = keys[b - 1];
    const z = keys[b];
    const mix = clamp01((t - a.time) / Math.max(.0001, z.time - a.time));
    return {
      x: a.x + (z.x - a.x) * mix, y: a.y + (z.y - a.y) * mix,
      radiusX: a.radiusX + (z.radiusX - a.radiusX) * mix,
      radiusY: a.radiusY + (z.radiusY - a.radiusY) * mix,
    };
  };
  game.add(<Circle position={() => {
    const p = focus();
    return p ? [(p.x - 960) * 1000 / 1920, -140 + (p.y - 540) * 1000 / 1920] : [0, 0];
  }} size={() => {
    const p = focus(); return p ? [p.radiusX * 2000 / 1920, p.radiusY * 2000 / 1920] : [1, 1];
  }} stroke={C.green} lineWidth={7} opacity={() => focus() ? 1 : 0}/>);

  const cat = new Rect({size: [460, 560], position: [290, 430], clip: true, opacity: catOpacity});
  view.add(cat);
  cat.add(<Img src={() => images[reaction()?.kind ?? 'realize']} size={650}
    position={() => [55 + 14 * (1 - catOpacity()), 0]}/>);

  yield view.toPromise();
  yield* time(timing.frames / timing.fps, timing.frames / timing.fps, linear);
});
