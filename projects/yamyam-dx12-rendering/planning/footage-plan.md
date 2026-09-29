# 실제 엔진 녹화 + 설명 도식 계획

아직 녹화하지 않은 촬영 계획이다. 본편 8씬, 목표 5~7분. 예시 슬롯 19.5초는 초깃값이며 실측 TTS와 유의미한 동작에 맞춰 조절한다. 짧은 영상을 반복하거나 느리게 늘리지 않는다.

| 씬 | 실제 개발 화면(먼저) | 자체 Motion Canvas 설명(다음) | 코드 근거 |
|---|---|---|---|
| 01 | 현행 엔진 Scene/Game 전체 모습. 실행 확인 전 성공 화면으로 주장하지 않음 | 한 장의 화면 뒤 CPU/GPU/재질/에디터 레이어 | 두 커밋 전체 |
| 02 | 디버거에서 frame index, allocator, fence 값. 입력/개인 경로 숨김 | CPU와 GPU 두 타임라인, 사용 중인 슬롯은 잠금 | yaGraphicDevice_DX12.cpp: WaitForNextFrameResources, SignalFrameCompletion, MoveToNextFrame |
| 03 | 같은 씬을 다른 두 카메라에서 관찰 | 카메라2개 → 별도 렌더 타깃 → ImGui | guiSceneWindow.cpp, guiEditorApplication.cpp, yaConstantBuffer.cpp |
| 04 | Game 패널 크기 변경, 포커스 이동, Scene 기즈모. 수동 동작 녹화 필요 | 기존 텍스처 보관 → fence 완료 → 회수 | yaRenderTarget.cpp, CollectRetiredResources |
| 05 | 같은 Shader를 사용하는 서로 다른 Material 설정과 결과 | 공유 Shader + 모드별 PSO 선택. 공유 객체 변경과 draw-time 선택 비교 | yaMaterial.cpp, yaShader.cpp |
| 06 | 불투명/컷아웃/반투명 색·깊이 비교. 현행 제약도 보여줌 | 3모드 겹침 비교, Transparent Always/no-write 명시 | YA_ALPHA_TEST, Shader::GetPipelineState |
| 07 | 테스트용 반투명 결과의 원본 RGBA와 에디터 표시 비교 | 원본 RGBA 보존 / 표시용 SRV alpha=1 분기 | RenderTarget::GetDisplaySRV |
| 08 | 새로 실행한 smoke test 실제 출력과 수동 확인 | 확인 항목 체크, 미확인 항목 별도 표시 | Tests/DX12RenderingSmoke.cpp |

## 촬영 안전·정확성

- 엔진 원본 저장소의 미커밋 파일을 덮거나 과거 커밋으로 전환하지 않는다. 과거 증상 재현 필요 시 별도 격리 checkout을 계획한다.
- 현재 커밋 코드 검토와 실행 검증을 구분한다. 테스트 소스 존재만으로 통과라고 말하지 않는다.
- 자동 테스트는 WARP/하드웨어를 구분해서 기록한다. 수동 도킹/기즈모 검증은 별도다.
- 오류 전후를 직접 재현하지 못하면 차이는 자체 도식으로 보여주고 설명용이라고 적는다.
- 외부 YouTube 개발 영상은 필요하지 않다. 사용자 엔진 코드와 새 실행 녹화를 우선한다. 게임 자산/텍스처의 게시 권리는 별도 확인한다.
- 원음에 말소리가 없으면 억지 효과음을 넣지 않는다. 승인된 BGM만 낮게 연속 사용하거나 무BGM을 선택받는다.
- 본편 뒤 10초 회원 감사 화면. 원본 프로필·핸들·배지 확보 전 대체 이미지를 만들지 않는다.
