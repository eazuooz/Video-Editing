// Narration segment 11 — 점프킹: charge while held, launch on release, no
// air control once airborne. First of three "modern take" examples.

import {makeScene2D} from '@motion-canvas/2d';
import jumpKingSprite from '../../assets/jump-physics/jumpking.png';
import {brollFor} from '../../broll';
import {SEGMENTS} from '../../narration';
import {jumpKing} from '../jumpPhysics/profiles';
import {addBackground, runJumpKing} from '../jumpPhysics/shared';

export default makeScene2D(function* (view) {
  addBackground(view);
  const {profile, chargeState} = jumpKing();
  yield* runJumpKing(view, profile, chargeState, jumpKingSprite, {
    spriteWidth: 115,
    duration: SEGMENTS.jumpKing.duration,
    broll: brollFor('jumpKing'),
  });
});
