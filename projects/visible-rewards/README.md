# 왜 조금만 더 하게 될까? | 보상이 보이는 게임 디자인

영상 프로젝트 visible-rewards · 2026-09-17 최종 v3 · 전체화면 / 하단 설명 제거 / 2.5D / 얼굴캠 없는 스타듀밸리 / 몬헌 와일즈

## 최종 전달 파일

- 업로드 자료: [썸네일 PNG](publishing/thumbnails/visible-rewards-ko-v1.png) · [제목](publishing/title.ko.txt) · [설명 전문 — 챕터/출처 포함](publishing/description.ko.txt).
- 영어 업로드 자료: [영어 제목](publishing/title.en.txt) · [영어 설명 전문 — 동일 챕터/출처 포함](publishing/description.en.txt).
- 영상: `shared/output/motion-canvas/visible-rewards-final.mp4` — 1920×1080 / 60fps / 375.766667초. A 내레이션 + 연속 Wanderlust + 작은 게임 원음 포함.
- 한국어: `shared/output/motion-canvas/visible-rewards-final.ko.srt`
- 영어: `shared/output/motion-canvas/visible-rewards-final.en.srt`
- [노션: 04. 게임 보상](https://app.notion.com/p/3de0b1ffa61e81f48cc4d3f4dce3b4d1) — 기존 강의 형식의 독립 읽기 문서, 실제 캡처 5장. 채널 게시 주소 미확인으로 상단 영상 임베드만 대기.
- [전달 해시·기술 검사](publishing/delivery-v3.json), [변경 기록](planning/revision-v3.md), [위키 원고](../../docs/wiki/game-design-basics/04-rewards.md).

영상 하단 설명은 제거했지만 게임의 원래 HUD·메뉴·획득 안내는 유지합니다. 출처와 가정 수치는 한영 게시 설명란 및 위키에 있습니다. SRT는 별도 제공하며 영상에 구워 넣지 않았습니다.

## 현재 상태

- [한국어 대본](script/review.ko.md): 8장 / 2026-09-15 승인.
- [구성안](planning/outline.md), [자료화면 작업표](planning/footage-plan.md).
- [목소리 연출·참고 링크](audio/performance-direction.md): 기존 사용자 화자 + 작은 감정 변화.
- [A 균형형](audio/samples/A-balanced.mp3) / [B 표현형 후보](audio/samples/B-expressive.mp3) 생성 완료. [검수 기록](audio/voice-comparison-review.md).
- 사용자 선택: **A 균형형 / Qwen3-TTS 1.7B Base**. B는 비교 자료로만 보존합니다.
- 본편 TTS·한국어/영어 SRT 각 94개 생성, 단어 타임스탬프 정렬 완료. [검수](audio/narration-review.md).
- **Wanderlust — Scott Buckley** 승인·공식 원본 확보. 내레이션과 연속 BGM을 섞은 검토본 생성.
- 편집기는 실측 375.767초(약 6분 16초), 8개 독립 씬과 같은 오디오 검토본을 사용합니다.
- 재사용 허용 소스에서 실제 예시 8 × 19.5초 편집. 가방 구매·확장·경험치와 강화 선택을 자체 도식과 페어로 연결.
- 설명 8개를 흰색·자연색 2.5D 디오라마로 변경. 캐릭터 보행, 수집, 가방 확장, 무기 선택·궤도 변화가 움직입니다.
- 스타듀밸리는 얼굴캠 없는 소스로 교체. 2,000G 구매와 12→24칸 확장을 실제 화면으로 확인했습니다.
- 몬헌 와일즈: **04:40.867부터 19.5초**, 방어구 제작 소재/보유량 메뉴 9.5초 + 사냥 10초. 별도 세이브의 자료이며 특정 소재 드롭을 보장하지 않습니다.
- 새 장 대본은 승인 대기여서 합성하지 않았습니다. 기존 8장 A 내레이션과 길이, 한영 SRT 각 94개를 그대로 사용합니다.
- 게임 원음 + 연속 Wanderlust + A 내레이션 전체 믹스 포함 MP4 생성. 375.766667초 / 22,546프레임 / H.264 + AAC. 전체 디코딩·AAC 패킷 일치 검사 통과.
- 전체 사람 청취 승인 전까지 publishReady=false 유지.
- 원본 TTS: shared/output/narration/visible-rewards/qwen3-1.7b-balanced-v1/visible-rewards-qwen3-1.7b-balanced-v1.wav
- 청취용 MP3: shared/output/narration/visible-rewards/qwen3-1.7b-balanced-v1/visible-rewards-narration-wanderlust-review-v1.mp3
- 편집기 오디오: motion-canvas/src/projects/visible-rewards/assets/final-mix-v2.wav (v2 및 최종 v3와 같은 믹스)

## 열기 / 재현

```powershell
cd D:\Github\VideoEditing\motion-canvas
npm start -- --host 127.0.0.1 --port 9100
```

- [간편 재생](http://127.0.0.1:9100/visible-rewards-review.html)
- [Motion Canvas 편집기](http://127.0.0.1:9100/src/projects/visible-rewards/project)
- 최종 MP4 v3: `shared/output/motion-canvas/visible-rewards-final.mp4`
- 이전 MP4 v2: `shared/output/motion-canvas/visible-rewards-v2.mp4` (이 PC에만 보존, 별도 복원 대상 아님)
- 이전 v1: `shared/output/motion-canvas/visible-rewards.mp4` (보존, 새 편집기와 화면이 다름)
- KO/EN SRT: `project.json.paths.captionsKo` / `captionsEn`. 기존 94개 큐·타임코드 유지.

새 PC에서 재생/편집하려면 원본 다운로드·TTS 재합성 없이 저장소 루트에서 복원합니다.

```powershell
node scripts/restore-media.cjs --project visible-rewards
node scripts/verify-visible-rewards-delivery.cjs
```

화면을 다시 렌더할 때에는 기존 최종 파일을 보존하고 새 버전 이름을 사용해야 합니다. 원본 구간까지 새로 편집하는 경우에만 다음 준비 순서가 필요합니다.

```powershell
node scripts/fetch-visible-rewards-v2.cjs
node scripts/prepare-visible-rewards-v2.cjs
node scripts/prepare-visible-rewards-v2.cjs --v3
# 믹스는 기존 final-mix-v2.wav/.m4a 재사용. 새 컷/타이밍으로 바꾸는 경우에만 별도 버전으로 재믹스.
cd motion-canvas
npx tsc --noEmit
node scripts/render-visible-rewards.cjs --v3 --qa-only
# 모든 씬의 캡처를 확인한 다음 렌더
node scripts/render-visible-rewards.cjs --v3
```

오디오·최종 영상이 이미 있으면 새 버전으로 보존한다. 믹서는 기존 출력이 있으면 중단한다.
게임 클립 재편집에는 `--rebuild`를 명시하며, 원본 캐시는 덮어쓰지 않는다.
최종 렌더러는 승인 TTS/KO·EN SRT/마스터 AAC가 바뀌지 않았는지 해시로 확인한다.
최종 결과가 이미 있으면 생성 단계는 생략하고 바로 재생합니다. 렌더 검사는 `shared/output/visible-rewards/visual-qa-v3/render-report.json`, 전달 검사는 `publishing/delivery-v3.json`입니다.
현재 게임 컷은 `gameplay-v3/`, 전체 믹스는 v2 그대로, 화면 검사는 `visual-qa-v3/`로 분리했습니다.
다음 수정은 v4 이상 새 출력 경로를 사용합니다. 같은 프레임 수의 그래픽 캐시도 디자인이 바뀌면 재사용하지 않습니다.
새 컴퓨터에서 보는 데에는 원본 다운로드 캐시나 TTS 모델이 필요 없습니다. 편집된 `gameplay-v3`와 전체 믹스는 Git에 포함됩니다.

## 제작 순서

1. 대본 / 짧은 비교 문구 확인.
2. 같은 문구·같은 사용자 화자로 균형형과 표현력 후보 비교.
3. 선택된 목소리로 장면 문맥을 유지해 연속 TTS 생성. 누락·숫자·말끝 검수.
4. 실제 예시에서 무엇을 봐야 하는지 우리 내레이션을 계속 배치. 장면 앞에 19.5초 자동 무음을 넣지 않음.
5. 실제 음성 길이에 맞춰 KO/EN SRT·타이밍·8개 독립 씬 동기화.
6. 출처와 화면/원음 사용 조건이 확인된 실제 클립 확보.
7. 별도 BGM 후보 승인 후 전체 연속 BGM + 작은 게임 원음 믹스.
8. 최종 영상과 편집기에 같은 믹스 연결, 전체 청취 뒤 게시 가능 여부 결정.

기본 Qwen3 Base의 직접 감정 지시 한계와 Chatterbox 모델 준비 상태를 음성 문서에 기록했습니다.
사용자가 선택한 A의 Qwen3 엔진을 유지합니다. 참고 영상 화자의 음성은 복제하지 않습니다.

## 이번 프로젝트의 음성 생성·동기화

저장소 루트에서 실행합니다. 다른 완료 프로젝트는 처리하지 않습니다.
각 단계의 성공과 ASR 차이 검토 후 다음 단계로 진행합니다.

```powershell
# 승인된 A 설정으로 8개 장면 합성. 깨끗한 기존 청크는 재사용합니다.
qwen3-tts/.venv/Scripts/python.exe -X utf8 -u qwen3-tts/render_visible_rewards.py

# 음성 받아쓰기·단어 타임스탬프 검수
qwen3-tts/.venv/Scripts/python.exe -X utf8 -u qwen3-tts/review_project_narration.py --project visible-rewards --device cuda

# ASR 내용을 대본과 대조한 뒤, 한영 자막을 같은 타임코드로 생성
qwen3-tts/.venv/Scripts/python.exe -X utf8 qwen3-tts/align_project_subtitles.py --project visible-rewards
qwen3-tts/.venv/Scripts/python.exe -X utf8 qwen3-tts/build_project_timing.py --project visible-rewards

# 원본과 별도의 청취용 WAV/MP3 및 실측 편집 큐 생성
qwen3-tts/.venv/Scripts/python.exe -X utf8 qwen3-tts/prepare_visible_rewards_review.py --version 1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-video-project.ps1 -Project visible-rewards -Stage narration
```

청취본이 이미 있으면 마지막 내보내기의 `--version`을 올립니다.
승인된 완성 음성의 본격 수정은 출력 디렉터리도 v2 이상으로 분리합니다.
위 prepare 단계의 청취본은 배경음 없는 내레이션이며 `final-mix.m4a`가 아닙니다.
별도 승인된 음악은 다음 명령으로 믹스합니다. 원음 없는 검토본으로 명확히 구분합니다.

```powershell
qwen3-tts/.venv/Scripts/python.exe -X utf8 qwen3-tts/mix_visible_rewards_review.py --version 1
```

기존 내보내기가 있으면 버전을 올립니다. [음악 선택 기록](audio/bgm-candidates.md), [믹스 검사](audio/mix-report.md).

## 주의

- 기본 예시 길이는 project.json.editing.exampleSeconds = 19.5초.
- 현재 실측 6분 15.76초. 자료화면 편집으로 시간이 바뀌면 양쪽 SRT·믹스·씬 길이를 함께 갱신.
- 구버전의 예시 앞 무음 조립기를 그대로 실행하지 말고 연속 내레이션 경로를 확인.
- 음악은 이번에 별도 선택한 Wanderlust. 이전 프로젝트 곡을 자동 사용하지 않음.
- 내레이션 -16 / 게임 원음 -23 / BGM -28 LUFS는 믹스 시작점. 레이어별·합산 피크·청취 검수 필요.
- 소스 출처는 설명란 우선이지만 자료별 필수 표기 조건은 준수.

## 코드 위치

- Motion Canvas: motion-canvas/src/projects/visible-rewards
- Manim: manim/projects/visible-rewards (수학 애니메이션이 필요할 때만 사용)
- 기준: docs/VIDEO_WORKFLOW.md / VIDEO_VISUAL_STYLE.md / NARRATION_AUDIO_STANDARD.md
