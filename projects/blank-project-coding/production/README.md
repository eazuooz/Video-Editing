# 백지 구현 영상 제작과 재현

최신 상태는 `checkpoint.json`, `final-v1/local-pipeline.json`, 프로젝트 매니페스트와 실제 업로드 영수증으로 확인한다. 이 문서는 완료 영수증을 대신하지 않는다. `start-production.cjs`는 최초 초기화용이므로 재개할 때 다시 실행하지 않는다.

## 보존한 입력과 검수

- `source-snapshots/actual-v1~v3`: 초기 녹화의 실제 소스 버전. 최신 작업 코드는 `../examples/`다.
- `capture-report.json`: 사전 촬영의 실제 입력·네이티브 C++ 실행·JavaScript 상태·파일 해시. 버그가 있던 초기 테이크도 보존한다.
- `actual-source-review.json`와 `../planning/storyboard.json`의 `preNarrationSourceEvidence`: TTS 전에 읽은 소스 인/아웃과 주장·관찰 동작·도식 연결.
- `voice-approval.json`: 현재 34개 음성의 해시, 전체 ASR 차이 검토와 종결부 측정. 인간 청취는 별도로 pending이다.
- `accepted-voice-repairs.json`: 09의 20+조사 발음, 16의 도입, 20의 Recognition 발음을 더 명료한 문장으로 보정한 실제 후보와 승인 근거. 원래 WAV/ASR은 출력 폴더의 `superseded/`에 남긴다.
- `final-v1/capture-final.json`와 `actual-visual-review.json`: 현재 음성 문단 시점에 맞춰 새로 실행한19개 예제와 직접 화면 검수. `supersededReason` 또는 중단 상태의 테이크는 사용하지 않는다.
- `final-v1/plan.json`: 인트로120프레임, 본편 실제 동작48841프레임/설명32561프레임, 엔딩600프레임. 총82122프레임/1368.7초, 본편60:40 오차0.2프레임.

## 현재 로컬 파이프라인

1. `prepare-timeline.py`가 현재 음성 승인 해시를 확인하고 KO/EN461개 자막과 전체 타임라인을 만든다. 설명을 자르지 않고 필요한 설명 읽기 시간을 추가했다.
2. `capture-final.cjs`는 자체 워크벤치의 실제 동작을 문단별 시점에 맞춰 기록한다. 소스가 바뀌거나 음성이 바뀌면 기존 테이크를 보존하고 해당 장면을 다시 촬영한다. 녹화 중 다른 프로세스가 같은 보고서를 수정하지 않는다.
3. `build-final.cjs setup`으로 편집기 계획을 동기화한 뒤 `check-reel-timing.cjs`로 Motion Canvas가 계산한 각 장면 프레임을 대조한다. 첫 장면 초기화 프레임을 고려해 인트로 트윈을119/60초로 조정했으며 전체 인트로는 정확히120프레임이다.
4. `render-reel.cjs`는15개 설명과 인트로/엔딩을 렌더한다. 전용 Vite는 `motion-canvas/vite.blank-project.config.ts`, 포트9342다. 동시 작업 중 다른 영상의 WAV 교체가 Windows EBUSY를 일으켰으므로 바이너리 미디어를 파일 감시에서 제외한다. 중단된 첫 출력과 로그는 보존했다.
5. `build-final.cjs mix`는 같은 승인 음성/Nimbus로 전체 믹스를 만든다. `verify-mix-alignment.py`는 현재 원음→음량 보정 음성의 짧은 파형 구간, 보정 음성→최종 AAC의 음량 포락선을 단계별로 비교한다. 동적 음량 보정으로 달라진 장기 음량 비율을 시간 오차로 오인하지 않는다. 최초 진단도 보존한다.
6. `finish-local.cjs`는 기존 설명 렌더 완료를 기다린 뒤 계획 동기화→전체 조립→고정 한글 자막→기술 QA를 순차 실행한다. 재개할 때 같은 컨트롤러를 중복 실행하지 않는다. 최종 자막 중심은 모두(960,970)이며 충돌이 나면 원래 화면/큐 길이를 고친다.
7. `verify-video.py`의 전체 디코딩·프레임·AAC 동일성·한영 타이밍 검사 뒤 실제 최종 화면을 직접 검토한다. QA 파일 생성만으로 시각 검수를 완료했다고 기록하지 않는다.
8. `node scripts/collect-video-output.cjs blank-project-coding`으로4개 납품 파일을 수집한다. 검수가 완료되면 `prepare-publishing.cjs`, 공용 `prepare-youtube-upload.cjs` 순서로 설명/챕터/비공개 영수증을 준비한다. 기존 영수증을 재생성하지 않는다.

업로드는 고정 한글 자막판을 사용한다. 실제 Studio에서 한영 수동 SRT, 영어 제목/설명, 썸네일, 시작 카드, 마지막10초의 과외 외부 링크·재생목록·구독과 광고 검사 결과를 확인한다. 비공개 영상의 고정댓글은 공개 후 처리할 항목으로 남기며, 댓글을 위해 공개 상태를 바꾸지 않는다.

영상·음성·음악·미디어 압축 파일은 Git에 넣지 않는다. 재현 매니페스트와 미디어 검사 후 이 프로젝트와 승인된 공통 규칙 변경만 선택 커밋/일반 push한다. 사람 청취, 원래 Audio Library 파일 확인, 외부 미디어 백업과 공개 판단의 pending 상태는 실제 증거 없이 바꾸지 않는다.
