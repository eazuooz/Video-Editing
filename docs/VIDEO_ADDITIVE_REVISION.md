# 기존 설명을 보존하고 실제 게임 예시를 중간에 추가하는 제작 방식

2026-10-02 사용자 요청: `지금까지 만들어진거 + 영상 추가삽입으로 만드는 방식 기록 기억해줘 md 같은데 적어줘`.

이 문서는 완료한 비공개 보강본과 앞으로 항상 적용할 제작 방식을 함께 기록한다. 최신 실행 상태와 완료 증거는 [보강 대기열](../production/batches/private-review-expansion/queue.json), 원래 주제의 중복 검토와 새 제작 순서는 [24편 대기열](../production/batches/sakurai-planning-game-design/queue.json)을 기준으로 한다. 아래 목록은 실제 렌더·검수·수집·비공개 저장·Git 전달을 확인한 시점의 기록이다.

## 기존 제작물 중 실제 게시를 확인한 영상

2026-10-02 현재 Studio 콘텐츠 목록에서 기존 프로젝트와 대응하는 다음 11편의 ID·제목·공개 상태를 직접 확인했다. [실제 목록 기록](references/created-video-inventory-20261002.json)을 함께 보존한다. 아래는 공개된 기존 제작물의 기록이며, 이번 보강 요청만으로 수정하거나 재업로드하지 않는다. 과거 manifest의 단계 이름이 오래되었거나 미디어 경로 구조가 다르더라도 이를 새 미제작 영상으로 판단하지 않는다. 채널 전체 465편을 전부 조사한 목록은 아니다.

| 기존 프로젝트 / 주제 | 실제 게시 영상 | Studio 표시 길이 |
|---|---|---:|
| [one-button-game-design](../projects/one-button-game-design/project.json) | [원버튼 게임 디자인: 버튼 하나로 재미를 만드는 4가지 방법](https://youtu.be/DeSXTV41GXs) | 3:55 |
| [small-window-game-design](../projects/small-window-game-design/project.json) | [화면 비율과 시야각이 게임을 바꾼다](https://youtu.be/84xPzR2ww88) | 3:53 |
| [renderformer-explained](../projects/renderformer-explained/project.json) | [RenderFormer 논문 완전 해설](https://youtu.be/_Zz5JF5WGj4) | 44:09 |
| [play-first](../projects/play-first/project.json) | [마리오 오디세이는 왜 3분 만에 재밌을까?](https://youtu.be/IHKv1p_aSJ4) | 3:29 |
| [game-dev-career](../projects/game-dev-career/project.json) | [게임을 만드는 사람들은 각자 무슨 일을 하고 있을까요?](https://youtu.be/7ZjcujPX_uc) | 6:50 |
| [visible-rewards](../projects/visible-rewards/project.json) | [왜 조금만 더 하게 될까? 보상이 보이는 게임 디자인](https://youtu.be/5W5f6T8Hho8) | 6:16 |
| [gpt-astra-showcase](../projects/gpt-astra-showcase/project.json) | [AI로 이런 게임까지? 아스트라 게임·3D 제작 사례 8선](https://youtu.be/zR0Z2nYpDYQ) | 3:59 |
| [let-them-play](../projects/let-them-play/project.json) | [게임은 어떻게 시작해야 할까? 첫 장면과 튜토리얼 디자인](https://youtu.be/bSPwEfdU_JI) | 8:02 |
| [ai-era-cs-fundamentals](../projects/ai-era-cs-fundamentals/project.json) | [AI가 코딩해 주는데, 개발자는 뭘 공부해야 할까?](https://youtu.be/OjC6Hhyvybw) | 17:37 |
| [frame-rate-modern-rendering](../projects/frame-rate-modern-rendering/project.json) | [30·60·120 FPS 차이, 왜 중요할까? 게임 프레임과 DLSS](https://youtu.be/mAO_tit6Qjs) | 7:26 |
| [jump-physics](../projects/jump-physics/project.json) | [재미있는 점프는 어떻게 만들까? 다양한 게임 점프 물리와 조작감 분석](https://youtu.be/_j3H7lg4p1s) | 6:14 |

`choice-driven-classics`와 DX12의 planning/script-review 프로젝트는 위 게시 완료 목록에 포함하지 않는다. 새 주제를 만들기 전에는 이 기록과 전체 기존 대본, 실제 현재 Studio 업로드를 다시 대조해 내용 중복을 확인한다.

## 지금까지 완료한 보강본

본편 시간은 고양이 인트로 2초와 회원 엔딩 10초를 제외한다. 기존 PPT 보존 시간과 최종 설명 시간은 다를 수 있다. 새 예시의 정리 도식을 추가한 경우에도 원래 PPT를 줄이지 않았다.

| 주제 / 버전 | 전체 길이 | 본편 실제 영상 | 본편 설명 | 원래 PPT 보존 | 새 비공개 영상 / 기록 |
|---|---:|---:|---:|---:|---|
| 게임 애니메이션 프레임 세기 / final-v3 | 442.450초 | 258.267초 | 172.183초 | 168.400초 | [NcnZoofzGNk](https://youtu.be/NcnZoofzGNk) · [업로드 증거](../projects/counting-animation-frames/publishing/youtube-upload-v3.json) |
| 게임 분석·분해·재조립 / final-v2 | 479.033초 | 280.217초 | 186.817초 | 169.450초 | [pY04E8aRvJQ](https://youtu.be/pY04E8aRvJQ) · [업로드 증거](../projects/deconstruct-analyze-rebuild/publishing/youtube-upload-v2.json) |
| 의미 있는 퀘스트 / final-v2 | 450.050초 | 262.833초 | 175.217초 | 153.250초 | [lX7SXU7tMBc](https://youtu.be/lX7SXU7tMBc) · [업로드 증거](../projects/meaningful-quests/publishing/youtube-upload-v2.json) |
| 플레이어 칭찬·성공 피드백 / final-v2 | 520.367초 | 305.017초 | 203.350초 | 192.533초 | [gSN8tbGkJ5E](https://youtu.be/gSN8tbGkJ5E) · [업로드 증거](../projects/praise-player/publishing/youtube-upload-v2.json) |
| 입력 응답·거절·진행 상태 / final-v2 | 526.200초 | 308.517초 | 205.683초 | 191.867초 | [BYk6cLsO9Mc](https://youtu.be/BYk6cLsO9Mc) · [업로드 증거](../projects/responsive-game-feedback/publishing/youtube-upload-v2.json) |

다섯 편 모두 본편 60:40과 원래 설명/음성 보존을 검수했고, 최신 clean MP4·한글 자막 MP4·KO SRT·EN SRT를 `output/<slug>/`에 수집했다. 각 영상의 실제 커밋·일반 푸시 여부와 SHA는 보강 대기열의 `gitDelivery`를 확인한다. 로컬 확인 진입점은 [output/index.html](../output/index.html)이다.

입력 응답 `responsive-game-feedback` final-v2는 기존 48개 대사와 모든 설명 프레임·PCM을 보존하고, Oxygen Not Included의 선택·자원 경고·확인·작업 진행·도구 응답을 관찰하는 새 54개 대사를 더했다. 21개 새 정상 속도 구간, 한영 140큐와 자막/컷 154구간, 전체 믹스/본편 ASR, 전체 디코딩, 동일 AAC와 −16.02 LUFS/−1.98 dBTP를 확인했다. 실제 Studio에서 새 비공개·예약 없음, 썸네일, 한영 수동 자막, 영어 제목/설명, 00초 과외 카드, 마지막 10초 재생목록/구독, 광고 사용과 검토 알림 해소·소유권 주장 없음을 확인했다. 이 업로드는 clean master와 선택형 한영 수동 자막을 사용하며, 채널 형식의 한글 boxed 자막 MP4도 로컬 4개 납품 파일에 보존한다. 현재 Studio가 별도로 생성하는 자동 자막/더빙은 수동 파일 게시 증거를 대신하지 않는다. 기존 비공개 영상 `Lqbqugmpsl8`은 보존한다.

기존 업로드 ID `piZTx_239R8`, `reng7uTFE7s`, `n-NaCpzAMlE`, `nq7NhHi9FSE`, `Lqbqugmpsl8`도 보존한다. 비공개 보강본의 공개 여부는 사용자가 결정한다. 사람 청취, 최종 게시 권리, 원래 Nimbus 파일 확인, 잘린 회원 핸들 원본 확인, 외부 미디어 백업은 증거가 없으면 계속 pending이다. 자동 검수 통과나 비공개 저장만으로 이 상태를 완료로 바꾸지 않는다.

## 항상 적용할 제작 규칙

1. **기존 설명을 보존한다.** 요청받은 수정에서는 PPT·주장·도식형 자체 테스트·대사·승인 음성·설명 길이를 유지한다. 업로드 당시의 기준본, 미디어 해시, 타임라인, 양언어 대본/자막과 영수증을 `production/private-expansion-baseline/`에 기록한다. 기존 완료본은 별도 수정 요청 없이 재제작하지 않는다.
2. **설명에 맞는 실제 동작과 새 해설을 중간에 삽입한다.** 각 주요 설명에 대해 `주장 → 출처 인아웃 → 보이는 실제 동작 → 시청자가 볼 지점 → PPT와의 연결 → 삽입 위치`를 계획 파일에 적는다. 설명을 모두 끝낸 뒤 게임 영상을 몰아서 붙이지 않는다. 관찰·원리 비교·적용 결과를 본론 각 장에서 오가며 대본과 전체 길이를 늘린다. 사용자 확인 `그럼 재생목록 내용보다 영상이 길어지는게 당연해`에 따라 원본 재생목록의 재생 시간을 상한으로 삼지 않는다. 필요한 설명·실제 예시·새 해설을 충분히 담은 뒤 실측 길이를 정한다.
3. **본편 실제 영상 60% / 설명 40%를 실측한다.** 인트로 2초와 엔딩 10초를 제외하고 최대 1프레임 반올림만 허용한다. 숫자·도식 중심인 녹화나 실행 가능한 테스트는 PPT/설명으로 분류한다. 설명이 P초이고 유지할 실제 영상이 G초면 추가 실제 영상의 최초 계획은 `max(0, 1.5 × P − G)`초다. 새 해설 실측 후 타임라인을 조정하고, 새 정리 도식을 넣었으면 그 시간까지 포함해 다시 계산한다. 원래 PPT를 잘라 비중을 맞추지 않는다.
4. **주제마다 게임과 구간을 다시 검토한다.** 최근 사용 이력과 실제 업로드/대본 중복을 확인하고, 새 후보의 선택·제외 이유와 사용 조건을 `sources/game-candidates.json`에 기록한다. 프레임 설명처럼 주제에 격투게임이 맞으면 실제 준비·공격·회복 동작을 보여 주는 구간을 선정한다. 공식 예고편이라고 사용 권리를 자동 승인하지 않는다. 짧은 자료를 루프·저속·무관한 대기로 늘리지 않는다. 화면에 없는 조작이나 결과를 대사로 단정하지 않는다.
5. **채널의 승인 형식을 유지한다.** 원래 고양이 인트로, 전체 화면 게임 위 `boxed-white-forest-v1` 자막, 흰 2.5D 설명, 대본 장면별 독립 Motion Canvas 씬, 같은 승인 Qwen3-TTS 1.7B 목소리와 연속 Nimbus를 사용한다. 회원 엔딩은 10초이며 원본 프로필·이름·배지, 채널 로고와 정확한 제목 `멤버쉽가입 감사드립니다.`을 함께 보존한다. 게임 영상을 흰 PPT 프레임 안에 작게 넣지 않는다.
6. **추가 음성을 먼저 검수하고 모든 시간을 함께 갱신한다.** 현재 WAV 해시의 전체 ASR에서 누락·반복·발음·임의 인사·음성 끝을 직접 대조한다. 추가 음성 실측 뒤 컷·믹스·씬 시작·KO/EN SRT·챕터·엔딩 위치를 함께 수정한다. 원래 음성은 다시 합성하지 않는다. 승인된 기존 화자나 음악을 임의로 바꾸지 않는다.
7. **실제 최종본 전체를 검수한다.** 유지된 원본 프레임/PCM과 모든 삽입 구간의 보존·분류·연결을 확인한다. 모든 자막/컷 구간에서 줄바꿈과 게임 UI 겹침을 직접 살피고, 전체 디코딩·길이·음량·true peak·두 MP4의 동일 오디오·전체 ASR을 검사한다. 단일 합성/렌더를 실행하고 실제 PID·세션·로그·다음 작업을 대기열에 남겨 재실행을 피한다. 다른 사용자 GPU 작업을 중단하지 않는다.
8. **완료된 파일만 수집하고 비공개로 전달한다.** `node scripts/collect-video-output.cjs <slug>`로 최신 4개 파일과 `output/index.html`을 갱신한다. YouTube 파일 교체가 불가능하므로 보강본은 의도적인 새 비공개 업로드로 기존/신규 ID를 연결한다. [업로드 규칙](YOUTUBE_PUBLISHING.md)의 새 썸네일·설명/기존 채널 링크·한영 수동 SRT·영어 제목/설명·00초 과외 카드·마지막 10초 재생목록/구독·광고/저작권 검사 결과를 실제 Studio에서 저장 후 확인한다. 공개 전환과 공개 예약은 하지 않는다.
9. **완성 한 편마다 커밋·일반 푸시한다.** 해당 프로젝트의 rebuild manifest를 갱신하고 media/rebuild 검사를 통과한 승인 제작 파일·대본·자막·출처·검수/업로드 증거와 필요한 제작 규칙만 선택한다. 영상·음성·BGM·게임 소리·미디어 압축·원본 다운로드 `info.json`은 Git에 넣지 않는다. 다른 사용자 변경을 보존하고 실제 커밋 SHA·푸시 결과·원격 SHA 일치를 대기열에 남긴다.

## 작업을 이어갈 때 읽을 파일

먼저 이 문서와 [AGENTS.md](../AGENTS.md), [VIDEO_WORKFLOW.md](VIDEO_WORKFLOW.md), [보강 배치 README](../production/batches/private-review-expansion/README.md), 최신 대기열과 프로젝트 manifest를 읽는다. 화면·자막·음성·회원 엔딩·업로드 세부 사항은 각각 기존 전문 지침을 따른다. 이 기록은 대본만 늘리거나 자료를 준비한 상태를 영상 완료로 간주할 근거가 아니다. 실제 완료 증거가 있는 항목은 보존하고, 살아 있는 작업의 체크포인트부터 이어간다.
