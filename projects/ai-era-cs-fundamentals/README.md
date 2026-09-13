# AI 시대, 컴공생은 무엇을 공부해야 할까?

프로젝트: `ai-era-cs-fundamentals` · **v6 전체 렌더·한영 자막 검수 완료 / 음악 게시 조건·전체 청취 승인 대기**

현재 v6: **17분 36.567초**, 실제 음성에 맞춘 12개 독립 씬. 기존 v5는 15분 6.733초로 보존했습니다.

**v6 승인 (2026-09-12):** [자료화면에서도 이어지는 대본](script/review.v6.ko.md). 12챕터/86문단, 예시 영상 앞 자동 무음 제거, 원음 -31 LUFS·연속 Blue Dream BGM. [v6 제작·재시작 절차](audio/v6-production.md). 아래 v5 영상과 SRT는 구버전 기록이며 새 v6 타이밍과 혼용하지 않습니다.

## 현재 v6 보기

- **[전체 영상 — VS Code 호환 MP4](../../shared/output/motion-canvas/ai-era-cs-fundamentals-tts-review-full-20260912T141716Z-vscode.mp4)** · [표준 MP4 / AAC](../../shared/output/motion-canvas/ai-era-cs-fundamentals-tts-review-full-20260912T141716Z.mp4): **17:36.567 / 1080p60**, 자료화면에서도 우리 대사 + 작은 원음 + 연속 Blue Dream.
- 영상용 분리 자막: [한국어](../../shared/output/motion-canvas/ai-era-cs-fundamentals-tts-review-full-20260912T141716Z.ko.srt) · [영어](../../shared/output/motion-canvas/ai-era-cs-fundamentals-tts-review-full-20260912T141716Z.en.srt).
- [전체 영상 검수 기록](audio/render-review-v6.md). 자동 검사와 표본 화면 검토를 통과했으며, 사람의 전체 청취 승인은 별도입니다.

현재는 다음 v6 자료를 사용하세요. 아래의 v5 상태·경로는 당시 보존 기록입니다.

- [새 음성·원음·Blue Dream 도입 35초](../../shared/output/motion-canvas/ai-era-cs-v6-first35s-blue-dream-review.mp4): 실제 새 렌더 화면 + H.264/MP3, VS Code 재생용.
- [전체 미리보기](http://localhost:9100/ai-cs-review.html) → 챕터 선택 → **챕터 처음부터 듣기**.
- [전체 믹스 WAV](../../motion-canvas/src/projects/ai-era-cs-fundamentals/assets/mix-v6-artist-music-review.wav): 현재 편집기에 연결된 음성 + 작은 원음 + 연속 BGM.
- [한국어 SRT](../../shared/output/narration/ai-era-cs-fundamentals/qwen3-1.7b-balanced-v6/ai-era-cs-fundamentals-qwen3-1.7b-balanced-v6.srt) · [영어 SRT](../../shared/output/narration/ai-era-cs-fundamentals/qwen3-1.7b-balanced-v6/ai-era-cs-fundamentals-qwen3-1.7b-balanced-v6.en.srt): 동일한 253개 번호·타임코드.
- [믹스 실측](audio/mix-report.md) · [받아쓰기 확인 및 청취 체크 포인트](audio/v6-asr-notes.md).

Blue Dream은 **공식 작곡가 채널 음원으로 실제 포함**했습니다. 오디오 보관함 사용 조건은 미확인 상태이므로 비공개 청취 검토본이며 게시 보류입니다. [입수 경로·남은 확인](audio/blue-dream-creator-evidence.md).

## 기존 v5 보기 — 보존된 구버전

- **[전체 렌더 영상 — VS Code 호환본](../../shared/output/motion-canvas/ai-era-cs-fundamentals-tts-review-full-20260911T161653Z-vscode.mp4)** · [일반 MP4 / AAC 음성](../../shared/output/motion-canvas/ai-era-cs-fundamentals-tts-review-full-20260911T161653Z.mp4): 15:06.733, 1080p60, TTS + 예시 원음. **Blue Dream은 아직 미포함**.
- 렌더 영상 옆 자막: [한국어](../../shared/output/motion-canvas/ai-era-cs-fundamentals-tts-review-full-20260911T161653Z.ko.srt) · [영어](../../shared/output/motion-canvas/ai-era-cs-fundamentals-tts-review-full-20260911T161653Z.en.srt). 기존 SRT를 타이밍 변경 없이 복사했습니다.
- [35초 렌더 테스트 — VS Code 호환 MP4](../../shared/output/motion-canvas/ai-era-cs-fundamentals-tts-review-35s-vscode.mp4): 19.5초부터 TTS. 원음 포함, Blue Dream 미포함. [렌더·검수 명령과 현황](audio/render-review.md).
- 웹 미리보기 주소는 현재 v6를 엽니다. v5 확인에는 위 보존 MP4를 사용합니다.
- [Motion Canvas 편집기](http://localhost:9100/src/projects/ai-era-cs-fundamentals/project)
- [v5 전체 음성 + 예시 원음 M4A](../../motion-canvas/src/projects/ai-era-cs-fundamentals/assets/narration-source-mix.m4a): 구버전 보관 트랙이며 현재 편집기 연결은 아닙니다.
- [영상 싱크용 TTS WAV](../../shared/output/narration/ai-era-cs-fundamentals/qwen3-1.7b-balanced-v5/ai-era-cs-fundamentals-qwen3-1.7b-balanced-v5.wav): 각 챕터 앞 19.5초는 예시 삽입용 무음입니다.
- [한국어 SRT](../../shared/output/narration/ai-era-cs-fundamentals/qwen3-1.7b-balanced-v5/ai-era-cs-fundamentals-qwen3-1.7b-balanced-v5.srt) · [영어 SRT](../../shared/output/narration/ai-era-cs-fundamentals/qwen3-1.7b-balanced-v5/ai-era-cs-fundamentals-qwen3-1.7b-balanced-v5.en.srt): 동일한 156개 번호·타임코드. 54문단을 읽기 편하게 나눈 프로젝트 예외이며 원문 단위는 timing JSON에 보존.
- BGM: **Blue Dream — Cheel** 확정. [선택·사용 확인 상태](audio/bgm-selection.md). 보관함 MP3와 라이선스 확인 전이라 아직 미적용.

**현재는 전체 음성이 들어간 청취 검토본입니다.** 2026-09-12 전체 MP4 렌더와 12챕터 검수를 완료했습니다. 이전 14분 11초는 임시값이며 새 타임라인에 사용하지 않습니다. 12개 예시 19.5초와 원음을 유지하고, 모든 설명에 v5 전체 TTS를 연결했습니다. 연속 BGM을 넣은 게시용 MP4와 사람의 전체 청취 승인은 아직 남아 있습니다. 기존 편집기의 M4A 연결/파형 문제와 별개로, 위 VS Code 호환 MP4는 MP3 음성을 사용합니다. 이전 샘플·v1 결과·기존 FPS와 점프 물리 완성작은 보존했습니다.

## 이번에 반영한 것

- 사용자 PDF의 흰색 발표형 디자인: 좌측 제목, 검정/회색 글자, 파랑 도표, 각진 하단 요약 박스. [공통 기준](../../docs/VIDEO_VISUAL_STYLE.md).
- 12챕터에 유명 밈을 참고한 약2초 자체 연출. 원본 밈 영상·음성은 사용하지 않음. [매핑](sources/MEMES.md).
- 예시 슬롯 3배, 78초 → 234초. v6 전체 1056.567초에서는 약22.1%이며, 예시 시간에도 우리 대사가 계속됩니다.

- 01~12 독립 씬을 유지하고 각 씬에 **실제 예시 19.5초 → 자체 모션그래픽** 연결.
- PyCon JP 기술 예시 5개 + CC BY 테트리스 플레이 1개 + GDQuest 게임개발 영상 6개. 일반 스톡은 전부 교체했고 12챕터의 원본 영상도 서로 다릅니다.
- 새 구간: 01 Godot 편집기 / 02 인디 게임 프로토타입 / 06 코딩 연습 / 09 최적화 측정 / 10 게임 루프 완성 / 12 플레이 테스트.
- 반복문 수정, 큐·사전, 구조 단순화, 중복 제거, 테트리스 배열·충돌·줄 삭제·경계 테스트, 비용, 완료 조건, 로컬 구현 등 챕터별 자체 화면.
- 예시 12개 모두 원음을 검토 믹스에 보존. TTS 길이에 맞춰 씬 시작·편집 큐·한영 SRT·전체 믹스를 함께 변경.
- 한 프레임 늦는 시작 문제 수정. 전 컷 1920×1080 / 60fps / 1170프레임 / 19.5초 확인.
- 현재 편집기는 v6 전체 믹스 WAV를 사용합니다. v5와 v4 도입 샘플·옛 임시 믹스는 이력으로만 보존.

[사용 영상·정확한 구간·크레딧](sources/FOOTAGE.md) · [대본](script/review.ko.md) · [제작 계획](planning/production-plan.md)

## 실행·빌드

Git에서 내려받은 후 큰 WAV는 [분할 압축 복원 안내](../../shared/media-archives/README.md)에 따라 복원합니다. 기존 로컬 WAV는 삭제하거나 음질을 바꾸지 않았습니다. 선택적으로 전달되는 음악 포함 검토본의 게시 조건은 별도로 확인합니다.

저장소 루트 `D:\\Github\\VideoEditing`에서:

```powershell
npm run start
npm run build
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-video-project.ps1 -Project ai-era-cs-fundamentals -Stage setup
```

현재 서버 포트는 9100입니다. 서버를 재시작해 포트가 달라지면 터미널에 나온 주소를 사용하세요. 열어 둔 편집기는 새로고침합니다.

## 폴더

```text
projects/ai-era-cs-fundamentals/
├── script/       v6 한국어 대본 · 영어 번역 · v5 보존
├── sources/      실제 선정 컷 · 출처 · 라이선스 · 검증 결과
├── planning/     제작 단계와 남은 작업
├── audio/        전체 TTS 검수 · 원음/음성 믹스 실측 · BGM 상태
└── publishing/   게시용 문구 초안
motion-canvas/src/projects/ai-era-cs-fundamentals/
├── project.ts    12개 독립 씬 + 검토용 오디오
├── scenes/       scene01~12 · 페어 재생 · 챕터별 자체 애니메이션
└── assets/       broll/scene01~12.mp4 · mix-v6-artist-music-review.wav/m4a
shared/output/ai-cs-media-cache/  원본·확인 페이지·연속 프레임·시각 QA
```

다운로드 원본과 개별 편집 클립은 Git에서 제외했습니다. 다른 기기에서 재현할 때는 [재현 절차](sources/FOOTAGE.md)를 사용합니다. 과거 스톡 원본과 교체 전 컷도 삭제하지 않고 캐시에 보존했습니다.

## 다음 승인과 최종화

1. 현재 전체 음성본 청취 승인. 합성·받아쓰기·말끝 자동 검사와 실제 음성 타이밍 반영은 완료.
2. 선택된 Blue Dream의 오디오 보관함 파일·라이선스 확인.
3. 현재 BGM 포함 검토 MP4는 생성 완료. 보관함 사용 조건 및 전체 청취 승인 후 게시용 상태로 확정합니다. 보관함 파일로 바꿔 믹스할 때 영상과 한영 SRT 타이밍은 보존합니다.
4. v6 나레이션 -16 LUFS 후 +1.8dB / 원음 -31 / 연속 BGM -28 LUFS, 원음 겹침 BGM -3dB, 가벼운 덕킹·1초 루프 크로스페이드.
5. 편집기 PCM WAV와 MP4 AAC에 같은 믹스를 연결하고 전체 검수. 현재 20씬 FPS 전용 믹서는 직접 호출하지 않음.
6. [영상 크레딧](sources/FOOTAGE.md)을 게시 설명에 포함. 가격·라이선스 최종 재확인.

기준: [제작 워크플로](../../docs/VIDEO_WORKFLOW.md), [오디오 기준](../../docs/NARRATION_AUDIO_STANDARD.md). 기존 FPS·점프 물리 완성 파일은 변경하지 않았습니다.
