# 게임 시나리오 쓰는 법: 선택과 순서가 바뀌어도 말이 되게

2026-10-02 final-v1: 실제 최종 렌더·전체 기술 검수·4개 파일 수집·YouTube 비공개 저장과 설정 재열람을 완료했다. 영상은 692.966667초(11분33초), 1920×1080/60fps다. 기존 M22USoVEEPY는 clean 영상의 선택형 자막 업로드로 보존하며 기본 채널용 자막 요구를 충족하지 못했다. 사용자 재확인에 따라 검수된 고정 한글 자막판을 **AlRRtW5oz88**로 새 비공개 업로드했다. 플레이어 CC가 꺼진 실제 업로드 화면 두 구간에서도 아래 가운데 흰 박스 자막이 보임을 확인했다. [현재 자막판 영수증](publishing/youtube-upload-captioned.json)이 실제 저장 완료 근거다. 공개·예약은 사용자가 직접 한다. Git 전달은 [배치 대기열](../../production/batches/sakurai-planning-game-design/queue.json)의 실제 SHA·푸시 증거를 확인한다.

전체 21개 기존 프로젝트의 실질 대본과 현재 Studio 검색을 대조한 [사전 검토](../../production/batches/sakurai-planning-game-design/preflight/game-writing.json)를 통과했다. DOS2 공식 대화·게임 마스터 자료와 직접 만든 「항구의 봉인」에서 정보의 주인, 물건 소유, 동료의 부재, 분기 합류와 필수 사실 회복을 보여 준다. 출처 영상의 전체 대본·음성을 복사하지 않았으며 화면에 없는 내부 구현은 단정하지 않는다.

## 설명 사이에 실제 동작을 추가한 최종 타임라인

[최종 계획](production/final-v1/plan.json)은 독립 16장/80문단이다. 기존 여섯 흰 2.5D 설명의 주장과 승인 음성을 보존하고, 설명 사이에 네 개 새 관찰 장과 정상 속도의 실제 선택·결과 컷을 더했다. 본편 680.966667초 중 실제 동작 408.583333초, 설명 272.383333초이며 60:40 오차는 0.2프레임이다. 원본 고양이 인트로 2초와 원본 회원 프로필·이름·배지·로고의 10초 엔딩은 비중에서 제외한다. 47개 실제 컷은 반복·저속·무관한 대기로 늘리지 않았다. 계획의 출처 인아웃·보이는 행동·관찰 지점·설명 연결을 함께 읽는다.

공식 자료의 화면 하단 UI를 보존하기 위해 같은 컷의 흐린 전체 화면 배경 위에 선명한 게임 화면을 합성했다. 모든 한글 자막은 아래 가운데(960,970)의 boxed-white-forest-v1이며 최대 두 줄이다. 자체 실제 이야기 게임은 전체 화면이다. 회원 엔딩에는 정확한 제목 `멤버쉽가입 감사드립니다.`과 과외 URL을 원본 회원 정보를 가리지 않게 표시한다.

## 실제 기술 검수와 수집

[최종 QA](production/final-v1/qa.json)는 두 MP4의 전체 41,578프레임 디코딩, 길이·한영 자막 동일 타이밍·동일 AAC를 확인했다. 현재 영상의 174개 자막/컷 구간과 20개 구성 화면을 직접 검수했고, 선택한 47개 실제 컷의 첫·중간·끝 141화면도 검수했다. 최종 AAC는 −16.04 LUFS, −2.30 dBTP다. [전체 믹스 ASR 직접 대조](production/final-v1/full-mix-asr-review.json)와 집중 재검사에서 모든 80문단의 누락·반복·임의 인사·끝소리를 확인했다. ASR 철자 오인식과 실제 음성 문제를 구분하며 사람 청취를 완료했다고 주장하지 않는다.

음성 정규화와 2초 인트로 지연을 한 필터에서 처리하던 FFmpeg 버퍼 문제는 두 단계로 분리했다. [타이밍 수정 증거](production/final-v1/mix-timing-correction.json)에 현재 음성 첫 96,000 스테레오 샘플의 정확한 2초 무음과 전체 길이를 기록했다. 승인 기존 음성을 보존했으며 거부된 장면만 같은 목소리로 수정했다. 연속 Nimbus와 원래 승인 화자를 유지했다.

`node scripts/collect-video-output.cjs game-writing`를 실제 실행하여 [수집 기록](production/delivery-output.json)의 해시와 일치하는 clean MP4·한글 자막 MP4·KO SRT·EN SRT를 [output/game-writing](../../output/game-writing/index.html)에 모았다. 양언어 각각 154큐다. [output/index.html](../../output/index.html)이 전체 확인 진입점이다.

[자체 상태 검증](production/playtest-state-proof.json)은 13개 시나리오·4,581개 도달 상태·2,930개 표시 선택, [실제 UI 검증](production/playtest-ui-proof.json)은 여섯 경로·58개 입력·0오류를 실행했다. 기술적 일관성은 이야기의 재미·감정·이해에 대한 사람 평가를 대신하지 않는다.

## 비공개 저장과 재개

새 썸네일·사실에 맞는 한영 제목/설명·기존 채널 코칭/Discord/회원 링크를 적용했다. 수동 KO/EN SRT와 영어 언어의 별도 제목/설명을 게시 후 다시 열어 확인했다. 00:00 과외 카드는 하나이며 마지막 10초에는 관련 채널 재생목록·자기 채널 구독·클릭 가능한 외부 과외 링크를 저장했다. 세 요소 모두 11:22:58–11:32:58(60fps)이다. 비공개·예약 없음·수익 창출 사용, 새 자막판 저작권 검사 완료/문제 없음과 저장 후 광고 검토 알림 해소·설정에 따라 수익 창출·소유권 주장 없음을 확인했다. 새 자막판의 최종 wizard 완료 화면은 다시 열어 관찰하지 않았으며 실제 저장 후 결과와 구분한다. [고정댓글 파일](publishing/pinned-comment.ko.txt)은 비공개 댓글 제한으로 공개 후 적용 대기다. 플랫폼 자동 더빙은 별도 미검수 상태이며 수동 자막 게시를 대신하지 않는다.

[실행 기록](production/execution-sessions.json)의 합성·복구·ASR·촬영·렌더·현재 레이아웃·현재 QA 세션은 종료됐다. 재부팅 전 또는 종료된 runner를 기다리거나 다시 실행하지 않는다. Vite는 실제 살아 있으면 재사용한다. 초기 setup-editorial/setup-scenes/record-preparation/finish-preparation은 현재 최종 계획을 덮어쓰므로 재개 시 실행하지 않는다.

의도적 재빌드 순서는 승인 해시 음성·출처 복원 → prepare-timeline.py와 build-cuts.cjs → build-final.cjs setup → render-reel.cjs → build-final.cjs mix/assemble → apply-current-layout.cjs → 전체 ASR/verify-video.py와 직접 화면 검수 → complete-local-review.cjs의 실제 검수 인자 → 수집이다. `apply-current-layout.cjs`는 공식 자료의 자막 안전 영역과 과외 URL 엔딩을 최종 적용하므로 기본 Motion Canvas 조립만으로 현재 납품본을 대신하지 않는다. 실행 전 현재 계획의 원본/완성 경로와 실행 상태를 확인한다. 현재 완료본을 자동 재빌드하지 않는다.

전체 인간 청취·최종 공개 권리·원래 Audio Library Nimbus 파일·잘린 회원 핸들 원본·외부 미디어 백업은 계속 pending이다. [새 게임 후보](sources/game-candidates.json), [출처](sources/SOURCES.md), [재사용 제작 방식](../../docs/VIDEO_ADDITIVE_REVISION.md)와 프로젝트 manifest를 함께 보존한다. 다음 주제는 picking-sides이며 새 대본 전에 내용 중복과 현재 Studio 근거를 다시 검토한다.
