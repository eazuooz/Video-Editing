# 9편 검수본

검수 번호 8의 EUD 유즈맵을 제외하고 번호 1–7, 9, 10을 유지한다. 제목과 영상 상단 문구는 `nine.json`을 사용한다. 입력 검수본은 `delivery/review-ten-62f9b9be1224.json`의 SHA256으로 고정했다.

5번은 실제 지프·나무 장면에서 로프를 확인한 뒤 Unity 시연으로 이어진다. 옆면 시연은 길이 3.15 m의 동일한 줄을 40개 선분으로 그리고, 양 끝의 거리가 증가해도 전체 선분 길이를 유지하는 처짐을 구한다. 위에서 본 기둥 단면에서는 같은 91개 끝점 위치를 두 차례 재생한다. 빨강은 직선 중 사각 기둥 내부에 있는 구간이고, 초록 점은 기둥을 돌아가는 경로의 접점이다. 상용 게임에서 확인한 내용은 입자 로프와 모서리를 따라가는 별도 경로를 함께 유지했다는 개발자의 설명이다. 선분 예시는 우리 시연이다. [너티 독 프로그래머 인터뷰](https://80.lv/articles/how-naughty-dog-created-the-immersive-world-of-the-last-of-us-part-ii)

10번은 이전의 Unity 부대 6기와 동일한 명령·이동 속도로 시드 42와 7을 비교한다. 매 틱의 체력과 첫 전차의 다음 발사 시각을 기록했고, 시드 42의 체력이 지난 검수본의 기록과 다시 일치하는지 확인했다. 이어 기존 이동 속도 비교 영상에서 버전 변경의 영향을 보여준다. 원래 경기 재생에 필요한 실행 파일, 데이터 버전, 맵을 설명하고 옛 자료를 확보할 수 있는 경우와 없는 경우를 구분한다. [블리자드 기술 문서](https://github.com/Blizzard/s2client-proto/blob/master/docs/protocol.md#game-versions)

Unity 6000.6.0f1의 기존 격리 프로젝트에서 `RopeRig.cs`는 `Assets/VideoScenes/GeneralReview`에, `CloseupCapture.cs`는 그 아래 `Editor`에 둔다. 리플레이는 이전 검수본의 `FeedbackRTS/ReplaySquad.unity`와 갱신된 `CommandReplay.cs`를 사용한다. `YAMYAM_GENERAL_REVIEW`에 출력 폴더를 지정하고 D3D11 WARP로 `CloseupCapture.Run`을 실행한다. `unity-scene/`은 이번 로프 씬과 재질, 임포트 GUID의 스냅샷이다. 데모의 측정값과 소스는 `native-evidence.json`에서 확인할 수 있다.
