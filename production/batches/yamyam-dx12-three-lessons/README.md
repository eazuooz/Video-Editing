# YamYam Engine DX12 세 편의 전체 대본

노션의 세 강의와 `D:/Github/YamYam_Engine`의 현재 구현을 확인해, 각각 독립적인 한국어 영상 대본으로 구성했습니다. 각 편은 10개 장면이며 전체 발화문, 실제 개발 화면의 촬영 지시, 흰색 2.5D 설명 연출, 코드 위치를 함께 제공합니다. 예상 길이는 각 10~14분입니다. 음성 실측과 최종 영상 제작은 아직 진행하지 않았습니다.

## 편별 대본

| 순서 | 영상 주제와 전체 검토본 | 설명할 질문 | 낭독용 대본 |
|---|---|---|---|
| 1 | [DX12 프레임 동기화와 ImGui 렌더링](../../../projects/yamyam-dx12-frame-sync/script/review.ko.md) | CPU가 다음 프레임을 준비할 때 GPU가 쓰던 공간을 언제 다시 사용할까 | [전체 발화문](../../../projects/yamyam-dx12-frame-sync/script/narration.ko.md) |
| 2 | [DX12 Texture와 RenderTarget으로 Scene과 Game 뷰 만들기](../../../projects/yamyam-dx12-texture-views/script/review.ko.md) | 같은 장면을 두 카메라로 그리고 에디터 패널 안에 어떻게 표시할까 | [전체 발화문](../../../projects/yamyam-dx12-texture-views/script/narration.ko.md) |
| 3 | [DX12 PSO로 렌더링 모드와 ImGui 화면 합성하기](../../../projects/yamyam-dx12-pso-composition/script/review.ko.md) | 재질의 투명도와 완성된 화면의 알파와 자원 수명을 어떻게 나눌까 | [전체 발화문](../../../projects/yamyam-dx12-pso-composition/script/narration.ko.md) |

각 장면은 눈에 보이는 문제로 시작해, 원리와 실제 구현을 연결하고 직접 만들어 볼 순서로 끝납니다. 추상 용어를 먼저 길게 나열하지 않고 작업 지시서, 두 슬롯의 서랍, 카메라별 그림판, 읽기 창과 같은 도형으로 의미를 설명합니다. 코드가 나타날 때는 화면의 어느 동작과 연결되는지 함께 짚습니다.

## 노션 페이지와 최신 커밋의 관계

검토한 페이지는 다음 세 개입니다.

- [Dx12 Frame, imgui rendering 동기화](https://www.notion.so/3400b1ffa61e8054a80bc1d4b575b515)
- [DX12 Texture·RenderTarget 구현과 Scene / Game 뷰 연결](https://www.notion.so/3dc0b1ffa61e814e9e8bd403ca145ebe)
- [DX12 렌더링 모드 복구와 ImGui 화면 합성 완성](https://www.notion.so/3dc0b1ffa61e8153b02fd321cc48e655)

현재 로컬 HEAD는 `845442b7d756e7a991c09799ab58a775803a006a`입니다. 최근 세 커밋은 `845442b` 문서 묶음, `ce56f16` PSO·표시용 SRV, `49e04e5` 프레임 동기화·에디터 렌더링입니다. 문서 묶음 안에 후속 두 강의가 있고 동기화 페이지가 이를 연결하므로, 커밋 하나당 기능 한 개로 억지로 나누지 않고 위 세 페이지의 학습 흐름을 따랐습니다.

엔진 파일을 수정하거나 다른 커밋으로 체크아웃하지 않았습니다. 현재 소스, 관련 diff, 프로젝트의 기존 참고자료를 읽었습니다. 기존 `projects/yamyam-dx12-rendering`의 통합 개발기 초안도 보존하고 새 세 편을 별도로 만들었습니다.

첫 노션 페이지는 맨 위 임베드 하나를 커넥터가 해석하지 못해 `truncated=true`와 `unknown_block_count=1`을 반환했습니다. 읽을 수 있는 본문과 마지막 연결, 로컬 동기화 문서, 실제 함수를 검토했습니다. 그 임베드 영상 전체를 시청했다는 의미는 아닙니다.

## 2.5D 화면 구성

채널 원본 고양이 인트로 뒤에 실제 엔진·코드·디버거·자체 색 도형의 새 개발 자료를 화면 전체로 표시하고, 해당 원리는 흰 연구 발표형 2.5D 장면으로 이어 설명합니다. 검은 실제 에디터 UI는 그대로 보존하지만 자체 설명은 공유 `research-paper.ts` 테마를 사용합니다.

| 편 | 깊이와 움직임으로 보여 줄 핵심 | 제작 수단 |
|---|---|---|
| 1 | 서로 다른 CPU/GPU 시간 축, 슬롯별 잠금 해제, 번호 저장 후 다음 인덱스 이동, 별도 창의 마지막 소비 | Motion Canvas의 원근 판·서랍·레일·표식 애니메이션 |
| 2 | 한 장면과 두 카메라, Upload 행 패딩, Texture와 RTV/SRV, 256바이트 칸과 페이지 경계, Game/Scene 리사이즈 시점 | Motion Canvas의 그림판·포트·주소 칸·투영 비교 |
| 3 | 같은 alpha의 세 모드, Material별 PSO 선택, 반투명 판 순서, 두 번 합성되는 RGB, 같은 원본의 두 SRV, 마지막 Fence 뒤 반환 | Motion Canvas 중심, 깊이·카메라·반투명 판은 선택적 Manim ThreeDScene |

PPT처럼 보이는 설명 화면도 텍스트만 고정해 나열하지 않습니다. 판의 두께, 겹침, 원근, 투영 그림자와 실제 의미가 있는 이동을 장면마다 지정했습니다. 생성형 이미지 없이 직접 제작할 도형으로 설명할 수 있습니다. 각 장면의 구체적인 동작과 발화 연결은 검토본과 `planning/storyboard.json`에 있습니다.

본편 전체는 실제 개발 자료 60%와 자체 설명 40%를 목표로 계획했습니다. 장면별 비율은 다르게 배분했습니다. 새 영상이나 음성의 길이가 확정되면 자연스럽게 다시 맞추며, 원본을 반복하거나 인위적으로 느리게 만들어 시간을 채우지 않습니다. 현재 계획 타임코드는 TTS/SRT의 확정 타이밍이 아닙니다.

마지막에는 원본 회원 프로필·표시 이름·배지를 함께 보존한 10초 감사 씬을 한 번 계획했습니다. 제목은 `멤버쉽가입 감사드립니다.`이며 별도 발화나 SRT cue는 넣지 않습니다. 원본 이미지와 명단 확인은 렌더 전에 진행합니다.

## 코드 확인으로 대본에 반영한 구분

Allocator 재사용에는 이전 GPU 사용 완료가 필요합니다. Command List Close, Present, Resource Barrier는 각각 이 완료 확인과 역할이 다릅니다. Game-only도 다음 슬롯의 이전 사용을 기다리므로 CPU/GPU 겹침이 가능합니다. 일부 Signal/Wait 반환값 검사는 여전히 보완할 부분입니다.

카메라별 행렬의 메모리를 Draw마다 보존합니다. 현재 Transform 데이터는 192바이트, 시작 간격은 256바이트이며 64KiB 페이지당 256 Draw입니다. Scene/Game 단위로 렌더 결과를 나누는 구현이며 모든 게임 카메라가 전용 RT를 가진 구조라고 설명하지 않았습니다.

현재 Transparent는 `Always`와 깊이 기록 끔 정책을 유지합니다. 불투명 벽 뒤에서도 합성될 수 있는 동작을 모든 3D 엔진의 정답으로 소개하지 않습니다. 표시 SRV는 원본 RGB와 알파 1을 읽으며 원본 픽셀을 수정하지 않습니다. Resource와 descriptor는 프레임의 마지막 소비를 덮는 Fence가 완료된 뒤 반환합니다.

각 편의 `sources/code-evidence.json`에는 확인 범위의 실제 코드와 파일 SHA-256을 보관했습니다. 코드 위치와 출처는 제작 검토 문서에 남기며 공개 설명란의 출처 문구와 혼동하지 않습니다. 공식 API 조건도 [Microsoft의 Allocator Reset 설명](https://learn.microsoft.com/en-us/windows/win32/api/d3d12/nf-d3d12-id3d12commandallocator-reset), [텍스처 업로드](https://learn.microsoft.com/en-us/windows/win32/direct3d12/upload-and-readback-of-texture-data), [PSO 역할](https://learn.microsoft.com/en-us/windows/win32/direct3d12/managing-graphics-pipeline-state-in-direct3d-12), [SRV component mapping](https://learn.microsoft.com/en-us/windows/win32/api/d3d12/ne-d3d12-d3d12_shader_component_mapping)과 교차 확인했습니다.

## 실제 화면과 검증의 상태

기존 `scene-game-views.png`, `scene-view.png`, `lesson-texture-path.png`를 확인했습니다. 앞의 두 이미지는 노션에서 2026-09-15 실행 캡처로 설명한 참고자료이고 마지막 이미지는 개념도입니다. 새 촬영이나 영상 다운로드는 진행하지 않았습니다. 영상 분량은 기존 정지 화면을 늘리는 대신 장면마다 새로운 엔진 조작·코드 추적·테스트 예시를 촬영할 계획입니다.

노션은 2026-09-14/15 빌드와 테스트 기록을 제공합니다. 이번 검토는 테스트 소스를 읽었으며 현재 환경에서 다시 빌드하거나 실행한 검증은 아닙니다. 303 Draw, 두 카메라, 픽셀·깊이·정렬·ImGui 합성 검사 범위를 대본에 반영했습니다. 해당 ImGui 테스트는 multi-viewport를 끄므로 별도 OS 창의 도킹·분리·복귀와 입력은 수동 검수가 남습니다.

최근 게임·자료 사용 이력을 확인했고, 커비·Celeste·Super Meat Boy·Hollow Knight·Portal의 기존 클립은 이 엔진 내부 구현을 보여 주는 예시로 선택하지 않았습니다. 직접 만든 단색·마스크·반투명 도형과 새 YamYam 소스/실행 구간을 우선합니다. 후보·제외 이유와 권리는 각 편의 `sources/game-candidates.json`에 있습니다. 기존 실행 캡처의 스프라이트 권리는 게시 전에 별도 확인해야 합니다.

## 수정 기준 파일

발화문은 각 프로젝트의 `script/narration.ko.json`, 화면 연출은 이 배치의 `plan.json`이 기준입니다. 수정한 뒤 다음 명령으로 낭독용 문서·전체 검토본·스토리보드·편집 큐·출처·프로젝트 매니페스트를 다시 만듭니다.

```powershell
node production/batches/yamyam-dx12-three-lessons/build-review.cjs
node scripts/build-rebuild-manifests.cjs yamyam-dx12-frame-sync
node scripts/build-rebuild-manifests.cjs yamyam-dx12-texture-views
node scripts/build-rebuild-manifests.cjs yamyam-dx12-pso-composition
```

현재 요청 범위는 대본과 화면 계획입니다. TTS, KO/EN SRT, 실제 PPTX, Motion Canvas 씬 구현, Manim 클립, 최종 렌더와 업로드는 시작하지 않았습니다. 대본 검토 이후 저장소의 목소리·음악 승인 순서와 실제 화면 검수를 이어갈 수 있도록 상태를 분리해 두었습니다.
