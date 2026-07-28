import {makeScene2D} from '@motion-canvas/2d';
import celesteSprite from '../../assets/jump-physics/celeste.png';
import {EXPLANATIONS} from './explanations';
import {celestePair} from './profiles';
import {GREEN, addBackground, runProfileLeftAnchor, showExplanation} from './shared';

export default makeScene2D(function* (view) {
  addBackground(view);
  const [full, cut] = celestePair();
  yield* runProfileLeftAnchor(view, full, GREEN, {spriteSrc: celesteSprite, spriteWidth: 120, loops: 2});
  yield* runProfileLeftAnchor(view, cut, GREEN, {spriteSrc: celesteSprite, spriteWidth: 120, loops: 3});
  const e = EXPLANATIONS.celeste;
  yield* showExplanation(view, '현대 게임 — 셀레스트', e.why, e.how);
});
