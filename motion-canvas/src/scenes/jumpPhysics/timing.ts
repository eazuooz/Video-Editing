// Timing constants shared by the jump-physics renderer.
//
// Kept apart from shared.tsx (which pulls in @motion-canvas/2d, and with it the
// DOM) so the narration sync check can import this math in plain Node.

import type {Profile} from './profiles';

/** Demo animations play at 85% speed -- slower is easier to follow. */
export const PLAYBACK_SPEED = 0.85;

// Fixed costs of the intro/outro beats every segment shares. They are named
// (rather than inlined) because the narration-synced scenes subtract them from
// their target duration to work out how long the jump loop itself may run.
export const HEADER_FADE = 0.35;
export const CAPTION_FADE = 0.25;
export const AXES_FADE = 0.35;
export const PRE_ROLL = 0.1;
export const POST_ROLL = 0.2;
export const FADE_OUT = 0.3;

export function introOverhead(hasCaption: boolean) {
  return HEADER_FADE + (hasCaption ? CAPTION_FADE : 0) + AXES_FADE + PRE_ROLL;
}

export const OUTRO_OVERHEAD = POST_ROLL + FADE_OUT;

/**
 * Shortest a narration-synced scene can be without overrunning its slot.
 *
 * `padTo` can only stretch a scene, never trim it, so a segment shorter than
 * this would push every later scene out of sync with the audio. Enforced by
 * `npm run check:narration`.
 */
export function minimumSceneSeconds(profile: Profile, hasCaption = Boolean(profile.caption)) {
  return introOverhead(hasCaption) + profile.total / PLAYBACK_SPEED + OUTRO_OVERHEAD;
}

/**
 * Decide how long the jump loop runs and how many cycles it completes.
 *
 * With an explicit `duration` (narration-synced mode) the loop stretches to
 * fill the segment, and the cycle count is rounded so the character always
 * lands on the ground exactly as the segment ends rather than being cut
 * mid-jump. Without one, the caller's `loops` drives the length as before.
 */
export function planPlayback(
  profile: Profile,
  opts: {duration?: number; loops?: number},
  hasCaption: boolean,
) {
  if (opts.duration === undefined) {
    const loops = opts.loops ?? 2;
    return {loops, animSeconds: (profile.total * loops) / PLAYBACK_SPEED};
  }
  const animSeconds = Math.max(
    profile.total / PLAYBACK_SPEED,
    opts.duration - introOverhead(hasCaption) - OUTRO_OVERHEAD,
  );
  const loops = Math.max(1, Math.round((animSeconds * PLAYBACK_SPEED) / profile.total));
  return {loops, animSeconds};
}
