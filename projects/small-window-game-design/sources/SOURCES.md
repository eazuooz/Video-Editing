# 출처와 사용 상태 — 2026-09-26

## v2 본편에 선택한 소스 (아래 과거 후보와 구분)

- Forza Horizon 5: https://www.youtube.com/watch?v=ZnCxVxfv3MM — No Copyright Gameplay. 30초, 185초, 75초, 285초부터 각기 다른 주행 구간. 정확한 아웃점은 `production/full-v2/plan.json` 참조.
- DOOM: https://www.youtube.com/watch?v=YANZzc_bHSU — No Copyright Gameplay, “DOOM - Free To Use Gameplay (60 FPS)”. 65초, 115초부터 서로 겹치지 않는 전투/관찰 구간. DOOM Eternal로 표기하지 않는다. 초기 170초 아이템 획득 컷은 표적 설명에 맞지 않아 최종 제외했다.
- 두 소스의 실제 업로더 설명에서 해설·편집한 영상에 대한 재사용·수익화 허용 및 채널 크레딧 안내를 확인했다. 원본을 자체 무료 자료처럼 재배포하지 않는다.
- Bethesda 공식 정책 확인: https://bethesda.net/en-NZ/news/bethesda-video-policy — 게임 플레이를 이용한 팬 영상과 YouTube 파트너 프로그램을 허용하되 제3자 콘텐츠는 별도 허락 대상이다.
- Microsoft 공식 조건: https://www.xbox.com/en-US/developers/rules — 출처·비공식 안내를 설명란에 기록. 음악 등 제3자 권리는 별도이다.
- 전체 원본을 35초 간격 스틸로 확인했다. 얼굴 없는 실제 게임 플레이이며, 본편 컷은 반복/인위적 슬로다운 없이 정상 속도로 사용한다. 스틸 확인은 전체 청취나 제3자 음악 권리 확인을 대신하지 않는다.
- 원음은 해설 아래 작게 믹스한 **검토용 본편**에 포함된다. 최종 청취 및 원음 권리 검토 전에는 `publishReady=false`이다. 작은 음량이 권리 확인을 대신하지 않는다.
- 화면 비율·FOV 비교는 직접 그린 원근 투영 도식이다. Forza/DOOM의 실제 카메라 설정을 바꾸어 측정한 결과처럼 주장하지 않는다.
- 화면 비율 정책 참고: https://docs.unity3d.com/6000.0/Documentation/Manual/PhysicalCameras.html (Gate Fit: crop/overscan/stretch 설명). 고정 세로 FOV 비교에서 가로를 넓혀도 물체 비율을 왜곡하지 않는다.

현재 핵심 범위는 화면 프레임·비율·FOV·점유율·UI 가림이다. 아래 VR과 다른 게임 링크는 초기 조사 기록이며 본편 삽입 목록이 아니다.

## 논지 참고

- https://www.youtube.com/watch?v=DGIJk0Uh8jU — 사용자가 제공한 일본어 전문을 참고해 독립 대본을 작성했다. 원본 영상/음성/캐릭터/고유 구성은 복제하지 않는다. 영상 재사용 허용으로 취급하지 않는다.

## 기술 설명의 공식 근거

- Unity 카메라/원근 투영: https://docs.unity.com/en-us/engine/6000.0/manual/cameras/camera-view/understanding-frustum
- Unity FOV: https://docs.unity.com/en-us/engine/6000.3/script-reference/unityengine/camera/fieldofview
  - 원근 투영의 조건과 FOV 축을 구분한다. 비교는 자체 수평 60°/100° 예시다.
- PS VR2 공식 소개: https://blog.playstation.com/2022/01/04/playstation-vr2-and-playstation-vr2-sense-controller-the-next-generation-of-vr-gaming-on-ps5/
  - 눈 움직임 감지 기능이 명시된다. VR은 반드시 고개로만 봐야 한다고 일반화하지 않는다. 제품 수치/성능 비교는 하지 않는다.

## 게임 화면 후보 — 아직 최종 편집 미삽입

- https://www.youtube.com/watch?v=ZnCxVxfv3MM — Forza Horizon 5, No Copyright Gameplay, 2025-08-20.
- https://www.youtube.com/watch?v=LaDeFqohBD4 — Forza Horizon 5, No Copyright Gameplay, 2024-05-06.
  - 두 설명에서 해설·편집을 더한 재사용 허용과, 동일한 무료자료 채널로 자신의 것처럼 재배포 금지를 확인했다.
  - 설명란 크레딧 계획: `Gameplay — No Copyright Gameplay` + 실제 사용 URL.
  - 게임 IP 정책과 제3자 라디오/음악은 별도 확인 필요. 원하는 카메라 시점과 동작은 아직 프레임 미검수.
- https://www.youtube.com/watch?v=i9OAtLUswIQ — DOOM Eternal 후보. 설명을 추가 조회해 편집 재사용·채널 크레딧 안내를 확인했다. 좋아요·구독 요청도 포함되어 조건의 성격을 확정하지 않았으므로 사용 보류. 사용자 계정으로 좋아요/구독하지 않음. 게임 권리 정책·내용·인아웃도 추가 확인 필요.
- https://www.nintblkc.com/archive-64 — 편집용 재사용 안내 확인. 다른 채널/자료에 확장 적용하지 않음.

## 음악

- https://www.scottbuckley.com.au/library/discovery/
- https://www.scottbuckley.com.au/library/wanderlust/
- https://www.scottbuckley.com.au/library/using-this-music/

공식 CC BY 4.0 조건과 YouTube 설명란 크레딧 의무 확인. Discovery 사용자 선택 승인.
기존 원본 `shared/assets/music/scott-buckley/sb_discovery.mp3`를 사용한다. 선택 확정과 실제 믹스 완료는 별도다.

## 자체 도식

새 Motion Canvas 코드로 만든 설명용 도로/차/표적/모니터다. 실제 게임이나 사용자 실험 결과가 아니다.
현재 무음 콘셉트는 실사례를 삽입한 완성본이 아니다. 소스 인아웃표·원음·권리 확인 후 최종 편집한다.

## 첫 장면 승인용 영상에 실제 사용한 소스

- `sources/media/forza-ZnCxVxfv3MM-30-75-avc.mp4`: 원본 30–75초 확보, H.264/AAC, 1920×1080/60fps, 45초.
- 승인용 편집 사용 구간: 30.000–50.917초. 반복 없이 전체화면으로 재생. 원본 35/45초 스틸에서 추적 시점 주행·코너·차량 확인.
- TTS, 소리 낮춘 원음, Discovery 포함. 아직 전체 본편/게시본이 아니다.
- 업로더 설명에서 해설 추가 조건의 재사용 허용 재확인(yt-dlp로 실제 설명 조회). 출처: https://www.youtube.com/watch?v=ZnCxVxfv3MM
- Microsoft 가이드: https://www.xbox.com/en-US/developers/rules — YouTube 광고 수익 예외, 출처·비공식 안내 필요. 제3자 차량·브랜드·음악 권리는 별도이므로 최종 검토 전 `publishReady=false`를 유지한다.
- 원음 게시용 검토 미완료. 미확인 원음을 BGM 볼륨으로 숨겼다고 권리가 해결되는 것으로 취급하지 않는다.
- 원본 회원 사진·이름·배지 자료 미확보, 전체 엔딩 제작은 별도 대기.
