# 영상 프로젝트

영상 한 편마다 `projects/<slug>` 폴더 하나를 사용합니다. 이 폴더에는 사람이 직접 관리하는 대본, 기획, 출처, 게시 정보를 모읍니다.

새 프로젝트는 기본적으로 Qwen3-TTS 1.7B 장면 단위 연속 발화와 독립 Motion
Canvas 씬을 사용합니다. 음악은 후보·라이선스를 먼저 확인하고 사용자가 승인한 뒤
게임 원음과 함께 최종 믹스합니다. 상세 기준은
[`docs/NARRATION_AUDIO_STANDARD.md`](../docs/NARRATION_AUDIO_STANDARD.md)에 있습니다.

실행 코드와 큰 생성 파일은 용도에 맞는 위치에 둡니다.

- Motion Canvas 코드: `motion-canvas/src/projects/<slug>`
- Manim 코드: `manim/projects/<slug>`
- 렌더·TTS 결과: `shared/output`
- 영상별 작업 허브: `projects/<slug>`

## 프로젝트 목록

| 프로젝트 | 상태 | 설명 |
| --- | --- | --- |
| [jump-physics](jump-physics/) | 완성 | 게임 점프 물리와 조작감 분석 |
| [frame-rate-modern-rendering](frame-rate-modern-rendering/) | BGM 승인·최종 믹스 대기 | 30/60/120 FPS부터 PS5·DLSS·Frame Generation까지 |

## 새 프로젝트 만들기

저장소 루트에서 다음 명령을 실행합니다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/new-video-project.ps1 `
  -Slug "next-video" `
  -TitleKo "다음 영상 제목" `
  -TitleEn "Next Video Title"
```

프로젝트 허브, Motion Canvas 시작 씬, Manim 시작 씬이 함께 생성됩니다. 전체 작업 순서는 [영상 제작 워크플로](../docs/VIDEO_WORKFLOW.md)를 참고하세요.

대본과 TTS 샘플 승인 뒤 내레이션 패키지를 생성합니다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File scripts/build-project-narration.ps1 -Project "next-video"
```
