# 승인된 에디토리얼 2.5D — 본편 확장 v5

2026-09-14, 39.7초 샘플을 본편에 적용하자는 제안에 사용자 “좋아 해줘”.
대본은 승인된v4 그대로, **화면만 visualRevision5**로 바꾼다.

## 장면별 설계

| 장 | 해설 공간 | A/B가 비교하는 것 | 대표 동작 |
|---|---|---|---|
| 01 | 출발 유적과 먼 목적지 | 설명 먼저 / 경험 먼저 | 목적지 관찰, 설정 안내가 가리는 경험, 이동 |
| 02 | 사당 같은 가상 석실 | 같은 대상의 카메라 구도 | 주인공→대상→출구의 위치 관계 |
| 03 | 승인된 산과 전망탑 디오라마 | 같은 지형에서 강조 대비만 변경 | 주변 대비 감소, 첫 관심 대상 강조 |
| 04 | 작은 수집 정원 | 여러 행동 안내 / 가까운 행동부터 | 아이템 접근·줍기, 순차 안내 |
| 05 | 스위치와 문이 있는 석조 통로 | 같은 동작과 결과의 카메라 구도 | 스위치 밟기→문 열림→이동 |
| 06 | 눈 덮인 위험 지역 | 같은 위험·상태 변화에 단서의 유무 | 진입→상태 감소→되돌아오기 |
| 07 | 물건을 조사하는 목재 방 | 같은 정보의 전달 시점 | 관찰→조사→출구, 필요한 안내만 표시 |
| 08 | 첫 문과 계단 너머 전망대 | 첫 목표에서 끝 / 다음 관심사로 연결 | 첫 목표 도착 후 먼 대상 발견 |

공통 색은 `PAPER` 흰색/검정/파랑/노랑. 지형 재질만 저채도 돌·초목·목재·눈으로 구분한다.
오리지널 모험가 캐릭터와 간단한 공간감은 승인 샘플을 따른다.
큰 제목, 세 개의 짧은 원리, 그림과 A/B, 마지막 핵심 문장만 표시한다.
독립 씬01~08을 유지하고, 공통 렌더러는 스타일/타이밍 중복을 줄이는 용도로만 사용한다.
3D 엔진 구현이나 닌텐도 게임 화면 재현이 아닌, 자체 제작 설계 설명이다.

## 바꾸지 않는 것

- 게임 영상8개와 원래 프레임·원음 입력.
- 각 챕터1:1:1, 28908프레임 / 481.8초.
- 원본 대사·TTS·음량1.1배 전체 믹스AAC와 편집기PCM.
- 처음부터 끝까지 Discovery + 조용한 원음. 새 효과음은 추가하지 않는다.
- 한국어/영어 SRT 각각120개, 기존 타임코드.
- 작은 출처/상태 꼬리말 없음, 엔딩 크레딧 없음, 출처는 기존 한영 설명란.

## 백업·재현

기존 MP4: `shared/output/let-them-play/editorial-full-v5/before-editorial.mp4`.
이전 연결 함수: 같은 폴더 `paper-scene.before.tsx` 및 소스 내 `legacyConceptCard`.
v4 그래픽 출력/샘플은 보존하며 v5 캐시 이름으로 별도 렌더한다.

새 코드:

- `motion-canvas/src/projects/let-them-play/editorial/content.ts`: 짧은 화면 문구
- `editorial/layout.tsx`: 타이포·배치·안내·A/B·실측 길이
- `editorial/world.ts`, `art.ts`: 각 장면의 코드 기반 지형·캐릭터·동작
- 03장면은 승인된 `editorial-sample/world.ts`를 그대로 사용

```powershell
npm run build --prefix motion-canvas
node scripts/check-let-them-play-thirds.mjs
node motion-canvas/scripts/check-let-them-play-editorial.cjs
node motion-canvas/scripts/render-let-them-play-final.cjs --qa-only
# 표본 검사 후, 소스/매니페스트를 바꾸지 않고 렌더
node motion-canvas/scripts/render-let-them-play-hybrid.cjs
node scripts/verify-let-them-play-final.cjs
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-video-project.ps1 -Project let-them-play -Stage publish
```

하이브리드 렌더는 게임 프레임을 재인코딩하지 않고, 두 그래픽 구간만 렌더한다.
전체 디코드, AAC 마스터 패킷 일치, 보호 입력(음성/자막/타이밍/클립/대본) 해시를 검증한 후 MP4를 교체한다.
재믹스 시 `boost-let-them-play-voice.cjs`는 **현재** 영상의 그림을 보존해야 한다.
변경 전 백업 MP4를 입력으로 삼아 새 디자인을 되돌리지 않는다.

## 검수 기준

모든8장면의 게임/해설/비교24표본과 그래픽 앞·중간·뒤48표본, 마지막 프레임을 확인한다.
의도된 반례의 화면 가림과 실수로 생긴 글자·주인공 가림을 구분한다.
07장면의 순차 안내는 캐릭터 얼굴보다 위에 둔다. 02/05 A구도의 잘림은 비교 목적의 카메라 크롭이다.
그 밖의 제목/라벨은 잘리거나 겹치지 않아야 한다.
렌더 완료·기술 검수와 사람의 전체 청취 승인은 구분한다.

## 완료 검증 — 2026-09-14

본편8장면의 해설·A/B 화면을 모두 적용하고 `shared/output/motion-canvas/let-them-play.mp4`로 렌더했다.
H.264 1920×1080 / 60fps / 28908프레임, 영상·오디오·컨테이너 모두481.8초, 196326090바이트.

- TypeScript/Vite 빌드, 8씬24구간의 정확한1:1:1 타이밍 검사 통과.
- 라이브24구간 표본과 그래픽 앞·중간·뒤48표본, 마지막 프레임을 검토했다.
- 최종 MP4에서도24구간 +8개 비교 후반 +마지막 프레임을 따로 추출해 시각 검수했다.
- 01/08의 높은 지형 위 탑 바닥과07/08의 얼굴 위 안내 겹침을 수정했다. 02/05의 A 카메라 크롭은 의도한 반례다.
- 전체 디코드 통과, MP4의 AAC 패킷이 승인 믹스와 일치. 음성1.1배·연속 Discovery·작은 원음 유지.
- 믹스AAC/편집기PCM/원본8클립/대사/타임라인/한영SRT의 변경 전후 해시가 동일하다.
- 한영 각각120개 자막 번호·타임코드 일치, 마지막 종료08:01.030. 자막을 다시 생성하지 않았다.
- 편집기 PCM481.8초, 파형 피크0.7870, 음소거 해제·실제 재생시간 증가 확인.
- 게시 기술 검사 통과. 사람의 전체 청취 승인은 여전히 대기이며 `publishReady:false`를 유지한다.

근거: `shared/output/let-them-play/final-visual-qa/render-report.json`,
`shared/output/let-them-play/final-assembled-qa/report.json`,
`shared/output/let-them-play/editorial-full-v5/qa/`.
이 디자인 승인은 프로젝트 전용이며 전역 제작 스타일을 덮어쓰지 않는다.
