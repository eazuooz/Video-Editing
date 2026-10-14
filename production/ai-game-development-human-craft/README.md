# AI와 게임 개발 — 현재 한 편의 제작 실행기

현재 작업의 상태는 `projects/ai-game-development-human-craft/production/checkpoint.json` 및 기존 review ledger가 기준이다. 아래 실행기는 다른 영상·자동 반복 작업을 시작하지 않는다.

1. 승인 목소리로 `run-narration.py`를 한 번 실행한다. 현재 실행 중인 작업/lease/chunks를 먼저 확인하고 중복 실행하지 않는다.16GB5070Ti의 실제 여유 VRAM과 다른 Python/연구 작업 부재를 확인한 후 기존 GPU lease 프로토콜을 사용한다. 연구 프로세스 중단/재시작은 하지 않는다.
2. Unity 편집기에서 소스를 갱신한 뒤 `Library/AiCraftProduction.request`의 `build` 명령으로12개 씬을 저장한다. `preflight`는 소량의 검수 프레임, `render`는 실제60fps 캡처다. `sampleFrames`로 입력/구매 전후의 정확한 프레임을 검수할 수 있다.
3. `run-unity.py`는 현재 narration lease가 해제된 다음 `capture-plan.json` 순서로 각 씬을 캡처한다. 동일 입력/정상 완료 파일만 재사용하고, 달라진 기존 결과를 덮어쓰지 않는다.
4. `prepare-media.py`는 권리가 기록된 원본의 선택 구간을 무음1080p60으로 정규화한다. 원본은 보존한다. 실제 in/out과 해시가 `selected-footage/selection.json`에 기록된다.
5. `prepare-scenes.py`는 독립 Motion Canvas 프로젝트28개를 만든다. WAV timing 파일이 없을 때는 **레이아웃 예상 시간**만 생성한다. 최종 출력은 실제 음성과 자막 정렬을 마친 timing으로 다시 생성해야 한다.
6. `sync-media.py`는 로컬 capture 경로/포스터/실제 동영상만 연결한다. 프레임별 C# 상태는 로컬 capture JSON에서 읽으며 Git에 복사하지 않는다.
7. `motion-canvas/vite.ai-production.config.ts`(9199), `render-ai-production.cjs`로 문단별/자막 레이아웃을 확인한다. 실제 캡처와 측정된 음성 시간 없이는 본편 렌더가 거절된다. 예상 자막 시안은 최종 실제 자막 검수가 아니다.
8. 회원 엔딩은 `member-scene.tsx`와 `render-ai-members.cjs`.2026-09-29 원본12행의 프로필/표시 이름/배지를 그대로 유지하고, 원본 고양이 로고·정확한 제목·10초를 검수한다. 기존 text-only 샘플은 사용하지 않는다.

음성 완료 뒤의 순서:

1. `align-captions.py`: 한 번 수행한 full ASR의 단어 시각을 씬별로 분리해 정렬한다. 새 ASR을 실행하지 않는다. `complete-asr-scene-review.json`의 **전체** 원문/인식문을 직접 대조하고 숫자·고유명사·발음의 차이를 검토한다. 정렬 커버리지만으로 내용/발음을 승인하지 않는다.
2. `prepare-scenes.py`, `sync-media.py`: 확정 문단/자막 시간과 완료된 Unity 캡처를 연결한다. 실제 자막 상태가 없으면 최종 렌더가 거절된다. `render-ai-production.cjs --scenes=01,...,28 --captions`의 현재 타이밍과 모든 이동/구매 전후를 검토한다.
3. `build-audio.py`: 원본 보존, 일정한 씬 게인, 연속 음악과 음성 기준 음악 덕킹으로 믹스한다. 새 믹스의 전체 ASR은 한 번 별도로 수행한다. `audio/mix-report.json`의 실측값을 확인한다.
4. `render-ai-production.cjs --scenes=01,...,28 --render`: 현재 입력의28개 시각 씬을 순차 렌더한다. `assemble-video.py`는 원래2초 브랜딩과10초 회원 엔딩을 붙이고 같은 믹스를 연결한다. 이후 `prepare-scenes.py`로 편집기의 전체 믹스도 연결한다.
5. `caption-ai-production.cjs`: 기존 CaptionBox의 실제 그리기 코드로 모든 자막을 만든다. `--burn`은 같은 자막 PNG를 재사용해 clean에 합성한다. 원래 body SRT를 보존하고 `shared/output/<slug>/final.ko.srt`, `final.en.srt`에2초를 더한 납품 자막을 별도로 만든다.
6. `check-delivery.py`, `check-caption-pixels.py`, `inspect-audio.py`: 새 출력의 전체 프레임 디코드/PTS/AAC, 모든 자막 및 경계의 실제 픽셀, 원본→내레이션 stem→최종 파일의 국소 레벨을 확인한다. 픽셀 비교는 사람/에이전트의 내용·동작 검토를 대신하지 않으며 미해결 음량 의심 구간과 실제 청취는 그대로 pending으로 남긴다.
7. `prepare-publishing.py`: 실측 챕터/한영 소개/필수 라이선스/과외 링크/고정댓글 원문만 준비한다. 외부 업로드를 하지 않는다. 납품 전 manifest의 자막 경로를 위 final SRT로 연결하고 collector를 실행한다.

검수/보존: 원본 PCM, 현재 full ASR과 단어 시각, 내레이션 단독 트랙, 현재 믹스의 국소 음량, 최종 mix ASR, 전체 decode/PTS/자막/움직임을 기존 원장에 연결한다. 현재 전체 영상이 완료된 것으로 간주하지 않는다. 현재 요청 중인 화면 비율 예외는 사용자 응답 없이 승인하지 않는다.

최종 경계: clean/captioned/KO/EN 네 파일을 collector로 모은 뒤 **전체 자막 포함 완성본을 Google Drive에 먼저 업로드**한다. 해당 버전을 사용자가 검수하기 전에는 YouTube에 업로드하지 않는다. 다른 영상으로 넘어가지 않는다.
