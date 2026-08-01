// Narration segment 10b — "결론: 정답은 없다".
//
// The closing lines argue there is no single correct jump: what matters is the
// judgement and feeling it creates, and the way to find it is to tweak initial
// velocity / gravity / air control / prep frames and play. So the recap overlays
// every profile's curve on one set of axes -- same physics, deliberately
// different shapes -- and then lands on the closing message.

import {Line, Node, Txt, makeScene2D} from '@motion-canvas/2d';
import {all, createRef, createSignal, linear, useTime, waitFor} from '@motion-canvas/core';
import {brollFor} from '../../broll';
import {SEGMENTS} from '../../narration';
import {COLORS, FONT, TEXT_SIZE} from '../../theme';
import {playBroll} from '../jumpPhysics/broll';
import {
  basicConcept,
  celestePair,
  ghostsNGoblins,
  mario,
  metroid,
  smashUltimateSpecial,
} from '../jumpPhysics/profiles';
import {addBackground, padTo} from '../jumpPhysics/shared';

const SEGMENT = SEGMENTS.outro;

const PLOT_LEFT = -700;
const PLOT_RIGHT = 700;
const PLOT_BOTTOM = 250;
const PLOT_TOP = -230;

const CURVES = [
  {profile: mario(), label: '마리오', color: COLORS.blue},
  {profile: metroid(), label: '메트로이드', color: COLORS.green},
  {profile: ghostsNGoblins(), label: '마계촌', color: COLORS.orange},
  {profile: smashUltimateSpecial(), label: '스매시 얼티밋', color: COLORS.purple},
  {profile: celestePair()[0], label: '셀레스트', color: COLORS.red},
  {profile: basicConcept(), label: '기본 포물선', color: COLORS.greyB},
];

const MAX_TIME = Math.max(...CURVES.map(entry => entry.profile.total));
const MAX_HEIGHT = Math.max(
  ...CURVES.map(entry => {
    let peak = 0;
    for (let i = 0; i <= 120; i++) {
      peak = Math.max(peak, entry.profile.height((entry.profile.total * i) / 120));
    }
    return peak;
  }),
);

function point(time: number, height: number): [number, number] {
  return [
    PLOT_LEFT + (time / MAX_TIME) * (PLOT_RIGHT - PLOT_LEFT),
    PLOT_BOTTOM - (height / MAX_HEIGHT) * (PLOT_BOTTOM - PLOT_TOP),
  ];
}

export default makeScene2D(function* (view) {
  addBackground(view);

  const heading = createRef<Txt>();
  const axes = createRef<Node>();
  const progress = createSignal(0);

  view.add(
    <Txt
      ref={heading}
      text="정답은 없다 — 어떤 감각을 원하는지가 먼저다"
      fontFamily={FONT}
      fontSize={TEXT_SIZE.title}
      fill={COLORS.white}
      y={-420}
      opacity={0}
    />,
  );

  view.add(
    <Node ref={axes} opacity={0}>
      <Line
        points={[point(0, 0), point(MAX_TIME, 0)]}
        stroke={COLORS.greyC}
        lineWidth={3}
      />
      <Line
        points={[point(0, 0), point(0, MAX_HEIGHT)]}
        stroke={COLORS.greyC}
        lineWidth={3}
      />
      <Txt
        text="높이"
        fontFamily={FONT}
        fontSize={TEXT_SIZE.tick}
        fill={COLORS.greyC}
        x={PLOT_LEFT - 46}
        y={PLOT_TOP - 4}
      />
      <Txt
        text="시간"
        fontFamily={FONT}
        fontSize={TEXT_SIZE.tick}
        fill={COLORS.greyC}
        x={PLOT_RIGHT + 40}
        y={PLOT_BOTTOM}
      />
    </Node>,
  );

  yield* all(heading().opacity(1, 0.6), axes().opacity(1, 0.5));

  // Draw all six curves at once, each ending where its own jump ends.
  const curveGroup = createRef<Node>();
  view.add(
    <Node ref={curveGroup}>
      {CURVES.map((entry, index) => (
        <Node key={entry.label}>
          <Line
            points={() => {
              const {profile} = entry;
              const span = profile.total * progress();
              const steps = 48;
              const pts: [number, number][] = [];
              for (let i = 0; i <= steps; i++) {
                const time = (span * i) / steps;
                pts.push(point(time, profile.height(time)));
              }
              return pts;
            }}
            stroke={entry.color}
            lineWidth={5}
            radius={8}
          />
          <Txt
            text={`● ${entry.label}`}
            fontFamily={FONT}
            fontSize={TEXT_SIZE.legend}
            fill={entry.color}
            x={PLOT_LEFT + 20 + (index % 3) * 300}
            y={PLOT_BOTTOM + 90 + Math.floor(index / 3) * 46}
            offsetX={-1}
          />
        </Node>
      ))}
    </Node>,
  );

  yield* progress(1, 3.2, linear);
  yield* waitFor(2.0);

  // Closing takeaway, held under the final narrated lines.
  const closing = createRef<Node>();
  view.add(
    <Node ref={closing} opacity={0}>
      <Txt
        text="초기 속도 · 중력 · 공중 조작 · 준비 프레임"
        fontFamily={FONT}
        fontSize={TEXT_SIZE.subtitle}
        fill={COLORS.yellow}
        y={PLOT_BOTTOM + 220}
      />
      <Txt
        text="조금씩 바꾸고 직접 플레이하며 원하는 손맛을 찾는다"
        fontFamily={FONT}
        fontSize={TEXT_SIZE.body}
        fill={COLORS.greyB}
        y={PLOT_BOTTOM + 284}
      />
    </Node>,
  );
  yield* closing().opacity(1, 0.6);

  // Prototype footage plays over the recap.
  const broll = brollFor('outro');
  if (broll) {
    yield* playBroll(view, broll);
  }

  // Hold the recap until the last narrated sentence is almost done, then fade
  // everything out so the video ends on the exact frame the audio does.
  const fadeOut = 0.8;
  yield* waitFor(Math.max(0, SEGMENT.duration - useTime() - fadeOut));
  yield* all(
    heading().opacity(0, fadeOut),
    axes().opacity(0, fadeOut),
    curveGroup().opacity(0, fadeOut),
    closing().opacity(0, fadeOut),
  );
  yield* padTo(SEGMENT.duration);
});
