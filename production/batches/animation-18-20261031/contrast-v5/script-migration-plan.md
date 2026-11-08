# 17편 대본–새 게임 예시 연결 검수

승인된 게임 목록을 기존 설명 흐름에 연결하는 제작용 표입니다. 아래 확인 항목은 **아직 확보되지 않은 영상에서 확인해야 할 조건**이며, 확인 완료를 뜻하지 않습니다.
A03은 보존합니다. 17편 한국어 전체 대본을 읽고, 게임 고유 표현 및 인접 연결문만 교체 대상으로 분리했습니다. 기존 유효한 설명·순서·음성은 유지합니다.

| 편 | 주제 | 연결 구간 | 현재 상태 |
|---|---|---:|---|
| A01 | 애니메이션 제작 지시 | 4 | 전체 대본 검수 완료 · 실제 새 컷 확인 후 문장 확정 |
| A02 | 동작의 과장 | 4 | 전체 대본 검수 완료 · 실제 새 컷 확인 후 문장 확정 |
| A04 | 빠르고 강한 준비 동작 | 4 | 전체 대본 검수 완료 · 실제 새 컷 확인 후 문장 확정 |
| A05 | 공격 자세 | 5 | 전체 대본 검수 완료 · 실제 새 컷 확인 후 문장 확정 |
| A06 | 공격 이후의 후속 동작 | 4 | 전체 대본 검수 완료 · 실제 새 컷 확인 후 문장 확정 |
| A07 | 정보 손실을 보완하는 과장 | 3 | 전체 대본 검수 완료 · 실제 새 컷 확인 후 문장 확정 |
| A08 | 포즈 만들기 | 6 | 전체 대본 검수 완료 · 실제 새 컷 확인 후 문장 확정 |
| A09 | 압축·크기 변화 | 5 | 전체 대본 검수 완료 · 실제 새 컷 확인 후 문장 확정 |
| A10 | 피격 애니메이션 | 3 | 전체 대본 검수 완료 · 실제 새 컷 확인 후 문장 확정 |
| A11 | 보간의 함정 | 5 | 전체 대본 검수 완료 · 실제 새 컷 확인 후 문장 확정 |
| A12 | 표정 애니메이션 | 3 | 전체 대본 검수 완료 · 실제 새 컷 확인 후 문장 확정 |
| A13 | 좌우 반전 애니메이션 | 5 | 전체 대본 검수 완료 · 실제 새 컷 확인 후 문장 확정 |
| A14 | 애니메이션 블렌딩 | 5 | 전체 대본 검수 완료 · 실제 새 컷 확인 후 문장 확정 |
| A15 | 손가락 표현 | 3 | 전체 대본 검수 완료 · 실제 새 컷 확인 후 문장 확정 |
| A16 | 공격 판정과 동작 설계 | 4 | 전체 대본 검수 완료 · 실제 새 컷 확인 후 문장 확정 |
| A17 | 스켈레톤의 표현 한계 | 4 | 전체 대본 검수 완료 · 실제 새 컷 확인 후 문장 확정 |
| A18 | 두 축 회전 | 5 | 전체 대본 검수 완료 · 실제 새 컷 확인 후 문장 확정 |

## 공통 적용

- 같은 조건을 비교하는 장면은 카메라·모델·시간을 고정하고 실제 입력 하나만 변경합니다.
- 시간 단계 비교는 같은 동작의 서로 다른 순간임을 표시합니다. 같은 영상을 색만 바꿔 개선 전후로 부르지 않습니다.
- 실제 게임은 원속도와 행동 전→행동→결과를 먼저 보여 주고, 설명 중 같은 순간을 천천히 되짚습니다.
- 공격의 단계뿐 아니라 표정·손가락·시선·변형은 각 주제에 맞는 상태를 한 화면에서 연결합니다.
- 게임 고유 이름과 관찰 문장은 새 영상 검수 후 TTS를 생성합니다. 원문 핵심을 빼고 영상에 맞춰 내용을 축소하지 않습니다.

## A01 · 애니메이션 제작 지시

- `001–002`: Immediate observable action introduces concrete production instructions → **Sifu**
  - 확인할 장면: Female protagonist avoids an attack and responds; record body direction, planted foot and distance.
- `049–054`: Two bodies must agree in position and timing → **Pikmin 4**
  - 확인할 장면: Rider approaches, boards Oatchi, and remains in contact during motion. Explain cooperative contact rather than claiming a grab/throw.
- `055–059`: Weapon and prop clearance are part of the pose brief → **Sifu**
  - 확인할 장면: A weapon-bearing action with visible hand, weapon size and path. Do not remove this core weapon-role explanation if footage is unavailable.
- `068–073`: Non-human body needs a different instruction method → **Untitled Goose Game**
  - 확인할 장면: Beak lowers, grasps and transports one object; preserve neck/beak target explanation.

## A02 · 동작의 과장

- `013–017`: Anticipation and peak pose create visible movement amplitude → **The King of Fighters XIII / Kula**
  - 확인할 장면: Retain verified Kula upward attack and landing; exact same action normal then slow.
- `022–027`: Leg and torso jointly communicate attack direction → **Tekken 8 / Lili**
  - 확인할 장면: Retain verified consecutive kicks with body line and foot height.
- `028–034`: Exaggeration must survive actual gameplay screen size → **Splatoon 3 / Dynamo Roller**
  - 확인할 장면: Observe full-body windup and overhead swing, ink action and reset. Do not claim internal shoulder translation or proprietary rig settings.
- `053–057`: Awkward isolated twist can connect useful motion → **The King of Fighters XIII / Kula**
  - 확인할 장면: Retain verified airborne spin into low slide.

보존할 핵심: The shoulder-translation and 1.8x amplitude claims require actual changed rig conditions, not a colored copy, a larger picture or a separate motion.

## A04 · 빠르고 강한 준비 동작

- `001–005`: First visible signal precedes attack contact → **Hades II / Melinoe Moonstone Axe**
  - 확인할 장면: Show windup and release in one continuous independent clip; name exact weapon.
- `011–017`: Hold a readable preparation pose for a heavy action → **Hades II / Melinoe Moonstone Axe**
  - 확인할 장면: Record stance, weapon lift and release; no imported Wilds/greatsword statements.
- `026–031`: Rapid repeat action requires a different preparation budget → **Super Smash Bros. Ultimate / Zero Suit Samus + Cuphead Peashooter**
  - 확인할 장면: Verify ZSS first-jab frame-data primary evidence separately from video. Compare continuous firing without assigning jab hitbox frame data to Cuphead.
- `035–041`: Choose preparation for both actor and observer; reconnect to opening → **Hades II / Melinoe Moonstone Axe**
  - 확인할 장면: Reuse the same observed heavy attack context, with readable start and result.

보존할 핵심: Retain the reference rapid-jab distinction. Verify the one-frame ZSS claim independently; it is startup/active data, not end-to-end input latency.

## A05 · 공격 자세

- `001–006`: Impact pose persists through brief hit stop → **Hi-Fi RUSH / Chai**
  - 확인할 장면: Guitar Beat Hit with visible contact and pose; do not substitute a music timing judgement for hit-stop evidence.
- `012–015`: Pose should read at actual gameplay size → **Princess Peach: Showtime! / Swordfighter Peach**
  - 확인할 장면: Show sword arm and support leg at native camera size.
- `021–025`: Asymmetry gives limbs different jobs; symmetry may be intentional → **Hi-Fi RUSH + Princess Peach: Showtime!**
  - 확인할 장면: Use actual pose silhouettes and neutral demonstration for intended symmetric exception if no approved game cut demonstrates it.
- `026–030`: Choose a strong contact pose and stop timing → **Hi-Fi RUSH / Chai**
  - 확인할 장면: Inspect exact contact/held frame; keep early-versus-full-extension UE comparison.
- `039–042`: Return to the opening attack and assess direction/support → **Hi-Fi RUSH / Chai**
  - 확인할 장면: Return to the same observed guitar strike, not the removed Lili kick.

## A06 · 공격 이후의 후속 동작

- `001–004`: After-contact movement carries perceived weight → **Monster Hunter: World / Hammer**
  - 확인할 장면: Identify World or Iceborne version; inspect hammer swing and recovery.
- `026–032`: Jab, broad swing and projectile leave different follow-through → **Street Fighter 6 / Marisa + Monster Hunter: World / Hammer and Heavy Bowgun**
  - 확인할 장면: Record three distinct actions and native duration; game-specific hitbox/cancel data remain unknown unless verified.
- `039–047`: Recovery preserves direction rather than merely returning to idle → **Mario Tennis Aces / Daisy**
  - 확인할 장면: Forehand contact then racket/body follow-through; do not describe game input lock from pixels.
- `048–055`: Visual recovery and control recovery are separate choices → **Street Fighter 6 / Marisa**
  - 확인할 장면: Use actual jab/Gladius recovery as visual observation; own demo carries measured cancel values.

## A07 · 정보 손실을 보완하는 과장

- `001–008`: Large emotional gestures compensate for lost cues → **Clock Tower 3 / Alyssa**
  - 확인할 장면: Retain independently recorded Alyssa body/face motions.
- `029–035`: Camera size and available detail change readability → **Luigi's Mansion 3**
  - 확인할 장면: Compare close and normal camera gestures without implying these are controlled one-variable engine captures.
- `036–046`: Choose exaggeration for action and style → **Spiritfarer / Stella**
  - 확인할 장면: Observe clear noncombat body gesture such as hugging or interacting; replace incidental sword/fighting language while preserving body anticipation/action/recovery logic.

## A08 · 포즈 만들기

- `001–004`: Readable stance begins with purpose and support → **Clair Obscur: Expedition 33 / Maelle**
  - 확인할 장면: Spoiler-light stance or early weapon motion; no high kick claim without a matching cut.
- `018–026`: Head and torso orientation need not be identical → **Clair Obscur: Expedition 33 / Maelle**
  - 확인할 장면: Verify face/torso/hand relationship; remove tea-cup claim from Lili.
- `033–038`: Cloth follows and clarifies body flow → **Hades II / Melinoe**
  - 확인할 장면: Observe garment outline during an actual turn; do not assert simulation internals.
- `039–048`: Shoulder, arm silhouette and wrist continue the intended pose → **Ring Fit Adventure / Warrior II**
  - 확인할 장면: Arms and hands separate from torso in a held controlled pose.
- `049–056`: Support leg and feet establish stance → **Ring Fit Adventure / Warrior II**
  - 확인할 장면: Readable bent front knee, rear support and feet; guides are editorial not measured mass centre.
- `064–067`: Read the whole pose again at small size → **Clair Obscur: Expedition 33 / Maelle**
  - 확인할 장면: Return to opening stance, not removed Lili example.

보존할 핵심: Preserve cumulative editing of ONE pose. Existing real-clips-v2 dance/wave motions cannot stand in for incremental pose corrections. Use actual editable series-v1 Manny pose states with fixed model/camera/light.

## A09 · 압축·크기 변화

- `001–003`: Flattened contact shape differs from movement alone → **Kirby's Dream Land / Game Boy**
  - 확인할 장면: Keep verified landing; preserve original retro aspect in genuine FHD capture.
- `009–010`: Rotation/perspective differs from actual shape deformation → **Slime Rancher 2 / Pink Slime**
  - 확인할 장면: Use same object rotation or own transform illustration if actual comparison cannot isolate causes.
- `013–024`: Squash/stretch conveys contact and perceived volume → **Slime Rancher 2 / Pink Slime + Kirby's Dream Land**
  - 확인할 장면: Observe contact flattening and rise; do not infer hidden 3D volume from 2D footage.
- `032–042`: Authored contour differs from uniform scale → **Cuphead / Goopy Le Grande**
  - 확인할 장면: Goopy landing/rebound contour replaces removed Cala Maria mouth example.
- `054–060`: Impact emphasis and material deformation have different purposes → **Cuphead / Goopy Le Grande**
  - 확인할 장면: Observe expanding punch if available; otherwise preserve own fist illustration and describe it as ours.

보존할 핵심: 2D area, 3D volume and physical mass remain distinct. A picture does not establish the hidden deformation algorithm.

## A10 · 피격 애니메이션

- `001–004`: Hit reaction communicates contact before numerical UI → **Street Fighter 6 / Juri**
  - 확인할 장면: A clean received strike, limb silhouette change and recovery; avoid substituting attacking pose.
- `040–050`: Hit height, strength and knockback require different responses → **Street Fighter 6 / Juri**
  - 확인할 장면: Distinct received strikes shown with correct positions; own 3x3 grid carries authored values.
- `051–058`: Different body proportions need adapted reactions → **Super Mario Odyssey**
  - 확인할 장면: Actual Mario damage rather than opening cutscene; compare visible proportions without claiming same animation file or rig.

## A11 · 보간의 함정

- `001–004`: Key-pose timing changes sharpness → **Guilty Gear Xrd -SIGN- / Millia**
  - 확인할 장면: Find named -SIGN- action, inspect holds and transitions; technical claims cite developer GDC separately.
- `014–016`: 2D pose rhythm is not equivalent to smooth 3D interpolation → **Dead Cells**
  - 확인할 장면: Read distinct action poses at native speed; no assertion of internal interpolation from output alone.
- `021–024`: Equal total duration can allocate time differently → **Guilty Gear Xrd -SIGN- / Millia**
  - 확인할 장면: Return to observed action; own matched-pose demo proves controlled timing.
- `038–044`: Strong pose and recovery cannot be recreated just by reversing → **Paper Mario: The Thousand-Year Door (2024)**
  - 확인할 장면: Readable hammer/spring action and return; maintain specialist uppercut example in own demonstration.
- `055–062`: Outgoing and returning paths serve different roles → **Paper Mario: The Thousand-Year Door (2024)**
  - 확인할 장면: Same hammer action; inspect windup/contact/return, no imported greatsword claim.

## A12 · 표정 애니메이션

- `001–003`: Small face uses readable changes → **Animal Crossing: New Horizons**
  - 확인할 장면: Retain verified blink, add actual reactions if available.
- `036–040`: Quiet close-up and stylized small face need different ranges → **Clair Obscur: Expedition 33 / Maelle and Lune**
  - 확인할 장면: Early spoiler-light conversation, facial detail visible, no story plot or dialogue audio needed.
- `041–046`: Character identity can limit facial range → **Animal Crossing: New Horizons**
  - 확인할 장면: Observe body/face support; do not claim an unobserved robot or internal rig as the actual game.

## A13 · 좌우 반전 애니메이션

- `009–019`: 2D sprites can flip; rotation and mirroring differ → **Super Street Fighter II / Dee Jay**
  - 확인할 장면: Both facing directions with actual mirrored stance/sprites.
- `020–028`: 3D stance/hand/prop considerations → **Super Street Fighter IV / Dee Jay**
  - 확인할 장면: Correct same-character edition. Keep asymmetric shield/weapon issue in own demo rather than add Zelda outside roster.
- `029–039`: Actual play camera determines visibility → **Super Mario Bros. Wonder**
  - 확인할 장면: Both directions, actual model/camera observation. Do not assert hidden offscreen rotation without developer evidence.
- `040–047`: Clothing text shape may be chosen for mirroring → **Super Street Fighter II / Dee Jay**
  - 확인할 장면: Observe MAXIMUM on pants; developer evidence for design intention, not deduction alone.
- `050–051`: Return to facing-direction readability → **Super Street Fighter II / Dee Jay**
  - 확인할 장면: Revisit same character with face, forward hand and feet.

보존할 핵심: Reference-specific Dee Jay/MAXIMUM example must be supported; a different arbitrary mirrored game cannot replace its design lesson.

## A14 · 애니메이션 블렌딩

- `001–003`: Combine next input with residual pose → **Horizon Zero Dawn / Aloy**
  - 확인할 장면: Bow-to-run or aim-while-moving clip; visible before/action/result.
- `012–020`: Different preceding state affects transition into movement → **Horizon Zero Dawn / Aloy**
  - 확인할 장면: Same character moving from idle and an action; internal blend weights remain own implementation.
- `037–044`: Direction and magnitude can combine poses → **EA Sports FC 25 / same player**
  - 확인할 장면: Single player changes direction/pace; no claimed blend-space internals from video.
- `045–055`: Upper body, locomotion and ground conditions combine → **Splatoon 3**
  - 확인할 장면: Move and aim/fire, then traverse slope/stairs; own rig proves foot placement enabled/disabled.
- `059–061`: Return to action-to-locomotion connection → **Horizon Zero Dawn / Aloy**
  - 확인할 장면: Use same opening context.

## A15 · 손가락 표현

- `001–002`: Grip changes with object → **Half-Life: Alyx**
  - 확인할 장면: Verified bottle pickup with thumb/fingers visible; another object if clearly different grip.
- `028–036`: Cost should follow screen importance, not hardware comparison → **Half-Life: Alyx + Nintendo Switch Sports**
  - 확인할 장면: Alyx close hands, Switch Sports hands at native play size; if fingers unreadable use only scale/prioritization observation.
- `045–047`: Spend effort where hands carry gameplay meaning → **Ghostwire: Tokyo / Akito**
  - 확인할 장면: Read distinct spell hand shapes; do not claim measured GPU costs or continuous finger articulation from footage alone.

보존할 핵심: Do not infer processing cost or hand rig implementation from the appearance of two games. Switch Sports is conditional on observed hand legibility.

## A16 · 공격 판정과 동작 설계

- `001–003`: Visible weapon and hit result should agree → **Monster Hunter: World / Long Sword and Lance**
  - 확인할 장면: Verify exact edition; contrast sweep and thrust as observed paths.
- `012–027`: Path, apparent overlap and attack region are different → **Elden Ring**
  - 확인할 장면: An observable hit/miss pair; any boxes are editorial or own-demo values unless actual debug data exists.
- `028–038`: Active time and impact pose interact → **Metroid Dread**
  - 확인할 장면: Readable counter timing and result; no invented active frame counts.
- `041–044`: Return to weapon path plus result → **Monster Hunter: World / Long Sword and Lance**
  - 확인할 장면: Return to initial observed actions.

보존할 핵심: Editorial boxes are not measured commercial hitboxes. Preserve both play-view and simultaneous top/observer-view controlled implementation.

## A17 · 스켈레톤의 표현 한계

- `001–003`: Expressive silhouette can exceed ordinary arm proportions → **ARMS / Helix and Ribbon Girl**
  - 확인할 장면: Visible extending/curving arms; no inference of rig construction.
- `012–014`: FK illustration versus observable end position → **ARMS / Ribbon Girl**
  - 확인할 장면: Actual hand/arm path, while FK explanation is our rig only.
- `022–028`: Bending and target control can constrain pose → **Cuphead / Cala Maria**
  - 확인할 장면: Retain actual arm contour; explicitly hypothetical translation to joint rig.
- `032–044`: More controls may allow shape changes but need design → **ARMS / Helix**
  - 확인할 장면: Observable stretch/contour; complexity, joint count and cost shown only in our controlled demo.

보존할 핵심: FK, IK target, elbow hint, rotation constraint and skinning failure are distinct. Additional joints do not prove linear runtime cost.

## A18 · 두 축 회전

- `001–003`: Same goal can have different head/body paths → **Untitled Goose Game + Luigi's Mansion 3**
  - 확인할 장면: Retain verified goose movement, Luigi look-around replaces Alyssa.
- `018–029`: Change path while preserving end orientation → **Luigi's Mansion 3**
  - 확인할 장면: Head dip/turn visible; fixed angle claims belong only to own demonstration.
- `030–039`: Rotation and translation of connected parts differ → **The Last Guardian / boy and Trico**
  - 확인할 장면: Boy reaching/handling or Trico head/body sequence; keep wrist/shoulder procedural demo if no exact hand action.
- `040–055`: Different axes and body parts can start at different times → **Untitled Goose Game + Luigi's Mansion 3**
  - 확인할 장면: Visible neck/torso sequence; existing curves are own implementation, not extracted game engine values.
- `062–070`: Eye direction reduces required head motion → **The Last Guardian / Trico**
  - 확인할 장면: Clear target-facing eyes and head; do not describe eye intent from an unreadable frame.

보존할 핵심: Keep endpoint orientation fixed in controlled comparisons; eye aim and head rotation must be shown separately with the same target.
