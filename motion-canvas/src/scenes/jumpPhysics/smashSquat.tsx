import {makeScene2D} from '@motion-canvas/2d';
import smashSprite from '../../assets/jump-physics/smash.png';
import {EXPLANATIONS} from './explanations';
import {smashJumpSquat} from './profiles';
import {PURPLE, addBackground, runProfileLeftAnchor, showExplanation} from './shared';

export default makeScene2D(function* (view) {
  addBackground(view);
  const profile = smashJumpSquat();
  yield* runProfileLeftAnchor(view, profile, PURPLE, {
    spriteSrc: smashSprite,
    spriteWidth: 120,
    loops: 3,
    squatMarker: 0.12,
  });
  const e = EXPLANATIONS.smash_squat;
  yield* showExplanation(view, '대난투 스매시브라더스 — 점프 스쿼트', e.why, e.how);
});
