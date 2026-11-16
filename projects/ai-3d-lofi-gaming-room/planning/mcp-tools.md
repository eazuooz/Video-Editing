# 3D LOFI 방: 도구 실행 기록과 MCP 확장

기존 10개 후보는 제작 과정의 역할을 비교하는 목록이다. 모든 도구를 실행했다는 뜻으로 소개하지 않는다. 현재 캐릭터·소품 첫 샘플에 실제 사용한 것은 이미지 생성, Tripo Studio, Codex, Unity, Unity 공식 CLI·MCP, FFmpeg다.

| 도구 | 역할 | 이번 샘플의 실제 상태 |
|---|---|---|
| 이미지 생성 | 방 콘셉트, 중립 A 포즈 캐릭터, 헤드폰 참고 이미지 | 생성·검수 완료. 참고 이미지는 실행 중인 게임 화면과 구분 |
| Tripo Studio H3.1 | 이미지→3D, 리토폴로지, 휴머노이드 리깅, 걷기·대기 프리셋, FBX 내보내기 | 유료 Studio 계정에서 실제 실행, 175크레딧 사용 |
| Codex | 실제 단위의 방, 상호작용, 재질 연결, 동작 검수와 제작 기록 | C# 구현 완료. 방 가구는 직접 작성한 형상이며 Tripo 결과물로 소개하지 않음 |
| Unity 6000.6 / URP | 방 조립, 조명·날씨, 휴머노이드 동작, Windows 샘플 | 실제 임포트·실행·빌드. WebGL은 사용자 요청으로 뒤로 미룸 |
| **Unity 공식 CLI + Pipeline MCP** | 프로젝트를 지정해 모델 임포트, C# 실행, 씬 생성, Play, 상태 조회, FHD 캡처와 빌드 명령 호출 | **연결·실행 완료**. CLI 1.0.0-beta.13 / com.unity.pipeline 1.0.0. 다른 Unity 프로젝트는 조작하지 않음 |
| FFmpeg CLI | Unity가 직접 렌더한 1920×1080/60프레임을 인코딩, 자막·기존 CC0 음악 합성, 파일 검사 | 실제 사용. MCP 서버를 따로 설치한 것으로 표현하지 않음 |
| Meshy / Meshy 공식 MCP | 대체 이미지→3D와 모델 처리 비교 후보 | 공식 지원 확인, **설치·연결·생성 미실행**. 별도 계정·크레딧 확인 전 실행하지 않음 |
| ComfyUI + Hunyuan3D | 재현 가능한 노드 기반 3D 생성 후보 | 미실행. 버전별 로컬/클라우드 범위를 구분 |
| Blockbench | 규격 중심 저폴리 가구 편집 후보 | 미실행. 현재 방은 Unity C# 형상으로 제작 |
| Material Maker | 반복 가능한 절차적 나무·직물 재질 후보 | 미실행. 현재 단순 URP 재질을 제작 |
| Adobe Mixamo | 추가 검수된 걷기·앉기 동작 후보 | **Adobe 서비스 미사용**. Tripo의 “Mixamo 스켈레톤/FBX 프리셋” 선택과 구분 |
| DeepMotion | 직접 촬영한 동작의 모션 캡처 후보 | 미실행. 이번 샘플은 Tripo 기본 프리셋 사용 |

MCP를 많이 설치하는 것보다, 모델 생성과 엔진 실행에 필요한 인터페이스를 검증하는 것을 우선한다. Unity 공식 연결 하나로 씬·코드·실행·캡처·빌드를 처리한다. 기존 Blender 제외 결정과 Unity 우선 결정을 유지한다.

Tripo Studio 구독 크레딧과 Tripo API 크레딧은 별개다. 이번에는 이미 결제한 Studio를 사용했고 API 키를 추출하거나 API 크레딧을 추가 구매하지 않았다. 조사 중인 MCP 도구를 이번 샘플의 실행 사례로 꾸미지 않는다.

## 영상에 넣을 실제 흐름

참고 이미지 → Tripo 생성 결과 → 고밀도 원본과 리토폴로지 수치 → 리깅/기본 걷기·대기 → FBX → Unity 재질/크기 → 실제 root motion 거리 → 바닥 접촉/카메라 수정 → 실행 파일. 도구별 프롬프트·입력, 실제 출력, 수정 전후를 같은 소품과 캐릭터로 연결한다. 앉기·독서·메모 UI 및 최종 웹 게임은 별도 다음 구현 단계이며 첫 샘플에서 완료했다고 말하지 않는다.

## 근거

- [Unity 공식 CLI](https://docs.unity.com/en-us/unity-cli)
- [Unity Pipeline 설치·프로젝트별 연결](https://docs.unity.com/en-us/unity-cli/unity-pipeline/unity-pipeline-package)
- [Meshy 공식 MCP 소개](https://www.meshy.ai/mcp)
- [Meshy 공식 MCP 소스](https://github.com/meshy-dev/meshy-mcp-server)
- [Tripo Studio 구독과 API 구분](https://www.tripo3d.ai/help/api-plugins/tripo-studiotripo-api)
