# AI와 게임 개발 — 현재 한 편의 제작 실행기

## 현재 수정2차 — 2026-10-15

사용자의 v1 검수 피드백에 따라 내레이션/화면의 참고 영상 메타 표현을 제거하고, 인사·단어 시작·장면 접합의 음성을 다듬는다. `revision-v2-edits.json`이41문단의 한영 변경을 기록한다. 이전 대본·매니페스트·타이밍과 Drive v1은 보존된다.

`run-revision-v2.py`는 승인된 같은 Qwen 모델/레퍼런스로 변경23씬만 생성하고 완결 씬 문맥의 ASR을 캐시한다.01·03 표본의 첫 인사와 이전 누락 단어는 현재 ASR에서 완전하게 인식됐다. 나머지5씬 PCM/ASR은 해시가 같을 때만 재사용한다. 전체 현재 문장을 검토한 뒤 `assemble-revision-v2-narration.py`로 합성/자막 정렬/씬 타이밍을 만든다. 자연스러움에 대한 사람 청취는 기술 검사와 별도로 기록한다.

현재 작업 루트는 매니페스트 `revision.workDir`이다. `revision_paths.py`와 JS 실행기는 새 합성·자막·음량·무결성·영상 검수 결과를 `shared/output/<slug>/revision-v2`에 저장하며, 원래 v1 증거/마스터를 덮지 않는다. Unity 캡처와 확보 원본은 계속 재사용한다. 새 길이에 맞춰 실제 녹화 컷을 다시 배치하고60:40/정상속도/중복 없는 소스 범위를 재검증해야 한다.

Drive 연결 도구의 실제 전송 한도는100MiB다. `prepare-drive-mobile.py --compact`는 현재 전체 길이로 비트레이트를 계산하고720p30 H.2642pass/AAC160k 검수본을 만든다. 전편 디코드·PTS·오디오 연속성·모든 자막 구간/압축 비교와 실제 시각 검수 후 새로운 v2 파일로 업로드한다. 고화질1080p60 master와 기존 Drive 파일은 보존한다. 이 모바일 파일이 게시용 원본으로 자동 승격되지는 않는다.

수정2차의 마지막 기록은 `record-revision-v2-review.py`로 합친다. 현재 전편 내용·발화 접합·음량·자막·영상·네 파일·Drive 원격 바이트 증거가 모두 있어야 실행되며, 과거 v1 전용 `record-final-review.py`의 고정 길이·자막 수·업로드 ID를 사용하지 않는다. 사람 청취와 v2 사용자 검수는 별도로 남긴다.

아래는 기존 제작 순서와 보존된 v1 실행 기록이다. 현재 매니페스트·체크포인트가 우선한다.

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
3. `build-audio.py`: 원본 보존, 문단별 발화 게인과 짧은 피크 보호, 연속 음악과 음성 기준 음악 덕킹으로 믹스한다. 새 믹스의 전체 ASR은 한 번 별도로 수행한다. `audio/mix-report.json`의 실측값을 확인한다.
4. `render-ai-hybrid.cjs`: 현재 입력의28개 시각 씬을 순차 렌더한다. `assemble-video.py`는 원래2초 브랜딩과10초 회원 엔딩을 붙이고 같은 믹스를 연결한다. 편집기의 `project.ts`에도 이 전체 믹스를 연결한다.17장 정상 구매는 가격 설명이 시작되는 문단3에 맞춘다. 최초 렌더의 해당 구간 수정은 `repair-ai-purchase-timing.cjs`에 기록되어 있으며, 기존 영상과 수정 전 소스를 보존하고17장에만 영향을 주는 변경을 검증한 뒤 다른27장을 재사용한다.
5. `caption-ai-production.cjs`: 기존 CaptionBox의 실제 그리기 코드로 모든 자막을 만든다. `--burn`은 같은 자막 PNG를 재사용해 clean에 합성한다. 원래 body SRT를 보존하고 `shared/output/<slug>/final.ko.srt`, `final.en.srt`에2초를 더한 납품 자막을 별도로 만든다.
6. `check-delivery.py`, `check-caption-pixels.py`, `inspect-audio.py`: 새 출력의 전체 프레임 디코드/PTS/AAC, 모든 자막 및 경계의 실제 픽셀, 원본→내레이션 stem→최종 파일의 국소 레벨을 확인한다. 픽셀 비교는 사람/에이전트의 내용·동작 검토를 대신하지 않으며 미해결 음량 의심 구간과 실제 청취는 그대로 pending으로 남긴다.
7. `prepare-publishing.py`: 실측 챕터/한영 소개/필수 라이선스/과외 링크/고정댓글 원문만 준비한다. 외부 업로드를 하지 않는다. 납품 전 manifest의 자막 경로를 위 final SRT로 연결하고 collector를 실행한다.

검수/보존: 원본 PCM, 현재 full ASR과 단어 시각, 내레이션 단독 트랙, 현재 믹스의 국소 음량, 최종 mix ASR, 전체 decode/PTS/자막/움직임을 기존 원장에 연결한다. 완료 여부는 현재 checkpoint와 실제 증거를 따른다. 새 영상의 전체 AAC 패킷이 이미 측정한 믹스와 일치하고 파일 해시/전체 디코드가 검증되면 기존 국소 음량과 ASR 증거를 재사용한다. 최신 사용자 응답에 따라 실제 제작·개발·공예/역사·게임 녹화60%, 설명40%로 구성했다. 자체 Unity는 설명으로 분류하며 루프·저속 재생은 없다.

`finish-local.py --render-pid <PID>`는 이미 실행 중인 이번 렌더의 종료를 기다려 로컬 합성/기술 검수만 순서대로 수행한다. 렌더가 완료된 경우 PID0을 쓴다. 반복 예약이나 자동 업로드를 하지 않으며, `extract-motion-review.py`의 현재 인코딩 프레임을 직접 확인하고 원장에 남긴 다음 납품한다.

02장의 짧은 문 시연은 원본 캡처의2초부터 정상 속도로 사용해 접근→잠김→열쇠 획득→문 열림이 모두 보이게 했다. `repair-ai-door-timing.cjs`는02장만 다시 렌더하고 기존 결과를 보존한다. 합성할 때 각 입력의 정확한 `frames/60` 길이를 ffconcat에 기록해 연결부의 타임스탬프 반올림 누적을 막는다. 최종 픽셀 검수 프레임은 필터의 로컬 카운터가 아니라 검증된 전역 PTS의 `round(t*60)`으로 선택한다.

서로 다른 씬 스트림의 SAR 변경은 FFmpeg의 자막 framesync를 초기화해 현재 자막을 누락시킬 수 있다. 현재 clean은 해상도/픽셀 형식이 같고 전역60fps PTS가 검증되어 있으므로, 자막 합성에서는 clean 입력의 `-reinit_filter 0`, `setsar=1`, `-fps_mode passthrough`로 상태와 프레임을 유지한다.42초 표본에서 누락되던8번 자막을 먼저 확인했으며, 새 전체 출력은 모든340개 자막과 전환 경계의 픽셀 검사를 다시 통과해야 한다.

최종 경계: clean/captioned/KO/EN 네 파일을 collector로 모은 뒤 **전체 자막 포함 완성본을 Google Drive에 먼저 업로드**한다. 해당 버전을 사용자가 검수하기 전에는 YouTube에 업로드하지 않는다. 다른 영상으로 넘어가지 않는다.

`record-final-review.py`는 현재 해시의 기술·자막·동작 검수와 네 파일 확인을 기존 원장/체크포인트에 합친다. Drive 실제 업로드·권한 재열람 결과가 있을 때만 해당 버전을 납품으로 기록한다. 전체 사람 청취,01:43.2 첫 단어의 인식 차이, 원본 음성의 국소 운율 의심 구간은 실제 확인 전까지 pending으로 남긴다.

현재 연결 도구는 파일당512MiB 제한이 있고 웹 업로드도 시작 단계에서 진행되지 않았다. `optimize-drive-delivery.py`는 검수된 자막 포함 원본을 보존한 채1080p60 H.264와 동일 AAC로 용량을 줄인다. `verify-drive-copy.py`는 원본/기존 증거를 보존한 뒤 새 인코딩의 전체 decode/PTS/자막과 모든 프레임의 정렬된 SSIM을 검사한다. `check-drive-compression.py`의 장면별 최저점 및 전체 최저점 표본을 실제로 보고 압축 화질을 확인한다. 같은 대본·씬·타이밍의 의미 검수와 동일 AAC의 ASR/음량 측정은 재사용하며, 압축 수치만으로 사람 청취나 완성본 승인을 기록하지 않는다.

2026-10-14 전송 결과: 검수를 통과한527MB 파일도 내부 blob 전송 서비스에서HTTP413으로 거부되어 Drive 파일이 생성되지 않았다. 현재 최종 납품은 원래940MB 고화질 자막본이며 정확히 일치하는 기존 검수 증거를 복원했다. 압축 시도와 검수는 별도로 보존한다. `drive-transfer-block.json` 및 기존 원장/체크포인트에 실제 실패를 기록했고, 전송 가능한 경로와 완성본의 사용자 검수를 기다린다. 업로드 성공이나 재생 확인으로 표시하지 않는다.

실제 자료: `plan-actual-footage.py` → `prepare-actual-footage.py --normalize` → `sync-media.py`. `record-actual-sources.py`는 현재 자료의 출처/권리와 검수 근거를 한 곳에 기록한다. 하이브리드 합성은 설명 구간만 Motion Canvas로 프레임 렌더하고 실제 녹화에는 같은 MC 크레딧 레이어를 합성한다. 씬·부분 해시가 같은 완료 결과만 재사용한다.
