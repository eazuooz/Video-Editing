import {makeScene2D} from '@motion-canvas/2d';
import smashSprite from '../../assets/jump-physics/smash.png';
import {EXPLANATIONS} from './explanations';
import {smashUltimateSpecial} from './profiles';
import {PURPLE, addBackground, runProfileLeftAnchor, showExplanation} from './shared';

export default makeScene2D(function* (view) {
  addBackground(view);
  const profile = smashUltimateSpecial();
  yield* runProfileLeftAnchor(view, profile, PURPLE, {spriteSrc: smashSprite, spriteWidth: 120, loops: 3});
  const e = EXPLANATIONS.smash_ultimate;
  yield* showExplanation(view, '대난투 스매시브라더스 얼티밋', e.why, e.how);
});
