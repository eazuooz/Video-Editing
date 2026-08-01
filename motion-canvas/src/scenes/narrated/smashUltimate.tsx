// Narration segment 10a — 스매시브라더스 얼티밋: strong initial pop, then a few
// frames of very heavy gravity, then normal gravity.

import {makeScene2D} from '@motion-canvas/2d';
import smashSprite from '../../assets/jump-physics/smash.png';
import {brollFor} from '../../broll';
import {SEGMENTS} from '../../narration';
import {smashUltimateSpecial} from '../jumpPhysics/profiles';
import {PURPLE, addBackground, runProfileLeftAnchor} from '../jumpPhysics/shared';

export default makeScene2D(function* (view) {
  addBackground(view);
  yield* runProfileLeftAnchor(view, smashUltimateSpecial(), PURPLE, {
    spriteSrc: smashSprite,
    spriteWidth: 120,
    duration: SEGMENTS.smashUltimate.duration,
    broll: brollFor('smashUltimate'),
  });
});
