# DX12 프레임 동기화와 ImGui 렌더링 출처와 구현 확인

검토일 2026-10-01. 현재 엔진 HEAD는 845442b7d756e7a991c09799ab58a775803a006a입니다. 소스코드와 노션에서 읽을 수 있는 본문을 검토했으며 이번 세션에서 엔진 빌드·테스트·실행은 하지 않았습니다.

## 노션과 커밋 연결

- [해당 강의](https://www.notion.so/3400b1ffa61e8054a80bc1d4b575b515)
- 최신 문서 커밋 [845442b](https://github.com/eazuooz/YamYam_Engine/commit/845442b7d756e7a991c09799ab58a775803a006a)는 문서 묶음이며 엔진 기능 한 개를 추가한 커밋이 아닙니다.
- 구현은 주로 [49e04e5](https://github.com/eazuooz/YamYam_Engine/commit/49e04e5e875f04cfb792ea8a71e10667be78ad41)와 [ce56f16](https://github.com/eazuooz/YamYam_Engine/commit/ce56f16dd7a40fd2b4bf03c680790e5b637c7530)에 연결됩니다.
- 역사적 동기화 사례 일부는 이전 7ac7ef2에도 연결됩니다. 과거의 Reset 뒤 Wait 오류를 49e04e5에서 처음 고쳤다고 대본에 단정하지 않았습니다.

첫 페이지 fetch는 truncated=true, unknown_block_count=1입니다. 맨 위 external_object_instance 임베드를 도구가 해석하지 못했습니다. 반환 본문의 마지막 연결까지 검토하고 local Docs/DX12_FrameLoop_And_Fence.md와 실제 소스도 대조했습니다. 기존 임베드 영상 전체를 시청했다고 주장하지 않습니다.

## 직접 확인한 코드

범위별 발췌와 파일 SHA-256은 code-evidence.json에 보관합니다. 전체 코드 경로와 행 번호는 대본의 각 장면에 연결했습니다. 다음 사실은 현재 소스 범위로 확인했습니다.

- WaitForNextFrameResources는 현재 mFrameIndex의 슬롯을 조회하며 증가시키지 않습니다. Editor main에서 Reset보다 먼저 호출합니다.
- SignalFrameCompletion은 실제 사용한 슬롯의 FenceValue를 저장한 뒤 SwapChain 인덱스를 조회합니다.
- Game-only의 MoveToNextFrame도 다음 슬롯의 이전 사용만 기다리므로 CPU/GPU 작업 겹침이 가능합니다.
- Editor 최종 Signal은 main list, 추가 OS 창, main Present 뒤에 놓입니다. 로컬 ImGui backend는 engine queue를 사용하며 추가 창의 allocator 등은 별도로 관리합니다.
- SignalFrameCompletion/WaitForNextFrameResources 등에 일부 HRESULT·Wait 반환값 검사가 빠져 있습니다. 실패 안전성까지 완성됐다고 말하지 않습니다.

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
