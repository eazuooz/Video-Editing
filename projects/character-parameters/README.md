# 능력치는 어떻게 캐릭터의 개성을 만들까?

## 2026-10-10 현재 실측·믹스 이후 체크포인트

이 절과 `production/latest-checkpoint.json`의 실제 후속이 아래 초기 prototype/TTS 진행 기록보다 우선한다. 현재 대본은12씬37KOEN문단이며 두 명확화 문단의 현재 선택만 반영했고 나머지35문단과 원본 음성을 보존했다. source-action-bank-v2는20고유 행동 창이고, 원본 연구 영상·음성을 새 영상으로 복제하지 않았다.

v4 입력은325변경 표본55판과 해시가 같은520기존 표본을 직접 검수했다. `production/selected-input-direct-review-v4.json`과 채택된 `production/final-v1/plan.json`을 따른다. 본편22,677프레임(377.95초)은 실제게임13,606/검정설명9,071프레임으로60:40의 오차0.2프레임이다. 고양이120/회원600프레임을 포함한 최종길이는23,397프레임,389.95초다. 안내는 실측15.680041667초의 자연스러운3문장이며20–30초로 허위 표시하거나 늘리지 않는다.

현재12PCM은8,430,001샘플,351.250041667초이고17개 배치에 각각 정확히 보존했다. final mix session44684와 현재 믹스12whole+37독립완결문단 ASR session69501은 실제 outerexit0 종료를 확인했다. `full-mix-asr-review.json`은 전체 기대글/인식글/단어/현재PCM 해시를 직접 대조한 기록이며 인식 대안과 사람 전체청취·발음 pending을 보존한다. Nimbus 연속 믹스의 현재 AAC 실측은−16.05LUFS/−2.01dBTP다.

guarded pair session24722와 최종 인코딩 픽셀 worker session45129는 실제 outerexit0 종료했다. 두 영상 각각23,397프레임1080p60/90,000timebase/PTS1,500/전체decode0와 동일AAC를 확인했다. 1,266계획 표본211판을 모두 직접 읽고 201KO/95EN,41컷,37완결문맥,17PCM배치와17검정 입체 부분의 최종 자막·UI·움직임을 검수했다. `production/final-v1/final-pixel-direct-review-v1.json`과 실제 seal exit0가 현재 기술 QA 승인 근거다. collector session97368 실제exit0/chunk994424 뒤4파일 원본/output SHA256 일치를 확인했다. 완료 미디어/ASR/QA/추출/수집/종료세션은 반복하지 않는다.

실제 새 ID `nic5Sp6dylQ`는 검수된 captioned MP4 한 번 선택 뒤 비공개로 저장·재열람했다. SD·HD와 저작권·광고 검사가 문제없이 완료됐고 한영 수동201/95큐, 별도 영어 정보,13실측챕터, 썸네일,00초 코칭 카드와379.95–389.95초 회원 구간의 세 요소를 저장·재열람했다. 처리 후 실제60fps UI의6:19:57–6:29:57로 원래10초 구간에 정확히 맞췄다. 1080p60/CCoff 업로드5초 검정 입체와10초 실제게임에서 고정 자막·UI·원래 방송 크레딧을 직접 읽었다. `publishing/private-settings-direct-review-v1.json`과 실제 receipt를 따른다. 제작 기록482개 최종blob를 실제 production commit `d4e15fdc562771bd10beb6ca39fdbe2cd090b7d0`로 일반push했고 local/remote와 외부index 보존을 확인했다. 현재Studio의23개 미래예약·10/30빈슬롯을 읽은 뒤2026-10-30 오전09:00 Asia/Seoul/GMT+0900 공개예약을 실제 저장·재열람했고, 목록 재접속에서24개 미래예약과 기존23날짜 보존을 확인했다. 예약 증거19개 명시blob도 실제 `11efb5b2265f509f2aabaa8a595eef33b2aa5c0e`로 일반push한 뒤 local/remote와 모든blob·외부index 보존을 확인했다. 최종 handoff는 이미 존재하는 이 두 commit만 기록하며 미래 자기SHA를 추정하지 않는다. 사람 전체청취·발음·최종 공개권리·자동더빙·optionalCC·게시후 댓글은 pending이다. 전달 썸네일1+최소 게시 증거3 PNG만 개별 검수/registry/정확ignore예외로 준비했고 QA·원본·미디어는 local-only다.

이번 CPU 믹스/ASR/pair/QA 단계에서 연구pause/kill/suspend/외부lease삭제는0이다. TTS의 원래 연구 재개 증거는 이미 완료된 handoff 기록으로 보존하며 CPU 작업에서 새 연구 재개를 했다고 주장하지 않는다.

## 초기 준비 기록

현재 독립12씬/37KOEN문단 전체 대본·안내 약속을 직접 대조했다. 공식 Rivals of Aether/Dungeons of Aether의19개 고유 행동 창은 독립 해설 작성용으로 확보·검수했으며 실측 배정과 최종 자막 검수는 남아 있다. 원본 강의는 개념 연구용이다.

검정2.5D 구조 prototype은 v1 전체74표본13판, v2 수정32표본6판, v3 남은 글자 전환26표본5판을 모두 직접 읽었다. 현재 선택은12씬/37문단 상태의 기본74표본과 전환20표본, 총94표본17판이다. 발판·상태·경로 라벨의 여백, 통로의 두 적 가림 순서, 현재 효과→별도 STRIKE 글자 전환을 수정했다. 선택 표본의910이하 자막 공간은 비어 있다. `production/black-structural-direct-review-v3.json`은 무음 구조와 해당 표본만 승인하며 실측 음성·전체 연속 애니메이션·최종 고정자막·완성 영상 승인이 아니다. 모든 역사 렌더와 QA 파일은 보존한다.

단일 음성 배치 session59763은 실제 exit0으로 종료했고12개 현재 PCM의 총 실측은347.600041666667초다. 학습 `train_wireframe_p124_43`의 최종 저장·검증·done 뒤 owned lease `f1b25da1-321e-4515-9916-4a2a0a21bfcd`로 독점 실행했으며, 종료 뒤 원래 command/cwd로 연구 큐 PID58008/create1791585361.796079의 실제 `waiting_for_resources` 상태를 확인했다. `production/research-handoff-verification-v2.json`이 근거다. 첫 v1 요청의 의존성 오류와 실제 연구 복원은 별도 역사로 보존하고 완료 TTS를 재실행하지 않는다. 현재 전체 음성 ASR는 단일CPU2/GPU0 worker PID69136/create1791585412.338057/session57058로 진행하며 전체·독립 문맥 승인은 아직 없다. 도입 음성은15.680041666667초의 자연3문장이고20–30초라고 표시하거나 늘리지 않는다.

얌얌코딩 노랑·흰 삽화 썸네일은 전체 직접 검수 후 동일 픽셀의 업로드용 PNG(2,096,365bytes)를 준비했다. 한영 제목·설명·정확 링크·댓글과12개 챕터 이름은 준비·직접 읽기만 완료됐고 챕터 시간은 미실측이다. 음성 전체·독립 문맥 ASR, 실측60:40, Nimbus 믹스, 최종 pair/QA/4파일, 업로드/실제 예약/Git은 남아 있다. actualID는null,10/30 오전09시는 목표일이며 플랫폼 예약이 아니다. 사람 전체청취/발음·최종 공개권리와 이미지 Git 등록도 미완료다.
