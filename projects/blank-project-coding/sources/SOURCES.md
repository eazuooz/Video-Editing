# 대본과 촬영 출처 — blank-project-coding

기준일: 2026-10-02 (Asia/Seoul). 현재는 **전체 합성·최종 화면 검수 단계**다. 자체 C++/JavaScript 예제 19개 동작 장면과 34개 음성의 기술 검수를 마쳤다. 실제 최종 렌더·전체 사람 청취·비공개 저장 여부는 별도 완료 증거를 따른다.

## 사용자 원문과 보존 범위

현재 대화의 17~24장을 1차 원문으로 사용했다. 첨부 `붙여넣은 텍스트.txt`는 취업 대본 배경이며 16장 중간에서 끝나므로, 첨부만으로 17~24장을 재구성하지 않았다. 보존/추가 내용을 [source-map.json](../script/source-map.json)에 기록했다. 기존 `ai-era-cs-fundamentals` 영상과 파일을 변경하지 않는다.

## 교육 설명 확인

- [Roediger & Karpicke (2006), Test-enhanced learning](https://pubmed.ncbi.nlm.nih.gov/16507066/): 산문 학습 후 회상 테스트와 반복 학습을 비교한 원 연구의 초록을 확인했다. 지연된 기억 검사 결과를 다루며 **프로그래밍 독립 구현, 학년별 AI 금지나 취업 효과를 직접 검증한 연구가 아니다**. 대본은 코드 읽기/직접 만들기 구분을 화자의 교육 관점으로 설명하고, 효과 수치·뇌 기능·보편적인 학년 규칙을 주장하지 않는다.
- [Microsoft Learn, Debug C++ code](https://learn.microsoft.com/en-us/visualstudio/debugger/getting-started-with-the-debugger-cpp?view=visualstudio): 중단점, 단계 실행과 변수 관찰에 대한 공식 설명을 확인했다. 자체 코드에서 실제 값의 변화와 입력 결과를 새로 촬영한다. 문서의 예제·캡처를 그대로 대체 footage로 사용하지 않는다.
- [Microsoft Learn, Watch and QuickWatch](https://learn.microsoft.com/en-us/visualstudio/debugger/watch-and-quickwatch-windows): 실행을 멈췄을 때 식과 변수 값을 확인하는 용도를 참고한다. 정적인 Watch 표만 길게 보여주면 실제 동작 시간으로 계산하지 않는다.

## 실제 촬영 계획

1. 자체 작성 C++ Linked List: 읽기/단계 실행, 빈 프로젝트, 노드 두 개, 삽입, 삭제, 빈 목록/맨 앞/유일 노드, 맨 뒤 삽입.
2. 이번 영상 전용 자체 낙하 블록 프로토타입: 보드와 블록, 후보 이동/충돌, 단순 회전 허용/거절, 고정/줄 삭제, 의도적으로 준비한 이동 순서 버그의 재현/수정과 서로 다른 입력.
3. 이번 영상 전용 단순 벽돌 깨기 프로토타입: 패들/공 데이터, 입력과 충돌, 중앙/끝 조건 확인. 타사 그래픽·음악·브랜드 화면을 복제하지 않고 자체 도형과 코드로 만든다.

아래는 사전 선택의 근거다. 현재 소스는 `examples/`, 녹화와 재촬영 이력은 `production/final-v1/capture-final.json`, 현재 컷 직접 검수는 `production/final-v1/actual-visual-review.json`에 있다. 다른 사람의 완성 강의 코드를 자체 작업처럼 기록하지 않는다. 스스로 구현한 예제는 교육용 시연이지 실제 학생의 독립 학습 기록이나 효과 증거가 아니다. 버그 재연도 교육용으로 표시한다. 각 촬영 파일, 해시, 실제 인/아웃점과 음성에 맞는 관찰 근거를 [storyboard.json](../planning/storyboard.json)에 채운 뒤 TTS/최종 컷을 진행한다. 첫 빈 화면과 파일 닫기는 짧게 보여주고 나머지는 의미 있는 작성·조작·디버깅·플레이 결과로 구성한다.

## 최근 사용 이력과 새 후보

전체 기존 프로젝트의 대본/출처, `ai-era-cs-fundamentals/sources/selected-footage.json`, 최근 `game-writing` 및 `responsive-game-feedback` 후보 기록을 확인했다. 이전 공부법 영상은 외부 테트리스 플레이와 GDQuest/PyCon 자료가 있다. 이번 편은 그 클립과 코드를 재사용하지 않고 사용자 지정 테트리스 개념을 새 자체 구현/촬영으로 다룬다. 상용 게임 목록을 늘리기보다 이 영상의 질문에 맞는 실제 개발 행동을 우선한다. 후보와 제외 이유는 [game-candidates.json](game-candidates.json)에 기록한다.

## 채널 자산과 코칭 안내

고양이 인트로는 `shared/assets/branding/yamyamcoding-cats-original.png`를 기반으로 기존 승인 자산을 재사용한다. 회원 엔딩은 원본 프로필·이름/핸들·배지를 함께 보존하며 명단과 원본 확보/최신 확인 상태는 렌더 단계에서 검수한다.

코칭 URL은 `shared/publishing/youtube-defaults.json` 및 현재 공개된 `OjC6Hhyvybw` Studio 설명에서 실제 확인했다. [공식 코칭·과외 안내](https://www.yamyamcoding.com/1430b1ff-a61e-8040-a542-d672d5d25328)의 제목은 검색 도구에서 읽혔으나 후속 상세 본문 읽기는 오류였다. 구체적인 현행 커리큘럼·가격·일정·모집 상태는 확인한 것으로 주장하지 않는다. 대사는 기존 채널 설명의 직접 설계/구현 습관과 코칭 안내 링크 범위로 작성했다.

## 현재 확인과 잔여 검수

동일 승인 Qwen 기준 목소리와 Nimbus를 재사용했다. 34개 현재 음성 해시/ASR/종결 감쇠를 검토했고 09·16·20의 불명확한 발화를 보정했다. 총 길이 1368.7초, 본편 실제 동작 814.016667초·설명 542.683333초이며 비율 오차는 0.2프레임이다. KO/EN 461개 자막의 타이밍을 맞췄고 모든 고정 자막의 중심은 (960,970)이다. 이 수치는 실제 완성 렌더의 전체 디코딩·시각 검수와는 별도다.

19개 실제 예제는 자체 코드와 도형이다. C++는 MSVC 프로세스와 실제 포인터 값을, JavaScript는 실제 입력/충돌/회전/줄 삭제/패들 반응을 기록했다. 교육용 재현이며 상용 IDE나 학생의 학습 성과로 제시하지 않는다. 원본 회원 프로필/표시명/배지 이미지와 고양이 로고를 사용한다.

Nimbus는 기존 승인된 복원 사본을 사용한다. Studio에서 Eveningland의 4:40 Nimbus 및 수익 창출/표기 불필요 라이선스 문구를 확인했지만 원본 다운로드 파일과의 바이트 동일성을 확인한 것은 아니다. 증거는 `publishing/proof/nimbus-official-license.png`다. 원래 Audio Library 파일 확인, 전체 사람 청취, 외부 미디어 백업과 최종 공개 판단은 pending으로 유지한다.
