// Narration segment 13 — 록맨 X: dash speed carries into the jump, so height
// and air time stay identical and only horizontal distance changes.

import {makeScene2D} from '@motion-canvas/2d';
import megamanSprite from '../../assets/jump-physics/megaman.png';
import {brollFor} from '../../broll';
import {SEGMENTS} from '../../narration';
import {megamanXDashJump} from '../jumpPhysics/profiles';
import {BLUE, RED, addBackground, runDualSpatial} from '../jumpPhysics/shared';

export default makeScene2D(function* (view) {
  addBackground(view);
  const [walk, dash] = megamanXDashJump();
  yield* runDualSpatial(
    view,
    '록맨 X — 대시 점프',
    '높이와 체공 시간은 똑같이, 수평 속도만 이어받아 이동 거리만 늘어난다',
    walk,
    dash,
    BLUE,
    RED,
    '걷기 점프',
    '대시 점프',
    {
      spriteSrc: megamanSprite,
      spriteWidth: 90,
      duration: SEGMENTS.megaman.duration,
      broll: brollFor('megaman'),
    },
  );
});
