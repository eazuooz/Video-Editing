# 게임 시나리오 쓰는 법: 선택과 순서가 바뀌어도 말이 되게

2026-10-02 체크포인트: 독립 한영 12장/72대사, 새 DOS2 공식 자료 검토, 자체 이야기 게임 `항구의 봉인`, 6개 흰 2.5D 설명과 썸네일을 준비했다. **최종 내레이션·렌더·4파일 수집·YouTube 비공개 업로드는 아직 완료하지 않았다.** 0.1초 템플릿 WAV와 48초 설명 전용 lookdev는 완성 영상이 아니다.

제작 전 기존 활성 보강 대본까지 포함한 21개 프로젝트와 실제 Studio 검색/영상 ID를 직접 비교했다. [사전 중복 검토](../../production/batches/sakurai-planning-game-design/preflight/game-writing.json)는 distinct다. [장별 계획](planning/outline.md)에 주장·실제 동작·관찰 지점·설명 연결·출처 인아웃을 기록했다. 참고 대본의 복사/번역이나 원본 영상·음성 재사용은 하지 않았다.

## 현재 실행과 재개

- 재부팅 전 세션 `67834` / PID `46172`는 합성을 시작하지 못한 채 종료됐다. 재개한 단일 [resource-runner](production/resource-runner.cjs)는 세션 `95867` / PID `8104`다. 실제 현재 상태는 [resource-runner.json](production/resource-runner.json)과 [배치 대기열](../../production/batches/sakurai-planning-game-design/queue.json)을 읽는다. PID는 종료 후 재사용될 수 있으므로 실제 프로세스 명령까지 확인한다.
- 다른 사용자 학습의 GPU 사용 중에는 기다린다. 해당 작업을 중단하지 않는다. 안정적으로 여유가 생기면 이 runner가 승인 Qwen3-TTS 1.7B로 한 번 합성하고 CPU ASR을 이어 실행한다. 살아 있는 runner/TTS와 중복 실행하지 않는다.
- 기다리는 동안 `project.json`과 양언어 대본을 수정하면 입력 해시가 바뀌어 runner가 안전하게 실패한다. 수정이 필요하면 실제 종료 상태를 확인하고 명시적으로 새 실행을 시작한다.
- 합성/ASR 종료는 음성 승인이나 영상 완료가 아니다. 현재 WAV 해시의 72대사를 모두 받아쓰기와 직접 대조하고 반복·누락·발음·임의 인사·끝소리를 검수한다. 실제 거부된 장면만 같은 승인 목소리로 복구한다.
- 재부팅 뒤 Vite 세션 `13616` / PID `20548` / 포트 `9210`을 복구했다. 살아 있으면 재사용한다. 이전 Vite와 종료된 소스 샘플링·디코딩·UI 검증·lookdev 세션은 다시 기다리지 않는다.

## 준비된 증거와 남은 제작

[source-decode.json](production/source-decode.json)은 두 공식 자료 전체 디코딩의 실제 결과다. [출처 기록](sources/SOURCES.md), [새 게임 후보](sources/game-candidates.json), [native 검토](sources/native-review.json)는 화면에서 보이는 사실과 사용 조건/미완료 공개 권리 판단을 구분한다. 최종 선택 컷의 첫·중간·끝과 전환은 음성 실측 뒤 다시 검수한다.

[자체 상태 검증](production/playtest-state-proof.json)은 재부팅 뒤 알려진 규칙의 짧은 확인 경로를 보강해 13개 시나리오, 도달 가능한 4,581개 사실/대화 상태와 표시 선택 2,930개의 유효성을 실행했다. [실제 UI 입력](production/playtest-ui-proof.json)은 여섯 경로/58개 입력과 화면 결과를 확인했다. 이전 11개/2,209상태/1,424선택 및 다섯 경로/52입력은 별도 `-pre-reboot.json`에 보존한다. 이는 사람의 재미·감정·이해 검토를 대신하지 않는다. [실제 녹화](production/capture-story-takes.json)에 정상 속도의 새 입력과 각 선택/결과 시각을 기록했으며 [전체 디코딩/샘플](production/story-take-audit.json)은 최종 컷 선택을 위한 증거다.

[lookdev v3 결과](production/lookdev-render-result-v3.json)와 [시각 검토](production/lookdev-visual-review.json)는 설명 6개/12개 1080p 샘플의 준비 검수다. 분기 합류와 결과 보존, 정보 전달, 물건 소유 토큰, 필수 사실 재확인을 표시한다. 최종 영상 자막 검수는 아직 남아 있다. `timing.ts`의 `ACTUAL_MEDIA_READY=false`와 계획 시간은 실제 음성·미디어가 검증되기 전 유지한다.

본편은 실제 동작 60% / 설명 40%로 실측한다. 인트로 2초와 원본 회원 엔딩 10초를 제외하고 최대 1프레임 반올림만 허용한다. 도식/숫자 테스트는 설명이며, 실제 게임도 무관한 대기·루프·저속으로 비중을 채우지 않는다. 각 설명 사이의 행동/새 해설을 충분히 담아 참고 영상보다 길어질 수 있다. 같은 승인 목소리와 연속 Nimbus를 유지한다.

음성 검수 뒤 컷별 실제 게임 녹화/공식 자료 → 실측 60:40 타이밍·믹스·KO/EN SRT·챕터·엔딩 동시 확정 → 최종 렌더 → 모든 큐/컷 시각 검수·전체 ASR·디코딩·음량/true peak·두 MP4 동일 오디오 → `node scripts/collect-video-output.cjs game-writing` → 모든 저장 규칙으로 새 비공개 업로드 → rebuild/media 검사·선택 커밋·일반 푸시를 진행한다. 공개와 예약은 사용자가 직접 한다.

`setup-editorial.cjs`, `setup-scenes.cjs`, `record-preparation.cjs`는 초기 생성용이다. 현재 준비물이나 향후 실측 타이밍을 덮어쓰므로 재개할 때 자동 재실행하지 않는다. `finish-preparation.cjs`도 준비 검수 증거용이므로 최종 제작 단계에서는 재실행하지 않는다. 관련 규칙은 [VIDEO_ADDITIVE_REVISION](../../docs/VIDEO_ADDITIVE_REVISION.md), [VIDEO_WORKFLOW](../../docs/VIDEO_WORKFLOW.md), [NARRATION_AUDIO_STANDARD](../../docs/NARRATION_AUDIO_STANDARD.md), [YOUTUBE_PUBLISHING](../../docs/YOUTUBE_PUBLISHING.md)를 따른다. 사람 청취·공개 권리·원래 Nimbus 파일·잘린 회원 핸들·외부 백업은 증거가 없으면 pending을 유지한다.
