# 근거와 범위 — 2026-09-27

읽기 전용으로 로컬 Git 이력·diff·문서를 확인했다. 원격의 새로운 커밋은 fetch하지 않았으며 사용자 스크린샷과 로컬 HEAD의 최신 두 제목이 일치한다.

- 저장소: `D:/Github/YamYam_Engine`.
- 기반: `e6ca779`.
- `49e04e5e875f04cfb792ea8a71e10667be78ad41`: Fix DX12 frame sync and editor rendering.
- `ce56f16dd7a40fd2b4bf03c680790e5b637c7530`: Add DX12 PSO variants and display SRVs.
- 두 커밋 모두 로컬 기록상 2026-09-14 작성. 제작일과 혼동하지 않는다.

## 코드로 확인한 사실

- frame slot별 fence 추적, allocator 재사용 전 완료 대기, 단조 증가 fence 값.
- ImGui와 엔진 command queue / shader-visible SRV heap 공유. 프레임/리소스 수명 정리.
- Scene/Game 별도 카메라·오프스크린 타깃, per-draw 상수 버퍼 할당, 리사이즈 요청과 지연 회수.
- 재질의 Bind에서 모드를 전달. shader 상태 조합별 PSO 캐시, CutOut 전용 YA_ALPHA_TEST.
- Opaque/CutOut: LessEqual + depth write. Transparent: Always + no depth write, 원거리부터 정렬. 후자는 기존 정책을 보존한 것으로 일반적 정답 아님.
- 표시 SRV는 읽는 alpha만1. 원본 RGBA 텍스처 변경 아님. RGBA8 첫 컬러 attachment 대상.
- smoke test 추가/확장. 현재 세션에서 실행하지 않았으므로 통과 여부 미확인.

세부 근거: 해당 커밋의 `Docs/DX12_Scene_Game_Views.md`, `YamYamEngine_CORE/yaShader.cpp`, `yaMaterial.cpp`, `yaRenderTarget.cpp`, `yaGraphicDevice_DX12.cpp`, `Tests/DX12RenderingSmoke.cpp`.

## 공식 기술 교차 확인

- Allocator 재사용 전 GPU 완료: https://learn.microsoft.com/en-us/windows/win32/api/d3d12/nf-d3d12-id3d12commandallocator-reset
- PSO 역할: https://learn.microsoft.com/en-us/windows/win32/direct3d12/managing-graphics-pipeline-state-in-direct3d-12
- SRV component mapping: https://learn.microsoft.com/en-us/windows/win32/api/d3d12/ne-d3d12-d3d12_shader_component_mapping

## 미검증 / 게시 전 점검

엔진 실행 성공, 버그 전후 재현, WARP/실GPU 테스트 결과, 창 도킹·기즈모 조작, 포함 텍스처/스프라이트 권리, 사용자 최종 청취는 아직 검증하지 않았다. 성능 수치나 완전한 버그 해결을 추정해 말하지 않는다.
