# Mario Jump Physics — Real vs. Game Feel

같은 높이(H = 3.0)까지 뛰어오르는 두 점프를 나란히 비교하는 Manim 예제입니다.

- **Real physics** — 올라갈 때·내려갈 때 중력이 동일(`g = 7.0`)한 대칭 포물선
- **Game physics** — 올라갈 때 중력은 약하게(`g_up = 4.0`), 떨어질 때는 세게(`g_down = 11.0`)
  줘서 정점에서 살짝 더 머무르다(체공감) 빠르게 착지하는(경쾌한 손맛) 비대칭 점프

마리오/셀레스테류 플랫포머에서 흔히 쓰는 "낙하 중력 > 상승 중력" 기법을 그대로 수치화한 예제입니다.

## 파일

| 파일 | 설명 |
|---|---|
| `scene.py` | Manim 씬 소스 (`MarioJumpPhysics`) |
| `mario_sprite.png` | 배경 제거·크롭된 마리오 스프라이트 |
| `mario_jump_physics.mp4` | 렌더링된 최종 클립 (720p30) |

## 다시 렌더링하기

```powershell
cd d:/Github/VideoEditing
manim/.venv/Scripts/python.exe -m manim render -qm --media_dir "shared/output/manim" "examples/mario-jump-physics/scene.py" MarioJumpPhysics
```

결과는 `shared/output/manim/videos/scene/720p30/MarioJumpPhysics.mp4`에 생기며,
확정본을 이 폴더에 `mario_jump_physics.mp4`로 복사해 갱신합니다.

## 파라미터 바꿔보기

`scene.py` 상단의 `H`, `G_REAL`, `G_UP`, `G_DOWN` 값을 바꾸면 점프 높이/느낌이 달라집니다.
