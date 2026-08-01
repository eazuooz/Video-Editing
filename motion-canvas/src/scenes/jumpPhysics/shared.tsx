// Motion Canvas port of examples/jump-physics-showcase/scene.py's BaseJumpScene.
// Same visual language as the Manim reference: a header, a real (time or
// space) axes box with a live-drawn curve, a character anchored to its
// position on that curve, a live numeric readout, and (for the standalone
// per-game videos) a "why / how" explanation card shown afterwards.

import {Circle, Img, Line, Node, Rect, Txt} from '@motion-canvas/2d';
import {
  type ThreadGenerator,
  all,
  createRef,
  createSignal,
  linear,
  useTime,
  waitFor,
} from '@motion-canvas/core';
import type {BrollWindow} from '../../broll';
import {COLORS, FONT, MONO, TEXT_SIZE} from '../../theme';
import {playBroll} from './broll';
import type {ChargeState, Profile} from './profiles';
import {FADE_OUT, POST_ROLL, PRE_ROLL, planPlayback} from './timing';

export const BG = COLORS.bg;
export const WHITE = COLORS.white;
export const TEXT = COLORS.text;
export const GREY_B = COLORS.greyB;
export const GREY_C = COLORS.greyC;
export const YELLOW = COLORS.yellow;
export const BLUE = COLORS.blue;
export const GREEN = COLORS.green;
export const ORANGE = COLORS.orange;
export const RED = COLORS.red;
export const PURPLE = COLORS.purple;
const CODE_BLUE = COLORS.codeBlue;
const CODE_COMMENT = COLORS.codeComment;

/**
 * Wait until the scene has been running for exactly `target` seconds.
 *
 * Motion Canvas derives a scene's length from how long its generator runs, so
 * this is what pins a narration-synced scene to its slot in the audio: however
 * the animation math rounds, the scene still ends on the intended frame and the
 * next one starts in sync with the next sentence.
 */
export function* padTo(target: number) {
  const remaining = target - useTime();
  if (remaining > 1e-6) {
    yield* waitFor(remaining);
  }
}

/**
 * Run the jump animation, with any gameplay B-roll layered over it.
 *
 * The two run in parallel rather than in sequence: the graph keeps advancing
 * behind the footage, so the segment still finishes with the character back on
 * the ground, and covering the middle of it costs no extra time.
 */
function* animateWithBroll(
  view: any,
  tween: ThreadGenerator,
  broll: BrollWindow | undefined,
) {
  if (!broll) {
    yield* tween;
    return;
  }
  yield* all(tween, playBroll(view, broll));
}

const TITLE_Y = -480;
const SUBTITLE_Y = -388;
const CAPTION_Y = -320;

const AXES_LEFT = -680;
const AXES_RIGHT = 680;
const AXES_TOP = -110;
const AXES_BOTTOM = 390;
const AXES_W = AXES_RIGHT - AXES_LEFT;
const AXES_H = AXES_BOTTOM - AXES_TOP;

const CHAR_X = -0.15;

type C2P = (dataX: number, dataY: number) => [number, number];

function makeC2P(xMin: number, xMax: number, yMax: number): C2P {
  return (dataX, dataY) => {
    const px = AXES_LEFT + ((dataX - xMin) / (xMax - xMin)) * AXES_W;
    const py = AXES_BOTTOM - (dataY / (yMax || 1)) * AXES_H;
    return [px, py];
  };
}

function sampleMax(fn: (t: number) => number, total: number, n = 200) {
  let max = -Infinity;
  for (let i = 0; i <= n; i++) {
    max = Math.max(max, fn((total * i) / n));
  }
  return max;
}

function niceStep(range: number, divisions = 5) {
  return Math.max(range / divisions, 0.2);
}

function buildAxesNodes(c2p: C2P, xMin: number, xMax: number, yMax: number, xDisplayMax: number) {
  const [gx0, gy0] = c2p(xMin, 0);
  const [gx1] = c2p(xDisplayMax, 0);
  const [ax0, ay0] = c2p(0, 0);
  const [, ay1] = c2p(0, yMax);

  const yTicks = [];
  const yStep = 1;
  for (let v = 0; v <= yMax + 1e-6; v += yStep) {
    const [tx, ty] = c2p(0, v);
    yTicks.push(
      <Line key={`yt-${v}`} points={[[tx - 8, ty], [tx + 8, ty]]} stroke={GREY_C} lineWidth={2} />,
    );
    yTicks.push(
      <Txt
        key={`yl-${v}`}
        text={v.toFixed(v % 1 === 0 ? 0 : 1)}
        fontFamily={MONO}
        fontSize={TEXT_SIZE.tick}
        fill={GREY_C}
        x={tx - 22}
        y={ty}
        offsetX={1}
      />,
    );
  }

  const xTicks = [];
  const xStep = niceStep(xDisplayMax);
  for (let v = 0; v <= xDisplayMax + 1e-6; v += xStep) {
    const [tx, ty] = c2p(v, 0);
    xTicks.push(
      <Line key={`xt-${v}`} points={[[tx, ty - 8], [tx, ty + 8]]} stroke={GREY_C} lineWidth={2} />,
    );
    xTicks.push(
      <Txt
        key={`xl-${v}`}
        text={`${v.toFixed(1)}s`}
        fontFamily={MONO}
        fontSize={TEXT_SIZE.tick}
        fill={GREY_C}
        x={tx}
        y={ty + 22}
        offsetY={-1}
      />,
    );
  }

  return (
    <>
      <Line points={[[gx0, gy0], [gx1, gy0]]} stroke={GREY_C} lineWidth={3} />
      <Line points={[[ax0, ay0], [ax0, ay1]]} stroke={GREY_C} lineWidth={3} />
      {yTicks}
      {xTicks}
    </>
  );
}

function readoutText(t: number, total: number, profile: Profile) {
  const tt = t % total;
  const h = profile.height(t);
  let text = `t = ${tt.toFixed(2)}s   height = ${h.toFixed(2)}`;
  if (profile.velocity) {
    const v = profile.velocity(t);
    text += `   v = ${v >= 0 ? '+' : ''}${v.toFixed(1)}`;
  }
  return text;
}

function characterNode(spriteSrc: string | undefined, color: string, spriteWidth: number, x: () => number, y: () => number) {
  return spriteSrc ? (
    <Img src={spriteSrc} width={spriteWidth} x={x} y={y} />
  ) : (
    <Circle size={44} fill={color} x={x} y={y} />
  );
}

export function* fadeHeader(
  view: any,
  title: string,
  subtitle: string,
  caption?: string,
) {
  const headerGroup = createRef<Node>();
  const captionRef = createRef<Txt>();
  view.add(
    <Node ref={headerGroup} opacity={0}>
      <Txt text={title} fontFamily={FONT} fontSize={TEXT_SIZE.title} fill={WHITE} x={0} y={TITLE_Y} />
      <Txt text={subtitle} fontFamily={FONT} fontSize={TEXT_SIZE.subtitle} fill={TEXT} x={0} y={SUBTITLE_Y} />
    </Node>,
  );
  yield* headerGroup().opacity(1, 0.35);
  if (caption) {
    view.add(
      <Txt ref={captionRef} text={caption} fontFamily={FONT} fontSize={TEXT_SIZE.caption} fill={GREY_C} x={0} y={CAPTION_Y} opacity={0} />,
    );
    yield* captionRef().opacity(1, 0.25);
  }
  return {headerGroup, captionRef: caption ? captionRef : null};
}

export function* fadeOutAll(refs: Array<(() => any) | null | undefined>, duration = 0.3) {
  yield* all(...refs.filter(Boolean).map(r => (r as () => any)().opacity(0, duration)));
}

type LeftAnchorOpts = {
  spriteSrc?: string;
  spriteWidth?: number;
  loops?: number;
  /** How long THIS call should take, in seconds; overrides `loops` for narration sync. Safe to chain multiple calls in one scene -- each is timed relative to when it starts, not to the scene's start. */
  duration?: number;
  /** Gameplay footage to lay over the middle of this segment. */
  broll?: BrollWindow;
  squatMarker?: number;
  noAirControl?: boolean;
};

export function* runProfileLeftAnchor(view: any, profile: Profile, color: string, opts: LeftAnchorOpts = {}) {
  // Captured before anything runs so `duration` means "how long THIS call
  // takes", not "absolute scene time" -- required for scenes that chain more
  // than one of these calls back to back (e.g. Celeste's two demos).
  const startTime = useTime();
  const {spriteSrc, spriteWidth = 100, squatMarker, noAirControl} = opts;
  const {loops, animSeconds} = planPlayback(profile, opts, Boolean(profile.caption));
  const {headerGroup, captionRef} = yield* fadeHeader(view, profile.title, profile.subtitle, profile.caption);

  const total = profile.total;
  const yMax = sampleMax(profile.height, total) + 0.6;
  const xDisplayMax = total * 1.05;
  const xMin = -0.4;
  const xMax = total * 1.05;
  const c2p = makeC2P(xMin, xMax, yMax);

  const axesGroup = createRef<Node>();
  view.add(
    <Node ref={axesGroup} opacity={0}>
      {buildAxesNodes(c2p, xMin, xMax, yMax, xDisplayMax)}
    </Node>,
  );
  yield* axesGroup().opacity(1, 0.35);

  const t = createSignal(0);
  const wrappedT = () => t() % total;

  const curve = createRef<Line>();
  const readout = createRef<Txt>();
  const cursor = createRef<Circle>();
  const dataGroup = createRef<Node>();

  const noteRef = createRef<Txt>();
  const squatRef = createRef<Txt>();

  view.add(
    <Node ref={dataGroup} opacity={1}>
      <Line
        ref={curve}
        points={() => {
          const w = wrappedT();
          const steps = 40;
          const count = Math.max(2, Math.floor(steps * (w / total)) + 1);
          const pts: [number, number][] = [];
          for (let i = 0; i < count; i++) {
            const tp = (w * i) / (count - 1 || 1);
            pts.push(c2p(tp, profile.height(tp)));
          }
          return pts;
        }}
        stroke={color}
        lineWidth={4}
        radius={8}
      />
      {characterNode(spriteSrc, color, spriteWidth, () => c2p(CHAR_X, profile.height(t()))[0], () => c2p(CHAR_X, profile.height(t()))[1])}
      <Txt
        ref={readout}
        text={() => readoutText(t(), total, profile)}
        fontFamily={MONO}
        fontSize={TEXT_SIZE.accent}
        fill={YELLOW}
        x={AXES_LEFT}
        y={AXES_TOP - 46}
        offsetX={-1}
      />
      <Circle
        ref={cursor}
        size={12}
        fill={color}
        x={() => c2p(wrappedT(), profile.height(t()))[0]}
        y={() => c2p(wrappedT(), profile.height(t()))[1]}
      />
      {noAirControl ? (
        <Txt ref={noteRef} text="← 조작 무효 →" fontFamily={FONT} fontSize={26} fill={RED} x={0} y={AXES_TOP - 78} />
      ) : null}
      {squatMarker !== undefined ? (
        <Txt
          ref={squatRef}
          text="준비..."
          fontFamily={FONT}
          fontSize={48}
          fill={YELLOW}
          x={c2p(CHAR_X, 0)[0]}
          y={c2p(CHAR_X, 0)[1] - 50}
          opacity={() => (wrappedT() < squatMarker ? 1 : 0)}
        />
      ) : null}
    </Node>,
  );

  yield* waitFor(PRE_ROLL);
  yield* animateWithBroll(view, t(total * loops, animSeconds, linear), opts.broll);
  yield* waitFor(POST_ROLL);

  yield* fadeOutAll([headerGroup, captionRef, axesGroup, dataGroup], FADE_OUT);
  if (opts.duration !== undefined) {
    yield* padTo(startTime + opts.duration);
  }
}

export function* runJumpKing(
  view: any,
  profile: Profile,
  chargeState: (t: number) => ChargeState,
  spriteSrc: string,
  opts: {spriteWidth?: number; loops?: number; duration?: number; broll?: BrollWindow} = {},
) {
  const startTime = useTime();
  const {spriteWidth = 90} = opts;
  const {loops, animSeconds} = planPlayback(
    profile,
    {...opts, loops: opts.loops ?? 1},
    Boolean(profile.caption),
  );
  const {headerGroup, captionRef} = yield* fadeHeader(view, profile.title, profile.subtitle, profile.caption);

  const total = profile.total;
  const yMax = sampleMax(profile.height, total) + 0.5;
  const xMin = -0.4;
  const xMax = total * 1.05;
  const c2p = makeC2P(xMin, xMax, yMax);

  const axesGroup = createRef<Node>();
  view.add(
    <Node ref={axesGroup} opacity={0}>
      {buildAxesNodes(c2p, xMin, xMax, yMax, total * 1.05)}
    </Node>,
  );
  yield* axesGroup().opacity(1, 0.35);

  const t = createSignal(0);
  const wrappedT = () => t() % total;
  const dataGroup = createRef<Node>();

  view.add(
    <Node ref={dataGroup} opacity={1}>
      <Line
        points={() => {
          const w = wrappedT();
          const steps = 60;
          const count = Math.max(2, Math.floor(steps * (w / total)) + 1);
          const pts: [number, number][] = [];
          for (let i = 0; i < count; i++) {
            const tp = (w * i) / (count - 1 || 1);
            pts.push(c2p(tp, profile.height(tp)));
          }
          return pts;
        }}
        stroke={PURPLE}
        lineWidth={4}
        radius={8}
      />
      {characterNode(spriteSrc, PURPLE, spriteWidth, () => c2p(CHAR_X, profile.height(t()))[0], () => c2p(CHAR_X, profile.height(t()))[1])}
      <Txt
        text={() => readoutText(t(), total, profile)}
        fontFamily={MONO}
        fontSize={TEXT_SIZE.accent}
        fill={YELLOW}
        x={AXES_LEFT}
        y={AXES_TOP - 46}
        offsetX={-1}
      />
      <Circle
        size={12}
        fill={PURPLE}
        x={() => c2p(wrappedT(), profile.height(t()))[0]}
        y={() => c2p(wrappedT(), profile.height(t()))[1]}
      />
      <Txt
        text={() => {
          const {charging, label} = chargeState(t());
          if (!label) return '';
          return charging ? `차지: ${label}` : `발사! (${label})`;
        }}
        fontFamily={FONT}
        fontSize={56}
        fill={() => (chargeState(t()).charging ? YELLOW : RED)}
        x={c2p(CHAR_X, 0)[0]}
        y={c2p(CHAR_X, 0)[1] - 170}
      />
    </Node>,
  );

  yield* waitFor(PRE_ROLL);
  yield* animateWithBroll(view, t(total * loops, animSeconds, linear), opts.broll);
  yield* waitFor(POST_ROLL);

  yield* fadeOutAll([headerGroup, captionRef, axesGroup, dataGroup], FADE_OUT);
  if (opts.duration !== undefined) {
    yield* padTo(startTime + opts.duration);
  }
}

type DualOpts = {
  spriteSrc?: string;
  spriteWidth?: number;
  loops?: number;
  /** How long THIS call should take, in seconds; overrides `loops` for narration sync. Safe to chain multiple calls in one scene -- each is timed relative to when it starts, not to the scene's start. */
  duration?: number;
  /** Gameplay footage to lay over the middle of this segment. */
  broll?: BrollWindow;
};

export function* runDualLeftAnchor(
  view: any,
  titleText: string,
  subtitleText: string,
  profileA: Profile,
  profileB: Profile,
  colorA: string,
  colorB: string,
  legendA: string,
  legendB: string,
  opts: DualOpts = {},
) {
  const startTime = useTime();
  const {spriteSrc, spriteWidth = 90} = opts;
  const {loops, animSeconds} = planPlayback(profileA, {...opts, loops: opts.loops ?? 3}, false);
  const {headerGroup} = yield* fadeHeader(view, titleText, subtitleText);

  const total = profileA.total;
  const yMax = Math.max(sampleMax(profileA.height, total), sampleMax(profileB.height, total)) + 0.6;
  const xMin = -0.4;
  const xMax = total * 1.05;
  const c2p = makeC2P(xMin, xMax, yMax);

  const axesGroup = createRef<Node>();
  const legendY = AXES_TOP - 96;
  view.add(
    <Node ref={axesGroup} opacity={0}>
      {buildAxesNodes(c2p, xMin, xMax, yMax, total * 1.05)}
      <Txt text={`● ${legendA}`} fontFamily={FONT} fontSize={TEXT_SIZE.legend} fill={colorA} x={-220} y={legendY} />
      <Txt text={`● ${legendB}`} fontFamily={FONT} fontSize={TEXT_SIZE.legend} fill={colorB} x={220} y={legendY} />
    </Node>,
  );
  yield* axesGroup().opacity(1, 0.35);

  const t = createSignal(0);
  const wrappedT = () => t() % total;
  const dataGroup = createRef<Node>();

  const makeCurve = (profile: Profile, color: string) => (
    <Line
      points={() => {
        const w = wrappedT();
        const steps = 40;
        const count = Math.max(2, Math.floor(steps * (w / total)) + 1);
        const pts: [number, number][] = [];
        for (let i = 0; i < count; i++) {
          const tp = (w * i) / (count - 1 || 1);
          pts.push(c2p(tp, profile.height(tp)));
        }
        return pts;
      }}
      stroke={color}
      lineWidth={4}
      radius={8}
    />
  );

  const makeCharacter = (profile: Profile, color: string, screenOffset: number) =>
    characterNode(
      spriteSrc,
      color,
      spriteWidth,
      () => c2p(CHAR_X, profile.height(t()))[0] + screenOffset,
      () => c2p(CHAR_X, profile.height(t()))[1],
    );

  view.add(
    <Node ref={dataGroup} opacity={1}>
      {makeCurve(profileA, colorA)}
      {makeCurve(profileB, colorB)}
      {makeCharacter(profileA, colorA, -45)}
      {makeCharacter(profileB, colorB, 45)}
      <Txt
        text={() => `t = ${wrappedT().toFixed(2)}s`}
        fontFamily={MONO}
        fontSize={TEXT_SIZE.accent}
        fill={YELLOW}
        x={AXES_LEFT}
        y={AXES_TOP - 46}
        offsetX={-1}
      />
    </Node>,
  );

  yield* waitFor(PRE_ROLL);
  yield* animateWithBroll(view, t(total * loops, animSeconds, linear), opts.broll);
  yield* waitFor(POST_ROLL);

  yield* fadeOutAll([headerGroup, axesGroup, dataGroup], FADE_OUT);
  if (opts.duration !== undefined) {
    yield* padTo(startTime + opts.duration);
  }
}

export function* runDualSpatial(
  view: any,
  titleText: string,
  subtitleText: string,
  profileA: Profile,
  profileB: Profile,
  colorA: string,
  colorB: string,
  legendA: string,
  legendB: string,
  opts: DualOpts = {},
) {
  const startTime = useTime();
  const {spriteSrc, spriteWidth = 80} = opts;
  const {loops, animSeconds} = planPlayback(profileA, {...opts, loops: opts.loops ?? 3}, false);
  const {headerGroup} = yield* fadeHeader(view, titleText, subtitleText);

  const total = profileA.total;
  const xMax = Math.max(sampleMax(profileA.x, total), sampleMax(profileB.x, total));
  const yMax = sampleMax(profileA.height, total) + 0.5;
  const xMin = 0;
  const xDisplayMax = xMax * 1.05;
  const c2p = makeC2P(xMin, xMax * 1.08, yMax);

  const axesGroup = createRef<Node>();
  const legendY = AXES_TOP - 96;
  view.add(
    <Node ref={axesGroup} opacity={0}>
      {buildAxesNodes(c2p, xMin, xMax * 1.08, yMax, xDisplayMax)}
      <Txt text={`● ${legendA}`} fontFamily={FONT} fontSize={TEXT_SIZE.legend} fill={colorA} x={-220} y={legendY} />
      <Txt text={`● ${legendB}`} fontFamily={FONT} fontSize={TEXT_SIZE.legend} fill={colorB} x={220} y={legendY} />
    </Node>,
  );
  yield* axesGroup().opacity(1, 0.35);

  const t = createSignal(0);
  const wrappedT = () => t() % total;
  const dataGroup = createRef<Node>();

  const makeCurve = (profile: Profile, color: string) => (
    <Line
      points={() => {
        const w = wrappedT();
        const steps = 40;
        const count = Math.max(2, Math.floor(steps * (w / total)) + 1);
        const pts: [number, number][] = [];
        for (let i = 0; i < count; i++) {
          const tp = (w * i) / (count - 1 || 1);
          pts.push(c2p(profile.x(tp), profile.height(tp)));
        }
        return pts;
      }}
      stroke={color}
      lineWidth={4}
      radius={8}
    />
  );

  const makeCharacter = (profile: Profile, color: string) =>
    characterNode(
      spriteSrc,
      color,
      spriteWidth,
      () => c2p(profile.x(t()), profile.height(t()))[0],
      () => c2p(profile.x(t()), profile.height(t()))[1],
    );

  view.add(
    <Node ref={dataGroup} opacity={1}>
      {makeCurve(profileA, colorA)}
      {makeCurve(profileB, colorB)}
      {makeCharacter(profileA, colorA)}
      {makeCharacter(profileB, colorB)}
      <Txt
        text={() => `t = ${wrappedT().toFixed(2)}s`}
        fontFamily={MONO}
        fontSize={TEXT_SIZE.accent}
        fill={YELLOW}
        x={AXES_LEFT}
        y={AXES_TOP - 46}
        offsetX={-1}
      />
    </Node>,
  );

  yield* waitFor(PRE_ROLL);
  yield* animateWithBroll(view, t(total * loops, animSeconds, linear), opts.broll);
  yield* waitFor(POST_ROLL);

  yield* fadeOutAll([headerGroup, axesGroup, dataGroup], FADE_OUT);
  if (opts.duration !== undefined) {
    yield* padTo(startTime + opts.duration);
  }
}

function codeColor(line: string) {
  return line.trimStart().startsWith('//') ? CODE_COMMENT : CODE_BLUE;
}

export function* showExplanation(view: any, gameTitle: string, why: string[], how: string[]) {
  const CARD_X = -820;
  const heading = createRef<Txt>();
  const whyGroup = createRef<Node>();
  const codeGroup = createRef<Node>();

  view.add(<Txt ref={heading} text={gameTitle} fontFamily={FONT} fontSize={TEXT_SIZE.explanationTitle} fill={WHITE} x={0} y={TITLE_Y} opacity={0} />);
  yield* heading().opacity(1, 0.4);

  const whyLineH = 64;
  const whyTop = -392;
  view.add(
    <Node ref={whyGroup} opacity={0}>
      <Txt text="왜 이렇게 만들었나" fontFamily={FONT} fontSize={TEXT_SIZE.accentLabel} fill={YELLOW} x={CARD_X} y={whyTop} offsetX={-1} />
      {why.map((line, i) => (
        <Txt
          key={`why-${i}`}
          text={line}
          fontFamily={FONT}
          fontSize={TEXT_SIZE.body}
          fill={GREY_B}
          x={CARD_X}
          y={whyTop + 78 + i * whyLineH}
          offsetX={-1}
        />
      ))}
    </Node>,
  );
  yield* whyGroup().opacity(1, 0.35);
  yield* waitFor(1.4);

  const codeTop = whyTop + 78 + why.length * whyLineH + 65;
  const codeLineH = 36;
  const boxHeight = how.length * codeLineH + 56;
  const boxWidth = 1120;

  view.add(
    <Node ref={codeGroup} opacity={0}>
      <Txt text="어떻게 동작하는가 (C++ 핵심 로직)" fontFamily={FONT} fontSize={TEXT_SIZE.accentLabel} fill={YELLOW} x={CARD_X} y={codeTop} offsetX={-1} />
      <Rect
        x={CARD_X + boxWidth / 2 - 10}
        y={codeTop + 58 + boxHeight / 2}
        width={boxWidth}
        height={boxHeight}
        radius={12}
        stroke={GREY_C}
        lineWidth={2}
      />
      {how.map((line, i) => {
        const indent = line.length - line.trimStart().length;
        return (
          <Txt
            key={`how-${i}`}
            text={line.trimEnd() || ' '}
            fontFamily={MONO}
            fontSize={TEXT_SIZE.code}
            fill={codeColor(line)}
            x={CARD_X + 24 + indent * 12}
            y={codeTop + 84 + i * codeLineH}
            offsetX={-1}
          />
        );
      })}
    </Node>,
  );
  yield* codeGroup().opacity(1, 0.35);
  yield* waitFor(2.0);

  yield* all(heading().opacity(0, 0.35), whyGroup().opacity(0, 0.35), codeGroup().opacity(0, 0.35));
}

export function* showTitleCard(view: any) {
  view.add(<Rect width={1920} height={1080} fill={BG} />);
  const title = createRef<Txt>();
  const sub = createRef<Txt>();
  view.add(
    <>
      <Txt ref={title} text="점프 디자인 — 물리가 아니라 손맛" fontFamily={FONT} fontSize={TEXT_SIZE.titleCard} fill={WHITE} x={0} y={-48} opacity={0} />
      <Txt
        ref={sub}
        text="같은 중력 법칙 안에서, 게임마다 점프를 다르게 설계하는 이유"
        fontFamily={FONT}
        fontSize={TEXT_SIZE.titleCardSub}
        fill={GREY_B}
        x={0}
        y={36}
        opacity={0}
      />
    </>,
  );
  yield* title().opacity(1, 0.7);
  yield* sub().opacity(1, 0.4);
  yield* waitFor(1.0);
  yield* all(title().opacity(0, 0.4), sub().opacity(0, 0.4));
}

export function* showEndCard(view: any) {
  const title = createRef<Txt>();
  const sub = createRef<Txt>();
  view.add(
    <>
      <Txt ref={title} text="점프 하나에도 이렇게 많은 설계가 숨어 있다" fontFamily={FONT} fontSize={TEXT_SIZE.endCard} fill={WHITE} x={0} y={-36} opacity={0} />
      <Txt
        ref={sub}
        text="examples/jump-physics-showcase — profiles.py에서 직접 값을 바꿔보세요"
        fontFamily={FONT}
        fontSize={TEXT_SIZE.endCardSub}
        fill={GREY_B}
        x={0}
        y={36}
        opacity={0}
      />
    </>,
  );
  yield* title().opacity(1, 0.5);
  yield* sub().opacity(1, 0.35);
  yield* waitFor(1.5);
  yield* all(title().opacity(0, 0.4), sub().opacity(0, 0.4));
}

export function addBackground(view: any) {
  view.add(<Rect width={1920} height={1080} fill={BG} />);
}
