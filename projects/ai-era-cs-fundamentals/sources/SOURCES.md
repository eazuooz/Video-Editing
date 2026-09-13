# 출처와 사용 상태

> 2026-09-07 현재 사용 원본은 [FOOTAGE.md](FOOTAGE.md) / selected-footage.json v3가 기준입니다. 아래 초기 후보 중 오목 등은 **과거 조사 이력·미사용**입니다. 밈은 [MEMES.md](MEMES.md) 참고용이며 원본을 삽입하지 않았습니다.

조사일: 2026-09-06. 대본 v4 승인 후 12개 실제 클립을 확보·발췌하여 Motion Canvas에 연결했습니다. 전체 음성·음악·게시본은 대기 상태입니다.

## 현재 사용 영상 — 이 목록이 우선

- [선정 영상·사용 근거·정확한 구간](FOOTAGE.md): PyCon JP 5개 + 테트리스 1개 + GDQuest 게임개발 영상 6개. 기존 후보들은 아래에 조사 이력으로만 보존합니다.
- [선정 데이터](selected-footage.json), [미디어 검증 결과](media-check.json).
- PyCon JP 공식 CC BY 정책, 테트리스 YouTube CC BY, GDQuest 각 영상 설명의 CC BY 4.0을 확인했습니다. [게임개발 자료 허용 확인](gamedev-license-evidence.json). 출처·발췌 사실을 화면과 게시용 크레딧에 기록합니다.
- 출연자는 본 대본을 말하거나 지지한 사람이 아닙니다. 회사·시험장·취업 준비 상황은 가상 예시입니다.

## 기획의 출발점

[AI 시대에 컴공을 선택한 용사들에게 — 잡담](https://www.youtube.com/watch?v=luyBenV55xk)

사용자가 제공한 00:00~33:15 전사문을 참고했습니다. 화면·원음은 현재 사용하지 않습니다.
‘기초를 직접 익히고 AI 결과를 이해·검증하자’는 주제를 독립적인 예시와 문장으로 재구성했습니다.
원저자의 학부·직장 경험, 회사 채용의 단정, 특정 연도 예측, AI 활용에 대한 비하는 대본에서 제외하거나 관점으로 구분했습니다.

## 기술·학습 근거

| 자료 | 대본에서 쓰는 범위 |
| --- | --- |
| [GitHub: Learning a new programming language](https://docs.github.com/en/copilot/tutorials/learn-a-new-language) | 02·06: 이해 없이 생성 코드에 의존하지 않기, 코드 설명을 학습 보조로 사용 |
| [VS Code: Python tutorial](https://code.visualstudio.com/docs/python/python-tutorial) | 02·03: 실행·환경·중단점과 변수 확인 |
| [Python collections](https://docs.python.org/3/library/collections.html) | 04: deque·사전 등 자료 구조의 역할 |
| [Python unittest](https://docs.python.org/3/library/unittest.html) | 08: 입력에 대한 기대 결과 검사와 자동 테스트 |
| [Python profilers](https://docs.python.org/3/library/profile.html) | 09: 실행 시간 측정 개념의 근거; AI 요금 근거와 구분 |
| [GitHub: Review AI-generated code](https://docs.github.com/en/copilot/tutorials/review-ai-generated-code) | 10: 기능·맥락·의존성·테스트·사람 검토 |

학습 순서와 진학 판단은 채널의 제안이며 보편적으로 입증된 유일한 방법이나 취업 보장으로 표현하지 않습니다.

## v3 추가 검증 — AI 비용과 도구 독립성

확인일: **2026-09-06**. 사용자 표현 ‘아스트라 / 페이블’은 개발 AI 맥락에 맞는 **GPT-6 Astra / Claude Fable 5.1**로 해석했습니다.

| 모델 | 기본 입력 / 백만 토큰 | 기본 출력 / 백만 토큰 | 공식 근거 |
| --- | --- | --- | --- |
| GPT-6 Astra | USD 10 | USD 50 | [OpenAI 모델 요금](https://developers.openai.com/api/docs/models/gpt-6-astra) |
| Claude Fable 5.1 | USD 10 | USD 50 | [Anthropic 요금표](https://platform.claude.com/docs/en/about-claude/pricing) |

- 이는 **기본 API 사용량 과금**이지 월 구독료나 질문 한 번의 가격이 아닙니다. 입력과 출력에 각각 적용합니다.
- Astra는 입력 272K 토큰 초과 요청, 캐시, 실행 모드 등에 별도 조건이 있습니다. Fable도 캐시 쓰기·읽기 등 별도 요율이 있습니다. 실제 지출은 요청량·설정에 따라 달라집니다.
- 높은 토큰 단가가 항상 높은 작업당 비용을 뜻하지 않습니다. OpenAI는 일부 평가에서 출력 토큰 감소로 작업 비용이 낮아졌다고 보고합니다. 이는 공급사 평가이며 모든 작업에서 보장되는 결과로 말하지 않습니다. [공식 모델 안내](https://developers.openai.com/api/docs/guides/latest-model)
- ‘요금 상승 / 무료 제공량 감소’는 대비할 수 있는 **가정**입니다. 업체가 인상을 확정했다거나 산업 전체 가격이 계속 오른다는 뜻이 아닙니다.
- 최종 녹음·게시 직전 가격·모델 버전을 다시 확인합니다. 변동 시 본문·요금 카드·출처를 함께 갱신합니다.
- 빈 파일부터 개발하기와 오프라인 연습은 채널의 교육 제안입니다. 세대별 역량에 대한 통계적 주장이나 모든 취준생에 대한 평가가 아닙니다.
- 오프라인 예시는 설치된 언어 도구·라이브러리·로컬 문서로 가능한 프로그램에 한정합니다. 외부 서버 접근·새 패키지 다운로드가 필요하면 별도 준비가 필요합니다.

## 초기 유튜브 후보 조사 이력 — 아래 영상은 현재 편집에 미사용

| 씬 | 후보 | 찾을 화면 |
| --- | --- | --- |
| 01 | [Getting started with GitHub Copilot | Tutorial](https://www.youtube.com/watch?v=n0NlxUyA7FI) · GitHub | 코드 제안과 실행 결과가 함께 보이는 구간 |
| 02 | [Getting Started with Python in VS Code (Official Video)](https://www.youtube.com/watch?v=D2cwvpJSBX4) · Visual Studio Code | 04:50 이후 간단한 파일 실행·REPL 시연, 정확한 인점은 화면 검수 후 |
| 03 | [10 ways to debug Python code](https://www.youtube.com/watch?v=cokP4XAhcwo) · PyCon DE / Christoph Deil | 중단점·변수 검사 시연 구간 |
| 04 | [Modern Python Dictionaries — A confluence of a dozen great ideas](https://www.youtube.com/watch?v=npw4s1QTmPg) · PyCon 2017 / Raymond Hettinger | 딕셔너리 내부 자료 배치를 시각적으로 보여 주는 구간; CPython 3.6 당시 예시 |
| 05 | [The Clean Architecture in Python](https://www.youtube.com/watch?v=DJtef410XaM) · Next Day Video / Brandon Rhodes | 설계 계층 그림을 보여 주는 구간; 이 구조만 정답이라고 설명하지 않음 |
| 06 | [Understand your code using GitHub Copilot's explain feature](https://www.youtube.com/watch?v=r-iL_pCzBHc) · GitHub | 코드 설명 기능의 과거 시연(2022); 세로 영상이라 레이아웃 검수 필요, 현재 UI 안내용 아님 |
| 07 | [Gomoku — Unity 2D game demo](https://www.youtube.com/watch?v=5o5oJFNilRU) · zenz34 (개발자 저장소에서 연결) | 돌 배치와 턴 전환; 제목·게시자와 실제 화면은 직접 확인 필요 |
| 08 | [Getting Started Testing — PyCon 2014](https://www.youtube.com/watch?v=FxSsnHeWQBY) · PyCon 2014 / Ned Batchelder | 테스트 실행·실패 결과를 보여 주는 구간 |
| 09 | [Python Performance Profiling: The Guts And The Glory](https://www.youtube.com/watch?v=BOKcZjI5zME) · PyCon Taiwan / A. Jesse Jiryu Davis | 프로파일 결과와 느린 함수 확인 구간; 실측 배율로 오해시키지 않음 |
| 10 | [How to create a pull request in 4 min | GitHub for Beginners](https://www.youtube.com/watch?v=nCKdihvneS0) · GitHub | 변경 파일·코드 diff·리뷰 과정 구간 |
| 11 | [Getting started with GitHub Projects](https://www.youtube.com/watch?v=lzpcyYIbHqE) · Mickey Gousset | v3 빈 파일·오프라인 구현 시연에는 부적합하여 교체 검토. 기존 후보는 계획 화면 참고만 가능 |
| 12 | [GitHub Profile Readme](https://www.youtube.com/watch?v=KhGWbt1dAKQ) · 게시자 확인 대기 | 프로젝트 설명·작업 기록을 정리한 README 화면; 대학원 장면으로 오인시키지 않음 |

기계 판독용 상태는 [broll-candidates.json](broll-candidates.json)에 있습니다. 모든 인점·종점은 null이며 임의로 확정하지 않았습니다.
공식 게시나 출처 표기만으로 영상의 재사용 권리가 생기는 것은 아닙니다. 영상별 라이선스·별도 허가를 확인하고, 확인되지 않으면 게시본에 넣지 않습니다.
화면이 작거나 세로·자막·발표자 비중이 커서 설명과 맞지 않는 후보는 실제 화면 검수 후 대체합니다.
원음은 사용할 수 있는 구간에 한해 낮게 유지합니다. 보이스오버와 원어 발표 음성이 경쟁하면 사용 구간을 조정합니다.

## v4 추가 — 시험·면접·신입 상황극

- 01·02·05·06·10·11의 대화와 상황은 공감을 위한 가상 예시입니다. 실제 채용 평가 방식·회사 관행·특정인의 경험을 조사한 사례가 아닙니다.
- 06: 손코딩·직접 구현에서 막히는 데 긴장과 시간 압박도 영향을 줄 수 있음을 함께 언급합니다. 한 번의 수행으로 전체 실력을 단정하지 않습니다.
- 10: 지연에는 요구 변경·일정·지원 환경도 영향을 줄 수 있습니다. ‘정상 화면 동작’과 합의된 완료 조건을 구분하고 팀 검토·도움 요청을 제안합니다.
- 위 장면은 자체 그래픽으로 표현합니다. 기존 외부 코딩·리뷰 영상의 출연자가 대본 속 말을 했다고 오인시키지 않습니다.
- 영상 구성 작업에서 공식 모델·가격 페이지를 다시 열어 기본 API 입력 $10 / 출력 $50(각 100만 토큰)을 재확인했습니다. 자체 카드에 날짜와 별도 조건을 표시했습니다. 게시 직전 재확인은 여전히 필요합니다.

## v5 전체 TTS 직전 재확인 — 2026-09-10

OpenAI Docs 스킬의 공식 문서 확인 절차를 적용해 위 모델 페이지와 Anthropic 요금표를 다시 확인했습니다. GPT-6 Astra와 Claude Fable 5.1의 기본 API 입력 $10 / 출력 $50(각 100만 토큰) 표기는 유지합니다. 월 구독료가 아니며 캐시·긴 입력 등 별도 조건도 그대로 고지합니다. 요금 상승 가능성은 예측이 아닌 대비 가정입니다. 게시 시점이 달라지면 다시 확인합니다.

## 음악

**Blue Dream — Cheel 선택 확정**. [선택·파일·라이선스 상태](../audio/bgm-selection.md). 이전 Nimbus를 자동 적용하지 않으며 Blue Dream도 파일·라이선스 확인 전에는 믹스하지 않습니다.
