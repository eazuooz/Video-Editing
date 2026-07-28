import {makeScene2D} from '@motion-canvas/2d';
import arthurSprite from '../../assets/jump-physics/arthur.png';
import {EXPLANATIONS} from './explanations';
import {ghostsNGoblins} from './profiles';
import {ORANGE, addBackground, runProfileLeftAnchor, showExplanation} from './shared';

export default makeScene2D(function* (view) {
  addBackground(view);
  const profile = ghostsNGoblins();
  yield* runProfileLeftAnchor(view, profile, ORANGE, {
    spriteSrc: arthurSprite,
    spriteWidth: 120,
    loops: 5,
    noAirControl: true,
  });
  const e = EXPLANATIONS.ghosts_n_goblins;
  yield* showExplanation(view, '마계촌', e.why, e.how);
});
