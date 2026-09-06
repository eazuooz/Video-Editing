# {{TITLE_KO}}

- 프로젝트 ID: `{{SLUG}}`
- 생성일: {{CREATED_AT}}
- 상태: 기획 중

## 작업 순서

1. `planning/outline.md`에서 영상의 질문과 결론을 확정합니다.
2. `script/narration.ko.json`에 장면별 내레이션을 작성합니다.
3. `sources/SOURCES.md`에 사용할 자료의 출처와 라이선스를 기록합니다.
4. 짧은 TTS 샘플의 톤과 속도를 승인받습니다.
5. 1.7B 장면 단위 TTS, SRT, 타이밍과 전체 받아쓰기 검수를 만듭니다.
6. 대본과 같은 수의 독립 Motion Canvas 씬을 만들고, 실제 예시와 자체 설명 화면을 페어로 배치합니다.
7. 라이선스를 확인한 BGM 후보를 먼저 제시하고 사용자의 선택을 받습니다.
8. 승인된 내레이션은 유지하고 전체 연속 BGM 위에 게임 원음을 함께 믹스합니다.
9. 무자막 MP4와 편집기에 같은 전체 믹스를 연결하고 언어별 SRT·최종 청취 검수를 합니다.
10. `publishing/`의 제목, 설명, 챕터와 음악 출처를 완성합니다.

전체 절차는 저장소의 `docs/VIDEO_WORKFLOW.md`와
`docs/NARRATION_AUDIO_STANDARD.md`를 참고하세요.

## 기본 내레이션 명령

먼저 첫 장면 미리듣기를 생성합니다.

```powershell
qwen3-tts/.venv/Scripts/python.exe qwen3-tts/generate_sample.py `
  --project {{SLUG}} --scene 01
```

대본과 TTS 미리듣기가 승인된 뒤 전체 패키지를 생성합니다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File scripts/build-project-narration.ps1 -Project {{SLUG}}
```

음악은 이 단계에서 자동으로 섞이지 않습니다. `project.json`의
`audio.backgroundMusic.approvalStatus`는 곡을 선택할 때까지 `pending`으로 둡니다.

## 전체 믹스와 미리보기

`project.json`에는 2026-09-06 승인된 기본값인 내레이션 -16 LUFS, 게임 원음
-23 LUFS, BGM -28 LUFS와 가벼운 덕킹이 들어 있습니다. 곡 선택 후 파일 경로를
기록하고, 실제 타임라인에 맞춘 믹서에서 이 값을 사용합니다.
BGM은 처음부터 끝까지 이어지며 게임 원음 구간에도 함께 재생합니다.
겹칠 때 BGM만 3dB 낮추고, 곡 반복은 1초 크로스페이드로 연결합니다.

- 원본 TTS는 `paths.narration`에 보관하며 배경음 조정 때문에 다시 생성하지 않습니다.
- 전체 믹스는 `paths.audioMix`에 생성하고 `project.ts`의 `audio`에 연결합니다.
  처음 생성되는 무음 플레이스홀더·나레이션 전용 연결은 초안용입니다.
- MP4와 M4A를 함께 갱신하고, 개별 Video 재생만 음소거해 원음 중복을 막습니다.
- 각 씬의 배경 단독 트랙과 편집기 재생을 확인하고 `audio/mix-report.md`에 기록합니다.
- FPS 믹서는 20개 씬·6.5초 예시 구간용이므로 새 영상 길이에 맞춰 조정 후 사용합니다.

세부 수치와 재발 방지 규칙은 `docs/NARRATION_AUDIO_STANDARD.md`를 따릅니다.

## 관련 코드

- Motion Canvas: `motion-canvas/src/projects/{{SLUG}}`
- Manim: `manim/projects/{{SLUG}}`
- 생성 결과: `shared/output`
