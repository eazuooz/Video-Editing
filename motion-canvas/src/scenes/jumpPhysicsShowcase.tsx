// Motion Canvas port of examples/jump-physics-showcase/scene.py's
// JumpPhysicsShowcase — all 10 segments back to back with title/end bookends,
// no explanation cards (those are only in the per-game scenes/jumpPhysics/*).

import {makeScene2D} from '@motion-canvas/2d';
import arthurSprite from '../assets/jump-physics/arthur.png';
import celesteSprite from '../assets/jump-physics/celeste.png';
import jumpKingSprite from '../assets/jump-physics/jumpking.png';
import marioSprite from '../assets/jump-physics/mario.png';
import megamanSprite from '../assets/jump-physics/megaman.png';
import metroidSprite from '../assets/jump-physics/metroid.png';
import sf2Sprite from '../assets/jump-physics/streetfighter2.png';
import smashSprite from '../assets/jump-physics/smash.png';
import {
  basicConcept,
  celestePair,
  ghostsNGoblins,
  jumpKing,
  mario,
  megamanXDashJump,
  metroid,
  sf2ScrewPiledriver,
  smashJumpSquat,
  smashUltimateSpecial,
} from './jumpPhysics/profiles';
import {
  BLUE,
  GREEN,
  ORANGE,
  PURPLE,
  RED,
  addBackground,
  runDualLeftAnchor,
  runDualSpatial,
  runJumpKing,
  runProfileLeftAnchor,
  showEndCard,
  showTitleCard,
} from './jumpPhysics/shared';

export default makeScene2D(function* (view) {
  yield* showTitleCard(view);
  addBackground(view);

  yield* runProfileLeftAnchor(view, basicConcept(), ORANGE, {loops: 2});
  yield* runProfileLeftAnchor(view, mario(), BLUE, {spriteSrc: marioSprite, spriteWidth: 110, loops: 3});
  yield* runProfileLeftAnchor(view, metroid(), GREEN, {spriteSrc: metroidSprite, spriteWidth: 130, loops: 2});
  yield* runProfileLeftAnchor(view, ghostsNGoblins(), ORANGE, {
    spriteSrc: arthurSprite,
    spriteWidth: 120,
    loops: 5,
    noAirControl: true,
  });

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
    {spriteSrc: sf2Sprite, spriteWidth: 80, loops: 3},
  );

  yield* runProfileLeftAnchor(view, smashJumpSquat(), PURPLE, {
    spriteSrc: smashSprite,
    spriteWidth: 120,
    loops: 3,
    squatMarker: 0.12,
  });
  yield* runProfileLeftAnchor(view, smashUltimateSpecial(), PURPLE, {spriteSrc: smashSprite, spriteWidth: 120, loops: 3});

  const {profile: jumpKingProfile, chargeState} = jumpKing();
  yield* runJumpKing(view, jumpKingProfile, chargeState, jumpKingSprite, {spriteWidth: 115, loops: 1});

  const [celesteFull, celesteCut] = celestePair();
  yield* runProfileLeftAnchor(view, celesteFull, GREEN, {spriteSrc: celesteSprite, spriteWidth: 120, loops: 2});
  yield* runProfileLeftAnchor(view, celesteCut, GREEN, {spriteSrc: celesteSprite, spriteWidth: 120, loops: 3});

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

  yield* showEndCard(view);
});
