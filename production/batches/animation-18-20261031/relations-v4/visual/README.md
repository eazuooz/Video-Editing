# 관계도 설명 렌더러

실제 시연에 앞서 설명할 관계를 보여 주는1920×1080/60fps 코드 기반 Canvas2D 도식이다. 엔진 결과나 게임 내부 측정값으로 표시하지 않는다. 기존 무대의 실물 동작을 다시 제작하는 대신, 상태·조건·원인·시간축처럼 눈에 보이지 않는 관계를 직접 그리는 데 사용한다.

- 검정 바탕, 흰 본문, 따뜻한 노랑 제목, 청록 개념, 빨강 문제/명중, 초록 결과.
- 관계의 의미가 있는 선·화살표·구간과 간단한 인체/손/얼굴 도식. 장식 카드·그라데이션·글로우 없음.
- 최종 자막 영역은920px 아래에 비워 두고 부모 합성에서 승인된 자막을 넣는다.
- `planning/relations-plan.json`의 편별 제목·beat와 실측 문장 시각을 연결한다. preview만 임시 비례 시간 허용. production render에는 실측 타이밍이 필수다.

```powershell
node production/batches/animation-18-20261031/relations-v4/visual/renderer.cjs preview --plan <plan.json>
node production/batches/animation-18-20261031/relations-v4/visual/renderer.cjs render --plan <plan.json> --timing <timing.json> --id A03 --out <absolute-output.mp4>
```

타이밍 JSON:

```json
{"episodes":[{"id":"A03","duration":35.4,"frames":2124,"sentences":[{"id":"A03-S01","start":0,"end":4.1}]}]}
```

문장 ID는 계획의 `sentences[].id`와 일치해야 한다. 또는 `{id,duration,beats:[{id,start,end}]}`를 사용할 수 있다. `visualLevel:5`는 기존 음성을 유지하는 본문 보완용으로 완성된 도식 상태를 계속 표시한다. `variant:"wing-volume"`은A08 본문의 날개/부피 비교를 정면과 측면으로 보여 준다. 이 경우에도 녹음된 기존 대사의 시간 구간을 전달한다.

모듈 API는 `setup(plan)`, `frame(id,time,timing)`이다. 반환된Canvas에서PNG 또는RGBA를 읽을 수 있다. renderer가 생산한MP4는 무음이며, 내레이션·한영 자막은 부모 편집 과정에서 같은 시간축으로 합친다.

미리보기 파일은 `relations-v4/local/visual-previews`에 저장한다. 최종 인코딩 결과와375px 자막 가독성 검수는 이 미리보기 검수와 구별한다.


본문 보완에는 `visual/body-timing.json`의 실제 기존 자막 시각을 사용한다. A06 `three-actions`는 각 시간표의 진행점과 함께 주먹 회수·큰 휘두름·발사 반동을 다른 인체 도식으로 보여 준다. A08 `wing-volume`은 정면/측면의 평면과 입체 날개를 비교한다. A14는 두 클립·겹침·독립 가중치를 순서대로 공개한다. 원래 음성을 바꾸지 않는다. 표시된 길이와 동작은 관계 설명용이며 게임 내부 측정값이 아니다.

`node visual/preview-check.cjs`는 18편×3시점의 PNG와 375px 보기, 920px 아래 자막 영역 검사 결과를 만든다. 35초 비례 시각은 레이아웃 검사용이고 제작 타이밍이 아니다. 선택 beat만 넘겨도 전체 계획 안의 해당 단계에서 그린다. 등록되지 않은 문장/beat 또는 잘못된 시각은 오류로 멈춘다.

레이아웃 검수는 관계도 소스와 미리보기만의 검수다. 실제 녹음의 문장 시작/끝과 합친 최종 1080p/60fps 재생, 자막, 움직임 연결은 후속 검수에서 확인한다. 입력 타이밍의 프레임 수를 우선하며 본문 보완 범위는 60fps 단위로 반올림한다.
