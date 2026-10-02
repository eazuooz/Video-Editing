# 컴공 1·2학년 공부법 — 백지에서 시작하기

2026-10-02 사용자가 `영상제작 진행해줘`로 제작을 요청했다. **22분48.7초의 최종 자막판·무자막판과 KO/EN SRT461개를 렌더·기술 검수·직접 화면 검수 후 수집했다.** 실제 플랫폼 설정 상태는 `publishing/youtube-upload.json`, 제작 상태는 `production/checkpoint.json`으로 확인한다. 과외 링크는 설명란·엔딩·고정댓글, 자막은 항상 하단 중앙이라는 최신 규칙을 적용했다. 비공개 영상은 댓글을 지원하지 않으므로 댓글 원문은 준비하고 실제 등록·고정은 공개 후 처리할 항목으로 남긴다.

- 읽는 대본: [narration.review.md](script/narration.review.md)
- 장면별 낭독 기준: [narration.ko.json](script/narration.ko.json)
- 화면과 삽입 계획: [outline.md](planning/outline.md), [storyboard.json](planning/storyboard.json)
- 원문 17~24장 보존/보강: [source-map.json](script/source-map.json)
- 출처와 새 촬영 후보: [SOURCES.md](sources/SOURCES.md), [game-candidates.json](sources/game-candidates.json)
- 중복 비교: [검토 기록](../../production/preflight/blank-project-coding.json)

기존 공부법 영상 `OjC6Hhyvybw`의 빈 파일/테트리스 조언과 일부 겹친다. 이번 편은 Linked List 노드·삽입·삭제·경계 조건, 테트리스 최소 구현 순서·후보 검사·회전·두 줄 삭제의 실제 개발과 디버깅, 조건 변경 재구현과 필요한 힌트 이용을 구체적으로 다루는 후속편이다. 기존 완성 파일·공개/예약 영상·활성 배치와 사용자 작업은 변경하지 않는다.

고양이 인트로 → 본편의 실제 개발/플레이테스트 60%와 흰 2.5D 설명 40% → 코칭 안내를 포함한 본편 마무리 → 별도 10초 원본 회원 이미지 엔딩을 따른다. 코칭 안내는 본편 설명 비중에 포함한다. 현재 음성과 컷 실측은 총1368.7초(22분48.7초)다. 본편의 실제 개발814.016667초/설명542.683333초로60:40 오차0.2프레임이며, 인트로2초와 회원엔딩10초는 제외한다. KO/EN 자막461개의 타이밍을 일치시키고 고정 한글 자막은 모두하단중앙(960,970)에 배치했다. 최종 렌더/QA/수집은 checkpoint의 실제 상태를 따른다.

대본 수정은 JSON을 기준으로 하고 읽는 MD 및 화면 계획을 함께 맞춘다. 기존 승인 Qwen 목소리와 연속 Nimbus를 같은 제작 방식 요청에 따라 재사용하며, 새 음성의 ASR/발화 검수와 사람 청취 상태는 구분한다. 34개 한국어·영어 대본 장면은 각 독립 Motion Canvas 씬에 대응하며 인트로/10초 회원 엔딩은 별도다. 실제 녹화는 자체 개발 도구가 소스 코드를 MSVC/JavaScript로 실행하는 화면이며, 상용 IDE나 외부 강의 촬영으로 주장하지 않는다. C++ 중단점은 `inspect` 함수에서 실제 프로세스를 기다리게 하는 계측 방식이다. 원본 녹화의 동작·값·시간·해시를 보존하며 최종 컷은 실측 발화와 함께 확정한다.

후속 명령:

```powershell
node scripts/review-video-duplicates.cjs blank-project-coding --candidate-file production/preflight/blank-project-coding.candidate.json --check
node scripts/build-rebuild-manifests.cjs blank-project-coding
```

중복 검토는 업로드 직전 새 picking-sides 대본까지 읽고 실제 Studio 목록을 확인하여 갱신했다. 기존 배치 대기열에 이 독립 요청을 끼워 넣지 않았다. `output/index.html`에서 최신4파일을 확인할 수 있다.

**비공개 업로드 완료:** https://youtu.be/kcZL02MXtvI — 영상ID `kcZL02MXtvI`를 재사용하며 중복 업로드하지 않는다. KO/EN 수동 자막과 영어 제목·설명, 썸네일, 00:00 과외 카드, 마지막10초의 과외 링크·관련 재생목록·구독 요소를 저장하고 다시 열어 확인했다. 업로드된 시청 페이지의 플레이어 자막이 꺼진 상태에서도 하단 중앙 박스 자막을 확인했다. SD/HD 처리 완료, 수익 창출 사용·자동 미드롤 저장, 자동 검사 완료/발견된 문제 없음이 관찰됐다. 증거는 `publishing/proof/`, 구조화된 기록은 `publishing/youtube-upload.json`에 있다.

비공개 영상의 댓글 미지원은 실제 시청 페이지에서도 확인했다. `publishing/pinned-comment.ko.txt`는 준비됐지만 등록·고정은 사용자가 공개한 뒤 처리해야 한다. 사람의 전체 청취, 승인된 복원 음악의 원래 Audio Library 파일 확인, 외부 미디어 백업은 아직 남아 있다. 공개·예약은 하지 않았다. Git 납품 증거는 `production/git-delivery.json`을 따른다.
