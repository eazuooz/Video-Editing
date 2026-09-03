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
8. 게임 원음과 승인된 BGM을 낮은 음량으로 믹스합니다.
9. 무자막 본편과 언어별 SRT를 만들고 최종 청취 검수를 합니다.
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

## 관련 코드

- Motion Canvas: `motion-canvas/src/projects/{{SLUG}}`
- Manim: `manim/projects/{{SLUG}}`
- 생성 결과: `shared/output`
