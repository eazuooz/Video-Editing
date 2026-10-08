# 출처와 검토

- 사용자 Notion: https://app.notion.com/p/3e10b1ffa61e81b89e84e105448fbb50. 핵심 절을 대조하고 쉬운 원래 예제로 설명. 원문 낭독이 아니다.
- 실제 게임: https://www.youtube.com/watch?v=fN4iMYUyODc, Sunset Overdrive, NCR Gameplay. 촬영자 허락: Native description2026-10-09: Free to use Gameplay Recorded on PC,for your videos. Recording permission only; game-IP/publication review pending. No CC BY claim.. 공개 전 게임IP 검토는 별도 대기. 원음 제외, 편집한 발췌, 화면 출처 표기.
- 실제 게임: https://www.youtube.com/watch?v=wzQLP0Z3zII, Big Walk, NCR Gameplay. 촬영자 허락: Uploader native description explicitly offers Free to use Gameplay Recorded on PC, for your videos. Read2026-10-08; no named CC license. Recording permission only; public game-IP review pending; no guarantee against platform claims.. 공개 전 게임IP 검토는 별도 대기. 원음 제외, 편집한 발췌, 화면 출처 표기.
- 실제 게임: https://www.youtube.com/watch?v=kc8aMSmWSgw, Megabonk, NCR Gameplay. 2026-10-09에 원본 설명의 PC 녹화 재사용 허용 문구와 실제 플레이를 확인했다. 촬영 자료 사용 허락이며 게임IP·공개 권리 검토는 별도 대기한다. 메뉴 구간을 제외하고 각진 바위·벽·기둥 사이의 실제 이동을 발췌한다. 원음 없이 화면 출처를 표시한다. 상세 구간과 직접 검토 기록은 `production/batches/game-math-part2-full-series/preflight/mesh-uv-megabonk-fine-review.json`에 있다.
- Big Walk는 앞선 렌더링 강의에서 사용했던 게임이다. 이번에는 이전 구간과 겹치지 않는 초록 방, 노란 벽과 원형 구멍, 붉은 갑판 구간을 새로 확인했다. 픽셀로 내부 삼각형 수·법선 계산·UV 구현을 단정하지 않는다.
- 초록 방 장면06은 원본200–270초 범위다. 추가260–270초의 실제 이동·곡면·격자를11개 샘플로 직접 확인한 근거는 `projects/game-math-mesh-uv/production/green-room-extension.json`에 보존했다. 다음 편의270초 이후 자료와 중복하지 않으며, 최종 사용 길이는 실측 음성과 조용한 문장 경계의 관찰 휴지 허용치 안에서 확정한다.
- 노란 개구부 장면15의 추가706–708초는 실제 캐릭터가 구조물을 통과하는 동작이다.706–710초를5개 샘플로 직접 확인한 뒤 바닷가로 이동하는 뒤쪽709–710초는 제외했다. `production/yellow-opening-extension.json`에 근거를 보존하고, 이전 렌더링 편에서 사용한716초 이후 자료와 중복하지 않는다.
- 기존 채널 DirectX11 강의 https://www.youtube.com/watch?v=-3NQEd_8mWg 의 전체 자막을 중복 검토했다. UV 기본 개념의 일부는 겹치지만 이번 편의 질문은 메시 저장과 법선 만들기이며, 다음 편은 법선 변환과 보간 뒤 UV 주소 처리 순서를 설명한다. API 설정 강의를 다시 제작하는 것은 아니다. 실제 Studio와 내용 비교 근거는 `production/batches/game-math-part2-full-series/preflight/mesh-uv-content-duplicate-review.json`에 있다.
- 승인된 원본 회원·로고와 Qwen 참조 목소리를 유지한다. BGM과 게임 오디오 없음. 개인 음성참조·영상은 Git 제외한다.
