# Jump Physics Showcase

프레임마다 중력을 더하는 기본 원리부터, 게임마다 점프를 다르게 설계하는 이유까지
다루는 데모입니다. 캐릭터는 특정 게임 스프라이트 대신 캡슐(원통형 콜라이더)
하나로 통일해서, 어떤 게임이든 같은 시각 언어로 비교합니다.

10개 게임을 각각 **개별 영상**으로 뽑았고, 영상마다 데모 뒤에
"왜 이렇게 만들었나" + "어떻게 동작하는가(핵심 로직)" 설명 카드가 붙습니다.
전부 이어붙인 롱폼 버전(`jump_physics_showcase.mp4`)도 그대로 남아 있습니다.

## 영상 목록

| # | 파일 | 핵심 아이디어 |
|---|---|---|
| 01 | `01_basic_concept.mp4` | 매 프레임 일정한 중력을 속도에 더하는 것 뿐 |
| 02 | `02_mario.mp4` | 상승 중력 약하게 / 하강 중력 강하게 — 체공감 + 경쾌한 착지 |
| 03 | `03_metroid.mp4` | 상승·하강 모두 약하게 — 총알 조준을 위한 둥실둥실한 느낌 |
| 04 | `04_ghosts_n_goblins.mp4` | 낮은 점프 + 공중 좌우 조작 완전 불가 (궤적이 발판 순간 결정) |
| 05 | `05_street_fighter_zangief.mp4` | 궤적은 동일, 시간 배분만 바꿔 하강을 빠르게 — 손맛의 차이 |
| 06 | `06_smash_jump_squat.mp4` | 점프 스쿼트(준비 동작) — 스매시 공격과의 입력 구분 |
| 07 | `07_smash_ultimate.mp4` | 강한 초기 속도 + 순간적 고중력 → 일반 중력 전환 (입력 유예) |
| 08 | `08_jump_king.mp4` | 차지 시간에 비례한 파워, 발사 후 조작 불가 — 올인 설계 |
| 09 | `09_celeste.mp4` | 버튼 홀드 길이로 점프 높이 조절 + 조기 이탈 시 '점프 컷' |
| 10 | `10_megaman_x_dash.mp4` | 걷기 점프 vs 대시 점프 — 높이는 같고 이동 거리만 대폭 증가 |

각 항목의 정확한 "왜 / 어떻게" 문구는 [explanations.py](explanations.py)에
`profiles.py`의 물리 파라미터와 1:1로 매핑되어 있습니다.

## 파일

| 파일 | 설명 |
|---|---|
| `profiles.py` | 각 게임의 점프 물리(속도·중력·구간)를 정의하는 순수 함수 모음 |
| `explanations.py` | 각 점프별 "왜 이렇게 만들었나 / 어떻게 동작하는가" 텍스트 + 코드 |
| `scene.py` | Manim 씬 — `BaseJumpScene`(공용 렌더링) + 10개 개별 `SceneXX` 클래스 |
| `01_basic_concept.mp4` ~ `10_megaman_x_dash.mp4` | 게임별 개별 클립 (720p30) |
| `jump_physics_showcase.mp4` | 10개를 이어붙인 롱폼 버전 (약 105초) |

## 다시 렌더링하기

```powershell
cd d:/Github/VideoEditing

# 개별 영상 하나만
manim/.venv/Scripts/python.exe -m manim render -qm --media_dir "shared/output/manim" "examples/jump-physics-showcase/scene.py" Scene02Mario

# 10개 전부
manim/.venv/Scripts/python.exe -m manim render -qm --media_dir "shared/output/manim" "examples/jump-physics-showcase/scene.py" Scene01Basic Scene02Mario Scene03Metroid Scene04GhostsNGoblins Scene05StreetFighter Scene06SmashSquat Scene07SmashUltimate Scene08JumpKing Scene09Celeste Scene10MegaManDash

# 이어붙인 롱폼 버전
manim/.venv/Scripts/python.exe -m manim render -qm --media_dir "shared/output/manim" "examples/jump-physics-showcase/scene.py" JumpPhysicsShowcase
```

`profiles.py`의 각 함수(`mario()`, `metroid()`, `jump_king()` 등) 인자를 바꾸면
해당 영상의 느낌이 바로 달라집니다. 설명 문구를 바꾸려면 `explanations.py`의
`EXPLANATIONS` 딕셔너리를 수정하세요.

## 참고

원본 아이디어는 사쿠라이 마사히로(『대난투 스매시브라더스』 디렉터)의
"점프 디자인" 해설 영상에서 다룬 내용을 바탕으로, 현대 게임(점프킹·셀레스트·록맨 X)
사례를 추가해 확장했습니다.
