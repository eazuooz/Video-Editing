// Narration segment 06 — 메트로이드: weak gravity both ways, floaty hang time.

import {makeScene2D} from '@motion-canvas/2d';
import metroidSprite from '../../assets/jump-physics/metroid.png';
import {brollFor} from '../../broll';
import {SEGMENTS} from '../../narration';
import {metroid} from '../jumpPhysics/profiles';
import {GREEN, addBackground, runProfileLeftAnchor} from '../jumpPhysics/shared';

export default makeScene2D(function* (view) {
  addBackground(view);
  yield* runProfileLeftAnchor(view, metroid(), GREEN, {
    spriteSrc: metroidSprite,
    spriteWidth: 130,
    duration: SEGMENTS.metroid.duration,
    broll: brollFor('metroid'),
  });
});
