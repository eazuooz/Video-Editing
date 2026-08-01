// Narration segment 07 — 마계촌: low jump, landing spot locked at takeoff.

import {makeScene2D} from '@motion-canvas/2d';
import arthurSprite from '../../assets/jump-physics/arthur.png';
import {brollFor} from '../../broll';
import {SEGMENTS} from '../../narration';
import {ghostsNGoblins} from '../jumpPhysics/profiles';
import {ORANGE, addBackground, runProfileLeftAnchor} from '../jumpPhysics/shared';

export default makeScene2D(function* (view) {
  addBackground(view);
  yield* runProfileLeftAnchor(view, ghostsNGoblins(), ORANGE, {
    spriteSrc: arthurSprite,
    spriteWidth: 120,
    noAirControl: true,
    duration: SEGMENTS.ghosts.duration,
    broll: brollFor('ghosts'),
  });
});
