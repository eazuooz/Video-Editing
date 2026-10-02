# DX12 PSO로 렌더링 모드와 ImGui 화면 합성하기 출처와 구현 확인

검토일 2026-10-01. 현재 엔진 HEAD는 845442b7d756e7a991c09799ab58a775803a006a입니다. 소스코드와 노션에서 읽을 수 있는 본문을 검토했으며 이번 세션에서 엔진 빌드·테스트·실행은 하지 않았습니다.

## 노션과 커밋 연결

- [해당 강의](https://www.notion.so/3dc0b1ffa61e8153b02fd321cc48e655)
- 최신 문서 커밋 [845442b](https://github.com/eazuooz/YamYam_Engine/commit/845442b7d756e7a991c09799ab58a775803a006a)는 문서 묶음이며 엔진 기능 한 개를 추가한 커밋이 아닙니다.
- 구현은 주로 [49e04e5](https://github.com/eazuooz/YamYam_Engine/commit/49e04e5e875f04cfb792ea8a71e10667be78ad41)와 [ce56f16](https://github.com/eazuooz/YamYam_Engine/commit/ce56f16dd7a40fd2b4bf03c680790e5b637c7530)에 연결됩니다.
- 역사적 동기화 사례 일부는 이전 7ac7ef2에도 연결됩니다. 과거의 Reset 뒤 Wait 오류를 49e04e5에서 처음 고쳤다고 대본에 단정하지 않았습니다.

## 직접 확인한 코드

범위별 발췌와 파일 SHA-256은 code-evidence.json에 보관합니다. 전체 코드 경로와 행 번호는 대본의 각 장면에 연결했습니다. 다음 사실은 현재 소스 범위로 확인했습니다.

- Material은 mode만 저장하고 Bind 때 Shader::Bind(mMode)로 전달합니다. Shader는 raster/blend/depth 조합 PSO를 캐시합니다.
- Opaque/CutOut은 LessEqual 및 depth write, Transparent는 Always 및 no-write입니다. Transparent는 기존 정책을 보존해 불투명 뒤에서도 합성될 수 있습니다.
- CutOut에만 YA_ALPHA_TEST PS blob을 사용하며 clip(color.a-0.01f)는 음수만 버립니다. alpha0.01은 통과합니다. 일반 custom shader에도 해당 분기가 필요합니다.
- 정렬은 현재 전달된 scene 목록 안에서 object position 거리 기준입니다. 전체 scene들 간 전역 정렬이나 교차 삼각형 픽셀 정렬이 아닙니다.
- RGB는 SRC_ALPHA/INV_SRC_ALPHA, alpha는 ONE/ZERO입니다. 원본 RT alpha는 누적 coverage가 아닙니다.
- GetDisplaySRV는 첫 RGBA8 attachment의 같은 resource에 새 descriptor를 만들고 alpha를 1로 mapping합니다. 원본 픽셀 수정/전체 복사는 하지 않습니다.
- Retire는 resource와 descriptor를 UINT64_MAX 미확정 상태로 보관하고 최종 frame Signal에서 Seal한 뒤 completed value로 Collect합니다. 중간 Upload Wait는 미확정 retirement를 Seal하지 않습니다.
- Smoke test는 303 Draw, 두 카메라, 모드/깊이/정렬/공유 shader 변경/ImGui 합성을 검사하지만 해당 ImGui 구간은 ViewportsEnable를 끕니다. 별도 OS 창의 수동 조작 검증이 남습니다.

## 공식 기술 교차 확인

- [CommandAllocator Reset](https://learn.microsoft.com/en-us/windows/win32/api/d3d12/nf-d3d12-id3d12commandallocator-reset)
- [Texture upload](https://learn.microsoft.com/en-us/windows/win32/direct3d12/upload-and-readback-of-texture-data)
- [Graphics PSO](https://learn.microsoft.com/en-us/windows/win32/direct3d12/managing-graphics-pipeline-state-in-direct3d-12)
- [SRV component mapping](https://learn.microsoft.com/en-us/windows/win32/api/d3d12/ne-d3d12-d3d12_shader_component_mapping)

공식 문서는 API 조건 교차 확인에만 사용했습니다. YamYam 구현의 모든 정책이 일반적 정답이라는 근거로 쓰지 않습니다. 수치 예시는 측정 결과가 아닌 설명용 계산입니다.

## 실제 테스트 기록과 이번 검토의 구분

노션 후속 강의는 2026-09-14 Debug/Release x64 및 WARP·하드웨어 통과, 2026-09-15 실행 캡처와 하드웨어 재검사 이력을 기록합니다. 이는 페이지의 당시 기록입니다. 이번 세션은 테스트 소스를 읽었으며 현재 환경의 성공을 재확인한 것이 아닙니다. 통과 콘솔을 새로 만들어 붙이지 않습니다.

## 새 자료 후보와 권리

매 편 신규 후보 검토 결과는 game-candidates.json에 있습니다. 최근 커비·Celeste·Super Meat Boy·Hollow Knight·Portal 자료를 관성적으로 재사용하지 않고, 직접 만든 색 도형과 새 엔진/코드 조작 구간을 선택했습니다. 외부 그림·영상은 아직 확보하거나 최종본에 넣지 않았습니다. 원본 screenshot의 스프라이트 권리는 별도 확인 전 게시 미승인입니다.

기존 로컬 이미지 Docs/Wiki/DX12_Rendering_Continuation/images/scene-game-views.png와 scene-view.png는 날짜가 있는 실제 실행 참고자료입니다. lesson-texture-path.png는 자체 개념도이며 실제 UI가 아닙니다. 이번에는 이미지를 새로 캡처하거나 영상 파일을 생성하지 않았습니다.
