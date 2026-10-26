import {makeScene2D, Circle, Img, Line, Node, Rect, Txt} from '@motion-canvas/2d';
import {createSignal, linear} from '@motion-canvas/core';
import puzzled from '../../../../shared/assets/branding/cat-reactions-v1/puzzled.png';
import realize from '../../../../shared/assets/branding/cat-reactions-v1/realize.png';
import relief from '../../../../shared/assets/branding/cat-reactions-v1/relief.png';
import {DARK as C} from '../../styles/research-dark';
import {clamp01, expandedFrame, expandedState, sampleAt, smooth, type PoseKey, type Rate} from './model';
import {requireProductionInput, type SectionId} from './production-input';

const FONT = 'Malgun Gothic';
const ROUTE_LEFT = -350;
const ROUTE_RIGHT = 350;
const routeX = (progress: number) => ROUTE_LEFT + (ROUTE_RIGHT - ROUTE_LEFT) * progress;
const images = {puzzled, realize, relief};

/**
 * Own expanded diagram only: six consecutive60Hz samples occupy the available
 * actual speech cue, so a held pose and a changed position can be read together.
 * No time remapping, hold, loop or slowdown is applied to independent gameplay.
 * Header0..440, caption1290..1470 and the existing large-cat reserve stay fixed.
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
  const sourceKind = () => footage() ? '실제 게임 영상' : '우리 확대 도식';
  const comparing = () => id() === 'position24';
  const diagramProgress = () => id() === 'position24' ? rangeProgress('p5-2', 'p5-4')
    : id() === 'pose24' ? rangeProgress('p4-2', 'p4-3')
    : id() === 'frames' ? rangeProgress('p2-4', 'p2-4')
    : id() === 'source-rates' ? rangeProgress('p3-2', 'p3-2') : 0;
  const step = () => expandedFrame(diagramProgress());
  const state = (rate: Rate = 60) => expandedState(diagramProgress(), rate);
  const justDrawings = () => id() === 'frames' && frame() < timing.events['p2-3'].startFrame;
  const splitting = () => id() === 'frames' && frame() >= timing.events['p2-3'].startFrame;
  const pose = (): PoseKey => justDrawings()
    ? sampleAt(expandedFrame(rangeProgress('p2-2', 'p2-2')), 60, 60).poseKey
    : splitting() ? 'A' : state().current.poseKey;
  const singleX = () => id() === 'close' ? -230 : justDrawings() ? 0
    : splitting() && frame() < timing.events['p2-4'].startFrame ? 0 : routeX(state().routeProgress);
  const definition = () => id() === 'source-rates' && frame() < timing.events['p3-2'].startFrame;
  const showAxis = () => !justDrawings() && id() !== 'close' &&
    !(splitting() && frame() < timing.events['p2-4'].startFrame);

  const reaction = () => {
    if (comparing()) return undefined;
    if (timing.reactions) return timing.reactions.find(r => time() >= r.start && time() < r.end);
    const definitions = [
      {cue: 'p1-2', kind: 'puzzled' as const},
      // Let the expanded position changes finish before the large realization.
      {cue: 'p4-4', kind: 'realize' as const},
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
    game: '그림의 모양과 놓이는 위치는 별개',
    frames: '그림을 바꾸기 → 위치를 옮기기',
    'source-rates': '그림은24장 · 게임은60프레임',
    pose24: '같은 그림을 유지한 채 앞으로',
    position24: '같은 순간 · 위치 갱신만 바꾸기',
    close: '만화의 질감 + 매끄러운 움직임',
  };
  diagram.add(<Txt text={() => titles[id()]} position={[0, -406]}
    fill={C.title} fontFamily={FONT} fontSize={42} fontWeight={700}
    opacity={() => definition() ? 0 : 1}/>);
  diagram.add(<Txt text={() => justDrawings() ? '그림 예시를 한 장씩 바꿉니다'
    : comparing() ? `같은 화면 ${step() + 1} / 6 · 그림은 동일`
    : id() === 'close' ? '두 속도를 따로 정할 수 있습니다'
    : splitting() ? '그림 A는 그대로 · 화면 위치만 이동'
    : '연속된6개 화면을 천천히 확대한 도식'} position={[0, -343]}
    fill={C.ink} fontFamily={FONT} fontSize={33}
    opacity={() => definition() ? 0 : 1}/>);

  const definitionCard = new Node({opacity: () => definition() ? 1 : 0});
  diagram.add(definitionCard);
  definitionCard.add(<Txt text="Frame rate · fps" position={[0, -433]}
    fill={C.title} fontFamily={FONT} fontSize={39} fontWeight={700}/>);
  definitionCard.add(<Txt text="프레임 레이트" position={[0, -382]}
    fill={C.ink} fontFamily={FONT} fontSize={39} fontWeight={700}/>);
  definitionCard.add(<Txt text="일 초에 표시하는 프레임 수" position={[0, -331]}
    fill={C.ink} fontFamily={FONT} fontSize={33}/>);

  // One big, recognizable subject replaces three small screenshots and tables.
  const single = new Node({opacity: () => comparing() ? 0 : definition() ? .2 : 1});
  diagram.add(single);
  single.add(<Txt text={() => id() === 'close' ? '그림24장/초'
    : justDrawings() ? `그림 ${pose()}`
    : splitting() ? '① 그림 A 그대로'
    : state().poseChanged ? `① 그림 ${pose()}로 교체` : `① 그림 ${pose()} 유지`}
    position={() => id() === 'close' ? [-230, -285] : [0, -263]}
    fill={C.title} fontFamily={FONT} fontSize={43} fontWeight={700}/>);
  single.add(<Img src={() => config.poseImages[pose()]} size={[250, 250]}
    position={() => [singleX(), -90]}/>);

  // Previous/current anchors and the arrow use the SAME scale as the subject.
  // A hollow marker denotes the old position; it does not invent a game hitbox.
  single.add(<Circle position={() => [routeX(state().previousRouteProgress), 89]}
    size={28} stroke={C.muted} lineWidth={4}
    opacity={() => showAxis() && state().positionChanged ? .7 : 0}/>);
  single.add(<Line points={() => [[routeX(state().previousRouteProgress), 48], [singleX(), 48]]}
    stroke={C.teal} lineWidth={7} endArrow arrowSize={17}
    opacity={() => showAxis() && state().positionChanged ? 1 : 0}/>);
  single.add(<Line points={[[ROUTE_LEFT, 90], [ROUTE_RIGHT, 90]]}
    stroke={C.line} lineWidth={4} opacity={() => showAxis() ? 1 : 0}/>);
  for (let n = 0; n < 6; n++) {
    single.add(<Circle position={[routeX(n / 5), 90]} size={() => n === step() ? 23 : 12}
      fill={() => n <= step() ? C.teal : C.line} opacity={() => showAxis() ? 1 : 0}/>);
    single.add(<Txt text={String(n + 1)} position={[routeX(n / 5), 133]}
      fill={() => n === step() ? C.teal : C.muted}
      fontFamily={FONT} fontSize={32} fontWeight={700} opacity={() => showAxis() ? 1 : 0}/>);
  }
  single.add(<Txt text={() => id() === 'close' ? '게임60프레임/초'
    : justDrawings() ? '모양이 바뀌면 애니메이션'
    : splitting() ? '② 위치만 앞으로'
    : '② 위치는 계속 앞으로'} position={[-435, 219]} offset={[-1, 0]}
    fill={C.teal} fontFamily={FONT} fontSize={38} fontWeight={700}/>);
  single.add(<Txt text={() => id() === 'close' ? '위치 갱신은 별도'
    : justDrawings() ? '이동 속도는 따로 정할 수 있어요'
    : '작은 원=직전 위치 · 숫자=연속 화면 순서'}
    position={[-435, 284]} offset={[-1, 0]}
    fill={C.muted} fontFamily={FONT} fontSize={29}
    opacity={() => catOpacity() > .05 && id() !== 'close' ? 0 : 1}/>);

  // Same pose, path, camera, time cursor and endpoints. ONLY position rate changes.
  // Six60Hz presentation samples cover0..1/12s of model time, not a game capture.
  const comparison = new Node({opacity: () => comparing() ? 1 : 0});
  diagram.add(comparison);
  for (const [row, rate, label, color] of [
    [0, 60, '위치60회/초 · 매 화면 앞으로', C.teal],
    [1, 24, '위치24회/초 · 멈췄다가 이동', C.red],
  ] as const) {
    const y = row === 0 ? -159 : 122;
    const s = () => state(rate);
    comparison.add(<Txt text={label} position={[-440, y - 105]} offset={[-1, 0]}
      fill={color} fontFamily={FONT} fontSize={36} fontWeight={700}/>);
    comparison.add(<Line points={[[ROUTE_LEFT, y + 115], [ROUTE_RIGHT, y + 115]]}
      stroke={C.line} lineWidth={4}/>);
    const positions = rate === 60 ? [0, .2, .4, .6, .8, 1] : [0, .5, 1];
    for (const p of positions) comparison.add(<Circle position={[routeX(p), y + 115]}
      size={13} fill={color} opacity={.5}/>);
    comparison.add(<Circle position={() => [routeX(s().previousRouteProgress), y + 115]}
      size={29} stroke={C.muted} lineWidth={4}
      opacity={() => s().positionChanged ? .7 : 0}/>);
    comparison.add(<Line points={() => [[routeX(s().previousRouteProgress), y + 99], [routeX(s().routeProgress), y + 99]]}
      stroke={color} lineWidth={6} endArrow arrowSize={14}
      opacity={() => s().positionChanged ? 1 : 0}/>);
    comparison.add(<Img src={() => config.poseImages[s().current.poseKey]} size={[174, 174]}
      position={() => [routeX(s().routeProgress), y + 8]}/>);
    comparison.add(<Circle position={() => [routeX(s().routeProgress), y + 115]} size={25}
      fill={C.background} stroke={color} lineWidth={6}/>);
  }
  comparison.add(<Txt text="같은 그림 · 같은 길 · 같은 시간" position={[0, 292]}
    fill={C.ink} fontFamily={FONT} fontSize={32} fontWeight={700}/>);

  // Independent native gameplay routing and inspected focus marks are unchanged.
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
