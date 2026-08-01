// Narration segment 01 — "점프는 왜 중요한가".
//
// The narrator opens by arguing that a jump is not just "going up": it decides
// reach, risk, and how much control you keep mid-air. So this scene states the
// title, then puts three real games' jumps side by side on one ground line so
// the difference in height and hang time is visible while that point is made.

import {Img, Line, Node, Txt, makeScene2D} from '@motion-canvas/2d';
import {all, createRef, createSignal, linear, useTime, waitFor} from '@motion-canvas/core';
import arthurSprite from '../../assets/jump-physics/arthur.png';
import marioSprite from '../../assets/jump-physics/mario.png';
import metroidSprite from '../../assets/jump-physics/metroid.png';
import {brollFor} from '../../broll';
import {SEGMENTS} from '../../narration';
import {COLORS, FONT, TEXT_SIZE} from '../../theme';
import {playBroll} from '../jumpPhysics/broll';
import {ghostsNGoblins, mario, metroid} from '../jumpPhysics/profiles';
import {addBackground, padTo} from '../jumpPhysics/shared';

const SEGMENT = SEGMENTS.intro;

const GROUND_Y = 330;
const LANE_X = [-540, 0, 540];
const HEIGHT_SCALE = 118; // data-space height -> pixels

const CAST = [
  {profile: mario(), sprite: marioSprite, label: '슈퍼 마리오브라더스', note: '빠른 하강', color: COLORS.blue},
  {profile: metroid(), sprite: metroidSprite, label: '메트로이드', note: '긴 체공', color: COLORS.green},
  {profile: ghostsNGoblins(), sprite: arthurSprite, label: '마계촌', note: '공중 조작 없음', color: COLORS.orange},
];

export default makeScene2D(function* (view) {
  addBackground(view);

  const title = createRef<Txt>();
  const subtitle = createRef<Txt>();

  view.add(
    <>
      <Txt
        ref={title}
        text="점프 디자인 — 물리가 아니라 손맛"
        fontFamily={FONT}
        fontSize={TEXT_SIZE.titleCard}
        fill={COLORS.white}
        y={-60}
        opacity={0}
      />
      <Txt
        ref={subtitle}
        text="같은 중력 법칙 안에서, 게임마다 점프를 다르게 설계하는 이유"
        fontFamily={FONT}
        fontSize={TEXT_SIZE.subtitle}
        fill={COLORS.greyB}
        y={30}
        opacity={0}
      />
    </>,
  );

  yield* title().opacity(1, 0.8);
  yield* subtitle().opacity(1, 0.5);
  yield* waitFor(4.2);
  yield* all(title().opacity(0, 0.6), subtitle().opacity(0, 0.6));

  // --- three games, one ground line ------------------------------------

  const heading = createRef<Txt>();
  const stage = createRef<Node>();
  const t = createSignal(0);

  view.add(
    <Txt
      ref={heading}
      text="같은 장애물을 넘어도, 점프가 다르면 게임이 달라진다"
      fontFamily={FONT}
      fontSize={TEXT_SIZE.subtitle}
      fill={COLORS.text}
      y={-420}
      opacity={0}
    />,
  );

  view.add(
    <Node ref={stage} opacity={0}>
      <Line
        points={[[-820, GROUND_Y], [820, GROUND_Y]]}
        stroke={COLORS.greyC}
        lineWidth={4}
      />
      {CAST.map((entry, index) => {
        const x = LANE_X[index];
        const {profile} = entry;
        return (
          <Node key={entry.label}>
            <Img
              src={entry.sprite}
              width={120}
              x={x}
              y={() => GROUND_Y - profile.height(t()) * HEIGHT_SCALE}
            />
            <Txt
              text={entry.label}
              fontFamily={FONT}
              fontSize={TEXT_SIZE.legend}
              fill={entry.color}
              x={x}
              y={GROUND_Y + 60}
            />
            <Txt
              text={entry.note}
              fontFamily={FONT}
              fontSize={TEXT_SIZE.caption}
              fill={COLORS.greyC}
              x={x}
              y={GROUND_Y + 104}
            />
          </Node>
        );
      })}
    </Node>,
  );

  yield* all(heading().opacity(1, 0.5), stage().opacity(1, 0.5));

  // Keep every character jumping for whatever is left of the segment after the
  // title card, then clear the stage so the next scene starts on a clean frame.
  // Each profile has its own cycle length, so driving them all from one shared
  // clock is exactly the point: the hang-time differences show up on their own.
  const fadeOut = 0.5;
  const jumpSeconds = Math.max(1, SEGMENT.duration - useTime() - fadeOut);
  const slowest = Math.max(...CAST.map(entry => entry.profile.total));
  const cycles = Math.max(1, Math.round(jumpSeconds / slowest));

  // The montage plays over the comparison, which keeps running behind it.
  const broll = brollFor('intro');
  yield* all(
    t(slowest * cycles, jumpSeconds, linear),
    ...(broll ? [playBroll(view, broll)] : []),
  );

  yield* all(heading().opacity(0, fadeOut), stage().opacity(0, fadeOut));
  yield* padTo(SEGMENT.duration);
});
