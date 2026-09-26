# 얌얌코딩 — 독립 2초 인트로 제안

요청: “응 그것만 한번 만들어줘봐~”. 본편·내레이션·KO/EN SRT는 변경하지 않는다. 채널 공통 규칙으로 아직 확정하지 않는다.

- 1920×1080 / 60fps / 120프레임 / 2초.
- 흰 바탕, 노란 포인트, 검정 타이포. 문구: `얌얌코딩 | 게임 기획·디자인`.
- 기존 썸네일 `projects/let-them-play/publishing/thumbnails/let-them-play-ko-v1.png`의 픽셀 닭을 참고해 코드 도형으로 재구성한 애니메이션 초안. 원본 마스코트 래스터를 추출한 파일은 아니다.
- 0.12–0.67초 프레임 확장, 0.40–0.78초 타이틀 등장, 이후 홀드. 캐릭터는 프레임 오른쪽 변을 따라 두 발짝 이동.
- 기존 승인곡 Discovery의 4–6초 부분, -28 LUFS 전체곡 정규화 후 발췌. 샘플만 짧게 페이드. 추후 본편 적용 시에는 전체 타임라인의 연속 BGM으로 다시 믹스한다.
- 별도 내레이션 없음. 그러므로 인트로 SRT도 만들지 않는다. 회원 엔딩 불필요한 부분 디자인 프리뷰이다.

제작: `node motion-canvas/scripts/render-yamyam-intro.cjs`

결과: `output/intro-sample/index.html`, `output/intro-sample/yamyam-intro-v1.mp4`.

음악: 'Discovery' by Scott Buckley - released under CC-BY 4.0. www.scottbuckley.com.au
https://www.scottbuckley.com.au/library/discovery/ · https://creativecommons.org/licenses/by/4.0/
