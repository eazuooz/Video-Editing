import {makeScene2D} from '@motion-canvas/2d';
import megamanSprite from '../../assets/jump-physics/megaman.png';
import {EXPLANATIONS} from './explanations';
import {megamanXDashJump} from './profiles';
import {BLUE, RED, addBackground, runDualSpatial, showExplanation} from './shared';

export default makeScene2D(function* (view) {
  addBackground(view);
  const [walk, dash] = megamanXDashJump();
  yield* runDualSpatial(
    view,
    '현대 게임 — 록맨 X: 걷기 점프 vs 대시 점프',
    '높이는 똑같이, 수평 속도만 이어받아 이동 거리가 크게 늘어난다',
    walk,
    dash,
    BLUE,
    RED,
    '걷기 점프',
    '대시 점프',
    {spriteSrc: megamanSprite, spriteWidth: 90, loops: 3},
  );
  const e = EXPLANATIONS.megaman;
  yield* showExplanation(view, '현대 게임 — 록맨 X 대시 점프', e.why, e.how);
});
