# 게임의 프레임 레이트는 무엇일까? 30 FPS부터 DLSS까지

- 프로젝트 ID: `frame-rate-modern-rendering`
- 생성일: 2026-09-02
- 상태: 새 내레이션 완료, 최종 오디오 믹스 대기

- 새 내레이션 기준 길이: 약 7분 26초
- 해상도: 1920×1080
- 프레임 레이트: 60fps
- 내레이션: Qwen3-TTS 1.7B balanced v2, 한국어, 장면 단위 연속 발화
- 화면: 20개 독립 씬, 실제 게임 예시와 자체 제작 2D 모션그래픽의 페어 구성
- 장면 리듬: 실제 게임·공식 기술 영상 6.5초 → 같은 개념의 채널 모션그래픽
- 예시 캐릭터: 픽셀 액션 게임 캐릭터 이미지

## 최종 결과물

- 기존 무자막 본편(오디오 재믹스 전): `shared/output/motion-canvas/frame-rate-modern-rendering.mp4`
- 한국어 음성: `shared/output/narration/frame-rate-modern-rendering/qwen3-1.7b-balanced-v2/frame-rate-modern-rendering-qwen3-1.7b-balanced-v2.wav`
- 한국어 SRT: `shared/output/narration/frame-rate-modern-rendering/qwen3-1.7b-balanced-v2/frame-rate-modern-rendering-qwen3-1.7b-balanced-v2.srt`
- 영어 SRT: `shared/output/narration/frame-rate-modern-rendering/qwen3-1.7b-balanced-v2/frame-rate-modern-rendering-qwen3-1.7b-balanced-v2.en.srt`

## 반복 제작·렌더

```powershell
# 기준 음성의 정확한 발화문 추출(기준 음성을 바꿀 때만)
qwen3-tts/.venv/Scripts/python.exe qwen3-tts/transcribe_reference.py `
  shared/voice-reference/reference-15-35s.wav

# 1.7B 장면 단위 TTS, 한국어 SRT와 타이밍 JSON 생성
qwen3-tts/.venv/Scripts/python.exe qwen3-tts/render_narration.py `
  --project frame-rate-modern-rendering --batch-size 1

# 한국어·영어 SRT와 20개 Motion Canvas 씬 타이밍 동기화
qwen3-tts/.venv/Scripts/python.exe qwen3-tts/build_translated_srt.py `
  --project frame-rate-modern-rendering --language ko
qwen3-tts/.venv/Scripts/python.exe qwen3-tts/build_translated_srt.py `
  --project frame-rate-modern-rendering --language en
qwen3-tts/.venv/Scripts/python.exe qwen3-tts/build_project_timing.py `
  --project frame-rate-modern-rendering

# 기존 파일을 건드리지 않는 검수용 예시 클립 생성
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-frame-rate-broll.ps1 `
  -CacheDir .audit-fps-sources -OutputDir .audit-fps-broll-new

# 검수 완료 뒤 실제 자산 폴더로 생성
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-frame-rate-broll.ps1 `
  -CacheDir .audit-fps-sources

# 별도 터미널에서 Motion Canvas 편집기 실행
npm run start

# 편집기가 9100 포트에서 실행 중일 때 최종 MP4 렌더
npm run render:project -- frame-rate-modern-rendering 9100

# 게시 전 파일·자막 구조 검사
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-video-project.ps1 `
  -Project frame-rate-modern-rendering -Stage publish
```

각 씬의 원본 URL과 인용 구간은 `sources/SOURCES.md`, 화면 적합성 검토 결과는
`planning/broll-audit.md`, 게시 문구와 챕터는 `publishing/`에서 관리합니다.

## 작업 순서

1. `planning/outline.md`에서 영상의 질문과 결론을 확정합니다.
2. `script/narration.ko.json`에 장면별 내레이션을 작성합니다.
3. `sources/SOURCES.md`에 사용할 자료의 출처와 라이선스를 기록합니다.
4. TTS를 생성하고 SRT 타이밍을 확인합니다.
5. Motion Canvas와 Manim에서 필요한 장면을 제작합니다.
6. 각 씬 앞의 6.5초 B-roll을 넣고 음성·화면 동기화를 검사합니다.
7. 라이선스가 확인된 BGM 후보를 제시하고 사용자의 선택을 기다립니다.
8. 승인 뒤 게임 원음과 BGM을 내레이션 아래로 믹스하고 본편을 다시 렌더합니다.
9. `publishing/`의 제목, 설명, 챕터를 완성합니다.

전체 절차는 저장소의 `docs/VIDEO_WORKFLOW.md`, TTS·자막·오디오 승인 기준은
`docs/NARRATION_AUDIO_STANDARD.md`를 참고하세요.

## 관련 코드

- Motion Canvas: `motion-canvas/src/projects/frame-rate-modern-rendering`
- Manim: `manim/projects/frame-rate-modern-rendering`
- 생성 결과: `shared/output`
