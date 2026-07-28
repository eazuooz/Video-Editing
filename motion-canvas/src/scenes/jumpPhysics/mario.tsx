import {makeScene2D} from '@motion-canvas/2d';
import marioSprite from '../../assets/jump-physics/mario.png';
import {EXPLANATIONS} from './explanations';
import {mario} from './profiles';
import {BLUE, addBackground, runProfileLeftAnchor, showExplanation} from './shared';

export default makeScene2D(function* (view) {
  addBackground(view);
  const profile = mario();
  yield* runProfileLeftAnchor(view, profile, BLUE, {spriteSrc: marioSprite, spriteWidth: 110, loops: 3});
  const e = EXPLANATIONS.mario;
  yield* showExplanation(view, '슈퍼 마리오브라더스', e.why, e.how);
});
