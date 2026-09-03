# 자료 출처 및 사용 계획

각 씬은 실제 게임·기술 영상 6.5초 → 채널 자체 모션그래픽의 한 쌍으로 구성한다.
영상 원본을 길게 재생하지 않고, 해당 개념을 확인하는 짧은 교육·비평용 예시로만
사용한다. 화면에는 게임명과 출처를 표시하며, 게시 전 각 원본의 최신 이용 조건을
다시 확인한다.

## 기술 사실 확인 자료

| 확인 내용 | 공식 자료 | 반영 씬 |
| --- | --- | --- |
| deltaTime은 이전 프레임부터 현재 프레임까지의 시간 간격이며 프레임 독립 이동 계산에 활용할 수 있음 | [Unity Time.deltaTime](https://docs.unity3d.com/ScriptReference/Time-deltaTime.html) | 07 |
| PS5에는 지원 게임의 Performance Mode와 Resolution Mode 우선순위를 정하는 Game Presets가 있음 | [PlayStation Support — Game Presets](https://www.playstation.com/en-us/support/games/how-to-customize-game-presets-on-ps5-consoles/) | 10 |
| 전통적인 525/60 및 625/50 텔레비전 체계 | [ITU News — Recommendation 601](https://www.itu.int/bibar/ITUJournal/DocLibrary/ITU011-2007-03-en.pdf) | 09 |
| DLSS Super Resolution과 Frame Generation은 서로 다른 렌더링 단계임 | [NVIDIA Developer — DLSS](https://developer.nvidia.com/rtx/dlss) | 14–17 |
| DLSS 4 출시 당시 Multi Frame Generation은 직접 렌더 프레임당 최대 3개의 생성 프레임을 지원함 | [NVIDIA Blackwell Architecture](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf) | 16 |
| Reflex는 CPU·GPU 렌더 파이프라인을 조정해 시스템 지연을 줄이는 기술임 | [NVIDIA Developer — Reflex](https://developer.nvidia.com/performance-rendering-tools/reflex) | 18 |

## 장면별 영상 원본

| 씬 | 파일 | 원본과 사용 구간 | 이 장면에 적합한 이유 |
| --- | --- | --- | --- |
| 01 | scene01.mp4 | [Super Mario Bros. gameplay — Gameplay Project](https://www.youtube.com/watch?v=HGmyQS09VGQ), 00:09–00:15.5 | 캐릭터의 연속 이동을 개별 정지 프레임으로 분해하기 쉬움 |
| 02 | scene02.mp4 | [Street Fighter 6 — Zangief, Lily, and Cammy Gameplay Trailer](https://www.youtube.com/watch?v=F2347gyZp0U), 00:40–00:46.5 | 빠른 격투 동작으로 60 FPS의 많은 중간 자세를 직관적으로 보여 줌 |
| 03 | scene03.mp4 | [Street Fighter II Zangief gameplay — Sporefrog08](https://www.youtube.com/watch?v=myGdMOcdTcE), 정리 원본 00:00–00:06.5 | 공격·판정·히트 스톱처럼 프레임 단위 설계가 중요한 고전 격투 예시 |
| 04 | scene04.mp4 | [Forza Horizon 5 Official Gameplay Demo — Xbox](https://www.youtube.com/watch?v=d_20X1YM28U), 04:10–04:16.5를 30/60fps로 좌우 재표본화 | 같은 원본·같은 시간·같은 이동 거리에서 표본 수만 비교 가능 |
| 05 | scene05.mp4 | [Ratchet & Clank: Rift Apart gameplay — PlayStation](https://www.youtube.com/watch?v=GffelVJeGws), 02:56–03:02.5 | 복잡한 지오메트리와 이펙트가 한 프레임 예산을 소비하는 장면 |
| 06 | scene06.mp4 | [Overwatch 2 high-FPS gameplay — NVIDIA GeForce](https://www.youtube.com/watch?v=lbcYFgQJOLM), 00:14–00:20.5 | 실제 전투와 함께 FPS 카운터가 계속 변해 가변 프레임 레이트를 직접 확인 가능 |
| 07 | scene07.mp4 | [Celeste gameplay — UltraPita](https://www.youtube.com/watch?v=URBom7N3t6I), 01:30–01:36.5 | 빠른 이동·대시가 있는 2D 게임으로 프레임률과 게임 시간 분리를 설명하기 좋음 |
| 08 | scene08.mp4 | [Overwatch high-FPS comparison — NVIDIA GeForce](https://www.youtube.com/watch?v=LKBctwWbTOk), 00:05–00:11.5 | 60·144·360 FPS/Hz 화면을 직접 비교해 높은 FPS와 주사율의 관계를 보여 줌 |
| 09 | scene09.mp4 | [Sonic 1 — 50Hz vs 60Hz, PAL vs NTSC — redhotsonic](https://www.youtube.com/watch?v=iPhESbeKFIE), 02:34–02:40.5 | PAL/NTSC 버전의 실제 게임 속도 차이를 같은 화면에서 확인 가능 |
| 10 | scene10.mp4 | [Horizon Forbidden West — New Threats Gameplay Trailer — PlayStation](https://www.youtube.com/watch?v=jbu294Nv7Q8), 00:08–00:14.5 | PS5 세대 콘솔의 높은 그래픽 품질과 렌더링 부하를 보여 주는 일반 예시 |
| 11 | scene11.mp4 | [Alan Wake 2 Full Ray Tracing — NVIDIA GeForce](https://www.youtube.com/watch?v=tiUiCzzVu8g), 01:38–01:44.5 | 밝은 실외와 조명 장면에서 패스 트레이싱의 프레임 비용을 읽기 쉽게 보여 줌 |
| 12 | scene12.mp4 | [Black Myth: Wukong RTX 50 Series/DLSS 4 — NVIDIA GeForce](https://www.youtube.com/watch?v=wcn25vlHgec), 00:14–00:20.5 | RTX 50 시리즈와 AI 렌더링을 함께 소개하는 공식 사례 |
| 13 | scene13.mp4 | [Minecraft with RTX — NVIDIA GeForce](https://www.youtube.com/watch?v=91kxRGeg9wQ), 00:29–00:35.5 | 단순한 블록 장면에서도 픽셀 단위 광선 추적 비용이 생김을 선명하게 보여 줌 |
| 14 | scene14.mp4 | [DLSS 4 technology explainer — NVIDIA GeForce](https://www.youtube.com/watch?v=qQn3bsPNTyI), 04:47–04:53.5 | Horizon Forbidden West의 Super Resolution 입력·출력 차이를 보여 주는 공식 비교 |
| 15 | scene15.mp4 | [Cyberpunk 2077 DLSS 4 — NVIDIA GeForce](https://www.youtube.com/watch?v=avWMEd-H8Qg), 00:09–00:15.5 | 실제 게임에서 Frame Generation 적용 결과를 보여 주는 공식 사례 |
| 16 | scene16.mp4 | [Star Wars Outlaws DLSS 4 Multi Frame Generation — NVIDIA GeForce](https://www.youtube.com/watch?v=dR9i2WVcXTM), 00:10–00:16.5 | Multi Frame Generation과 표시 FPS 증가를 보여 주는 별도 게임 사례 |
| 17 | scene17.mp4 | [Black Myth: Wukong DLSS 4 launch video — NVIDIA GeForce](https://www.youtube.com/watch?v=k6YkuhUxETE), 00:14–00:20.5 | 성능 오버레이를 통해 렌더 FPS와 표시 FPS를 구분해야 하는 이유를 연결하기 좋음 |
| 18 | scene18.mp4 | [Counter-Strike 2 NVIDIA Reflex — NVIDIA GeForce](https://www.youtube.com/watch?v=96jRLXyjeao), 00:12–00:18.5 | 경쟁 FPS 게임에서 프레임률과 입력 지연을 함께 보되 같은 값으로 혼동하지 않게 함 |
| 19 | scene19.mp4 | Street Fighter II 00:00–00:06.5 + Alan Wake 2 01:38–01:44.5 좌우 합성 | 프레임 결합형 고전 로직과 현대 다단계 렌더 파이프라인을 의도적으로 재비교 |
| 20 | scene20.mp4 | Street Fighter 6 + Overwatch 2 + Horizon Forbidden West + Star Wars Outlaws 4분할 | 앞서 설명한 시간·반응성·그래픽·AI 렌더링을 한 화면에서 총정리 |

20개 클립은 scripts/build-frame-rate-broll.ps1로 1280×720, H.264, 60fps로
재생성한다. -OutputDir를 지정하면 기존 파일을 건드리지 않고 검수용 폴더에 먼저
출력할 수 있다.

## 반복 사용 원칙

- 01–18번은 씬마다 서로 다른 원본 또는 서로 다른 게임 사례를 사용한다.
- 19번의 Street Fighter II와 Alan Wake 2 재사용은 ‘과거 ↔ 현대’ 비교를 위한 합성이다.
- 20번의 네 영상 재사용은 새 단일 클립처럼 보이지 않게 4분할 총정리로 명시한다.
- 같은 원본의 비슷한 구간을 단순 배경처럼 반복하는 구성은 사용하지 않는다.

## 오디오와 이용 범위

- 01과 07의 Creative Commons 표시는 다운로드 당시 YouTube 메타데이터를 기준으로
  기록했다. 게시 직전 원본 페이지에서 라이선스와 표시 조건을 다시 확인한다.
- 03과 09는 비평·교육에 필요한 짧은 화면만 인용하고 원음은 최종 믹스에서 사용하지 않는다.
- 공식 게임·기술 영상은 출처를 화면과 설명란에 밝히고 짧게 변형 인용한다. 공식 영상의
  광고 음악과 음성은 최종 믹스에서 제거한다.
- 재생성된 단일 클립에는 편집 판단을 위해 원본 오디오 스트림을 보존한다. 사용이 허용된
  게임 효과음·환경음만 내레이션 아래에 작게 믹스한다.
- BGM은 사용자가 곡과 라이선스를 승인하기 전까지 넣지 않는다.
- 짧은 인용과 출처 표시는 자동으로 이용 허락을 보장하지 않는다. 실제 게시 지역과
  수익화 방식에 따른 최종 권리 판단은 업로더가 다시 확인한다.
