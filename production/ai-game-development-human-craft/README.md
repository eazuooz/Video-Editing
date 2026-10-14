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

검수/보존: 원본 PCM, 현재 full ASR과 단어 시각, 내레이션 단독 트랙, 현재 믹스의 국소 음량, 최종 mix ASR, 전체 decode/PTS/자막/움직임을 기존 원장에 연결한다. 현재 전체 영상이 완료된 것으로 간주하지 않는다. 현재 요청 중인 화면 비율 예외는 사용자 응답 없이 승인하지 않는다.

최종 경계: clean/captioned/KO/EN 네 파일을 collector로 모은 뒤 **전체 자막 포함 완성본을 Google Drive에 먼저 업로드**한다. 해당 버전을 사용자가 검수하기 전에는 YouTube에 업로드하지 않는다. 다른 영상으로 넘어가지 않는다.
