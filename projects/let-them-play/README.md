# 게임의 첫 화면은 어떻게 설계할까? | 젤다 야숨으로 보는 게임 디자인

let-them-play · 대본 v4 / 화면 v5 · **8분1.8초 에디토리얼 2.5D 본편 검토 MP4 제작 완료.** 균형형 목소리·작은 야숨 원음·연속 Discovery 포함.
진행 상태와 실제 길이는 [project.json](project.json)이 기준이다. 사람의 전체 청취 승인 전에는 완료로 표시하지 않는다.

2026-09-14 추가 수정: **본편 내레이션 음량 ×1.1 적용**, 속도·게임 원음·BGM·영상/SRT 타이밍 유지.
설명·비교 화면은 [승인된 39.7초 에디토리얼 2.5D 샘플](planning/editorial-sample.md)을 바탕으로 [본편8장면 v5](planning/editorial-v5.md)에 모두 적용하고 렌더했다.
장면마다 다른 공간·동작을 사용하며, 이전 샘플은 비교 이력으로 보존한다.

## 구성

8개 독립 Motion Canvas 씬. 각 씬은 **야숨 관찰 / 디자인 해설 / 가상 2.5D 설계 비교**를 1:1:1로 구성한다.
첫 플레이 장면의 시선, 목표, 첫 행동, 피드백, 정보 순서를 다룬다. 구현 튜토리얼이나 우리 게임 기능 시뮬레이션이 아니다.

- [승인 대본](script/review.ko.md), [장면별 한국어](script/narration.ko.json), [영어 번역](script/narration.en.json)
- [영상 큐](planning/footage-plan.md), [사용 허용과 출처](sources/archive64-rights.md)
- [실측 타임라인](../../motion-canvas/src/projects/let-them-play/timeline.generated.json)
- [오디오 검수](audio/mix-report.md), [ASR 검토 결정](audio/asr-decisions.md)
- [유튜브 한국어 설명란](publishing/youtube.ko.md), [영어 설명란](publishing/youtube.en.md)
- [업로드용 제목·설명·한영 SRT 묶음](publishing/README.md): 2026-09-15 게시 문구 추천 및 구간별 영어 자막 개선

19.5초×3×8=7분48초는 최초 가안이다. 승인 음성을 빠르게 만들지 않고 실제 발화에 따라 세 구간을 똑같이 늘린다.
`timeline.generated.json`의 실측 프레임이 화면·컷·오디오·자막의 최종 기준이다.
우리 내레이션은 게임 영상 중에도 이어지며 게임 원음은 작게, Discovery는 처음부터 끝까지 연속 재생한다.

## 화면과 출처

화면 위아래 작은 출처·장 번호·제작 상태 문구와 **마지막 크레딧을 넣지 않는다**.
영상·음악의 출처와 라이선스는 한글·영문 YouTube 설명란에만 넣는다.
게임 자체 HUD·대화와 큰 디자인 제목·의미 있는 A/B 라벨은 유지한다.

새 본편은 크레딧 선택 사항이 명시된 Archive64 녹화본을 사용한다.
업로더 표기 CEMU·영어판이며 Switch 실기 성능 자료가 아니다.
기존 World of Longplays 컷과 검토본은 보존하지만 새 출력에는 연결하지 않는다.

## 열기와 빌드

저장소 루트에서:

```powershell
npm run start --prefix motion-canvas -- --host 127.0.0.1 --port 9100
npm run build --prefix motion-canvas
```

- 본편 재생: http://localhost:9100/let-them-play-review.html
- Motion Canvas 편집기: http://localhost:9100/src/projects/let-them-play/project
- 재생 버튼을 누르면 소리를 켠다. 편집기는 스피커를 켜고 재생한다.
- 편집기에는 같은 최종 AAC를 디코딩한 PCM WAV를 연결해 AAC 미지원 환경도 대응한다.

## 재제작 순서

대본·목소리가 그대로면 TTS를 다시 생성하지 않는다. 대본을 바꿀 때는 새 음성 버전과 승인을 먼저 관리한다.
아래는 이 프로젝트 전용 **세 구간·연속 내레이션** 흐름이다. 공통 두 구간 타이밍 생성기로 덮어쓰지 않는다.

```powershell
# 실제 음성 완료 후 받아쓰기 캐시를 최신 WAV와 대조
qwen3-tts/.venv/Scripts/python.exe -X utf8 qwen3-tts/review_project_narration.py --project let-them-play --device cpu
qwen3-tts/.venv/Scripts/python.exe -X utf8 qwen3-tts/assemble_let_them_play.py
qwen3-tts/.venv/Scripts/python.exe -X utf8 qwen3-tts/align_project_subtitles.py --project let-them-play
node scripts/fetch-let-them-play-archive64.cjs
node scripts/prepare-let-them-play-archive64.cjs
node scripts/mix-let-them-play-audio.cjs
npm run build --prefix motion-canvas
node scripts/check-let-them-play-thirds.mjs
node motion-canvas/scripts/check-let-them-play-editorial.cjs
node motion-canvas/scripts/render-let-them-play-final.cjs --qa-only
# 전체 24지점 화면을 확인한 뒤 (dev server가 실행 중이어야 함)
# 게임 구간은 원본 프레임 유지, 설명/2.5D만 렌더해 연결
node motion-canvas/scripts/render-let-them-play-hybrid.cjs
node scripts/verify-let-them-play-final.cjs
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-video-project.ps1 -Project let-them-play -Stage publish
```

렌더 중에는 씬 코드·매니페스트·가져온 JSON을 수정하지 않는다. 개발 서버의 자동 갱신이 렌더를 중단할 수 있다.
믹서의 기준은 내레이션 -16 / 원음 -23 / BGM -28 LUFS이며, 겹침·덕킹 이후 측정값은 믹스 보고서에 따로 기록한다.
내레이션 정규화 후 `audio.narrationGain=1.1`을 한 번 적용한다. 덕킹 기준은 기존 정규화 음성으로 유지한다.
렌더한 본편의 음량만 다시 만들 때는 `node scripts/boost-let-them-play-voice.cjs`를 사용한다.
현재 음량판 측정/백업: `shared/output/let-them-play/voice-gain-1p1/`.

## 결과 파일

1080p60·28908프레임. 전체 디코드·AAC 패킷 일치·한영120개 자막 동기·게시 기술 검사를 통과했다.
실제 MP4의24개 구간 표본 +8개 비교 후반 +마지막 프레임을 확인했다. [최종 검토 기록](planning/final-review.md).
마지막08장면 종결음과07장면 `컷신` 발음은 사람이 최종 청취해 확인할 항목이다.

- [본편 MP4](../../shared/output/motion-canvas/let-them-play.mp4)
- [업로드용 한국어 SRT](publishing/subtitles/let-them-play.ko.srt)
- [업로드용 영어 SRT](publishing/subtitles/let-them-play.en.srt)
- [편집기 음성·원음·BGM 전체 믹스](../../motion-canvas/src/projects/let-them-play/assets/final-mix.wav)
- 배경 단독·레이어 측정: `shared/output/let-them-play/final-audio-v4/`
- 전체 화면 검수: `shared/output/let-them-play/final-visual-qa/`
- 최종 MP4 표본: `shared/output/let-them-play/final-assembled-qa/`
- 새 디자인의 시간대별 검수·이전 본편 백업: `shared/output/let-them-play/editorial-full-v5/`

이전 무음 스타일 비교·2.5D 모음·도입부 승인 샘플은 이력이며 최신 본편으로 혼동하지 않는다.
게시용 영어 SRT는 기존 자동 분할 번역을 구간별로 다듬은 별도 출력이다. 원래 TTS 폴더의 한영 SRT는 이력으로 유지한다.
재렌더 후 업로드 묶음은 `node scripts/prepare-let-them-play-publishing.cjs`로 검증·생성한다.
한국어 자막이 바뀌면 번역 기준 해시 검사에서 중단하므로, 새 구간에 맞춰 영어를 먼저 검토해야 한다.
