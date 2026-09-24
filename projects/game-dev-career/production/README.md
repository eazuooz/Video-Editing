# 게임 개발로 먹고살기 — 본편 제작

2026-09-20 사용자 승인 후 전체 제작. 이전 90초 프리뷰는 보존한다.

## 최신 본편

- 음성·자막: http://localhost:9191/career-final.html
- 무자막: http://localhost:9191/career-final.html?clean
- 편집기: http://localhost:9191/src/projects/game-dev-career/project
- 상자 직접 테스트: http://localhost:9191/career-prototype.html

자막 중심 `(0, 430)` → `(0, 400)`, **30px 위로 이동**.
1080p 두 줄 박스는 테두리·그림자 아래 약 51.5px, 한 줄은 약 82.5px 여백.
폰트·색은 승인된 `boxed-white-forest-v1` 유지. 이전 프리뷰는 재렌더하지 않는다.

## v3 역할군 소개 전면 교체본 — 현재 제작 명령

대본·음성·자료화면·타이밍을 함께 다시 만든 현재 버전이다. 원본·권리·인아웃은
`media-sources-v3.json`, 변경 이유는 `REVISION-v3.md`를 따른다.

```powershell
qwen3-tts/.venv/Scripts/python.exe projects/game-dev-career/production/prepare_footage_v3.py
qwen3-tts/.venv/Scripts/python.exe -X utf8 qwen3-tts/render_narration.py --project game-dev-career --batch-size 1
qwen3-tts/.venv/Scripts/python.exe -X utf8 projects/game-dev-career/production/build_episode_audio.py align
qwen3-tts/.venv/Scripts/python.exe -X utf8 projects/game-dev-career/production/build_episode_audio.py mix --revision v3
qwen3-tts/.venv/Scripts/python.exe -X utf8 projects/game-dev-career/production/check_audio.py
cd motion-canvas
npm run build
node scripts/render-career-final.cjs --qa-only
node scripts/check-career-cues.cjs
node scripts/render-career-final.cjs --render-only
```

Vite를 `127.0.0.1:9191`에 띄운 상태에서 렌더한다. 결과는 v1·v2를 덮지 않는
`game-dev-career-v3.mp4`와 `game-dev-career-v3-subtitled.mp4`다. 실측 타임라인은
409.95초 / 24,597프레임 / KO·EN 94큐다. 사람이 전체 청취하기 전에는
`publishReady=false`를 유지한다.

## v2 실제 자료화면 교체 재현 — 보존 기록

최신 소스·인아웃: `media-sources-v2.json`. 필요한 원본 파일은 해당 기록의 URL/구간과
허용 근거를 먼저 확인하여 준비한다. 캐시 파일을 다른 영상으로 대체하지 않는다.

```powershell
qwen3-tts/.venv/Scripts/python.exe projects/game-dev-career/production/prepare_footage_v2.py
qwen3-tts/.venv/Scripts/python.exe projects/game-dev-career/production/build_episode_audio.py mix --revision v2
qwen3-tts/.venv/Scripts/python.exe projects/game-dev-career/production/check_audio.py
cd motion-canvas
node scripts/render-career-final.cjs
node scripts/check-career-cues.cjs
```

Vite 서버를 9191 포트에 띄운 상태에서 실행한다. 현재 프로젝트 매니페스트가 v2 경로를 지정한다.
렌더 중에는 Motion Canvas 소스·매니페스트·미디어·오디오를 수정하지 않는다(HMR 재시작 방지).
프레임 26055개·1080p60·동일 AAC·전체 디코딩을 검사하며, 기존 최종 파일은 덮어쓰지 않는다.
TTS와 SRT는 재생성하지 않는다. 기존 v1 MP4·M4A·WAV·90초 프리뷰 보존.

검수 기록: `footage-build-v2.json`, `audio-layer-check-v2.json`, `mix-report-v2.json`,
`qa-final-v2/report.json`, `qa-final-v2/cues/report.json`, `render-clean-v2.json`, `render-captioned-v2.json`.

## v1 본편 최초 제작 기록 — 현재 타이밍을 바꿀 때만 참고

아래는 v1 당시 명령과 소스 구성이다. v2 재렌더에 아래 TTS/align/v1 mix를 다시 실행하지 않는다.

저장소 루트에서 실행한다. 먼저 `motion-canvas`에서 `npm start -- --host 127.0.0.1 --port 9191`.

```powershell
qwen3-tts/.venv/Scripts/python.exe -X utf8 qwen3-tts/render_narration.py --project game-dev-career --batch-size 1
qwen3-tts/.venv/Scripts/python.exe -X utf8 projects/game-dev-career/production/build_episode_audio.py align
powershell -NoProfile -ExecutionPolicy Bypass -File projects/game-dev-career/production/build_cpp.ps1
node --experimental-strip-types motion-canvas/scripts/prepare-career-examples.cjs
qwen3-tts/.venv/Scripts/python.exe -X utf8 projects/game-dev-career/production/build_episode_audio.py mix
node motion-canvas/scripts/check-career-prototype.cjs
node motion-canvas/scripts/render-career-final.cjs --qa-only
node motion-canvas/scripts/render-career-final.cjs --render-only
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-video-project.ps1 -Project game-dev-career -Stage publish
```

`align`은 Whisper 단어 시점과 승인 대본을 맞춘다. 60fps 경계의 timing JSON/TS,
원본 89문장 timing, 같은 시점 KO/EN SRT를 함께 생성한다. 이후 범용 timing 생성기를
실행하면 30fps로 반올림되므로 이 프로젝트는 위 전용 명령을 사용한다.
렌더 명령은 기존 납품 MP4를 덮지 않는다. 수정본은 버전을 분리해서 렌더한다.

매 장 앞 기본 19.5초는 작업 예시, 뒤는 자체 2.5D 설명. 대사는 계속 이어진다.
06은 '이 상자는' 발화에 맞춰 13.2초에 자체 상자로 전환한다. 전체 434.25초와 SRT는 바꾸지 않았다.
01–05·08–09는 자체 실행 프로토타입과 실제 C++ 테스트 결과이며 상용 게임이나 외부 엔진 녹화가 아니다.
06은 Krita 명암 시범, 07은 Blender Extrude 시범. 출처·실사용 구간은 `media-sources.json`.
Discovery는 연속 재생하며 외부 영어 해설은 -31 LUFS로 감쇠 후 덕킹한다.
편집기는 PCM WAV, 최종 MP4는 동일 믹스 AAC packet copy.

검수: `asr-review.json`, `prototype-tests.json`, `prototype-browser-tests.json`,
`qa-final/report.json`, `qa-final/contact-*.png`, `mix-report.json`, `render-clean.json`, `render-captioned.json`.
사람의 전체 청취 전 `publishReady=false`를 유지한다.

---

## 아래는 승인 전 콘티 제작 당시 기록 (현재 상태가 아님)

이 폴더는 본편 개발·검수용이다. 이전 `preview/v2`의 음성 포함 90초 프리뷰는 그대로 보존한다.

## 준비된 것

- 한국어·영어 대본: 9개 장면, 서로 대응하는 89개 문장.
- `script/review.ko.md`: 사용자 검토용 한국어 대본.
- 본편 9개 독립 씬: `motion-canvas/src/projects/game-dev-career/scenes/scene01.tsx` ~ `scene09.tsx`.
- 2.5D 시각 콘티: 기존 승인 상자를 중심으로 조건·코드·데이터·도형화·입체 회전·협업 설명 구성.
- 승인된 흰 박스 자막 배치 샘플. 실제 내레이션 자막 정렬은 아직 하지 않았다.
- TypeScript/Vite 빌드 통과. 9개 씬의 앞·중간·뒤 27개 화면 캡처 검사.

## 열기

`motion-canvas` 폴더에서:

```powershell
npm start -- --host 127.0.0.1 --port 9191
```

- 압축 콘티: http://localhost:9191/career-storyboard.html?reel
- 본편 임시 시간 콘티: http://localhost:9191/career-storyboard.html
- 본편 편집기: http://localhost:9191/src/projects/game-dev-career/project

**두 콘티 모두 무음이며 본편 완성 영상이 아니다.** 54초 압축본이나 495초 편집 예산으로 SRT를 만들지 않는다. 음성 포함 승인 스타일 프리뷰는 상위 README의 `career-preview.html?v=2&captions=full` 링크다.

## 남은 순서

1. 본편 대본과 기존 균형형 목소리 사용 확인. 음악 Discovery·박스 자막 스타일 승인은 유지.
2. 자료영상별 사용 허용과 실제 동작을 확인하고 인·아웃점 확정.
3. 전체 TTS → ASR 확인 → 실측 timing JSON → 한글·영어 SRT.
4. 콘티의 임시 시간·샘플 문구를 실제 타이밍으로 교체. 장면당 외부 예시 기본 19.5초를 포함하고 예시 중에도 우리 내레이션을 이어감.
5. 원음·연속 Discovery 믹스 → 편집기/MP4 오디오 동기화 → 무자막판/박스 자막판 렌더.
6. 전체 청취·자막·미디어 검수 후에만 게시 상태 변경.

대본 미승인·외부 자료 미삽입 상태를 완료로 표시하지 않는다. 음악 후보를 다시 고르게 하거나 승인된 목소리를 임의로 다른 모델로 바꾸지 않는다.
