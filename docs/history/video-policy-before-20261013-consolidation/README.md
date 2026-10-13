# 통합 이전 원문 보관

이 디렉터리는2026-10-13 통합 이전의 정확한 원문 스냅샷이다. 실행 지침이 아니며 일반 제작에서 읽지 않는다. 현재 규칙은 `docs/VIDEO_WORKFLOW.md`, 자동 실행/사용자 확인 경계는 `shared/publishing/video-production-control.json`이다.

`manifest.json`의 원래 경로·보관 경로·SHA256으로21개 파일의 바이트 보존을 확인했다. 원문 내부 상대 링크와 과거 상태는 당시 맥락 그대로 보존되며 현재 상태를 나타내지 않는다. 보관된 AGENTS는 적용 가능한 새 지침으로 오인되지 않도록 `.snapshot.txt`로 저장했다.

통합 대응:

| 이전 누적 내용 | 현재 기준 위치 |
|---|---|
| 개론·인과·기초·원문 보존·중복·4게임·비중·20분 분할 | VIDEO_WORKFLOW의 제작 전 설계표 |
| 상세 인물/물건·검정/흰 예외·2.5D·추적 도형 | VIDEO_VISUAL_STYLE와씬설계템플릿 |
| 실제 게임 확보·권리·최근사용·행동 전후·엔진데모 | VIDEO_GAME_FOOTAGE_POLICY / VIDEO_EXAMPLE_TRANSFER_REVIEW |
| 음성/ASR·GPU인계·연속음악·원음·동일믹스 | NARRATION_AUDIO_STANDARD |
| 고정박스자막·회원원본10초·고양이2초 | CAPTION_STYLE / MEMBERSHIP_OUTRO / VIDEO_SCREEN_LAYOUT |
| 채널삽화썸네일·KOEN/영어정보·링크·광고·예약·댓글 | VIDEO_25D_THUMBNAIL_REVIEW / YOUTUBE_PUBLISHING |
| 보강/시각수정·원본보존·영향범위검사 | VIDEO_ADDITIVE_REVISION / VIDEO_WORKFLOW의재검수표 |
|4파일·미디어제외·필수이미지·임시index·실제push | MEDIA_STORAGE / VIDEO_WORKFLOW |
| 기존 자동계속/자동 다음편/예전예약간격 | 역사로만 보존. 현재manual-one-video-at-a-time이우선 |

세부 기술 기준은 유지하되 같은 규칙의 날짜별 반복과 완료영상 일지는 현재 운영 문서에서 분리했다. 근거 없는 새 승인이나 기존 영상의 미디어 재생성은 수행하지 않았다. 새 plan/ledger 템플릿은 기록 양식이며 모든 과거 실행기에 소프트웨어 가드를 소급 설치한 것은 아니다. 에이전트는 새 작업 전 운영 상태를 읽어야 한다.

Two archived publishing templates use `youtube.*.git.md` in Git, expressing the original two-space Markdown line breaks as `<br>`. The exact `youtube.*.md` bytes remain local and their original SHA256 values are unchanged in `manifest.json`; `gitArchive` records the distributable equivalent.
