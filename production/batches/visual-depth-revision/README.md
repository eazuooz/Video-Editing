# 2.5D 설명 화면·자연스러운 채널 썸네일 수정

2026-10-07 사용자 요청에 따라 `picking-sides`부터 `familiar-game-rules`까지 일곱 편만 수정한다. 정확한 범위와 기존 YouTube ID는 `queue.json`을 따른다. 기존 업로드와 공개·예약 상태를 보존하고, 새 검수본은 새 비공개 영상으로 전달한다. 이번 범위 뒤 새 주제/TTS는 착수하지 않는다. 자동화24와 GPU TTS hold는 계속 PAUSED/active다.

## 제작 방식

각 `production/visual-depth-v1/baseline.json`은 원래 manifest와 대본·KOEN SRT·믹스·미디어의 실제 SHA를 보존한다. `familiar-game-rules`의 추가 안내 8문단은 `guide-preservation.json`으로 별도 보존한다. 재생 시간·본편 60:40·실제 게임 구간·승인 음성/AAC를 바꾸지 않고, 기존 흰 설명 구간의 같은 프레임만 입체 설명으로 교체한다.

`motion-canvas/src/projects/<slug>/depth-explanations-v1.tsx`와 독립 `scenes/depth*.tsx`, `depth-reel-plan-v1.json`이 편집 가능한 원본이다. `motion-canvas/src/shared/depth-diagrams.tsx`의 XYZ 투영, 앞/옆/윗면과 높이, 시점 회전, 배우·경로·화살표의 문단별 움직임으로 개념을 설명한다. 브라우저 로컬 프리뷰가 거부되어, 승인된 코드 트리를 실행하는 CPU Canvas 어댑터로 제작했다. 이를 네이티브 Motion Canvas 브라우저 exporter 실행으로 기록하지 않는다.

각 수정 버전의 raw와 실제 ASS preflight 보드를 모두 직접 읽은 뒤 현재 소스 SHA를 잠근다. 이전 버전의 검토는 수정 버전의 승인이 아니다. `render-depth-cpu.cjs`는 현재 직접 검토 기록을 요구한다. 실제 렌더 raw 샘플과 preflight의 SHA가 같을 때 `prepare-rendered-assembly.py`가 정확한 원본 concat 구간을 교체한다. `build-reviewed-pair.py`는 흰 구간의 전체 decode, clean/captioned 전체 decode 두 번, 모든 90000 timebase PTS(1500 간격), 원래 AAC 패킷 동일성을 검사한다. 최종 `extract-final-pixels.py`는 모든 KO 큐의 시작/중간/끝, 게임 컷 경계, 입체 문단 변화, 도입·회원 엔딩을 로컬 추출한다. 직접 읽기 전 allFinalPixels/upload/collection은 승인하지 않는다.

옛 `continue-local-reviews.py` 실행은 멀미 편의 최종 자막 가림을 발견한 뒤 다음 작업 배정만 중단했다. 당시 진행하던 계층형 pair는 끝까지 보존했으며 종료된 PID/세션을 재사용하지 않는다. `caption-safe-dispatch-pause.json`과 `local-review-pipeline-execution.json`은 그 이력이다.

현재 `run-caption-safe-local.py`는 명시한 slug의 승인된 최신 preflight만 직렬 CPU2/GPU0으로 렌더한다. `--resume-caption-safe`는 멀미와 계층형의 옛 미승인 pair·검수·로그를 별도 보존하고 수정된 흰 구간을 사용한다. 멀미 원본 회원 엔딩의 프레임0 잔상만 실제 확인되어 trim1+앞1프레임 유지로 고쳤고, 나머지 다섯 편의 원본 엔딩은 직접 검토한 정상 프레임0을 그대로 보존한다. 각 최종 픽셀 직접 검수에서 멈추며 자동 승인·업로드·Git 쓰기를 하지 않는다. 실제 실행 상태/명령/PID/로그와 다음 작업은 `caption-safe-pipeline-<first-slug>.json`, 각 execution와 queue를 따른다. 다른 사용자 GPU 논문 실험·Pythonw·공유/staging을 조작하지 않는다.

## 현재 검수 근거

`picking-sides`의 첫 최종 픽셀 600개/100보드를 직접 읽다가 회원 엔딩 첫 프레임의 옛 PPT 잔상을 발견했다. 이전 pair·검수·실패를 보존하고, 원본 회원 영상의 프레임1을 첫 프레임에도 배치했다. 수정본과 이전 검수본의 본편 36293프레임을 decode 해시로 대조했고 첫36290프레임은 완전히 같았다. 마지막3프레임과 새 엔딩11프레임의 두 보드를 직접 읽었다. `encoded-pixel-direct-review.json`과 `boundary-pixel-comparison.json`이 현재 승인의 근거다. 36893프레임/614.883333초, 원래 AAC/KOEN SRT를 보존한 네 파일이 `output/picking-sides/`에 수집됐다.

일곱 편 모두 현재 clean/captioned pair의 전체 decode 두 번, 정확한 90000 timebase/1500 PTS 간격/전체 프레임 수, 원래 AAC 패킷과 KOEN SRT 보존을 확인했다. 모든 계획 큐·컷·입체 문단 변화·엔딩 픽셀을 직접 읽은 후 승인했고 각 네 파일을 `output/<slug>/`에 수집했다. 현재 로컬 완료 근거는 `local-review-completion.json`이며 재업로드/Git 완료와 구별한다.

| 영상 | 현재 최종 픽셀 직접 검토 | 한글 큐 | 네 파일 수집 |
|---|---:|---:|---|
| picking-sides | 이전 100보드/600프레임 + 수정 경계 2보드/11프레임, 본편 decode 동일 대조 | 151 | 완료 |
| motion-sickness-games | 104보드/621프레임 | 166 | 완료 |
| hierarchical-game-outlines | 173보드/1035프레임 | 299 | 완료 |
| game-reward-planning | 165보드/990프레임 | 268 | 완료 |
| avoid-game-comparisons | 150보드/897프레임 | 199 | 완료 |
| making-game-sequels | 190보드/1136프레임 | 308 | 완료 |
| familiar-game-rules | 165보드/985프레임 | 253 | 완료 |

멀미 편의 마지막 푸터 겹침 기록은 원본 해상도 재검토에서 서로 떨어져 있음을 확인했다. 잘못된 발견을 삭제하지 않고 `resolved-current-pixel-findings.json`에 실제 영상·프레임 SHA와 해결 근거를 남겼다. 속편 수집의 첫 실행은 네 파일 수집 후 전역 rebuild index 쓰기에서 실패했고 정상 명령 한 번 재시도가 exit0으로 끝났다. `local-collection-first-failure.json`과 `local-collection-retry-resolution.json`을 보존한다. 마지막 편의 승인 도구는 “REJECT 없음”이라는 부재 진술을 거부 항목으로 잘못 읽어 두 번 실패했다. 정확한 상태 토큰과 부재 진술을 구별하도록 고쳤으며 실제 거부 항목·혼합 문장의 해결 게이트는 유지했다. `negative-finding-marker-clarification.json`에 아홉 검증 사례와 실패 이력을 기록했다.

## 썸네일·업로드·Git

일곱 `publishing/thumbnail-depth-v1.png`를 저장 후 원본 해상도로 직접 읽었다. 얌얌코딩·노란 상단 띠·흰 바탕·큰 검정/빨강 한글·원래 고양이의 자연스러운 주제 삽화를 사용한다. 영상 캡처 액자는 없다. 각 JSON은 실제 SHA/크기/검토를 기록하며 아직 uploaded=false다. 모두 2MiB 미만이며 기본 local-only다. QA/contactsheet/렌더 시퀀스는 Git에 추가하지 않는다.

과거 첫 비공개 업로드의 `fileChooser.setFiles`가 브라우저 보안 정책에서 사용자 권한 거부로 차단됐다. 당시 파일은 전송되지 않았고 새 ID는 없었다. 실패 기록 `private-reupload-block.json`과 두 후속 실패는 보존한다. 이후 사용자 업로드 허용 지시를 받고 정상 CUA 파일 선택에서 실제 전송이 시작됐다. 현재 첫 수정본 `xtUVcAHtQzg`는 비공개·HD·새 썸네일·한영 수동 자막·영어 메타데이터·시작 카드·회원 엔딩 3요소·CC off 게임/입체 설명 픽셀을 저장 후 검수했다. 소유권 주장 없음과 현재 수익 창출 상태도 직접 읽었다. 두 번째 `c18rkesgBSw`는 비공개로 저장하고 파일 전송 중이며 아직 최종 업로드 검수 완료가 아니다. 최신 receipt와 queue가 과거 차단 기록보다 우선한다.

과거 세션의 `.git` 읽기 전용 제한은 당시 Git 미전달 근거로 보존한다. 현재 세션에서 승인된 전달만 실제 HEAD 기반 임시 index와 명시적 파일 목록으로 검증한다. `deliver-reviewed-source.cjs`는 현재 비공개 저장/픽셀 검수와 필수 썸네일 등록을 요구하며, 실제 staged blob·media-policy·해당 slug rebuild·whitespace를 확인한 뒤 HEAD를 비교하고 일반 push한다. 다른 작업의 index 항목과 공유 파일 편집은 보존한다. QA 이미지는 로컬에 두며, 실제 commit/remote SHA 없이 Git 완료를 기록하지 않는다. 사람 전체 청취·발음, 최종 공개 권리, 원래 Nimbus, 잘린 회원 핸들, 외부 백업과 비공개 고정 댓글은 기존 pending을 유지한다.

## 논문 실험을 위한 정지

새 썸네일과 수정 영상을 함께 보는 로컬 진입점은 `output/visual-depth-revision.html`이며 전체 네 파일 목록은 `output/index.html`이다. 일곱 편 로컬 수정이 끝난 뒤 새 제작/TTS를 정지했다. 자동화24의 실제 TOML `PAUSED`, GPU TTS hold의 active/실제 SHA 보존을 읽어 확인했다. `resources-after-local-review-confirmed.json`에서 실제 Python/Node/FFmpeg 명령줄과 생성 시각을 대조했고 이 수정 작업의 무거운 프로세스는 0개였다. 다른 사용자 논문 GPU 작업과 Pythonw는 보존했다. 허용된 일곱 수정본의 비공개 업로드/검수/Git 전달만 계속하고 새 제작/TTS는 시작하지 않는다.
