# Jump Physics

게임의 점프 물리와 조작감을 비교하는 6분 13초 분량의 영상 프로젝트입니다.

- 상태: 완성
- 해상도: 1920×1080
- 프레임 레이트: 60fps
- 내레이션: Qwen3-TTS balanced, 한국어
- 영상 엔진: Motion Canvas + Manim

## 프로젝트 자료

| 종류 | 기준 파일 |
| --- | --- |
| 한국어 대본 | [script/narration.ko.json](script/narration.ko.json) |
| 초기 편집 계획 | [planning/legacy-edit-cues.md](planning/legacy-edit-cues.md) |
| 게임 영상 출처 | [sources/gameplay.md](sources/gameplay.md) |
| 한국어 게시 정보 | [publishing/youtube.ko.md](publishing/youtube.ko.md) |
| 영어 게시 정보 | [publishing/youtube.en.md](publishing/youtube.en.md) |
| 전체 파일 경로 | [project.json](project.json) |

## 실행 소스

- Motion Canvas 본편: `motion-canvas/src/narrated.ts`
- Motion Canvas 물리 씬: `motion-canvas/src/scenes/jumpPhysics`
- Motion Canvas 내레이션 씬: `motion-canvas/src/scenes/narrated`
- 게임 영상: `motion-canvas/src/assets/gameplay`
- Manim 완성 예제: `examples/jump-physics-showcase`

현재 완성본의 실행 경로는 기존 렌더 안정성을 위해 유지했습니다. 다음 영상부터는 생성 스크립트가 `motion-canvas/src/projects/<slug>`와 `manim/projects/<slug>`를 만듭니다.

## 최종 산출물

- 무자막 영상: `shared/output/motion-canvas/jump-physics-narrated.mp4`
- 고정 자막 영상: `shared/output/motion-canvas/jump-physics-narrated-subtitled.mp4`
- 한국어 SRT: `shared/output/narration/qwen3-balanced/jump-physics-qwen3-balanced.srt`
- 영어 SRT: `shared/output/narration/qwen3-balanced/jump-physics-qwen3-balanced.en.srt`
- 최종 음성: `shared/output/narration/qwen3-balanced/jump-physics-qwen3-balanced.wav`

## 다시 렌더링하기

```powershell
# 1. TTS와 한국어 SRT 생성
qwen3-tts/.venv/Scripts/python.exe qwen3-tts/render_narration.py --project jump-physics

# 2. 내레이션 타이밍을 Motion Canvas에 동기화
qwen3-tts/.venv/Scripts/python.exe qwen3-tts/build_motion_canvas_timing.py

# 3. 타이밍과 B-roll 슬롯 검사
npm run check:narration
npm run cues

# 4. Motion Canvas 편집기 실행
npm start
```

자동 렌더는 Vite 서버를 9100번 포트로 실행한 상태에서 `npm run render:auto`를 사용합니다.

## 완성 상태 확인

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-video-project.ps1 -Project jump-physics -Stage publish
```
