# 20개 씬 B-roll 적합성 검토

검토일: 2026-09-03

판정 기준은 다음 네 가지다.

1. 내레이션의 핵심 개념이 화면에서 직접 보이는가
2. 앞 장면과 동일한 영상을 단순 반복하지 않는가
3. 6.5초 안에 의미를 파악할 수 있는가
4. 출처와 사용 구간을 다시 만들 수 있게 기록했는가

| 씬 | 설명의 핵심 | 최종 예시 | 판정과 이유 |
| --- | --- | --- | --- |
| 01 | 프레임은 화면 한 장 | Super Mario Bros. | 적합 — 이동 궤적을 정지 프레임으로 나누기 쉬움 |
| 02 | 1초에 60장 | Street Fighter 6 | 교체 — Smash 반복 대신 60fps 격투 동작의 중간 자세가 잘 보임 |
| 03 | 프레임이 시간 눈금이던 설계 | Street Fighter II | 유지 — 고전 격투의 프레임 단위 타이밍과 직접 연결됨 |
| 04 | 30fps와 60fps의 표본 수 | Forza Horizon 5 30/60 재표본화 | 교체 — 이동이 일정한 레이싱 장면이라 같은 시간·거리 비교가 명확함 |
| 05 | 프레임 예산 | Ratchet & Clank | 유지 — 복잡한 오브젝트와 이펙트가 GPU 작업량을 보여 줌 |
| 06 | 가변 프레임 레이트 | Overwatch 2 FPS 카운터 | 교체 — 전투 중 FPS 수치 변동이 화면에 직접 나타남 |
| 07 | deltaTime | Celeste | 구간 교체 — 대시와 이동이 이어져 프레임 독립 시간 설명에 적합함 |
| 08 | 120/240fps와 Hz | Overwatch 60/144/360 비교 | 교체 — 경쟁 슈팅에서 높은 FPS·주사율 차이를 직접 비교함 |
| 09 | NTSC와 PAL | Sonic 50Hz/60Hz 비교 | 교체 — 실제 PAL/NTSC 속도 차이를 좌우로 볼 수 있음 |
| 10 | PS5 품질·성능 선택 | Horizon Forbidden West | 교체 — PS5 세대 그래픽 부하를 보여 주되 특정 옵션 수치는 단정하지 않음 |
| 11 | 프레임당 GPU 작업 | Alan Wake 2 Full RT | 교체 — 조명·반사·그림자·패스 트레이싱 사례가 선명함 |
| 12 | RTX 50 시리즈 | Black Myth: Wukong RTX 50 | 교체 — 해당 세대 GPU와 DLSS 4를 직접 다루는 공식 사례 |
| 13 | 4K·광선 추적 계산량 | Minecraft with RTX | 교체 — 픽셀과 광선 개념을 단순한 공간에서 읽기 쉬움 |
| 14 | DLSS Super Resolution | Horizon DLSS 비교 | 유지 — 내부 렌더 해상도와 출력 해상도의 차이를 보여 주는 공식 비교 |
| 15 | Frame Generation | Cyberpunk 2077 | 유지 — 직접 렌더 사이의 생성 프레임 결과를 설명하는 공식 사례 |
| 16 | Multi Frame Generation | Star Wars Outlaws | 교체 — 15번과 다른 게임으로 MFG 단계를 분리함 |
| 17 | 렌더 FPS와 표시 FPS | Black Myth: Wukong 성능 영상 | 교체 — 성능 오버레이가 있어 두 수치의 구분으로 연결 가능함 |
| 18 | FPS와 입력 지연 | Counter-Strike 2 Reflex | 유지 — 경쟁 FPS의 입력 지연 사례와 직접 맞음 |
| 19 | 과거·현대 파이프라인 | Street Fighter II ↔ Alan Wake 2 | 의도적 재사용 — 비교 목적을 좌우 합성으로 명확히 표시함 |
| 20 | 전체 정리 | SF6·Overwatch·Horizon·Star Wars 4분할 | 의도적 재사용 — 네 범주를 동시에 복습하는 몽타주임 |

## 검토 결론

- 기존 구성에서 단순 반복되던 Mario, Ratchet & Clank, Cyberpunk/DLSS 구간을 줄였다.
- 격투 게임은 02·03번에서 60fps 움직임과 프레임 단위 설계를 각각 담당한다.
- 슈팅 게임은 06·08·18번에서 가변 FPS, 고주사율 체감, 입력 지연을 각각 담당한다.
- 동일 원본의 재사용은 19·20번의 비교·요약 합성에만 남겼다.
- 최종 영상은 각 B-roll의 원본 소리와 설명 구간 BGM을 내레이션 우선으로 믹스했다.

## 최종 출력 검증

- 최종본: shared/output/motion-canvas/frame-rate-modern-rendering.mp4
- 출력 규격: 1920×1080, 60fps, 445.8초, H.264 영상 + 48kHz 스테레오 AAC
- 장면 클립: 20개, SHA-256 기준 20개 모두 서로 다른 파일
- B-roll 접촉시트: shared/output/motion-canvas/frame-rate-modern-rendering-qa/broll-contact.jpg
- 모션그래픽 접촉시트: shared/output/motion-canvas/frame-rate-modern-rendering-qa/motion-contact.jpg
- 한국어 SRT: 83개 큐, 영어 SRT: 109개 큐, 모두 2줄 이하·겹침 없음·445.68초 종료
- narration 단계 자동 검사는 통과했다.
- 19개 장면의 원본 소리를 보존했다. 원본이 사실상 무음인 07번은 BGM으로 대체했다.
- 설명 구간에는 `Nimbus — Eveningland`를 사용했고, 최종 측정값은 -17.0 LUFS / -1.6 dBTP다.
