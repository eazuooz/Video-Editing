// Gameplay B-roll slots for the narrated cut.
//
// Motion Canvas can composite the real footage itself, so there is no need to
// take the video into an external editor: drop a file at
// src/assets/gameplay/<clip>.(mp4|webm|mov) and it is picked up automatically by
// the glob below. Until then the slot renders a placeholder slate with the same
// geometry, so filling it in later never moves anything.

import {Node, Rect, Txt, Video} from '@motion-canvas/2d';
import {all, createRef, useTime, waitFor} from '@motion-canvas/core';
import {type BrollWindow, absoluteEnd, absoluteStart, timecode} from '../../broll';
import {COLORS, FONT, MONO, TEXT_SIZE} from '../../theme';

// Whatever gameplay files happen to exist right now. A glob (rather than static
// imports) is what lets a missing clip be a placeholder instead of a build
// error, and lets new footage register without touching any code.
const CLIPS = import.meta.glob('../../assets/gameplay/*.{mp4,webm,mov}', {
  eager: true,
  query: '?url',
  import: 'default',
}) as Record<string, string>;

function findClip(name: string): string | undefined {
  const match = Object.entries(CLIPS).find(([path]) => {
    const file = path.split('/').pop() ?? '';
    return file.replace(/\.[^.]+$/, '') === name;
  });
  return match?.[1];
}

// 16:9 stage, sized to leave the scene title readable above it.
const STAGE_WIDTH = 1420;
const STAGE_HEIGHT = 799;
const STAGE_Y = 80;

const FADE = 0.4;

/**
 * The B-roll stage: real footage when the clip exists, a labelled slate when it
 * does not. Starts hidden; {@link playBroll} fades it in and out.
 */
export function brollStage(window: BrollWindow) {
  const src = findClip(window.clip);
  const range = `${timecode(absoluteStart(window))} – ${timecode(absoluteEnd(window))}`;

  return (
    <Node opacity={0}>
      {/* Opaque backing so the physics graph never shows through the footage. */}
      <Rect
        width={1920}
        height={1080}
        fill={COLORS.bg}
      />
      {src ? (
        <>
          <Video
            src={src}
            width={STAGE_WIDTH}
            height={STAGE_HEIGHT}
            y={STAGE_Y}
            radius={18}
            play
            loop
          />
          <Txt
            text={window.label}
            fontFamily={FONT}
            fontSize={TEXT_SIZE.caption}
            fill={COLORS.greyC}
            y={STAGE_Y + STAGE_HEIGHT / 2 + 42}
          />
        </>
      ) : (
        <>
          <Rect
            width={STAGE_WIDTH}
            height={STAGE_HEIGHT}
            y={STAGE_Y}
            radius={18}
            fill={'#141926'}
            stroke={COLORS.greyC}
            lineWidth={4}
            lineDash={[18, 14]}
          />
          <Txt
            text="게임 영상 자리"
            fontFamily={FONT}
            fontSize={TEXT_SIZE.accentLabel}
            fill={COLORS.yellow}
            y={STAGE_Y - 150}
          />
          <Txt
            text={window.label}
            fontFamily={FONT}
            fontSize={TEXT_SIZE.subtitle}
            fill={COLORS.white}
            y={STAGE_Y - 60}
          />
          <Txt
            text={window.hint}
            fontFamily={FONT}
            fontSize={TEXT_SIZE.body}
            fill={COLORS.greyB}
            y={STAGE_Y + 20}
          />
          <Txt
            text={`${range}   (${window.duration.toFixed(1)}초)`}
            fontFamily={MONO}
            fontSize={TEXT_SIZE.body}
            fill={COLORS.greyC}
            y={STAGE_Y + 110}
          />
          <Txt
            text={`src/assets/gameplay/${window.clip}.mp4`}
            fontFamily={MONO}
            fontSize={TEXT_SIZE.caption}
            fill={COLORS.codeBlue}
            y={STAGE_Y + 180}
          />
        </>
      )}
    </Node>
  );
}

/**
 * Hold the B-roll stage on screen for its window.
 *
 * Run this in parallel with the scene's own animation (`all(tween, playBroll())`)
 * -- the graph keeps advancing underneath, so the segment still ends with the
 * character on the ground even though the footage covered the middle of it.
 */
export function* playBroll(view: any, window: BrollWindow) {
  const stage = createRef<Node>();
  view.add(<Node ref={stage}>{brollStage(window)}</Node>);

  // `offset` is measured from the start of the scene, and some of that time has
  // already been spent fading the header and axes in.
  yield* waitFor(Math.max(0, window.offset - useTime()));
  const inner = stage().children()[0];
  yield* inner.opacity(1, FADE);
  yield* waitFor(Math.max(0, window.duration - FADE * 2));
  yield* inner.opacity(0, FADE);
  stage().remove();
}

/** Seconds from scene start until the B-roll window is finished. */
export function brollEnd(window: BrollWindow | undefined): number {
  return window ? window.offset + window.duration : 0;
}
