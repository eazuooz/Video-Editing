# 버튼 하나로 얼마나 재미있게 만들 수 있을까? | 원버튼 게임 디자인

- 프로젝트 ID: `one-button-game-design`
- 생성일: 2026-09-29
- 상태: 대본 검토 및 무음 2.5D 디자인 샘플 완성 / 본편 제작 승인 대기

## 현재 확인할 파일

- 대본: `script/review.ko.md` — 7장, 한국어 내레이션 검토본
- 디자인 샘플: `preview/v2/one-button-concept-v2.mp4` — 24초, 무음·자체 도식만
- 편집 계획: `planning/timeline.plan.json` — 본문 임시240초, 실제 영상144초/설명96초 목표
- 자료 후보: `sources/footage-candidates.json` — 아직 권리/구간/실제 화면 확인 전
- 음악 후보: `audio/bgm-candidates.md` — 선택 대기

한국어·영어 JSON 대본은 같은 7장·같은 문장 수로 정리했습니다. 실제 SRT와 TTS는 아직 없습니다.
편집기 본문 씬은 자료 미확보 구간을 명시하는 시각 초안입니다. 무음 완성작이 아닙니다.
최종에는 원본 프로필·이름·뱃지를 유지하는 10초 회원 엔딩이 필요하며, 원본 이미지 확보 대기입니다.
공유된 텍스트 전용 엔딩은 이번 프로젝트에서 렌더하지 않습니다.

## 작업 순서

1. `planning/outline.md`에서 영상의 질문과 결론을 확정합니다.
2. `script/narration.ko.json`에 장면별 내레이션을 작성합니다.
3. `sources/SOURCES.md`에 사용할 자료의 출처와 라이선스를 기록합니다.
4. 짧은 TTS 샘플의 톤과 속도를 승인받습니다.
5. 1.7B 장면 단위 TTS, SRT, 타이밍과 전체 받아쓰기 검수를 만듭니다.
6. 대본과 같은 수의 독립 Motion Canvas 씬을 만들고, 실제 예시와 자체 설명 화면을 페어로 배치합니다.
7. 라이선스를 확인한 BGM 후보를 먼저 제시하고 사용자의 선택을 받습니다.
8. 승인된 내레이션은 유지하고 전체 연속 BGM 위에 게임 원음을 함께 믹스합니다.
9. 무자막 MP4·기본 한국어 박스 자막판·편집기에 같은 전체 믹스를 연결하고 언어별 SRT·최종 청취 검수를 합니다.
10. `publishing/`의 제목, 설명, 챕터와 음악 출처를 완성합니다.

전체 절차는 저장소의 `docs/VIDEO_WORKFLOW.md`와
`docs/NARRATION_AUDIO_STANDARD.md`를 참고하세요.

## 기본 내레이션 명령

먼저 첫 장면 미리듣기를 생성합니다.

```powershell
qwen3-tts/.venv/Scripts/python.exe qwen3-tts/generate_sample.py `
  --project one-button-game-design --scene 01
```

대본과 TTS 미리듣기가 승인된 뒤 전체 패키지를 생성합니다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File scripts/build-project-narration.ps1 -Project one-button-game-design
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
- 디자인 기본값은 `docs/VIDEO_VISUAL_STYLE.md`의 흰색 연구 발표형입니다. 공통 테마와 기본 씬에 반영되어 있습니다.
- 내레이션 자막 기본값은 `docs/CAPTION_STYLE.md`의 `boxed-white-forest-v1`입니다. 흰 사각 박스·검정 글자와 얇은 테두리·짙은 초록 하드 그림자, 1080p 기준 Noto Sans KR 500/48px·최대 두 줄을 사용합니다. 매니페스트 설정만으로 자동 표시되지는 않으므로 씬의 자막 레이어에 실측 타이밍을 연결합니다.
- 무자막 원본·한국어 자막판·KO/EN SRT를 별도 보관합니다. 모든 큐의 잘림과 게임 UI·하단 요약 겹침을 검사하고, 스타일 때문에 음성이나 영상 길이를 바꾸지 않습니다.
- 본편의 실제 게임·개발 영상:자체 설명은 **60:40 기본, 필요하면 62:38까지**입니다. 인트로·회원 엔딩은 제외하고 씬별 비율보다 본편 전체 흐름을 우선합니다. 설명은 2.5D 비교·화살표·강조 애니메이션 위주로 설계합니다.
- `editing.targetGameplayShare = 0.6`을 시작점으로 사용합니다. `exampleSeconds = 19.5`는 기획 참고값이며 고정 길이가 아닙니다. 템플릿의 준비 화면을 실제 허용 영상으로 교체하고 실측 구간을 편집 큐·믹서에 함께 반영해야 합니다.
- 내레이션은 실제 예시와 설명에 걸쳐 계속 이어집니다. 장면 앞에 예시 길이만큼 무음을 추가하지 않습니다. KO/EN SRT와 씬 타이밍을 함께 맞춥니다.
- 편집 완료 시 `actualGameplaySeconds`, `actualExplanationSeconds`, `actualGameplayShare`를 실측하여 기록하고 `rebuild.json`을 갱신합니다. 60:40 목표를 맞추려고 원본을 억지로 반복하거나 늦추지 않습니다.
- FPS 믹서는 과거 20개 씬·6.5초 예시 구간용이므로 새 영상에 그대로 쓰지 않습니다.

세부 수치와 재발 방지 규칙은 `docs/NARRATION_AUDIO_STANDARD.md`를 따릅니다.

## 관련 코드

- Motion Canvas: `motion-canvas/src/projects/one-button-game-design`
- Manim: `manim/projects/one-button-game-design`
- 생성 결과: `shared/output`
