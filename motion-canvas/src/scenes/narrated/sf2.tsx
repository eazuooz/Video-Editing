// Narration segment 08 — 스트리트 파이터 II 장기에프: same path, faster fall.

import {makeScene2D} from '@motion-canvas/2d';
import sf2Sprite from '../../assets/jump-physics/streetfighter2.png';
import {brollFor} from '../../broll';
import {SEGMENTS} from '../../narration';
import {sf2ScrewPiledriver} from '../jumpPhysics/profiles';
import {BLUE, RED, addBackground, runDualLeftAnchor} from '../jumpPhysics/shared';

export default makeScene2D(function* (view) {
  addBackground(view);
  const [vanilla, turbo] = sf2ScrewPiledriver();
  yield* runDualLeftAnchor(
    view,
    '스트리트 파이터 II — 장기에프 스크류 파일드라이버',
    '이동 경로(궤적)는 완전히 동일 — 속도 배분만 다르다',
    vanilla,
    turbo,
    BLUE,
    RED,
    '오리지널 (등속)',
    '터보 이후 (하강 가속)',
    {
      spriteSrc: sf2Sprite,
      spriteWidth: 80,
      duration: SEGMENTS.sf2.duration,
      broll: brollFor('sf2'),
    },
  );
});
