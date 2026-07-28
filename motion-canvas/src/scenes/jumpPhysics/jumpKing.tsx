import {makeScene2D} from '@motion-canvas/2d';
import jumpKingSprite from '../../assets/jump-physics/jumpking.png';
import {EXPLANATIONS} from './explanations';
import {jumpKing} from './profiles';
import {addBackground, runJumpKing, showExplanation} from './shared';

export default makeScene2D(function* (view) {
  addBackground(view);
  const {profile, chargeState} = jumpKing();
  yield* runJumpKing(view, profile, chargeState, jumpKingSprite, {spriteWidth: 115, loops: 1});
  const e = EXPLANATIONS.jump_king;
  yield* showExplanation(view, '현대 게임 — 점프킹', e.why, e.how);
});
