// Narration segment 04 — "지금까지는 Y축 이야기, X축 가로 이동은 다르다".
//
// Mega Man X's walk-jump vs dash-jump is the cleanest illustration of the point:
// identical vertical motion, different horizontal speed, so only the distance
// changes. Plotted in real space (x vs height) because that is the only view in
// which the two arcs actually differ.

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
    'X축 가로 이동 — 세로와 따로 계산된다',
    '체공 시간은 그대로, 수평 속도만 바꾸면 이동 거리만 달라진다',
    walk,
    dash,
    BLUE,
    RED,
    '느린 가로 속도',
    '빠른 가로 속도',
    {
      spriteSrc: megamanSprite,
      spriteWidth: 90,
      duration: SEGMENTS.axes.duration,
      broll: brollFor('axes'),
    },
  );
});
