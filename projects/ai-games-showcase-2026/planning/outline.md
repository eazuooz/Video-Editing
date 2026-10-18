# AI 게임 제작 근황 — 전체 대본과 화면 구성

2026-10-18 수정: 긴 AI 설명 영상은 제외한다. **각 게임의 실행 환경·제작 기반·사용 도구만 PPT 한 장으로 5초씩** 보여 준다. 개발 기간과 사람이 다듬은 내용은 실제 게임 장면 위에서 설명한다. 별도 강의 구조나 60:40 비율을 강제하지 않는다.

**현재 상태:** 전체 한영 대본 수정 완료. PPT와 음성·편집 진행 상태는 [현재 체크포인트](../production/checkpoint.json)에 기록한다. 최종 마스터는 1920×1080/60fps이며 완성본은 Drive에서 먼저 검수한다. 대본·무음 미리보기는 완성 영상이 아니다.

## 실행 환경과 제작 기반

| 게임 | 어디서 실행하는가 | 엔진·프레임워크·플랫폼 | 확인 범위 |
|---|---|---|---|
| [I Just Wanted to Fish](https://store.steampowered.com/app/5350560/I_Just_Wanted_to_Fish/) | Steam 출시 준비 중인 PC 게임 | Unity 6 / HDRP | 플레이 중 AI 미사용은 Steam 안내로 확인. 세부 PC 사양·HDRP 버전 미확정. |
| [Emberfall — Luminati](https://broad-grass-ea4b.supportinfo-593.workers.dev/game) · [레벨 에디터](https://broad-grass-ea4b.supportinfo-593.workers.dev/editor) | 공개 웹페이지에서 실행 | Luminati 편집기·게임 기반 / Three.js 그래픽 라이브러리 | 직접 이동·카메라 회전 확인. 전체 엔진 구현·AI 모델·정확한 기간 미확인. |
| [Nightshoal](https://profactor.itch.io/nightshoal) | Windows 다운로드형 PC 공개 빌드 | Godot 게임 엔진 | pre-demo·개발 중. Godot 세부 버전 및 최소 사양 미확인. |
| [VECTOR: Anti-Gravity Racing](https://wavedash.com/games/vector-anti-gravity-racing) | Wavedash 웹페이지의 브라우저 게임 | Three.js / WebGPU, WebGL 2 대체 경로 | 그래픽 라이브러리·그래픽 API를 엔진/AI와 구분. 모바일 호환 미검증. |
| [AUGURY: Duel of the Gods](https://sybiote.itch.io/augury-duel) | itch.io 웹페이지의 HTML5 브라우저 게임 | Phaser 2D 게임 프레임워크 / TypeScript | 직접 선택·미리보기·확정 조작 확인. 프레임워크 세부 버전 미공개. |
| [Rally Road Rash — Off-Road Championship](https://sandscape.app/play?g=3UpDloEh) | Sandscape 웹페이지의 브라우저 게임 | Sandscape 제작·배포 플랫폼 / 내부 엔진 미확인 | Unity·Unreal·Three.js 중 하나로 임의 확정하지 않음. 모바일 호환 미검증. |

## 개발 기간과 AI 사용 근거

| 게임 | 개발 기간의 의미 | 공개된 모델·AI |
|---|---|---|
| I Just Wanted to Fish | Almost three weeks · Creator's progress report | Claude Opus 5.5 |
| Emberfall — Luminati | 전체 기간 미공개/미확인 · Total development time undisclosed | Claude Opus 5.5 (소개자 언급만 확인·확정 사실로 내레이션하지 않음) |
| Nightshoal | Week 11 · Ongoing project update | Claude Opus 5.5 / Codex Astra |
| VECTOR: Anti-Gravity Racing | 전체 기간 미공개/미확인 · Total duration undisclosed | Opus, exact version undisclosed (소개자 언급만 확인·확정 사실로 내레이션하지 않음) |
| AUGURY: Duel of the Gods | 전체 기간 미공개/미확인 · Total duration undisclosed | 정확한 모델 미공개 |
| Rally Road Rash — Off-Road Championship | About three days · Initial version shown in creator post | Opus 5.5 / Astra 6 |

기간은 제작자가 공개한 해당 단계의 기록이다. 초기 버전 3일, 진행 중 11주 차, 약 3주 작업을 같은 완성 기준으로 비교하지 않는다. [게임별 조사 근거](../sources/research.json)와 [확보 영상 목록](../sources/media.json)을 구분해 보관한다.

## 게임마다 한 번 나오는 5초 요약 PPT

각 화면은 300프레임(60fps), 여섯 장 합계 30초다. 실제 게임 화면 옆에 확인된 환경과 도구를 간단히 나열한다. 한 문장으로 핵심만 말하고 다시 게임으로 돌아간다. 말을 5초에 억지로 압축하지 않으며 필요하면 문장 끝은 돌아온 게임 화면 위로 자연스럽게 잇는다. 제작 기간은 별도 설명하고, 미확인 모델과 내부 엔진은 그대로 표시한다.

| 위치 | 게임 | 5초 동안 표시할 내용 |
|---|---|---|
| 02장 · 3문단 | I Just Wanted to Fish | 실행 환경: PC · Steam 출시 준비<br>게임 엔진: Unity 6 · HDRP<br>AI 코딩: Claude Opus 5.5 · Claude Code<br>제작 도구: Blender MCP · Unity MCP |
| 03장 · 2문단 | Emberfall — Luminati | 실행 환경: 브라우저<br>제작 기반: Luminati · Three.js<br>AI 모델: 정확한 버전 미확인<br>편집 도구: 레벨 에디터 별도 공개 |
| 04장 · 2문단 | Nightshoal | 실행 / 엔진: Windows · Godot<br>AI 코딩: Opus 5.5 · Codex Astra(이전)<br>모델 / 그림: Tripo AI · Blender MCP · OpenAI 이미지 API<br>효과음 / 음악: ElevenLabs · Stable Audio |
| 05장 · 2문단 | VECTOR: Anti-Gravity Racing | 실행 환경: 브라우저<br>그래픽 기반: Three.js · WebGPU / WebGL 2<br>제작 도구: AI 코딩 · Blender<br>AI 모델: 정확한 버전 미확인 |
| 06장 · 2문단 | AUGURY | 실행 환경: 브라우저<br>제작 기반: Phaser · TypeScript<br>이미지 도구: DreamLayer · ImageGen<br>AI 모델: 정확한 버전 미공개 |
| 07장 · 2문단 | Rally Road Rash | 실행 / 제작: 브라우저 · Sandscape<br>AI 코딩: Opus 5.5 · Astra 6<br>모델 / 음악: Meshy · ElevenLabs<br>내부 엔진: 확인되지 않음 |

## 전체 대본

고유명사는 화면 표기로 적었다. 음성 생성용 한글 발음과 화면·자막의 정식 표기는 별도로 관리한다.

### 01. 게임부터 보자

안녕하세요, 얌얌코딩입니다. 물고기를 낚고, 미래의 트랙을 달리고, 신들의 다음 공격을 예측하는 게임. 이 작품들을 만드는 데도 AI가 쓰였습니다.

오늘은 여섯 게임의 실제 모습과 제작자가 공개한 개발 과정을 보겠습니다. 개발 환경과 도구는 게임마다 짧게 정리하고, 빠르게 만든 초기 버전과 계속 다듬고 있는 작품도 구분할게요.

먼저, 바닷속까지 들여다보이는 이 작은 섬으로 가보죠.

화면 구성: 섬의 낚시 → 미래 레이싱 → 전술 선택을 한 화면씩 짧게 보여 준다. 소개의 섬 장면을 02 첫 화면으로 이어받는다.

다음 연결: 개요의 섬을 다음 낚시 장면이 그대로 이어받는다.

### 02. I Just Wanted to Fish

I Just Wanted to Fish는 섬을 돌아다니며 낚시하는 게임입니다. 모래사장에 선 캐릭터가 낚싯대를 드리우고, 얕은 물 아래에는 물고기와 산호가 보이죠. 해변에는 작은 게도 돌아다닙니다.

제작자가 공개한 작업 기간은 거의 삼 주입니다. Steam 출시를 준비 중인 게임의 개발 기록이고, 출시까지 끝냈다는 뜻은 아닙니다.

> **개발 환경·도구 PPT — 5초**
>
> 실제 게임 캡처와 위 표의 도구 목록. 이 문장 시작에 띄우고 5초 뒤 게임 화면으로 복귀한다.

Unity를 기반으로, Opus와 Blender를 제작에 활용했습니다.

제작자는 지형과 배치를 직접 정하고, 참고 그림을 주면서 모델과 움직임을 여러 번 수정했습니다. 캐릭터와 물, 주변 환경을 한 장면으로 맞추는 작업이 쌓인 결과죠. Steam 안내에는 플레이 중에는 AI를 사용하지 않는다고 적혀 있습니다.

이 작품이 PC용 낚시 게임이라면, 다음 작품은 브라우저에서 바로 들어갈 수 있는 작은 세계입니다.

화면 구성: 실제 게임 모습 → 개발 환경·도구 요약 PPT5초 → 같은 게임의 실제 장면과 제작 이야기. 별도 AI 기능 설명 영상 없음.

다음 연결: Unity 기반 PC 게임에서 웹페이지로 들어가는 다음 게임으로 실행 환경을 연결한다.

### 03. Emberfall — Luminati

Emberfall — Luminati입니다. 캐릭터는 도트 그림처럼 보이지만, 집과 길이 놓인 공간은 카메라를 돌려서 다른 각도로 볼 수 있습니다. 작은 모형 마을 같은 느낌이죠.

> **개발 환경·도구 PPT — 5초**
>
> 실제 게임 캡처와 위 표의 도구 목록. 이 문장 시작에 띄우고 5초 뒤 게임 화면으로 복귀한다.

브라우저에서 실행하고, Three.js를 기반으로 만들었습니다.

게임 플레이 페이지와 레벨 에디터가 따로 공개되어 있습니다. 플레이 화면에서는 캐릭터를 움직이고 카메라를 돌릴 수 있고, 에디터에서는 지형 높이와 물건, 조명을 다룹니다. 두 링크는 설명란에 구분해 둘게요.

정확한 AI 모델 버전과 전체 개발 기간은 확인되지 않았습니다. 작은 세계의 모습을 봤다면, 다음에는 그 안에 이야기와 여러 시스템을 쌓아 가는 게임을 보죠.

화면 구성: 실제 게임 모습 → 개발 환경·도구 요약 PPT5초 → 같은 게임의 실제 장면과 제작 이야기. 별도 AI 기능 설명 영상 없음. 본게임·에디터를 구분 표시한다.

다음 연결: 작은 세계의 공간 구성에서 그 안에 이야기·시스템을 채우는 Nightshoal로 넘어간다.

### 04. Nightshoal

Nightshoal도 낚시와 탐험을 다루지만, 분위기는 다릅니다. 절벽과 숲 사이로 물길이 이어지고, 배가 그 안을 지나갑니다.

> **개발 환경·도구 PPT — 5초**
>
> 실제 게임 캡처와 위 표의 도구 목록. 이 문장 시작에 띄우고 5초 뒤 게임 화면으로 복귀한다.

Godot를 기반으로, 코드와 그래픽, 소리에 AI를 나누어 썼습니다.

Windows용 공개 빌드가 있고, 제작자가 공개한 개발 기록은 십일 주 차입니다. 퀘스트와 이야기, 낚시와 인벤토리 시스템을 계속 더하고 있어요.

여러 도구의 결과를 한 게임으로 연결하면서 지도와 기능도 다시 다듬고 있습니다. 이번에는 이렇게 채운 세계를 떠나, 조작에 빠르게 반응하는 레이싱을 보겠습니다.

화면 구성: 실제 게임 모습 → 개발 환경·도구 요약 PPT5초 → 같은 게임의 실제 장면과 제작 이야기. 별도 AI 기능 설명 영상 없음.

다음 연결: 세계 채우기에서 빠르게 움직일 때 필요한 조작·화면 반응으로 초점을 옮긴다.

### 05. VECTOR: Anti-Gravity Racing

VECTOR: Anti-Gravity Racing입니다. 공중에 뜬 기체로 코너를 통과하고, 가속 구간을 밟으며 다른 기체와 순위를 겨룹니다.

> **개발 환경·도구 PPT — 5초**
>
> 실제 게임 캡처와 위 표의 도구 목록. 이 문장 시작에 띄우고 5초 뒤 게임 화면으로 복귀한다.

Three.js 기반의 브라우저 게임이며, AI로 코딩했습니다.

제작자는 WebGPU를 사용하고, 지원하지 않는 환경에는 WebGL 2 방식도 마련했다고 설명합니다. 둘 다 브라우저에서 화면을 그리는 데 쓰는 기능입니다. 모델 제작에는 Blender를 사용하도록 AI에 요청했다고 해요.

정확한 개발 기간과 AI 모델 버전은 공개 자료로 확정할 수 없었습니다. 다음 게임은 이 속도감과 반대로, 시간을 멈추고 한 수씩 생각하게 만듭니다.

화면 구성: 실제 게임 모습 → 개발 환경·도구 요약 PPT5초 → 같은 게임의 실제 장면과 제작 이야기. 별도 AI 기능 설명 영상 없음.

다음 연결: 빠른 레이싱 입력과 시간을 멈추는 전술 선택을 대비한다.

### 06. AUGURY: Duel of the Gods

AUGURY는 행동을 고르는 동안 시간이 멈추는 신들의 결투 게임입니다. 이동을 선택하면 초록색 모습으로 예상 위치를 보여 주고, 선택을 확정하면 결과가 진행됩니다. 상대의 다음 행동을 예상하는 판단이 중심이죠.

> **개발 환경·도구 PPT — 5초**
>
> 실제 게임 캡처와 위 표의 도구 목록. 이 문장 시작에 띄우고 5초 뒤 게임 화면으로 복귀한다.

Phaser로 만들었고, 이미지 제작에는 DreamLayer 등을 썼습니다.

웹페이지에서 바로 플레이할 수 있습니다. 제작 기록을 보면 생성한 그림의 배경을 지우고, 크기와 색을 정리하고, 몸과 소품의 겹치는 순서와 움직임을 맞췄어요. 한 장의 그림을 게임에서 읽히는 캐릭터로 바꾼 겁니다.

전체 개발 기간과 정확한 모델 버전은 확인되지 않았습니다. 이런 손질이 필요하다는 점은, 다음 게임의 짧은 제작 기간을 볼 때도 기억할 만합니다.

화면 구성: 실제 게임 모습 → 개발 환경·도구 요약 PPT5초 → 같은 게임의 실제 장면과 제작 이야기. 별도 AI 기능 설명 영상 없음. 이동 전→예상 위치→확정 후 실제 캡처의 상태 순서이며 연속 녹화처럼 꾸미지 않는다.

다음 연결: 이미지 후처리의 실제 작업을 이어받아 다음 게임의 초기 3일이라는 기간을 해석한다.

### 07. Rally Road Rash

Rally Road Rash는 흙길에서 차량이 부딪치고, 점프대를 넘고, 로켓까지 사용하는 레이싱 게임입니다. 제작자는 약 사흘 만에 초기 버전을 만들었다고 밝혔습니다.

> **개발 환경·도구 PPT — 5초**
>
> 실제 게임 캡처와 위 표의 도구 목록. 이 문장 시작에 띄우고 5초 뒤 게임 화면으로 복귀한다.

Sandscape에서 만들었고, Opus와 Astra를 나누어 썼습니다.

브라우저에서 실행하며, 제작자는 Opus에 차량과 물리를, Astra에 화면을 다듬는 작업을 맡겼다고 설명합니다. 주요 차량과 소품에는 Meshy를 사용했고요.

제작자는 레벨을 직접 편집했고, 이십오 년의 경험이 있다고 밝혔습니다. 오토바이의 물리 동작도 계속 다듬는 중이었어요. 사흘은 이런 초기 버전의 기록입니다.

그래서 여섯 게임을 나란히 보면, 제작 기간의 숫자보다 더 분명하게 보이는 변화가 있습니다.

화면 구성: 실제 게임 모습 → 개발 환경·도구 요약 PPT5초 → 같은 게임의 실제 장면과 제작 이야기. 별도 AI 기능 설명 영상 없음.

다음 연결: 기간 숫자의 한계를 짚은 뒤 여섯 게임에 공통된 도구 역할과 인간의 판단으로 정리한다.

### 08. 어디까지 왔을까

AI가 쓰인 곳이 코드에만 머물지 않습니다. 모델과 그림, 움직임과 소리까지 제작에 연결되고, 그 결과를 직접 조작할 수 있는 게임도 나오고 있습니다.

같은 AI 게임이라는 말 안에서도, 생성한 것을 골라 게임에 맞게 고치는 과정은 서로 달랐죠. 어떤 도구를 썼는지와 함께 무엇을 만들고 어떻게 다듬었는지를 보면, 지금의 변화를 더 잘 볼 수 있습니다.

오늘 내용은 이천이십육 년 시월 십팔 일에 확인한 공개 자료 기준입니다. 게임과 제작 기록 링크는 설명란에 정리해 둘게요. 여러분은 어떤 게임을 직접 해 보고 싶으신가요?

화면 구성: 여섯 게임의 서로 다른 결과를 순서대로 회고. 실행 기반과 제작 AI를 두 역할로 정리하며 새 게임이나 확인되지 않은 AI를 추가하지 않는다.

다음 연결: 게임 링크 안내와 참여 질문 뒤 기존 회원 엔딩으로 이어진다.

## AI·기술 설명의 공식 근거

- [Claude Opus](https://www.anthropic.com/claude/opus): Anthropic의 코드 작성·추론 모델. 실제 게임 사용 버전은 제작자 기록으로 별도 확인.
- [Claude Code 공식 문서](https://code.claude.com/docs/en/overview): 프로젝트 파일 읽기·수정, 명령 실행을 수행하는 코딩 도구.
- [Model Context Protocol 공식 소개](https://modelcontextprotocol.io/docs/2026-07-28/getting-started/intro): AI 애플리케이션과 외부 도구를 연결하는 규격. AI 모델 자체가 아님.
- [Unity HDRP 공식 문서](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.0/manual/index.html): High Definition Render Pipeline의 역할. 문서 버전을 게임의 패키지 버전으로 추정하지 않음.
- [Three.js 공식 저장소](https://github.com/mrdoob/three.js): JavaScript 3D 그래픽 라이브러리이며 WebGL/WebGPU 렌더러 제공.
- [Phaser 공식 저장소](https://github.com/phaserjs/phaser): 브라우저용 HTML5 2D 게임 프레임워크. 게임의 실제 모바일 지원 여부는 별개.
- [OpenAI Codex·코드 생성 공식 문서](https://developers.openai.com/api/docs/guides/code-generation): Codex는 코드 작성·검토·디버깅을 수행하는 코딩 에이전트.
- [GPT-6 Astra 공식 모델 문서](https://developers.openai.com/api/docs/models/gpt-6-astra): 코드 작성과 복잡한 추론에 사용하는 모델. 제작자의 구체적인 API 스냅샷을 확정하지 않음.
- [Tripo AI 공식 제품 소개](https://www.tripo3d.ai/): 문장·이미지에서 3D 모델 생성. 게임별 사용 세부 버전은 미공개.
- [OpenAI 이미지 생성 공식 문서](https://developers.openai.com/api/docs/guides/image-generation): 문장·이미지 입력으로 이미지 생성·수정. 현재 문서의 최신 모델명을 Nightshoal 사용 모델로 대입하지 않음.
- [ElevenLabs 효과음 생성](https://elevenlabs.io/sound-effects): 글로 원하는 효과음을 설명해 생성하는 기능. 음원 사용 조건은 실제 확보 단계에서 별도 확인.
- [Stability AI Stable Audio](https://stability.ai/stable-audio): 스타일·분위기 설명을 통한 음악 생성 기능. 최신 제품 버전을 Nightshoal 사용 버전으로 대입하지 않음.
- [DreamLayer 공식 게임잼 안내](https://itch.io/jam/dreamlayer-jam-1): 이미지 모델을 선택해 창작 작업을 수행하는 에이전트와 캐릭터 참조 이미지 사용. 게임 엔진·정확한 기반 모델명과 구분.
- [Meshy 공식 제품 소개](https://www.meshy.ai/): 문장·이미지 기반 3D 모델 생성. 실제 게임의 메시/주행 동작까지 자동 완성했다고 주장하지 않음.
- [Sandscape 공식 소개](https://sandscape.app/): 요청·시각 편집·코드 수정·공유를 제공하는 브라우저 게임 제작 플랫폼. 내부 엔진은 확인되지 않음.
- [ElevenLabs 음악 생성](https://elevenlabs.io/music): 스타일·장르 등에 따른 음악 생성 기능. Rally의 정확한 사용 모델 버전은 미공개.

## 제작 상태

- 완료: 여섯 게임 조사, 전체 한영 대본 32문단, 실행 환경·엔진 구분, 5초 요약 PPT 여섯 장의 내용·위치 설계. 긴 AI 기능 소개 삭제.
- 확보: 네 게임의 FHD 이상 영상과 두 브라우저 게임의 FHD 화면. 기존 12초 무음 화면 샘플은 배치 검수 범위만 유효.
- 제작: 실제 게임 캡처를 포함한 PPT 여섯 장과 편집용 프레임 준비, 실제 게임 컷 검수. 상세 상태는 체크포인트를 기준으로 한다.
- 음성: 사용자의 이전 지시에 따라 게임·Unity 사용 종료/GPU 인계 확인 대기. 새 음성·완성 편집·최종 QA는 아직 완료되지 않음.
- 완성 후: clean/captioned/KO/EN 출력과 Drive 검수본. 사용자 검수 이후 같은 버전의 YouTube 업로드. 자동 다음 편 없음.
