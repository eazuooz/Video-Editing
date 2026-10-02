# 원문 순서 복원 영상 v2

사용자 지시: “처음준 대본 순서대로 내용 그대로 만들어줘 영상.”

취업의 어려움 → 직접 구현하지 못하는 문제 → AI 사용 방식의 차이 → 라이브 서비스와 기존 코드의 복잡성 → 신입 성장의 첫 계단 → 백지 구현 훈련 순서와 원래 문장을 보존한다. 원문을 다시 요약하지 않는다. 코칭 안내는 원래 결론 다음에 별도로 붙인다.

최초 첨부의 16장은 첫 문장 중간에서 끊어졌다. 그 조각을 보존하고, 사용자가 별도로 제공한 19장의 같은 테트리스 사례로 연결했다. `original-preservation-audit.json`에 재구성 범위가 표시되어 있다. 나머지 원문 장은 공백·마크다운을 제외한 문장 순서와 내용이 일치한다. 취업 관련 추론 표시와 개인적인 교육 경험이라는 유보도 유지한다.

## 보존과 현재 상태

- `checkpoint.json`은 현재 진행 단계다. 최종 완료 여부는 `qa.json`, 업로드 영수증과 Git 증거로 판단한다.
- `baseline/`은 거절된 v1의 대본·메타데이터·검토 기록과 로컬 MP4/믹스를 보존한다. 이전 비공개 영상 `kcZL02MXtvI`와 기존 업로드 영수증을 덮어쓰거나 삭제하지 않는다.
- `narration.ko.json`이 원문 대본이다. `narration.tts.ko.json`은 영어 기술 용어의 발음만 풀어 쓴 합성 입력이다.
- `narration.en.json`은 전체 118문단의 번역이다. 양 언어 자막의 번호와 시간은 같다.
- 화면 설명 원본은 `motion-canvas/src/projects/blank-project-coding/restored-v2/`에 있고, Linked List 원본은 `manim/projects/blank-project-coding/linked_list.py`에 있다.

## 실제 영상과 설명의 분류

`sources.json`, `source-pools.json`, `concept-connections.json`을 함께 읽는다. 외부 Tetris 플레이와 GDQuest의 실제 Godot 편집·실행을 사용한다. 같은 출처의 예전에 쓴 구간, 밈·사무실 스톡·정적인 홍보 화면은 제외한다. 각 외부 컷에 제작자·제목·원본 주소·CC 라이선스 주소·수정 사실을 표시한다. 원음은 제거하고 승인된 내레이션과 Nimbus를 계속 재생한다.

직접 만든 게임이나 예전 workbench 예시는 이번 실제 영상 분량에 쓰지 않는다. Linked List의 Manim 애니메이션은 설명 40%에 속한다. 인트로 2초와 멤버십 엔딩 10초를 제외한 본편은 실제 행동 60%, 설명 40%로 측정하며 프레임 반올림만 허용한다. 원문 보존이라는 이번 명시적 수정 요청에 따라 v1의 임의 확장 문단을 이어 붙이는 대신 최초 대본 전체를 복원한다.

## 제작 순서

1. 기존 완료 파일을 먼저 확인한다. `production/start-original-restoration.cjs`는 최초 보존 작업이므로 다시 실행하지 않는다. 대본·소스·미리보기 준비 스크립트도 최종 타이밍을 덮어쓸 수 있으므로 일괄 재실행하지 않는다.
2. `voice.manifest.json`으로 승인된 Qwen 목소리를 재사용한다. 이미 시작한 합성 작업과 겹치는 장 번호를 병렬 생성하지 않는다. 이번 합성은 1–35장 파일을 보존한 뒤 남은 번호를 `voice-part-a`/`voice-part-b`로 분리했다. ASR 감시는 전체 manifest를 읽는다.
3. 실제 WAV의 SHA256, 독립 받아쓰기, 모든 차이, 끝음 측정값을 확인한다. 필요한 장면만 이전 테이크를 보존한 뒤 재생성한다. 사람의 최종 청취는 별도이며, 자동 받아쓰기로 완료 처리하지 않는다.

   이번 43번 장면의 반복 목록과 52번 장면의 숫자는 반복 합성에서도 누락되어, 같은 목소리로 이미 검수한 동일 문장·숫자를 문장 쉼 또는 목록 경계에서 연결했다. `voice43-editorial-repair.json`, `voice52-editorial-repair.json`에 소스 해시와 구간을 기록했고 연결 후 전체 장면을 다시 받아썼다. 56번 코칭 부록은 이전 검토본의 검수된 코칭 안내 두 문단을 재사용했다(`voice56-reuse.json`). 원문 0–24장의 문구와 순서는 그대로이며 코칭 부록은 원래 결론 뒤에 있다.
4. `voice-approval.json`의 56개 현재 해시가 검수되면 `build-timeline.py`를 실행한다. 최종 컷·본문 WAV·한영 SRT·설명 씬 길이가 함께 생성된다. 원문 자막 누락과 60:40을 검사한다.
5. `node check-reel-timing.cjs`와 `node caption-video.cjs --layout-only`를 통과시킨다. `render-reel.cjs`, `render-cuts.cjs media`, `mix-audio.cjs`는 독립 작업이다. 소스 컷이 끝난 다음 `render-cuts.cjs reel`을 실행한다. 두 컷 작업은 같은 plan을 쓰므로 동시에 실행하지 않는다.
6. `assemble-final.cjs` 후 `caption-video.cjs`를 실행한다. 자막은 모든 컷에서 중심 `(960,970)`을 유지한다. 코드·게임판은 920px 위, 자료 출처는 1033px 아래에 배치한다. 긴 자막은 문구를 나누고 위치를 옮기지 않는다.
7. `verify-video.py --cuts-only`, `verify-video.py`, `make-caption-strips.py`, `verify-mix-alignment.py`로 실제 파일을 검사하고 모든 컷과 자막 이미지를 직접 확인한다. `build-editor.cjs`와 `check-reel-timing.cjs --full`로 56개 편집 씬과 동일 믹스의 시간도 확인한다.
8. 최종 QA 후에만 현재 `project.json`을 새 manifest로 바꾸고 `node scripts/collect-video-output.cjs blank-project-coding`을 저장소 루트에서 실행한다.
9. `prepare-publishing.cjs`는 측정된 챕터, 원래 채널 하단 설명, 한영 메타데이터, 고정댓글 원고, 별도 v2 업로드 영수증을 준비한다. 자막이 영구 포함된 MP4를 비공개로 업로드하고 플레이어 CC를 꺼서 확인한다. 기존 영수증은 보존한다.
10. 코칭 카드 00:00, 마지막 10초의 코칭 링크·관련 재생목록·구독, KO/EN 수동 자막과 영어 메타데이터, 광고 검사를 실제 UI에서 확인한다. 비공개 영상의 고정댓글 게시·고정은 대기 상태다.
11. 재제작 manifest와 미디어 검사를 통과한 후 이번 영상의 코드·대본·증거만 커밋·푸시한다. 영상·음성·BGM·압축 미디어는 Git에 넣지 않는다.

실제 렌더와 업로드가 끝나기 전에는 준비된 스크립트나 미리보기를 완성 영상으로 표시하지 않는다.
