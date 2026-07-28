import {makeScene2D} from '@motion-canvas/2d';
import metroidSprite from '../../assets/jump-physics/metroid.png';
import {EXPLANATIONS} from './explanations';
import {metroid} from './profiles';
import {GREEN, addBackground, runProfileLeftAnchor, showExplanation} from './shared';

export default makeScene2D(function* (view) {
  addBackground(view);
  const profile = metroid();
  yield* runProfileLeftAnchor(view, profile, GREEN, {spriteSrc: metroidSprite, spriteWidth: 130, loops: 2});
  const e = EXPLANATIONS.metroid;
  yield* showExplanation(view, '메트로이드', e.why, e.how);
});
