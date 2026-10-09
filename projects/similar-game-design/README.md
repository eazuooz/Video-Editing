# 비슷한 게임, 왜 새로 할까? 플레이어가 고를 이유를 만드는 설계

2026-10-09 현재: 24씬·73독립 한영 문단, 원래 PCM 605.540083333초를 보존한 최종 입력과 Nimbus 믹스를 채택했다. 본편은 실제 게임 21,827프레임·설명 14,551프레임, 총 36,378프레임이며 원본 고양이 120프레임·회원 600프레임을 더한 전체는 37,098프레임/618.3초다. 본편 60:40 오차는 0.2프레임이다. 400KO/148EN과 모든 입력 664샘플·111판을 직접 검수했고, 최종 혼합 ASR 24전체장+24독립 완결 문맥 및 현재 PCM 샘플을 직접 대조해 기술 검수를 봉인했다. 인식 모호성과 사람 전체 청취·발음 pending은 보존한다. 근거는 `production/final-v1/plan.json`, `full-mix-asr-review.json`, `mix-settings.json`과 현재 체크포인트다.

최종 clean/captioned 합성은 실제 종료0·두 전체 decode0·90000 PTS·동일 AAC·−15.99 LUFS/−1.99 dBTP를 확인했다. 1,810프레임/302판의 최종 자막·컷·입체 움직임을 모두 직접 검수해 기술 QA를 봉인했고, clean/captioned/KO/EN 4파일 수집과 소스 바이트 일치를 확인했다. `production/final-v1/final-pixel-direct-review-v1.json`과 `production/current-collection-verification-v1.json`이 근거다. 현재 단일 새 비공개 기본 업로드 `_p1IqDeg6YE`가 전송 중이며 전체 설정·플랫폼 검사·업로드 픽셀·Git 전달은 아직 pending이다. 준비된 파일이나 전송 중 상태를 완료로 표시하지 않는다. 요청 전에 착수한 이 영상은 흰 2.5D를 유지하며, 검정 설명 팔레트는 다음 미착수 영상부터 적용한다.

아래 13장/51문단은 최초 대본 준비의 역사다. 현재 제작의 24씬/73문단과 구별한다.

독립 대본 준비 단계. 공식 원본 전체 화면 논증과45개 기존개념/관련전체KOEN/현재Studio 비교를 완료하고, 공식게임43 native+10 edge/crop 판을 직접 읽은 뒤 작성했다. 실제 제작/음성/최종픽셀/수집/비공개 저장은 아직 완료되지 않았다.

현재 script/narration.ko.json 및 narration.en.json의51문단/13장은 같은 질문/순서/예시/유보 표현을 담는다. planning/outline.md와 sources/game-candidates.json의258초 자료은행은 PCM실측 전에 만든 계획이다. 최종60:40 승인이 아니다.

GPU TTS는 현재 연구의 최종 checkpoint/validation/done과 queue job boundary 뒤 협력인계로 단일실행한다. 자신이 만든 token 요청만 해제하고 성공·실패 모두 원래연구큐를 재개해 실제상태를 확인한다. 다른TTS 인계 lease를 변경하지 않는다.

원본고양이2초/회원10초, 승인목소리/Nimbus, 흰실제2.5D, 고정하단자막, 얌얌코딩삽화썸네일을 따른다. 전체ASR/독립문맥과최종픽셀검수 후4파일을수집하고 captioned만 단일비공개로올린다. 사람청취·발음/공개권리/Nimbus원래파일/잘린회원핸들/외부백업/자동더빙/CC/비공개고정댓글은pending을보존한다.
