// Narration segment 05 — 슈퍼 마리오브라더스: slow rise, fast fall.

import {makeScene2D} from '@motion-canvas/2d';
import marioSprite from '../../assets/jump-physics/mario.png';
import {brollFor} from '../../broll';
import {SEGMENTS} from '../../narration';
import {mario} from '../jumpPhysics/profiles';
import {BLUE, addBackground, runProfileLeftAnchor} from '../jumpPhysics/shared';

export default makeScene2D(function* (view) {
  addBackground(view);
  yield* runProfileLeftAnchor(view, mario(), BLUE, {
    spriteSrc: marioSprite,
    spriteWidth: 110,
    duration: SEGMENTS.mario.duration,
    broll: brollFor('mario'),
  });
});
