# 검수 의견을 반영한 10편 (2026-11-05)

고정 입력은 최초 검수본 `delivery/review-ten-be331655c1ba.json`의 네 파일과 해시다. 이 수정은 기존 게임 녹화와 원래 대사를 보존하고 필요한 문장만 덧붙인다. 제목·화면 문구·추가 한영 문장은 `edit.json`, 네 편에 추가하는 음성은 `extra-speech.json`에 있다. 사용자 검수 전에 게시하지 않는다.

| 번호 | 바뀐 설명/화면 | 근거 |
|---|---|---|
| 1 | 병에 고정된 경계와 중력에 수직인 경계를 차례로 그린다. 완전히 정착한 수평선은 반 채운 대칭 몸통의 설명 예시이며, 흔들림까지 계산한 원작 셰이더의 복제는 아니다. | 기존 제작 원장의 Valve 개발자 인터뷰 |
| 2 | 눈 **아래**에서 발목까지 쳐다보는 직교 카메라, 발바닥 실루엣, 흔적 누적, 테셀레이션으로 내부 꼭짓점 생성, 같은 높이맵을 샘플링해 변위. 콘솔의 릴리프 매핑은 구분한다. | [개발자 GDC 발표 12쪽부터](https://colinbarrebrisebois.com/wp-content/uploads/2022/06/gdc2014-deformable_snow_rendering.pdf#page=12) |
| 3 | 선체 단면·노란 마스킹 메시의 경계·바다 픽셀·별도 침수 수면을 차례로 표시한다. 배를 띄우는 부력과 물을 숨기는 렌더링은 다른 문제다. | [개발자 설명](https://speps.fr/articles/water-masking-sea-of-thieves/) |
| 4·5·7·9 | 새 제목을 실제 인코딩 영상 상단부터 마지막 화면까지 반영하고, 대사·자막·음원은 보존한다. | 직전 검수본 |
| 6 | 막히는 광물 입금 → 다음 병력 생산 중단 → 전투를 멈추고 기지에 돌아와야 하는 문제를 설명한다. 재미에 대한 해설은 개발자의 직접 인용이 아니다. | [원래 길찾기를 만든 개발자의 회고](https://www.codeofhonor.com/blog/the-starcraft-path-finding-hack) |
| 8 | 안전하지 않은 메모리 접근을 다시 열지 않고, 지원 요청의 뜻만 해석해 옛 맵의 규칙을 되살리는 선택을 보여준다. 모든 EUD 맵을 복구했다고 말하지 않는다. | [블리자드 1.21.0 공지](https://news.blizzard.com/en-us/article/21313396/patch-1-21-0-the-return-of-eud-maps) |
| 10 | 원래 경기/리플레이는 독립적으로 처음부터 실행한다. 6기의 위치와 포탑 HP를 매 두 번째 틱에서 대조한다. 세 번째 실행은 이동 속도만 바꾼다. | [Blizzard 리플레이 프로토콜](https://github.com/Blizzard/s2client-proto/blob/master/docs/protocol.md) |

Unity 실험은 자체 단순화한 60틱/초 RTS다. 제120틱 이동, 제240틱 공격. 6기 부대는 전차 두 종류, 지프, 헬기의 조합이며 상대는 포탑과 격납고다. 보유한 Army Pack – Cute Series에서 사용한 원본·해시는 `unity-source.json`에 있다. `scene/`은 편집 가능한 씬·재질·임포트 설정 스냅샷이다. 새 프로젝트에서 열려면 `Assets/VideoScenes/FeedbackRTS`에 복사하고, 루트에 `CommandReplay.cs`, `Editor`에 `ReplayCapture.cs`, `Models`에는 목록의 FBX와 텍스처를 기존 메타 파일 옆에 둔다. 상품 바이너리는 Git에 재배포하지 않는다.

`capture-replay.py`는 격리된 Unity 프로젝트에서 소프트웨어 장치만 사용한다. `build.py`는 자막·무자막 마스터, KO/EN SRT, 대본 검수 페이지를 만든다. `check.py`는 실제 두 인코딩 전체를 디코딩하고 양쪽 AAC 동일성, 자막 시각, 모바일 표본을 확인한다. `review.py`는 허용한 파일만 범위 요청으로 제공하고, `check-player.cjs`는 검수 대본의 재생과 중간 문장 탐색을 점검한다. 이 점검은 전체 청취나 사람의 최종 승인과 다르다.
