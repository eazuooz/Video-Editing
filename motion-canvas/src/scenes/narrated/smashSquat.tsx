// Narration segment 09 — 스매시브라더스: the short jump-squat prep frames.

import {makeScene2D} from '@motion-canvas/2d';
import smashSprite from '../../assets/jump-physics/smash.png';
import {brollFor} from '../../broll';
import {SEGMENTS} from '../../narration';
import {smashJumpSquat} from '../jumpPhysics/profiles';
import {PURPLE, addBackground, runProfileLeftAnchor} from '../jumpPhysics/shared';

export default makeScene2D(function* (view) {
  addBackground(view);
  yield* runProfileLeftAnchor(view, smashJumpSquat(), PURPLE, {
    spriteSrc: smashSprite,
    spriteWidth: 120,
    squatMarker: 0.12,
    duration: SEGMENTS.smashSquat.duration,
    broll: brollFor('smashSquat'),
  });
});
