# 원버튼 영상 재제작

현재 제작은 `final-v2/plan.json`과 프로젝트 manifest가 기준이다. 이전 240초 계획은 초기 기획이다.
실제 출력의 게시 승인 상태 및 원본 음악·회원 핸들·백업 잔여 사항을 유지한다.

1. `SOURCES.md`, 프로젝트 manifest 및 채널 제작 기준을 읽고 원본 미디어를 같은 경로로 복원한다.
2. Qwen3-TTS 런타임과 개인 기준 WAV/정확한 전사문을 준비한다.
3. `python -X utf8 -u projects/one-button-game-design/production/render-narration.py`
4. `python -X utf8 qwen3-tts/build_translated_srt.py --project one-button-game-design --language en`
5. `python -X utf8 qwen3-tts/build_project_timing.py --project one-button-game-design`
6. `python -X utf8 qwen3-tts/review_project_narration.py --project one-button-game-design` 후 전사/문장 끝을 검수한다.
7. `python -X utf8 qwen3-tts/align_project_subtitles.py --project one-button-game-design` (KO/EN 함께 정렬).
8. `node projects/one-button-game-design/production/build-video.cjs prepare`
9. Motion Canvas에서 Vite를 9210 포트로 실행한다. `node motion-canvas/scripts/render-one-button-full.cjs`
10. `node projects/one-button-game-design/production/build-video.cjs mix` 후 `assemble`.
11. `node motion-canvas/scripts/caption-one-button.cjs`
12. `python -X utf8 projects/one-button-game-design/production/verify-video.py`. 실제 출력 캡처와 모바일 가독성을 검수하고 QA의 visualReview를 기록한다.
13. `node projects/one-button-game-design/production/finalize.cjs`
14. `node scripts/collect-video-output.cjs one-button-game-design`, `node scripts/build-rebuild-manifests.cjs one-button-game-design`, `npm run media:check`, `npm run rebuild:check`.

Python은 저장소의 `qwen3-tts/.venv/Scripts/python.exe`를 사용한다.
음성 재생성은 같은 바이트/길이를 보장하지 않는다. 반드시 컷·타이밍·양쪽 자막·믹스를 함께 다시 검수한다.
음성·영상·음악·모델 및 압축 미디어는 Git에 넣지 않는다. 로컬 파일을 보존하고 외부 저장소에 따로 보관한다.

이전 final-v1 검수: 두 영상 전체 디코딩, 동일 AAC 해시, 한영 63개 큐, 전 장면 캡처,
모바일 자막 가독성, 편집기 미디어 및 결과 페이지 재생을 확인했다.
`media:check`와 원버튼 프로젝트의 `rebuild --check`는 통과했다.
저장소 전체 `rebuild:check`는 수정하지 않은 `gpt-astra-showcase/rebuild.json`의
기존 갱신 누락으로 실패한다. 원버튼의 재제작 manifest는 현재 제작과 일치한다.
게시 검사는 원본 회원 명단의 미확인/잘린 핸들 때문에 차단된다. 원본 표시를 유지하며 추정으로 해제하지 않는다.

## 2026-09-30 화면 구성 수정 — final-v2

`docs/VIDEO_SCREEN_LAYOUT.md`에 사용자 첨부 네 화면을 먼저 기록했습니다.
인트로는 기존 원본 고양이 로고와 승인된 카드 씬을 재렌더하며 2초입니다.
커비에 Canabalt HD와 Geometry Dash 실제 플레이 발췌를 추가합니다.
16:9 게임은 전체 화면, 레트로 게임은 원본 비율 전체 높이와 같은 프레임의 움직이는 배경 확장입니다.
모든 설명 씬은 직접 편집 가능한 2.5D 면·두께·원근·그림자·카메라 움직임을 사용합니다.
엔딩은 원본 12개 회원 행과 왼쪽 제목·부제, 오른쪽 아래 원본 로고로 10초입니다.
음성의 01·03·06만 재합성하고 나머지는 승인된 v1 테이크를 재사용합니다.
원음에 섞인 별도 게임 음악이 있는 신규 두 예시는 음소거하며, 승인된 Nimbus를 이어 사용합니다.

render-narration.py가 합성/재사용 전에 manifest의 captionsKo/captionsEn을 TTS 출력의 원래 본편 SRT로 자동 지정합니다. 대본을 변경했을 때는 --force-scenes 01,03,06처럼 바뀐 씬을 명시하여 이전 문장의 WAV를 재사용하지 않도록 합니다.
prepare가 본편 SRT에서 정확히 2초를 더한 final-v2/captions.ko.srt와 captions.en.srt를 만들고 manifest를 최종 경로로 바꿉니다.
반복 prepare는 항상 원래 본편 파일을 읽으므로 인트로 지연을 중복 누적하지 않습니다.
KO/EN 원본 본편 SRT, WAV와 타이밍 JSON은 TTS v2 폴더에 보존됩니다.
이전 v1 결과 영상과 source-snapshot은 삭제하지 않습니다.

## final-v2 출력 검수

2026-09-30: 1920×1080 / 60fps, 14074프레임, 234.567초.
두 MP4 전체 디코딩과 동일 AAC 스트림, 한영 63개 큐의 동일 시각을 확인했습니다.
컷 전환을 포함한 자막 81개 구간과 전 장면·추가 게임·모바일 캡처를 검수했습니다.
커비 에그 캐처는 메뉴 대신 세 실제 달걀·폭탄 플레이 범위를 사용하며 원본 시각을 plan.json에 보존합니다.
회원 원본 12행과 작은 로고 사이의 간격을 확인했습니다.
믹스 실측 -16.00 LUFS / -1.84 dBTP, 음성 시작 지연 2초, 본편 게임 비중 60.004%입니다.
최종 사용자 청취·게시 승인과 기록된 권리/원본 음악/외부 백업 항목은 pending을 유지합니다.

최종 수집 후 결과 페이지의 두 영상 재생과 다운로드 네 개를 확인했습니다.
media:check, 원버튼 rebuild --check, 원버튼 TypeScript와 편집기 미디어 재생 검사를 통과했습니다.
저장소 전체 rebuild:check는 기존 gpt-astra-showcase/rebuild.json 갱신 누락으로 실패하며 해당 프로젝트는 유지했습니다.

미리보기 서버는 motion-canvas 폴더에서 node node_modules/vite/bin/vite.js --host 127.0.0.1 --port 9210으로 실행합니다.
Windows에서 Vite의 폴더 감시 때문에 수집 시 EPERM 이름 변경 오류가 나면, 이 작업에서 실행한 Vite 서버를 종료하고 collect-video-output.cjs를 실행한 뒤 서버를 다시 켭니다.
