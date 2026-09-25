# BGM 후보 — play-first (선택 대기)

2026-09-25. 선택 전에는 새 곡을 다운로드하거나 최종 믹스에 넣지 않는다.
참고 이력: 2026-09-18 “Carefree”는 “너무 통통 튐, 살짝 게임 어드벤처 느낌 선호”로 반려됨.
세 곡 모두 Scott Buckley 공식 페이지 기준 CC BY 4.0, 설명란 출처 표기 필요. 영상 전체(마지막 멤버십 10초 포함) 연속 사용.

| 순위 | 곡 | 분위기(추론) | 파일 | 최근 사용 |
|---|---|---|---|---|
| 1 | Wanderlust — Scott Buckley · https://www.scottbuckley.com.au/library/wanderlust/ | 만돌린·현악·피아노의 가벼운 여행·모험. 마리오의 왕국 여행과 잘 맞음 | 보유 `shared/assets/music/scott-buckley/Wanderlust-ScottBuckley.mp3` | visible-rewards |
| 2 | Discovery — Scott Buckley · https://www.scottbuckley.com.au/library/discovery/ | 밝게 차오르는 발견·시작의 느낌 | 보유 `shared/assets/music/scott-buckley/sb_discovery.mp3` | let-them-play, game-dev-career |
| 3 | Path Through The Mountains — Scott Buckley · https://www.scottbuckley.com.au/library/path-through-the-mountains/ | 느리고 신비로운 판타지 산길. 차분한 쪽 | 미보유(선택 시 공식 페이지에서 확보) | 없음 |

출처 표기 형식: `'<곡명>' by Scott Buckley - released under CC-BY 4.0. www.scottbuckley.com.au`

선택 후: `project.json.audio.backgroundMusic` 갱신 → `node scripts/mix-play-first-audio.cjs`(final-mix 생성) → 무자막/자막판 재렌더.
