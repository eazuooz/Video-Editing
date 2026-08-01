// Narration segment 12 — 셀레스트: same initial velocity every time, but an
// early release applies a much stronger "cut" gravity, so hold length alone
// tunes jump height. The narration covers both the long-hold and early-release
// case in one breath, so this scene runs both demos back to back.

import {makeScene2D} from '@motion-canvas/2d';
import celesteSprite from '../../assets/jump-physics/celeste.png';
import {brollFor} from '../../broll';
import {SEGMENTS} from '../../narration';
import {brollEnd} from '../jumpPhysics/broll';
import {celestePair} from '../jumpPhysics/profiles';
import {GREEN, addBackground, runProfileLeftAnchor} from '../jumpPhysics/shared';
import {minimumSceneSeconds} from '../jumpPhysics/timing';

export default makeScene2D(function* (view) {
  addBackground(view);
  const [full, cut] = celestePair();
  const broll = brollFor('celeste');

  // `duration` is relative to when each call starts (see shared.tsx), so
  // chaining two calls here safely lands on the segment's total length as long
  // as the two shares add up to it. Split proportional to each profile's own
  // length, so the much shorter "cut" demo doesn't get an unfairly long, static
  // second half -- but the B-roll window is attached to the first demo, so its
  // share can never be clamped shorter than that window needs, no matter how
  // the split math or the narration timing shifts later.
  const total = SEGMENTS.celeste.duration;
  const rawFirstShare = total * (full.total / (full.total + cut.total));
  const firstShare = Math.max(rawFirstShare, brollEnd(broll) + 1, minimumSceneSeconds(full));

  yield* runProfileLeftAnchor(view, full, GREEN, {
    spriteSrc: celesteSprite,
    spriteWidth: 120,
    duration: firstShare,
    broll,
  });
  yield* runProfileLeftAnchor(view, cut, GREEN, {
    spriteSrc: celesteSprite,
    spriteWidth: 120,
    duration: total - firstShare,
  });
});
